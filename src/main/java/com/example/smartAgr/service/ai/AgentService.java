package com.example.smartAgr.service.ai;

import com.example.smartAgr.config.LLMConfig;
import com.example.smartAgr.model.ai.AgentResponse;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.extern.slf4j.Slf4j;
import okhttp3.*;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import javax.annotation.PostConstruct;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CopyOnWriteArrayList;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Slf4j
@Service
public class AgentService {

    private final LLMConfig llmConfig;
    private final List<AgentTool> tools;
    private final ObjectMapper objectMapper = new ObjectMapper();

    private final ConcurrentHashMap<String, List<Map<String, Object>>> conversations = new ConcurrentHashMap<>();
    private static final int MAX_HISTORY = 30;
    private static final long SSE_TIMEOUT = 5 * 60 * 1000L;

    private OkHttpClient httpClient;
    private String systemPrompt;

    public AgentService(LLMConfig llmConfig, List<AgentTool> tools) {
        this.llmConfig = llmConfig;
        this.tools = tools;
    }

    @PostConstruct
    public void init() {
        this.httpClient = new OkHttpClient.Builder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(120, TimeUnit.SECONDS)
                .writeTimeout(60, TimeUnit.SECONDS)
                .build();
        this.systemPrompt = llmConfig.getSystemPrompt() != null
                ? llmConfig.getSystemPrompt()
                : "你是智慧农业管理系统的 AI 助手，擅长农业遥感分析和农情诊断。";
        log.info("AgentService initialized with {} tools: {}",
                tools.size(), tools.stream().map(AgentTool::getName).collect(Collectors.joining(", ")));
    }

    /**
     * 非流式对话 - 完整返回回答
     */
    public String chat(String sessionId, String userMessage) throws Exception {
        List<Map<String, Object>> messages = getOrCreateHistory(sessionId);
        messages.add(buildMessage("user", userMessage));

        int maxIterations = 10;
        for (int i = 0; i < maxIterations; i++) {
            AgentResponse response = callLlmWithTools(messages);

            if (response.hasToolCalls()) {
                Map<String, Object> assistantMsg = new HashMap<>();
                assistantMsg.put("role", "assistant");
                assistantMsg.put("content", response.getContent() != null ? response.getContent() : "");
                assistantMsg.put("tool_calls", serializeToolCalls(response.getToolCalls()));
                messages.add(assistantMsg);

                for (AgentResponse.ToolCall tc : response.getToolCalls()) {
                    String result = executeTool(tc.getName(), tc.getArguments());
                    Map<String, Object> toolMsg = new HashMap<>();
                    toolMsg.put("role", "tool");
                    toolMsg.put("tool_call_id", tc.getId());
                    toolMsg.put("content", result);
                    messages.add(toolMsg);
                }
            } else {
                String content = response.getContent();
                messages.add(buildMessage("assistant", content));
                trimHistory(messages);
                return content;
            }
        }
        return "抱歉，处理过程过于复杂，请尝试简化您的问题。";
    }

    /**
     * 流式对话 - SSE 推送 token 和工具调用状态
     */
    public SseEmitter chatStream(String sessionId, String userMessage) {
        SseEmitter emitter = new SseEmitter(SSE_TIMEOUT);

        new Thread(() -> {
            try {
                List<Map<String, Object>> messages = getOrCreateHistory(sessionId);
                messages.add(buildMessage("user", userMessage));

                int maxIterations = 10;
                for (int i = 0; i < maxIterations; i++) {
                    sendSseEvent(emitter, "step", mapOf("step", String.valueOf(i + 1)));
                    AgentResponse response = streamLlmCall(messages, emitter);

                    if (response.hasToolCalls()) {
                        String thought = response.getContent();
                        if (thought != null && !thought.trim().isEmpty()) {
                            sendSseEvent(emitter, "thought", mapOf("content", thought));
                        }
                        Map<String, Object> assistantMsg = new HashMap<>();
                        assistantMsg.put("role", "assistant");
                        assistantMsg.put("content", response.getContent() != null ? response.getContent() : "");
                        assistantMsg.put("tool_calls", serializeToolCalls(response.getToolCalls()));
                        messages.add(assistantMsg);

                        for (AgentResponse.ToolCall tc : response.getToolCalls()) {
                            sendSseEvent(emitter, "tool_start", mapOf("tool_name", tc.getName()));
                            String result = executeTool(tc.getName(), tc.getArguments());
                            sendSseEvent(emitter, "tool_result", mapOf("tool_name", tc.getName(), "result_preview",
                                    result.length() > 200 ? result.substring(0, 200) + "..." : result));

                            Map<String, Object> toolMsg = new HashMap<>();
                            toolMsg.put("role", "tool");
                            toolMsg.put("tool_call_id", tc.getId());
                            toolMsg.put("content", result);
                            messages.add(toolMsg);
                        }
                    } else {
                        String content = response.getContent();
                        messages.add(buildMessage("assistant", content));
                        trimHistory(messages);
                        sendSseEvent(emitter, "done", emptyMap());
                        emitter.complete();
                        return;
                    }
                }
                sendSseEvent(emitter, "token", mapOf("content", "抱歉，处理过程过于复杂，请尝试简化您的问题。"));
                sendSseEvent(emitter, "done", emptyMap());
                emitter.complete();
            } catch (Exception e) {
                log.error("Agent stream error", e);
                try {
                    sendSseEvent(emitter, "token", mapOf("content", "错误: " + e.getMessage()));
                    sendSseEvent(emitter, "done", emptyMap());
                    emitter.complete();
                } catch (Exception ex) {
                    emitter.completeWithError(ex);
                }
            }
        }).start();

        emitter.onTimeout(() -> log.warn("SSE emitter timeout for session {}", sessionId));
        emitter.onError(e -> log.warn("SSE emitter error for session {}", sessionId));

        return emitter;
    }

    /**
     * 获取工具列表
     */
    public List<Map<String, String>> listTools() {
        return tools.stream().map(t -> {
            Map<String, String> info = new HashMap<>();
            info.put("name", t.getName());
            info.put("description", t.getDescription());
            return info;
        }).collect(Collectors.toList());
    }

    /**
     * 清除会话历史
     */
    public void clearConversation(String sessionId) {
        conversations.remove(sessionId);
    }

    // ========== 内部方法 ==========

    private AgentResponse callLlmWithTools(List<Map<String, Object>> messages) throws Exception {
        String requestBody = buildRequestBody(messages, false);
        Request request = new Request.Builder()
                .url(llmConfig.getBaseUrl() + llmConfig.getChatEndpoint())
                .header("Authorization", "Bearer " + llmConfig.getApiKey())
                .header("Content-Type", "application/json")
                .post(RequestBody.create(requestBody, MediaType.parse("application/json")))
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new RuntimeException("LLM API 调用失败: " + response.code() + " " + response.message());
            }
            return parseResponse(response.body().string());
        }
    }

    private AgentResponse streamLlmCall(List<Map<String, Object>> messages, SseEmitter emitter) throws Exception {
        String requestBody = buildRequestBody(messages, true);
        Request request = new Request.Builder()
                .url(llmConfig.getBaseUrl() + llmConfig.getChatEndpoint())
                .header("Authorization", "Bearer " + llmConfig.getApiKey())
                .header("Content-Type", "application/json")
                .post(RequestBody.create(requestBody, MediaType.parse("application/json")))
                .build();

        log.debug("LLM request body: {}", requestBody);
        Response response = httpClient.newCall(request).execute();
        if (!response.isSuccessful()) {
            String errorBody = response.body() != null ? response.body().string() : "no body";
            log.error("LLM API error: {} {}, body: {}", response.code(), response.message(), errorBody);
            throw new RuntimeException("LLM API 调用失败: " + response.code() + " " + errorBody);
        }

        StringBuilder fullContent = new StringBuilder();
        List<AgentResponse.ToolCall> toolCalls = new ArrayList<>();
        Map<Integer, StringBuilder> toolCallArguments = new HashMap<>();

        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(response.body().byteStream(), StandardCharsets.UTF_8))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (!line.startsWith("data: ")) continue;
                String data = line.substring(6).trim();
                if ("[DONE]".equals(data)) break;

                JsonNode chunk = objectMapper.readTree(data);
                JsonNode delta = chunk.path("choices").path(0).path("delta");

                if (delta.has("content") && !delta.get("content").isNull()) {
                    String token = delta.get("content").asText();
                    fullContent.append(token);
                    sendSseEvent(emitter, "token", mapOf("content", token));
                }

                if (delta.has("tool_calls")) {
                    for (JsonNode tc : delta.get("tool_calls")) {
                        int index = tc.get("index").asInt();
                        if (tc.has("id")) {
                            AgentResponse.ToolCall toolCall = new AgentResponse.ToolCall();
                            toolCall.setId(tc.get("id").asText());
                            String funcName = tc.path("function").path("name").asText(null);
                            toolCall.setName(funcName);
                            toolCalls.add(toolCall);
                            toolCallArguments.put(index, new StringBuilder());
                        }
                        // name 可能在后续 chunk 中到达
                        if (tc.has("function") && tc.get("function").has("name")) {
                            String name = tc.get("function").get("name").asText(null);
                            if (name != null && index < toolCalls.size() && toolCalls.get(index).getName() == null) {
                                toolCalls.get(index).setName(name);
                            }
                        }
                        if (tc.has("function") && tc.get("function").has("arguments")) {
                            if (toolCallArguments.containsKey(index)) {
                                toolCallArguments.get(index).append(tc.get("function").get("arguments").asText());
                            }
                        }
                    }
                }
            }
        }

        // 解析工具调用参数，过滤掉 name 为空的无效调用
        List<AgentResponse.ToolCall> validToolCalls = new ArrayList<>();
        for (int i = 0; i < toolCalls.size(); i++) {
            AgentResponse.ToolCall tc = toolCalls.get(i);
            if (tc.getName() == null) {
                log.warn("Skipping tool call with null name at index {}", i);
                continue;
            }
            StringBuilder argsStr = toolCallArguments.get(i);
            if (argsStr != null && argsStr.length() > 0) {
                try {
                    tc.setArguments(objectMapper.readTree(argsStr.toString()));
                } catch (Exception e) {
                    log.warn("Failed to parse tool call arguments for {}: {}", tc.getName(), argsStr, e);
                    tc.setArguments(objectMapper.createObjectNode());
                }
            }
            validToolCalls.add(tc);
        }

        AgentResponse agentResponse = new AgentResponse();
        agentResponse.setContent(fullContent.toString());
        agentResponse.setToolCalls(validToolCalls.isEmpty() ? null : validToolCalls);
        return agentResponse;
    }

    private String buildRequestBody(List<Map<String, Object>> messages, boolean stream) throws JsonProcessingException {
        ObjectNode body = objectMapper.createObjectNode();
        body.put("model", llmConfig.getModel());
        body.put("stream", stream);

        ArrayNode messagesNode = objectMapper.createArrayNode();

        // System prompt
        ObjectNode sysMsg = objectMapper.createObjectNode();
        sysMsg.put("role", "system");
        sysMsg.put("content", systemPrompt + "\n\n你可以使用以下工具：\n" + buildToolDescriptions());
        messagesNode.add(sysMsg);

        // History messages
        for (Map<String, Object> msg : messages) {
            ObjectNode msgNode = objectMapper.createObjectNode();
            msgNode.put("role", (String) msg.get("role"));
            msgNode.put("content", (String) msg.get("content"));

            if (msg.containsKey("tool_call_id")) {
                msgNode.put("tool_call_id", (String) msg.get("tool_call_id"));
            }
            if (msg.containsKey("tool_calls")) {
                msgNode.set("tool_calls", objectMapper.valueToTree(msg.get("tool_calls")));
            }
            messagesNode.add(msgNode);
        }

        body.set("messages", messagesNode);

        // Tools definition
        ArrayNode toolsNode = objectMapper.createArrayNode();
        for (AgentTool tool : tools) {
            ObjectNode toolNode = objectMapper.createObjectNode();
            toolNode.put("type", "function");
            ObjectNode function = objectMapper.createObjectNode();
            function.put("name", tool.getName());
            function.put("description", tool.getDescription());
            function.set("parameters", tool.getParametersSchema());
            toolNode.set("function", function);
            toolsNode.add(toolNode);
        }
        body.set("tools", toolsNode);

        return objectMapper.writeValueAsString(body);
    }

    private AgentResponse parseResponse(String responseBody) throws Exception {
        JsonNode root = objectMapper.readTree(responseBody);
        JsonNode message = root.path("choices").get(0).path("message");

        AgentResponse response = new AgentResponse();
        response.setContent(message.has("content") ? message.get("content").asText() : null);

        if (message.has("tool_calls") && message.get("tool_calls").isArray()) {
            List<AgentResponse.ToolCall> toolCalls = new ArrayList<>();
            for (JsonNode tc : message.get("tool_calls")) {
                AgentResponse.ToolCall toolCall = new AgentResponse.ToolCall();
                toolCall.setId(tc.get("id").asText());
                toolCall.setName(tc.path("function").path("name").asText());
                String argsStr = tc.path("function").path("arguments").asText();
                try {
                    toolCall.setArguments(objectMapper.readTree(argsStr));
                } catch (Exception e) {
                    log.warn("Failed to parse tool call arguments: {}", argsStr, e);
                    toolCall.setArguments(objectMapper.createObjectNode());
                }
                toolCalls.add(toolCall);
            }
            response.setToolCalls(toolCalls);
        }

        return response;
    }

    private String executeTool(String toolName, JsonNode arguments) {
        return tools.stream()
                .filter(t -> t.getName().equals(toolName))
                .findFirst()
                .map(t -> {
                    try {
                        return t.execute(arguments);
                    } catch (Exception e) {
                        log.error("Tool execution error: {}", toolName, e);
                        return "{\"error\": \"" + e.getMessage().replace("\"", "'") + "\"}";
                    }
                })
                .orElse("{\"error\": \"Unknown tool: " + toolName + "\"}");
    }

    private List<Map<String, Object>> getOrCreateHistory(String sessionId) {
        return conversations.computeIfAbsent(sessionId, k -> new CopyOnWriteArrayList<>());
    }

    private Map<String, Object> buildMessage(String role, String content) {
        Map<String, Object> msg = new HashMap<>();
        msg.put("role", role);
        msg.put("content", content);
        return msg;
    }

    private void trimHistory(List<Map<String, Object>> messages) {
        while (messages.size() > MAX_HISTORY) {
            messages.remove(0);
        }
    }

    private List<Map<String, Object>> serializeToolCalls(List<AgentResponse.ToolCall> toolCalls) {
        return toolCalls.stream().map(tc -> {
            Map<String, Object> tcMap = new HashMap<>();
            tcMap.put("id", tc.getId());
            tcMap.put("type", "function");
            Map<String, Object> function = new HashMap<>();
            function.put("name", tc.getName());
            function.put("arguments", tc.getArguments() != null ? tc.getArguments().toString() : "{}");
            tcMap.put("function", function);
            return tcMap;
        }).collect(Collectors.toList());
    }

    private String buildToolDescriptions() {
        StringBuilder sb = new StringBuilder();
        for (AgentTool tool : tools) {
            sb.append("- ").append(tool.getName()).append(": ").append(tool.getDescription()).append("\n");
        }
        return sb.toString();
    }

    private void sendSseEvent(SseEmitter emitter, String eventType, Map<String, String> data) throws IOException {
        Map<String, String> payload = new HashMap<>(data);
        payload.put("type", eventType);
        emitter.send(SseEmitter.event()
                .data(objectMapper.writeValueAsString(payload)));
    }

    // Java 8 compatible Map.of() replacement
    @SuppressWarnings("unchecked")
    private static Map<String, String> mapOf(Object... keyValues) {
        Map<String, String> map = new HashMap<>();
        for (int i = 0; i < keyValues.length; i += 2) {
            map.put((String) keyValues[i], (String) keyValues[i + 1]);
        }
        return map;
    }

    private static Map<String, String> emptyMap() {
        return new HashMap<>();
    }
}

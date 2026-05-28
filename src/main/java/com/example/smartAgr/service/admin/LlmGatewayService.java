/*
package com.example.smartAgr.service.admin;

import com.example.smartAgr.config.LLMConfig;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import okhttp3.*;
import org.springframework.stereotype.Service;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
public class LlmGatewayService {

    private final LLMConfig config;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(120, TimeUnit.SECONDS)
            .writeTimeout(120, TimeUnit.SECONDS)
            .build();

    */
/**
     * 非流式调用 - 用于简单场景
     *//*

    public String chat(String systemPrompt, String userPrompt) throws Exception {
        List<Map<String, String>> messages = new ArrayList<>();
        messages.add(Map.of("role", "system", "content", systemPrompt));
        messages.add(Map.of("role", "user", "content", userPrompt));

        String jsonBody = objectMapper.writeValueAsString(Map.of(
                "model", config.getModel(),
                "messages", messages,
                "stream", false
        ));

        RequestBody body = RequestBody.create(jsonBody, MediaType.parse("application/json"));

        Request request = new Request.Builder()
                .url(config.getBaseUrl() + config.getChatEndpoint())
                .header("Authorization", "Bearer " + config.getApiKey())
                .post(body)
                .build();

        try (Response response = client.newCall(request).execute()) {
            if (!response.isSuccessful()) {
                throw new RuntimeException("调用 LLM 失败：" + response);
            }

            String respString = response.body().string();
            return objectMapper.readTree(respString)
                    .path("choices").get(0)
                    .path("message")
                    .path("content")
                    .asText();
        }
    }

    */
/**
     * 流式调用 - 用于 SSE 实时推送
     *//*

    public SseEmitter chatStream(String systemPrompt, String userPrompt) {
        SseEmitter emitter = new SseEmitter(5 * 60 * 1000L); // 5 分钟超时

        List<Map<String, String>> messages = new ArrayList<>();
        messages.add(Map.of("role", "system", "content", systemPrompt));
        messages.add(Map.of("role", "user", "content", userPrompt));

        String jsonBody;
        try {
            jsonBody = objectMapper.writeValueAsString(Map.of(
                    "model", config.getModel(),
                    "messages", messages,
                    "stream", true
            ));
        } catch (Exception e) {
            emitter.completeWithError(e);
            return emitter;
        }

        RequestBody body = RequestBody.create(jsonBody, MediaType.parse("application/json"));

        Request request = new Request.Builder()
                .url(config.getBaseUrl() + config.getChatEndpoint())
                .header("Authorization", "Bearer " + config.getApiKey())
                .post(body)
                .build();

        // 异步执行
        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                emitter.completeWithError(e);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (!response.isSuccessful()) {
                    emitter.completeWithError(new RuntimeException("LLM 调用失败：" + response));
                    return;
                }

                try (ResponseBody responseBody = response.body();
                     BufferedReader reader = new BufferedReader(new java.io.InputStreamReader(responseBody.byteStream()))) {

                    String line;
                    while ((line = reader.readLine()) != null) {
                        if (line.startsWith("data: ")) {
                            String data = line.substring(6);
                            if ("[DONE]".equals(data)) {
                                break;
                            }

                            try {
                                JsonNode jsonNode = objectMapper.readTree(data);
                                String content = jsonNode
                                        .path("choices").get(0)
                                        .path("delta")
                                        .path("content")
                                        .asText();

                                if (!content.isEmpty()) {
                                    emitter.send(SseEmitter.event()
                                            .name("message")
                                            .data(content));
                                }
                            } catch (Exception e) {
                                // 忽略解析错误
                            }
                        }
                    }
                    emitter.complete();
                } catch (Exception e) {
                    emitter.completeWithError(e);
                }
            }
        });

        return emitter;
    }

    */
/**
     * 带进度回调的流式调用 - 用于多步骤任务
     *//*

    public SseEmitter chatStreamWithProgress(
            String systemPrompt,
            String userPrompt,
            Runnable onStart,
            java.util.function.Consumer<String> onProgress,
            Runnable onComplete) {

        SseEmitter emitter = new SseEmitter(5 * 60 * 1000L);

        // 发送开始事件
        if (onStart != null) {
            onStart.run();
        }

        List<Map<String, String>> messages = new ArrayList<>();
        messages.add(Map.of("role", "system", "content", systemPrompt));
        messages.add(Map.of("role", "user", "content", userPrompt));

        String jsonBody;
        try {
            jsonBody = objectMapper.writeValueAsString(Map.of(
                    "model", config.getModel(),
                    "messages", messages,
                    "stream", true
            ));
        } catch (Exception e) {
            emitter.completeWithError(e);
            return emitter;
        }

        RequestBody body = RequestBody.create(jsonBody, MediaType.parse("application/json"));

        Request request = new Request.Builder()
                .url(config.getBaseUrl() + config.getChatEndpoint())
                .header("Authorization", "Bearer " + config.getApiKey())
                .post(body)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, IOException e) {
                emitter.completeWithError(e);
            }

            @Override
            public void onResponse(Call call, Response response) throws IOException {
                if (!response.isSuccessful()) {
                    emitter.completeWithError(new RuntimeException("LLM 调用失败：" + response));
                    return;
                }

                try (ResponseBody responseBody = response.body();
                     BufferedReader reader = new BufferedReader(new java.io.InputStreamReader(responseBody.byteStream()))) {

                    String line;
                    while ((line = reader.readLine()) != null) {
                        if (line.startsWith("data: ")) {
                            String data = line.substring(6);
                            if ("[DONE]".equals(data)) {
                                break;
                            }

                            try {
                                JsonNode jsonNode = objectMapper.readTree(data);
                                String content = jsonNode
                                        .path("choices").get(0)
                                        .path("delta")
                                        .path("content")
                                        .asText();

                                if (!content.isEmpty()) {
                                    // 发送进度更新
                                    if (onProgress != null) {
                                        onProgress.accept(content);
                                    }

                                    // 通过 SSE 发送给前端
                                    emitter.send(SseEmitter.event()
                                            .name("message")
                                            .data(content));
                                }
                            } catch (Exception e) {
                                // 忽略解析错误
                            }
                        }
                    }

                    // 完成回调
                    if (onComplete != null) {
                        onComplete.run();
                    }

                    emitter.complete();
                } catch (Exception e) {
                    emitter.completeWithError(e);
                }
            }
        });

        return emitter;
    }
}
*/

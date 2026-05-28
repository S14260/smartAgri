package com.example.smartAgr.controller.admin;

import com.example.smartAgr.result.Result;
import com.example.smartAgr.service.ai.AgentService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/admin/ai")
@RequiredArgsConstructor
public class AgentController {

    private final AgentService agentService;

    /**
     * 非流式对话
     */
    @PostMapping("/chat")
    public Result<String> chat(@RequestBody Map<String, String> request) {
        try {
            String sessionId = request.getOrDefault("sessionId", "default");
            String message = request.get("message");
            if (message == null || message.trim().isEmpty()) {
                return Result.error("消息不能为空");
            }
            String response = agentService.chat(sessionId, message);
            return Result.success(response);
        } catch (Exception e) {
            return Result.error("AI 对话失败: " + e.getMessage());
        }
    }

    /**
     * 流式对话 (SSE)
     */
    @PostMapping(value = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter chatStream(@RequestBody Map<String, String> request) {
        String sessionId = request.getOrDefault("sessionId", "default");
        String message = request.get("message");
        return agentService.chatStream(sessionId, message);
    }

    /**
     * 列出可用工具
     */
    @GetMapping("/tools")
    public Result<List<Map<String, String>>> listTools() {
        return Result.success(agentService.listTools());
    }

    /**
     * 清除会话历史
     */
    @DeleteMapping("/conversation")
    public Result<Void> clearConversation(@RequestParam String sessionId) {
        agentService.clearConversation(sessionId);
        return Result.success();
    }
}

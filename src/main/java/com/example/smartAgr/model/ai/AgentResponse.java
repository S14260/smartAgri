package com.example.smartAgr.model.ai;

import com.fasterxml.jackson.databind.JsonNode;
import lombok.Data;

import java.util.List;
import java.util.Map;

@Data
public class AgentResponse {
    private String content;
    private List<ToolCall> toolCalls;

    public boolean hasToolCalls() {
        return toolCalls != null && !toolCalls.isEmpty();
    }

    @Data
    public static class ToolCall {
        private String id;
        private String name;
        private JsonNode arguments;
    }
}

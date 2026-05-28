package com.example.smartAgr.config;

import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Data
@Configuration
@ConfigurationProperties(prefix = "llm")
public class LLMConfig {
    private String apiKey;
    private String baseUrl; // e.g. https://api.deepseek.com
    private String model;   // e.g. deepseek-chat
    private String chatEndpoint; // /v1/chat/completions
    private String systemPrompt; // Agent 系统提示词
}

package com.example.smartAgr.config;


import lombok.Data;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.context.annotation.Configuration;

@Data
@Configuration
@ConfigurationProperties(prefix = "llm")
public class LLMConfig {
    private String apiKey;
    private String baseUrl; // e.g. https://api.deepseek.com/v1
    private String model;   // e.g. deepseek-chat
}
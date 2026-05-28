package com.example.smartAgr.service.ai;

import com.fasterxml.jackson.databind.JsonNode;

/**
 * AI Agent 工具接口 - 实现此接口的 Bean 会被自动注册为 Agent 可调用的工具
 */
public interface AgentTool {

    /** 工具名称，LLM 通过此名称调用 */
    String getName();

    /** 工具描述，LLM 根据描述决定何时调用 */
    String getDescription();

    /** 参数的 JSON Schema，遵循 OpenAI function calling 格式 */
    JsonNode getParametersSchema();

    /** 执行工具，返回结果字符串（通常是 JSON） */
    String execute(JsonNode parameters) throws Exception;
}

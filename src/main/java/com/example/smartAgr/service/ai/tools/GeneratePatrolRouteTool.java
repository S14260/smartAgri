package com.example.smartAgr.service.ai.tools;

import com.example.smartAgr.service.ai.AgentTool;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.RequiredArgsConstructor;
import okhttp3.*;
import org.springframework.stereotype.Component;

import java.util.concurrent.TimeUnit;

@Component
@RequiredArgsConstructor
public class GeneratePatrolRouteTool implements AgentTool {

    private final ObjectMapper objectMapper = new ObjectMapper();
private final OkHttpClient httpClient = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(120, TimeUnit.SECONDS)
            .build();
    private static final String FLASK_BASE = "http://123.56.228.32:8000";

    @Override
    public String getName() {
        return "generate_patrol_route";
    }

    @Override
    public String getDescription() {
        return "基于巡田工单生成巡田路径规划。输入工单路径，返回 GeoJSON 路径、路径长度、评估结果等。";
    }

    @Override
    public JsonNode getParametersSchema() {
        ObjectNode schema = objectMapper.createObjectNode();
        schema.put("type", "object");
        ObjectNode properties = objectMapper.createObjectNode();

        ObjectNode reportPathProp = objectMapper.createObjectNode();
        reportPathProp.put("type", "string");
        reportPathProp.put("description", "巡田工单的文件路径或URL");
        properties.set("report_path", reportPathProp);

        ObjectNode enable2optProp = objectMapper.createObjectNode();
        enable2optProp.put("type", "boolean");
        enable2optProp.put("description", "是否启用2-opt路径优化，默认true");
        properties.set("enable_2opt", enable2optProp);

        schema.set("properties", properties);
        ArrayNode required = objectMapper.createArrayNode();
        required.add("report_path");
        schema.set("required", required);
        return schema;
    }

    @Override
    public String execute(JsonNode parameters) throws Exception {
        String reportPath = parameters.get("report_path").asText();
        boolean enable2opt = parameters.has("enable_2opt") && parameters.get("enable_2opt").asBoolean(true);

        ObjectNode requestBody = objectMapper.createObjectNode();
        requestBody.put("report_path", reportPath);
        requestBody.put("enable_2opt", enable2opt);

        RequestBody body = RequestBody.create(
                objectMapper.writeValueAsString(requestBody),
                MediaType.parse("application/json"));

        Request request = new Request.Builder()
                .url(FLASK_BASE + "/xuntian/patrol/plan")
                .post(body)
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            return response.body().string();
        }
    }
}

package com.example.smartAgr.service.ai.tools;

import com.example.smartAgr.service.ai.AgentTool;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.RequiredArgsConstructor;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class GetAnomalyRecordsTool implements AgentTool {

    private final OkHttpClient httpClient = new OkHttpClient();
    private final ObjectMapper objectMapper = new ObjectMapper();
    private static final String FLASK_BASE = "http://123.56.228.32:8000";

    @Override
    public String getName() {
        return "get_anomaly_records";
    }

    @Override
    public String getDescription() {
        return "获取巡田异常记录。可查看历史工单列表，或查看指定工单的详细异常数据（包含 NDVI/EVI 等遥感指标）。";
    }

    @Override
    public JsonNode getParametersSchema() {
        ObjectNode schema = objectMapper.createObjectNode();
        schema.put("type", "object");
        ObjectNode properties = objectMapper.createObjectNode();
        ObjectNode actionProp = objectMapper.createObjectNode();
        actionProp.put("type", "string");
        actionProp.put("description", "操作类型：'list' 获取工单列表，'detail' 获取工单详情");
        com.fasterxml.jackson.databind.node.ArrayNode enumNode = objectMapper.createArrayNode();
        enumNode.add("list");
        enumNode.add("detail");
        actionProp.set("enum", enumNode);
        properties.set("action", actionProp);
        ObjectNode pathProp = objectMapper.createObjectNode();
        pathProp.put("type", "string");
        pathProp.put("description", "工单文件路径（action=detail 时必填）");
        properties.set("report_path", pathProp);
        schema.set("properties", properties);
        return schema;
    }

    @Override
    public String execute(JsonNode parameters) throws Exception {
        String action = parameters.has("action") ? parameters.get("action").asText() : "list";

        if ("list".equals(action)) {
            Request request = new Request.Builder()
                    .url(FLASK_BASE + "/xuntian/reports")
                    .get()
                    .build();
            try (Response response = httpClient.newCall(request).execute()) {
                return response.body().string();
            }
        } else {
            String reportPath = parameters.get("report_path").asText();
            Request request = new Request.Builder()
                    .url(FLASK_BASE + "/xuntian/report/detail?path=" + reportPath)
                    .get()
                    .build();
            try (Response response = httpClient.newCall(request).execute()) {
                return response.body().string();
            }
        }
    }
}

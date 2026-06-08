package com.example.smartAgr.service.ai.tools;

import com.example.smartAgr.service.ai.AgentTool;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
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
        ArrayNode required = objectMapper.createArrayNode();
        required.add("action");
        schema.set("required", required);
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
                String raw = response.body().string();
                // 精简返回给 LLM 的数据，只保留关键字段
                try {
                    com.fasterxml.jackson.databind.JsonNode arr = objectMapper.readTree(raw);
                    if (arr.isArray()) {
                        com.fasterxml.jackson.databind.node.ArrayNode summary = objectMapper.createArrayNode();
                        for (com.fasterxml.jackson.databind.JsonNode r : arr) {
                            ObjectNode item = objectMapper.createObjectNode();
                            item.put("generate_time", r.path("generate_time").asText(""));
                            item.put("total_anomaly_count", r.path("total_anomaly_count").asInt(0));
                            item.put("report_url", r.path("report_url").asText(""));
                            summary.add(item);
                        }
                        return objectMapper.writeValueAsString(summary);
                    }
                } catch (Exception ignored) {}
                return raw;
            }
        } else {
            if (!parameters.has("report_path") || parameters.get("report_path").asText().isEmpty()) {
                return "{\"error\": \"当 action=detail 时，必须提供 report_path 参数。请先用 action=list 获取工单列表，再用 report_url 作为 report_path 查询详情。\"}";
            }
            String reportPath = parameters.get("report_path").asText();
            Request request = new Request.Builder()
                    .url(FLASK_BASE + "/xuntian/report/detail?path=" + reportPath)
                    .get()
                    .build();
            try (Response response = httpClient.newCall(request).execute()) {
                String raw = response.body().string();
                // 精简详情数据，去掉大段的 geojson 等
                try {
                    com.fasterxml.jackson.databind.JsonNode root = objectMapper.readTree(raw);
                    ObjectNode summary = objectMapper.createObjectNode();
                    summary.put("total_anomaly_count", root.path("total_anomaly_count").asInt(0));
                    summary.set("ndvi_grade_stats", root.path("ndvi_grade_stats"));
                    com.fasterxml.jackson.databind.JsonNode subregions = root.path("anomaly_subregions");
                    if (subregions.isArray()) {
                        com.fasterxml.jackson.databind.node.ArrayNode anomalies = objectMapper.createArrayNode();
                        for (com.fasterxml.jackson.databind.JsonNode s : subregions) {
                            ObjectNode a = objectMapper.createObjectNode();
                            a.put("plot_name", s.path("plot_name").asText(""));
                            a.put("anomaly_category", s.path("anomaly_category").asText(""));
                            a.put("ndvi_grade_label", s.path("ndvi_grade_label").asText(""));
                            a.put("mean_ndvi", s.path("mean_ndvi").asDouble(0));
                            a.put("area_m2", s.path("area_m2").asDouble(0));
                            a.put("priority", s.path("priority").asDouble(0));
                            a.put("contact_person", s.path("contact_person").asText(""));
                            anomalies.add(a);
                        }
                        summary.set("anomaly_subregions", anomalies);
                    }
                    return objectMapper.writeValueAsString(summary);
                } catch (Exception ignored) {}
                return raw;
            }
        }
    }
}

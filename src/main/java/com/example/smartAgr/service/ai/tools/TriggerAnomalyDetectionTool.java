package com.example.smartAgr.service.ai.tools;

import com.example.smartAgr.dao.admin.AdminPlotDao;
import com.example.smartAgr.model.AdminPlot;
import com.example.smartAgr.service.ai.AgentTool;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.RequiredArgsConstructor;
import okhttp3.*;
import org.springframework.stereotype.Component;

import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Component
@RequiredArgsConstructor
public class TriggerAnomalyDetectionTool implements AgentTool {

    private final AdminPlotDao plotDao;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final OkHttpClient httpClient = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .build();
    private static final String FLASK_BASE = "http://123.56.228.32:8000";

    @Override
    public String getName() {
        return "trigger_anomaly_detection";
    }

    @Override
    public String getDescription() {
        return "对指定地块启动异常检测任务。需要提供地块ID列表、日期范围和地区。返回任务时间戳，可用于查询检测进度和结果。";
    }

    @Override
    public JsonNode getParametersSchema() {
        ObjectNode schema = objectMapper.createObjectNode();
        schema.put("type", "object");
        ObjectNode properties = objectMapper.createObjectNode();

        ObjectNode plotIdsProp = objectMapper.createObjectNode();
        plotIdsProp.put("type", "array");
        plotIdsProp.put("description", "地块ID列表，如 [1,2,3,4,5]");
        ObjectNode items = objectMapper.createObjectNode();
        items.put("type", "integer");
        plotIdsProp.set("items", items);
        properties.set("plot_ids", plotIdsProp);

        ObjectNode startDateProp = objectMapper.createObjectNode();
        startDateProp.put("type", "string");
        startDateProp.put("description", "开始日期，格式 YYYY-MM-DD");
        properties.set("start_date", startDateProp);

        ObjectNode endDateProp = objectMapper.createObjectNode();
        endDateProp.put("type", "string");
        endDateProp.put("description", "结束日期，格式 YYYY-MM-DD");
        properties.set("end_date", endDateProp);

        ObjectNode regionProp = objectMapper.createObjectNode();
        regionProp.put("type", "string");
        regionProp.put("description", "地区中文名，如：沽源、张北、宁河");
        properties.set("region", regionProp);

        schema.set("properties", properties);
        ArrayNode required = objectMapper.createArrayNode();
        required.add("plot_ids");
        required.add("start_date");
        required.add("end_date");
        required.add("region");
        schema.set("required", required);
        return schema;
    }

    @Override
    public String execute(JsonNode parameters) throws Exception {
        String startDate = parameters.get("start_date").asText();
        String endDate = parameters.get("end_date").asText();
        String region = parameters.get("region").asText();

        // 从数据库查询地块信息，获取地块名
        List<AdminPlot> regionPlots = plotDao.findByRegion(region);
        JsonNode plotIdsNode = parameters.get("plot_ids");
        List<Long> requestedIds = new java.util.ArrayList<>();
        for (JsonNode id : plotIdsNode) {
            requestedIds.add(id.asLong());
        }
        List<AdminPlot> targetPlots = regionPlots.stream()
                .filter(p -> requestedIds.contains(p.getId()))
                .collect(Collectors.toList());

        if (targetPlots.isEmpty()) {
            return "{\"error\": \"未找到指定ID的地块，请确认地块ID和地区是否正确\"}";
        }

        // ndvi_folder 映射
        String ndviFolder;
        switch (region) {
            case "沽源": ndviFolder = "./static/ndvi_clips/guyuan/admin"; break;
            case "张北": ndviFolder = "./static/ndvi_clips/zhangbei/admin"; break;
            case "宁河": ndviFolder = "./static/ndvi_clips/ninghe/admin"; break;
            default: ndviFolder = "./static/ndvi_clips/" + region + "/admin";
        }

        // 构建请求体：直接是 JSON 数组，格式为 [{plot_id, start_date, end_date, ndvi_folder}, ...]
        ArrayNode requestData = objectMapper.createArrayNode();
        for (AdminPlot plot : targetPlots) {
            ObjectNode item = objectMapper.createObjectNode();
            item.put("plot_id", plot.getId() + "_" + plot.getPlotName());
            item.put("start_date", startDate);
            item.put("end_date", endDate);
            item.put("ndvi_folder", ndviFolder);
            requestData.add(item);
        }

        RequestBody body = RequestBody.create(
                objectMapper.writeValueAsString(requestData),
                MediaType.parse("application/json"));

        Request request = new Request.Builder()
                .url(FLASK_BASE + "/xuntian/run")
                .post(body)
                .build();

        try (Response response = httpClient.newCall(request).execute()) {
            String resp = response.body().string();
            ObjectNode result = objectMapper.createObjectNode();
            result.put("message", "异常检测任务已启动，共 " + targetPlots.size() + " 个地块，可使用 get_anomaly_records 工具查看结果");
            result.put("plots", objectMapper.writeValueAsString(
                    targetPlots.stream().map(p -> p.getId() + "_" + p.getPlotName()).collect(Collectors.toList())));
            result.set("task_info", objectMapper.readTree(resp));
            return objectMapper.writeValueAsString(result);
        }
    }
}

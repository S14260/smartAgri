package com.example.smartAgr.controller.admin;

import com.example.smartAgr.config.LLMConfig;
import com.example.smartAgr.result.Result;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import okhttp3.Call;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.Response;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.TimeUnit;

@RestController
@RequestMapping("/admin/report")
public class ReportController {

    @Autowired
    private LLMConfig config;

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(300, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .build();

    @PostMapping("/generate")
    public Result<Map<String, Object>> generate(@RequestBody Map<String, Object> body) {
        try {
            List<Map<String, Object>> anomalies = (List<Map<String, Object>>) body.get("anomaly_subregions");
            String reportTime = (String) body.get("report_time");

            if (anomalies == null || anomalies.isEmpty()) {
                return Result.error("无异常数据");
            }

            // 按 priority 降序排序
            anomalies.sort((a, b) -> {
                double pa = a.get("priority") instanceof Number ? ((Number) a.get("priority")).doubleValue() : 0;
                double pb = b.get("priority") instanceof Number ? ((Number) b.get("priority")).doubleValue() : 0;
                return Double.compare(pb, pa);
            });

            // 统计
            int total = anomalies.size();
            int high = 0, medium = 0, low = 0;
            for (Map<String, Object> a : anomalies) {
                double p = a.get("priority") instanceof Number ? ((Number) a.get("priority")).doubleValue() : 0;
                if (p >= 3) high++;
                else if (p >= 2) medium++;
                else low++;
            }

            // 限制发送给 LLM 的异常数量，避免 prompt 过大
            List<Map<String, Object>> topAnomalies = anomalies.size() > 15 ? anomalies.subList(0, 15) : anomalies;

            // 拼接 LLM prompt
            String prompt = buildPrompt(topAnomalies, reportTime);

            // 调用 LLM（失败时降级为模板报告）
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("total_anomaly", total);
            result.put("high_count", high);
            result.put("medium_count", medium);
            result.put("low_count", low);
            result.put("generated_time", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));

            try {
                String llmResponse = callLlm(prompt);
                JsonNode llmJson = objectMapper.readTree(llmResponse);
                result.put("summary", llmJson.path("summary").asText("本次巡田发现 " + total + " 处异常"));
                result.put("risk_level", llmJson.path("risk_level").asText(high > 0 ? "高" : (medium > 0 ? "中" : "低")));
                result.put("route_suggestion", llmJson.path("route_suggestion").asText(""));
                result.put("tasks", objectMapper.convertValue(llmJson.path("tasks"), List.class));
            } catch (Exception e) {
                // LLM 调用失败（超时等），降级为模板报告
                result.put("summary", "本次巡田发现 " + total + " 处异常（高危" + high + "处、中危" + medium + "处、低危" + low + "处），请按优先级逐一处理。");
                result.put("risk_level", high > 0 ? "高" : (medium > 0 ? "中" : "低"));
                result.put("route_suggestion", "建议按优先级从高到低依次巡检，优先处理高危异常地块。");
                result.put("tasks", buildFallbackTasks(anomalies));
            }

            return Result.success(result);
        } catch (Exception e) {
            return Result.error("生成报告失败: " + e.getMessage());
        }
    }

    private String buildPrompt(List<Map<String, Object>> anomalies, String reportTime) {
        StringBuilder sb = new StringBuilder();
        sb.append("你是农业巡田报告生成专家。请根据以下异常检测数据，生成一份面向一线巡检人员的巡田任务单。\n\n");
        sb.append("要求：\n");
        sb.append("1. 输出严格的 JSON 格式，不要包含其他文字\n");
        sb.append("2. tasks 数组按优先级从高到低排序\n");
        sb.append("3. 每条 task 的 action 字段要给出具体的、可执行的处理建议（不要泛泛而谈）\n");
        sb.append("4. summary 用一句话概括本次巡田的核心发现\n");
        sb.append("5. route_suggestion 给出合理的巡检路线建议\n\n");

        sb.append("输出 JSON 结构：\n");
        sb.append("{\n");
        sb.append("  \"summary\": \"一句话总结\",\n");
        sb.append("  \"risk_level\": \"高/中/低\",\n");
        sb.append("  \"route_suggestion\": \"路线建议\",\n");
        sb.append("  \"tasks\": [\n");
        sb.append("    {\n");
        sb.append("      \"plot_name\": \"地块名\",\n");
        sb.append("      \"anomaly_category\": \"异常类型\",\n");
        sb.append("      \"severity_label\": \"高危/中危/低危\",\n");
        sb.append("      \"area_mu\": 12.5,\n");
        sb.append("      \"ndvi_mean\": 0.15,\n");
        sb.append("      \"action\": \"具体处理建议\",\n");
        sb.append("      \"contact\": \"负责人\",\n");
        sb.append("      \"phone\": \"电话\"\n");
        sb.append("    }\n");
        sb.append("  ]\n");
        sb.append("}\n\n");

        sb.append("巡田时间: ").append(reportTime != null ? reportTime : "未知").append("\n");
        sb.append("异常总数: ").append(anomalies.size()).append("\n\n");
        sb.append("异常数据：\n");

        for (int i = 0; i < anomalies.size(); i++) {
            Map<String, Object> a = anomalies.get(i);
            sb.append("---\n");
            sb.append("地块: ").append(a.getOrDefault("plot_name", "未知")).append("\n");
            sb.append("异常类型: ").append(a.getOrDefault("anomaly_category", "未知")).append("\n");
            sb.append("NDVI等级: ").append(a.getOrDefault("ndvi_grade_label", "未知")).append("\n");
            sb.append("面积(m²): ").append(a.getOrDefault("area_m2", 0)).append("\n");
            sb.append("NDVI均值: ").append(a.getOrDefault("mean_ndvi", 0)).append("\n");
            sb.append("优先级: ").append(a.getOrDefault("priority", 0)).append("\n");
            sb.append("严重程度: ").append(a.getOrDefault("severity", 0)).append("\n");
            sb.append("联系人: ").append(a.getOrDefault("contact_person", "无")).append("\n");
            sb.append("电话: ").append(a.getOrDefault("phone", "无")).append("\n");
        }

        return sb.toString();
    }

    private String callLlm(String userPrompt) throws Exception {
        String systemPrompt = "你是一名农业巡田报告生成专家，擅长根据遥感异常检测数据生成可执行的巡检任务单。请严格输出 JSON 格式。";

        ObjectNode body = objectMapper.createObjectNode();
        body.put("model", config.getModel());
        body.put("temperature", 0.3);
        ArrayNode messages = objectMapper.createArrayNode();
        messages.add(objectMapper.createObjectNode().put("role", "system").put("content", systemPrompt));
        messages.add(objectMapper.createObjectNode().put("role", "user").put("content", userPrompt));
        body.set("messages", messages);

        okhttp3.RequestBody reqBody = okhttp3.RequestBody.create(
                objectMapper.writeValueAsString(body), MediaType.parse("application/json"));

        Request request = new Request.Builder()
                .url(config.getBaseUrl() + "/chat/completions")
                .header("Authorization", "Bearer " + config.getApiKey())
                .post(reqBody)
                .build();

        Response response = client.newCall(request).execute();
        if (!response.isSuccessful()) {
            throw new RuntimeException("LLM 调用失败: " + response.code() + " " + response.message());
        }

        String content = objectMapper.readTree(response.body().string())
                .path("choices").get(0)
                .path("message")
                .path("content")
                .asText();

        // 清理可能的 markdown 代码块标记
        content = content.trim();
        if (content.startsWith("```json")) content = content.substring(7);
        if (content.startsWith("```")) content = content.substring(3);
        if (content.endsWith("```")) content = content.substring(0, content.length() - 3);
        return content.trim();
    }

    private List<Map<String, Object>> buildFallbackTasks(List<Map<String, Object>> anomalies) {
        List<Map<String, Object>> tasks = new ArrayList<>();
        for (Map<String, Object> a : anomalies) {
            Map<String, Object> task = new LinkedHashMap<>();
            task.put("plot_name", a.getOrDefault("plot_name", "未知"));
            task.put("anomaly_category", a.getOrDefault("anomaly_category", "未知"));
            double p = a.get("priority") instanceof Number ? ((Number) a.get("priority")).doubleValue() : 0;
            task.put("severity_label", p >= 3 ? "高危" : (p >= 2 ? "中危" : "低危"));
            double areaM2 = a.get("area_m2") instanceof Number ? ((Number) a.get("area_m2")).doubleValue() : 0;
            task.put("area_mu", Math.round(areaM2 / 666.67 * 100.0) / 100.0);
            task.put("ndvi_mean", a.getOrDefault("mean_ndvi", 0));
            task.put("action", "请现场核实异常情况并记录");
            task.put("contact", a.getOrDefault("contact_person", ""));
            task.put("phone", a.getOrDefault("phone", ""));
            tasks.add(task);
        }
        return tasks;
    }
}

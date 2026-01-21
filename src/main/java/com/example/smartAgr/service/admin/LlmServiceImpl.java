package com.example.smartAgr.service.admin;

import com.example.smartAgr.config.LLMConfig;
import com.example.smartAgr.model.AnomalyRecordDTO;
import com.example.smartAgr.service.admin.LlmService;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import okhttp3.*;
import org.springframework.stereotype.Service;

import java.util.concurrent.TimeUnit;

@Service
@RequiredArgsConstructor
public class LlmServiceImpl implements LlmService {

    private final LLMConfig config;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final OkHttpClient client = new OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(60, TimeUnit.SECONDS)
            .writeTimeout(60, TimeUnit.SECONDS)
            .build();

    @Override
    public String explainAnomaly(AnomalyRecordDTO record) throws Exception {

        // 构建 prompt
        String systemPrompt =
                "你是一名农业遥感与农情诊断专家，擅长分析 NDVI/EVI/SAVI/NDWI 异常。\n" +
                        "下面是张家口市沽源县的地块，根据输入异常工单信息，输出：\n" +
                        "1. 异常原因解释\n" +
                        "2. 农情风险判断（高/中/低）\n" +
                        "3. 现场建议（3~5 条）\n" +
                        "要求逻辑清晰、专业、简洁，不夸张，不虚构。异常工单仅供参考\n";

        StringBuilder userPrompt = new StringBuilder();
        userPrompt.append("地块: ").append(record.getPlot()).append("\n")
                .append("日期: ").append(record.getDate()).append("\n")
                .append("异常类型: ").append(record.getAnomaly_type()).append("\n")
                .append("异常类别: ").append(record.getAnomaly_category()).append("\n")
                .append("面积(m²): ").append(record.getArea_m2()).append("\n")
                .append("NDVI均值: ").append(record.getMean_ndvi()).append(", 增量: ").append(record.getDelta_ndvi()).append("\n")
                .append("EVI均值: ").append(record.getMean_evi()).append(", 增量: ").append(record.getDelta_evi()).append("\n")
                .append("SAVI均值: ").append(record.getMean_savi()).append(", 增量: ").append(record.getDelta_savi()).append("\n")
                .append("NDWI均值: ").append(record.getMean_ndwi()).append(", 增量: ").append(record.getDelta_ndwi()).append("\n")
                .append("优先级: ").append(record.getPriority()).append(", 严重程度: ").append(record.getSeverity()).append("\n");

        // ===== 构造 LLM 请求体 =====
        String jsonBody = "{"
                + "\"model\": \"" + config.getModel() + "\","
                + "\"messages\": ["
                + "{\"role\": \"system\", \"content\": \"" + escape(systemPrompt) + "\"},"
                + "{\"role\": \"user\", \"content\": \"" + escape(userPrompt.toString()) + "\"}"
                + "]"
                + "}";

        RequestBody body = RequestBody.create(jsonBody, MediaType.parse("application/json"));

        Request request = new Request.Builder()
                .url(config.getBaseUrl() + "/chat/completions")
                .header("Authorization", "Bearer " + config.getApiKey())
                .post(body)
                .build();

        Response response = client.newCall(request).execute();

        if (!response.isSuccessful()) {
            throw new RuntimeException("调用 LLM 失败: " + response);
        }

        String respString = response.body().string();

        return objectMapper.readTree(respString)
                .path("choices").get(0)
                .path("message")
                .path("content")
                .asText();
    }

    private String escape(String s) {
        return s.replace("\"", "\\\"").replace("\n", "\\n");
    }
}

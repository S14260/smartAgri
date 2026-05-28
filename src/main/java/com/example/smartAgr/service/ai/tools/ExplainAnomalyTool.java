package com.example.smartAgr.service.ai.tools;

import com.example.smartAgr.model.AnomalyRecordDTO;
import com.example.smartAgr.service.admin.LlmService;
import com.example.smartAgr.service.ai.AgentTool;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

@Component
@RequiredArgsConstructor
public class ExplainAnomalyTool implements AgentTool {

    private final LlmService llmService;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public String getName() {
        return "explain_anomaly";
    }

    @Override
    public String getDescription() {
        return "对异常记录进行智能解释分析。输入异常数据（NDVI/EVI/SAVI/NDWI 指标），返回异常原因、风险评估和现场建议。";
    }

    @Override
    public JsonNode getParametersSchema() {
        ObjectNode schema = objectMapper.createObjectNode();
        schema.put("type", "object");
        ObjectNode p = objectMapper.createObjectNode();

        ObjectNode plot = objectMapper.createObjectNode();
        plot.put("type", "string"); plot.put("description", "地块名称");
        p.set("plot", plot);

        ObjectNode date = objectMapper.createObjectNode();
        date.put("type", "string"); date.put("description", "日期");
        p.set("date", date);

        ObjectNode anomalyType = objectMapper.createObjectNode();
        anomalyType.put("type", "string"); anomalyType.put("description", "异常类型");
        p.set("anomaly_type", anomalyType);

        ObjectNode anomalyCategory = objectMapper.createObjectNode();
        anomalyCategory.put("type", "string"); anomalyCategory.put("description", "异常类别");
        p.set("anomaly_category", anomalyCategory);

        ObjectNode meanNdvi = objectMapper.createObjectNode();
        meanNdvi.put("type", "number"); meanNdvi.put("description", "NDVI均值");
        p.set("mean_ndvi", meanNdvi);

        ObjectNode deltaNdvi = objectMapper.createObjectNode();
        deltaNdvi.put("type", "number"); deltaNdvi.put("description", "NDVI增量");
        p.set("delta_ndvi", deltaNdvi);

        ObjectNode meanEvi = objectMapper.createObjectNode();
        meanEvi.put("type", "number"); meanEvi.put("description", "EVI均值");
        p.set("mean_evi", meanEvi);

        ObjectNode meanSavi = objectMapper.createObjectNode();
        meanSavi.put("type", "number"); meanSavi.put("description", "SAVI均值");
        p.set("mean_savi", meanSavi);

        ObjectNode meanNdwi = objectMapper.createObjectNode();
        meanNdwi.put("type", "number"); meanNdwi.put("description", "NDWI均值");
        p.set("mean_ndwi", meanNdwi);

        ObjectNode area = objectMapper.createObjectNode();
        area.put("type", "number"); area.put("description", "异常面积(m²)");
        p.set("area_m2", area);

        ObjectNode priority = objectMapper.createObjectNode();
        priority.put("type", "number"); priority.put("description", "优先级");
        p.set("priority", priority);

        ObjectNode severity = objectMapper.createObjectNode();
        severity.put("type", "number"); severity.put("description", "严重程度");
        p.set("severity", severity);

        schema.set("properties", p);
        return schema;
    }

    @Override
    public String execute(JsonNode parameters) throws Exception {
        AnomalyRecordDTO dto = new AnomalyRecordDTO();
        if (parameters.has("plot")) dto.setPlot(parameters.get("plot").asText());
        if (parameters.has("date")) dto.setDate(parameters.get("date").asText());
        if (parameters.has("anomaly_type")) dto.setAnomaly_type(parameters.get("anomaly_type").asText());
        if (parameters.has("anomaly_category")) dto.setAnomaly_category(parameters.get("anomaly_category").asText());
        if (parameters.has("mean_ndvi")) dto.setMean_ndvi(parameters.get("mean_ndvi").asDouble());
        if (parameters.has("delta_ndvi")) dto.setDelta_ndvi(parameters.get("delta_ndvi").asDouble());
        if (parameters.has("mean_evi")) dto.setMean_evi(parameters.get("mean_evi").asDouble());
        if (parameters.has("mean_savi")) dto.setMean_savi(parameters.get("mean_savi").asDouble());
        if (parameters.has("mean_ndwi")) dto.setMean_ndwi(parameters.get("mean_ndwi").asDouble());
        if (parameters.has("area_m2")) dto.setArea_m2(parameters.get("area_m2").asDouble());
        if (parameters.has("priority")) dto.setPriority(parameters.get("priority").asDouble());
        if (parameters.has("severity")) dto.setSeverity(parameters.get("severity").asDouble());

        String explanation = llmService.explainAnomaly(dto);
        return "{\"explanation\": \"" + explanation.replace("\"", "\\\"").replace("\n", "\\n") + "\"}";
    }
}

package com.example.smartAgr.service.ai.tools;

import com.example.smartAgr.dao.admin.AdminPlotDao;
import com.example.smartAgr.model.AdminPlot;
import com.example.smartAgr.service.ai.AgentTool;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.ObjectNode;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
@RequiredArgsConstructor
public class QueryPlotsTool implements AgentTool {

    private final AdminPlotDao plotDao;
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public String getName() {
        return "query_plots";
    }

    @Override
    public String getDescription() {
        return "查询农业地块信息。可按地区(region)、作物类型(crop_type)、地块名称(name)筛选。返回地块列表包含名称、面积、作物、联系人等信息。";
    }

    @Override
    public JsonNode getParametersSchema() {
        ObjectNode schema = objectMapper.createObjectNode();
        schema.put("type", "object");
        ObjectNode properties = objectMapper.createObjectNode();
        ObjectNode regionProp = objectMapper.createObjectNode();
        regionProp.put("type", "string");
        regionProp.put("description", "地区名称，如：张北、沽源");
        properties.set("region", regionProp);
        ObjectNode cropProp = objectMapper.createObjectNode();
        cropProp.put("type", "string");
        cropProp.put("description", "当前作物类型，如：玉米、燕麦");
        properties.set("crop_type", cropProp);
        ObjectNode nameProp = objectMapper.createObjectNode();
        nameProp.put("type", "string");
        nameProp.put("description", "地块名称关键词");
        properties.set("name", nameProp);
        schema.set("properties", properties);
        return schema;
    }

    @Override
    public String execute(JsonNode parameters) throws Exception {
        List<AdminPlot> plots;
        String region = parameters.has("region") ? parameters.get("region").asText() : null;

        if (region != null && !region.isEmpty()) {
            plots = plotDao.findByRegion(region);
        } else {
            plots = plotDao.findAll();
        }

        String cropType = parameters.has("crop_type") ? parameters.get("crop_type").asText() : null;
        String name = parameters.has("name") ? parameters.get("name").asText() : null;

        ArrayNode result = objectMapper.createArrayNode();
        for (AdminPlot plot : plots) {
            if (cropType != null && !cropType.isEmpty()
                    && plot.getCurrentCrop() != null && !plot.getCurrentCrop().contains(cropType)) {
                continue;
            }
            if (name != null && !name.isEmpty()
                    && plot.getPlotName() != null && !plot.getPlotName().contains(name)) {
                continue;
            }
            ObjectNode node = objectMapper.createObjectNode();
            node.put("id", plot.getId());
            node.put("name", plot.getPlotName());
            node.put("area", plot.getArea());
            node.put("currentCrop", plot.getCurrentCrop());
            node.put("region", plot.getRegion());
            node.put("soilType", plot.getSoilType());
            node.put("irrigationType", plot.getIrrigationType());
            node.put("contactPerson", plot.getContactPerson());
            node.put("phone", plot.getPhone());
            result.add(node);
        }

        ObjectNode wrapper = objectMapper.createObjectNode();
        wrapper.put("total", result.size());
        wrapper.set("plots", result);
        return objectMapper.writeValueAsString(wrapper);
    }
}

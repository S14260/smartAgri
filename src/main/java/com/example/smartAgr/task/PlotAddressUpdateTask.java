package com.example.smartAgr.task;

import com.example.smartAgr.dao.admin.AdminPlotDao;
import com.example.smartAgr.model.Plot;
import lombok.extern.slf4j.Slf4j;
import org.json.JSONArray;
import org.json.JSONObject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestTemplate;

import java.util.List;

/**
 * 定时任务类，用于定时给前端已有的地块更新地址（逆地理编码）
 */

@Slf4j
@Component
public class PlotAddressUpdateTask {
    @Autowired
    private AdminPlotDao adminPlotDao;
    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${amap.key}")
    private String amapKey;
    public PlotAddressUpdateTask(AdminPlotDao adminPlotDao) {
        this.adminPlotDao = adminPlotDao;
    }

    // 每天凌晨1点执行（可按需调整）
    @Scheduled(cron = "1 * * * * ?")
    public void updatePlotAddresses() {
        log.info("开始执行地块地址更新任务");

        List<Plot> plots = adminPlotDao.findAll();

        for (Plot plot : plots) {
            try {
                if (plot.getAddress() != null && !plot.getAddress().isEmpty()) continue;

                double lng = 0, lat = 0;
                String shapeType = plot.getShapeType();
                String coordinatesJson = plot.getCoordinates();

                JSONObject coordinates = new JSONObject(coordinatesJson);

                if ("circle".equalsIgnoreCase(shapeType)) {
                    JSONObject center = coordinates.optJSONObject("center");
                    if (center == null) {
                        log.warn("地块ID {}: 缺少 center 字段", plot.getId());
                        continue;
                    }
                    lng = center.optDouble("lng");
                    lat = center.optDouble("lat");
                } else if ("polygon".equalsIgnoreCase(shapeType)) {
                    JSONArray points = coordinates.optJSONArray("latlngs");
                    if (points == null || points.length() == 0) {
                        log.warn("地块ID {}: latlngs 字段为空", plot.getId());
                        continue;
                    }
                    double totalLng = 0, totalLat = 0;
                    for (int i = 0; i < points.length(); i++) {
                        JSONObject point = points.getJSONObject(i);
                        totalLng += point.optDouble("lng");
                        totalLat += point.optDouble("lat");
                    }
                    lng = totalLng / points.length();
                    lat = totalLat / points.length();
                } else {
                    log.warn("地块ID {}: 未知的 shapeType {}", plot.getId(), shapeType);
                    continue;
                }

                // 构建高德API URL
                String url = String.format(
                        "https://restapi.amap.com/v3/geocode/regeo?location=%f,%f&key=%s",
                        lng, lat, amapKey
                );

                String response = restTemplate.getForObject(url, String.class);
                JSONObject json = new JSONObject(response);

                if ("1".equals(json.optString("status"))) {
                    JSONObject regeocode = json.optJSONObject("regeocode");
                    if (regeocode != null) {
                        String address = regeocode.optString("formatted_address");
                        plot.setAddress(address);
                        adminPlotDao.save(plot);
                        log.info("地块 [{}] 地址更新成功: {}", plot.getName(), address);
                    } else {
                        log.warn("地块ID {}: 未返回 regeocode 字段", plot.getId());
                    }
                } else {
                    log.warn("地块ID {}: 地址请求失败，状态码 {}", plot.getId(), json.optString("status"));
                }

                Thread.sleep(300); // 控制请求频率

            } catch (Exception e) {
                log.warn("地址获取失败，地块ID {}: {}", plot.getId(), e.getMessage());
            }
        }

        log.info("地块地址更新任务完成");
    }
}

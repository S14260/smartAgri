package com.example.smartAgr.controller;

import com.example.smartAgr.dao.PunchRecordMapper;
import com.example.smartAgr.model.PunchRecord;
import com.example.smartAgr.utils.Result;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.example.smartAgr.model.AdminPlot;
import com.example.smartAgr.service.admin.AdminPlotService;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.List;

@RestController
@RequestMapping("/punch")
@Slf4j
public class PunchController {

    @Autowired
    private AdminPlotService adminPlotService;
    @Autowired
    private PunchRecordMapper punchRecordMapper;

    /**
     * 打卡接口
     * @param location
     * @return
     */
    @PostMapping
    public Result punchIn(@RequestBody Location location) {
        //用于记录打卡坐标
        double lng = location.lng;
        double lat = location.lat;

        List<AdminPlot> plots = adminPlotService.getAllPlots();
        for (AdminPlot adminPlot : plots) {
            try {
                ObjectMapper mapper = new ObjectMapper();
                JsonNode coordJson = mapper.readTree(adminPlot.getCoordinates());
                String type = adminPlot.getShapeType();

                if ("circle".equalsIgnoreCase(type)) {
                    JsonNode center = coordJson.get("center");
                    double radius = coordJson.get("radius").asDouble();
                    double dist = distance(lat, lng,
                            center.get("lat").asDouble(), center.get("lng").asDouble());
                    if (dist <= radius) {
                        return Result.success("进入地块：" + adminPlot.getPlotName());
                    }
                } else if ("polygon".equalsIgnoreCase(type)) {
                    JsonNode points = coordJson.get("latlngs");
                    double[][] polygon = new double[points.size()][2];
                    for (int i = 0; i < points.size(); i++) {
                        polygon[i][0] = points.get(i).get("lat").asDouble();
                        polygon[i][1] = points.get(i).get("lng").asDouble();
                    }
                    if (inPolygon(lat, lng, polygon)) {
                        // 命中地块，保存打卡记录
                        PunchRecord record = new PunchRecord();
                        record.setPlotId(adminPlot.getId());
                        record.setPlotName(adminPlot.getPlotName());
                        record.setLongitude(lng);
                        record.setLatitude(lat);
                        record.setPunchTime(LocalDateTime.now());
                        record.setStatus(1);
                        // record.setUserId   //TODO这里还没实现，需要和登录校验一起整？？

                        punchRecordMapper.insert(record);

                        return Result.success("进入地块：" + adminPlot.getPlotName());
                    }
                }
            } catch (Exception e) {
                return Result.error("解析失败: " + e.getMessage());
            }
        }
        return Result.error("当前位置未在任何地块内");
    }


    private boolean inPolygon(double lat, double lng, double[][] polygon) {
        int cnt = 0;
        for (int i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
            if (((polygon[i][1] > lng) != (polygon[j][1] > lng)) &&
                    (lat < (polygon[j][0] - polygon[i][0]) * (lng - polygon[i][1]) / (polygon[j][1] - polygon[i][1]) + polygon[i][0])) {
                cnt++;
            }
        }
        return cnt % 2 == 1;
    }

    private double distance(double lat1, double lng1, double lat2, double lng2) {
        double r = 6371000; // Earth radius in meters
        double dLat = Math.toRadians(lat2 - lat1);
        double dLng = Math.toRadians(lng2 - lng1);
        double a = Math.sin(dLat / 2) * Math.sin(dLat / 2)
                + Math.cos(Math.toRadians(lat1)) * Math.cos(Math.toRadians(lat2))
                * Math.sin(dLng / 2) * Math.sin(dLng / 2);
        return r * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    }

    @Data
    public static class Location {
        public double lat;
        public double lng;
    }

    /**
     * 获取打卡记录
     * @return
     */
    @GetMapping
    public List<PunchRecord> getPunchRecords() {
        log.info("获取所有打卡记录");
        List<PunchRecord> records = punchRecordMapper.getAllPunchRecords();
        log.info("打卡记录：{}",records);
        return records;
    }
}

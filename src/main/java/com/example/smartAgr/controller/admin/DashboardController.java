package com.example.smartAgr.controller.admin;

import com.example.smartAgr.dao.admin.AdminPlotDao;
import com.example.smartAgr.dao.PunchRecordMapper;
import com.example.smartAgr.model.AdminPlot;
import com.example.smartAgr.result.Result;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/admin/dashboard")
public class DashboardController {

    @Autowired
    private AdminPlotDao adminPlotDao;

    @Autowired
    private PunchRecordMapper punchRecordMapper;

    @GetMapping("/overview")
    public Result<Map<String, Object>> overview() {
        try {
            List<AdminPlot> plots = adminPlotDao.findAll();
            int plotCount = plots.size();
            double totalArea = plots.stream()
                    .filter(p -> p.getArea() != null)
                    .mapToDouble(AdminPlot::getArea)
                    .sum();

            Map<String, Object> data = new HashMap<>();
            data.put("plotCount", plotCount);
            data.put("totalArea", Math.round(totalArea * 100.0) / 100.0);
            data.put("punchCount", punchRecordMapper.getAllPunchRecords().size());
            return Result.success(data);
        } catch (Exception e) {
            return Result.error("获取概览数据失败: " + e.getMessage());
        }
    }

    @GetMapping("/plot-stats")
    public Result<Map<String, Object>> plotStats() {
        try {
            List<AdminPlot> plots = adminPlotDao.findAll();

            Map<String, Long> byCrop = plots.stream()
                    .filter(p -> p.getCurrentCrop() != null && !p.getCurrentCrop().isEmpty())
                    .collect(Collectors.groupingBy(AdminPlot::getCurrentCrop, Collectors.counting()));

            Map<String, Long> byRegion = plots.stream()
                    .filter(p -> p.getRegion() != null && !p.getRegion().isEmpty())
                    .collect(Collectors.groupingBy(AdminPlot::getRegion, Collectors.counting()));

            Map<String, Long> bySoil = plots.stream()
                    .filter(p -> p.getSoilType() != null && !p.getSoilType().isEmpty())
                    .collect(Collectors.groupingBy(AdminPlot::getSoilType, Collectors.counting()));

            Map<String, Object> data = new HashMap<>();
            data.put("byCrop", byCrop);
            data.put("byRegion", byRegion);
            data.put("bySoil", bySoil);
            return Result.success(data);
        } catch (Exception e) {
            return Result.error("获取统计失败: " + e.getMessage());
        }
    }
}

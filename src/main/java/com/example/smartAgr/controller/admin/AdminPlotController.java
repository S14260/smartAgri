package com.example.smartAgr.controller.admin;

import com.example.smartAgr.model.AdminPlot;
import com.example.smartAgr.dao.admin.AdminPlotDao;
import com.example.smartAgr.service.admin.AdminPlotService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/admin/plots")
public class AdminPlotController {

    @Autowired
    private AdminPlotService adminPlotService;
    @Autowired
    private AdminPlotDao adminPlotDao;


    @GetMapping
    public List<AdminPlot> getAllPlots() {

        return adminPlotDao.findAll();
    }

    /**
     * 根据地区获取地块
     * /admin/plots?region=xxx
     */
    @GetMapping(params = "region")
    public List<AdminPlot> getPlotsByRegion(@RequestParam("region") String region) {
        return adminPlotDao.findByRegion(region);
    }


    @PostMapping
    public AdminPlot savePlot(@RequestBody AdminPlot adminPlot) {
        return adminPlotDao.save(adminPlot);
    }


    @DeleteMapping("/{id}")
    public void deletePlot(@PathVariable Long id) {
        adminPlotDao.deleteById(id);
    }


    // 修改地块面积
    @PutMapping("/{id}/area")
    public AdminPlot updatePlotArea(@PathVariable Long id, @RequestBody Map<String, Double> requestBody) {
        Double area = requestBody.get("area");
        if (area == null || area <= 0) {
            throw new IllegalArgumentException("面积必须大于0");
        }

        AdminPlot adminPlot = adminPlotDao.findById(id)
                .orElseThrow(() -> new RuntimeException("地块未找到"));

        adminPlot.setArea(area);
        return adminPlotDao.save(adminPlot);
    }



    @PostMapping("/{id}/address")
    public ResponseEntity<?> updatePlotAddress(@PathVariable Long id, @RequestBody Map<String, String> payload) {
        String address = payload.get("address");
        AdminPlot adminPlot = adminPlotDao.findById(id).get();
        if (adminPlot != null) {
            adminPlot.setAddress(address);
            adminPlotDao.save(adminPlot);
            return ResponseEntity.ok("地址更新成功");
        } else {
            return ResponseEntity.status(404).body("地块不存在");
        }
    }

    @PutMapping("/{id}")
    public AdminPlot updatePlot(@PathVariable Long id, @RequestBody AdminPlot newPlot) {
        AdminPlot adminPlot = adminPlotDao.findById(id)
                .orElseThrow(() -> new RuntimeException("地块未找到"));

        //更新字段
        adminPlot.setPlotName(newPlot.getPlotName());
        adminPlot.setLastCrop(newPlot.getLastCrop());
        adminPlot.setCurrentCrop(newPlot.getCurrentCrop());
        adminPlot.setContactPerson(newPlot.getContactPerson());
        adminPlot.setPhone(newPlot.getPhone());
        adminPlot.setSoilType(newPlot.getSoilType());
        adminPlot.setIrrigationType(newPlot.getIrrigationType());
        adminPlot.setLandType(newPlot.getLandType());
        //adminPlot.setShapeType(newPlot.getShapeType());
        //adminPlot.setCoordinates(newPlot.getCoordinates());
        //adminPlot.setArea(newPlot.getArea());
        //adminPlot.setAddress(newPlot.getAddress());

        return adminPlotDao.save(adminPlot);
    }

    /**
     * 批量删除地块
     * @param ids
     * @return
     */
    @DeleteMapping("/deleteBatch")
    public ResponseEntity<?> deleteBatch(@RequestBody List<Long> ids) {
        try {
            adminPlotService.deletePlotsByIds(ids);
            return ResponseEntity.ok("删除成功");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("删除失败");
        }
    }

}

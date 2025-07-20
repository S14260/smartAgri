package com.example.smartAgr.controller.user;

import com.example.smartAgr.model.UserPlot;
import com.example.smartAgr.dao.user.UserPlotDao;
import com.example.smartAgr.service.user.UserPlotService;
import com.example.smartAgr.context.BaseContext;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/user/plots")
@CrossOrigin
public class UserPlotController {

    @Autowired
    private UserPlotService userPlotService;
    @Autowired
    private UserPlotDao userPlotDao;

    /**
     * 获取当前用户ID（通过BaseContext）
     */
    private Long getCurrentUserId() {
        return BaseContext.getCurrentId();
    }

    @GetMapping
    public List<UserPlot> getUserPlots() {
        Long userId = getCurrentUserId();
        return userPlotDao.findByUserId(getCurrentUserId()); //获取ID
    }

    @PostMapping
    public UserPlot savePlot(@RequestBody UserPlot plot) {
        Long userId = getCurrentUserId();
        System.out.println("当前用户ID: " + userId);
        plot.setUserId(userId);
        return userPlotDao.save(plot);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> deletePlot(@PathVariable Long id) {
        Long userId = getCurrentUserId();
        UserPlot plot = userPlotDao.findById(id).orElse(null);
        if (plot == null || !userId.equals(plot.getUserId())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body("无权限删除该地块");
        }
        userPlotDao.deleteById(id);
        return ResponseEntity.ok("删除成功");
    }

    @PutMapping("/{id}/area")
    public ResponseEntity<?> updatePlotArea(@PathVariable Long id, @RequestBody Map<String, Double> requestBody) {
        Double area = requestBody.get("area");
        if (area == null || area <= 0) {
            return ResponseEntity.badRequest().body("面积必须大于0");
        }

        Long userId = getCurrentUserId();
        UserPlot plot = userPlotDao.findById(id).orElse(null);
        if (plot == null || !userId.equals(plot.getUserId())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body("无权限修改该地块");
        }
        plot.setArea(area);
        userPlotDao.save(plot);
        return ResponseEntity.ok(plot);
    }

    @PutMapping("/{id}")
    public ResponseEntity<?> updatePlot(@PathVariable Long id, @RequestBody UserPlot newPlot) {
        Long userId = getCurrentUserId();
        UserPlot plot = userPlotDao.findById(id).orElse(null);
        if (plot == null || !userId.equals(plot.getUserId())) {
            return ResponseEntity.status(HttpStatus.FORBIDDEN).body("无权限修改该地块");
        }

        plot.setName(newPlot.getName());
        plot.setLastCrop(newPlot.getLastCrop());
        plot.setCurrentCrop(newPlot.getCurrentCrop());
        plot.setContactPerson(newPlot.getContactPerson());
        plot.setPhone(newPlot.getPhone());
        plot.setSoilType(newPlot.getSoilType());
        plot.setIrrigationType(newPlot.getIrrigationType());
        plot.setLandType(newPlot.getLandType());
        plot.setShapeType(newPlot.getShapeType());
        plot.setCoordinates(newPlot.getCoordinates());
        plot.setArea(newPlot.getArea());
        plot.setAddress(newPlot.getAddress());

        userPlotDao.save(plot);
        return ResponseEntity.ok(plot);
    }

    /**
     * 批量删除当前用户地块
     */
    @DeleteMapping("/deleteBatch")
    public ResponseEntity<?> deleteBatch(@RequestBody List<Long> ids) {
        Long userId = getCurrentUserId();
        try {
            for (Long id : ids) {
                UserPlot plot = userPlotDao.findById(id).orElse(null);
                if (plot != null && userId.equals(plot.getUserId())) {
                    userPlotDao.deleteById(id);
                }
            }
            return ResponseEntity.ok("删除成功");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("删除失败");
        }
    }
}

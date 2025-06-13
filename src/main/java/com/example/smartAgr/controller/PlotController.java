package com.example.smartAgr.controller;

import com.example.smartAgr.model.Plot;
import com.example.smartAgr.dao.PlotDao;
import com.example.smartAgr.service.PlotService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/plots")
@CrossOrigin
public class PlotController {

    @Autowired
    private PlotService plotService;
    @Autowired
    private PlotDao plotDao;


    @GetMapping
    public List<Plot> getAllPlots() {
        return plotDao.findAll();
    }

    @PostMapping
    public Plot savePlot(@RequestBody Plot plot) {
        return plotDao.save(plot);
    }


    @DeleteMapping("/{id}")
    public void deletePlot(@PathVariable Long id) {
        plotDao.deleteById(id);
    }

    
    // 修改地块面积
    @PutMapping("/{id}/area")
    public Plot updatePlotArea(@PathVariable Long id, @RequestBody Map<String, Double> requestBody) {
        Double area = requestBody.get("area");
        if (area == null || area <= 0) {
            throw new IllegalArgumentException("面积必须大于0");
        }

        Plot plot = plotDao.findById(id)
                .orElseThrow(() -> new RuntimeException("地块未找到"));

        plot.setArea(area);
        return plotDao.save(plot);
    }



    @PostMapping("/plots/{id}/address")
    public ResponseEntity<?> updatePlotAddress(@PathVariable Long id, @RequestBody Map<String, String> payload) {
        String address = payload.get("address");
        Plot plot = plotDao.findById(id).get();
        if (plot != null) {
            plot.setAddress(address);
            plotDao.save(plot);
            return ResponseEntity.ok("地址更新成功");
        } else {
            return ResponseEntity.status(404).body("地块不存在");
        }
    }

    @PutMapping("/{id}")
    public Plot updatePlot(@PathVariable Long id, @RequestBody Plot newPlot) {
        Plot plot = plotDao.findById(id)
                .orElseThrow(() -> new RuntimeException("地块未找到"));

        //更新字段
        plot.setName(newPlot.getName());
        plot.setLastCrop(newPlot.getLastCrop());
        plot.setCurrentCrop(newPlot.getCurrentCrop());
        plot.setContactPerson(newPlot.getContactPerson());
        plot.setPhone(newPlot.getPhone());
        plot.setSoilType(newPlot.getSoilType());
        plot.setIrrigationType(newPlot.getIrrigationType());
        plot.setLandType(newPlot.getLandType());
        //plot.setShapeType(newPlot.getShapeType());
        //plot.setCoordinates(newPlot.getCoordinates());
        //plot.setArea(newPlot.getArea());
        //plot.setAddress(newPlot.getAddress());

        return plotDao.save(plot);
    }

    /**
     * 批量删除地块
     * @param ids
     * @return
     */
    @DeleteMapping("/deleteBatch")
    public ResponseEntity<?> deleteBatch(@RequestBody List<Long> ids) {
        try {
            plotService.deletePlotsByIds(ids);
            return ResponseEntity.ok("删除成功");
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("删除失败");
        }
    }

}

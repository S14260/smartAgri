package com.example.smartAgr.controller;

import com.example.smartAgr.model.Plot;
import com.example.smartAgr.dao.PlotDao;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/plots")
@CrossOrigin
public class PlotController {

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

}

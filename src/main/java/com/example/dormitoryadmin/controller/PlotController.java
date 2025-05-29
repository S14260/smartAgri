package com.example.dormitoryadmin.controller;

import com.example.dormitoryadmin.model.Plot;
import com.example.dormitoryadmin.dao.PlotDao;
import com.example.dormitoryadmin.model.Student;
import com.example.dormitoryadmin.service.PlotService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

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
    public Plot updatePlotArea(@PathVariable Long id, @RequestBody double area) {
        Plot plot = plotDao.findById(id)
                .orElseThrow(() -> new RuntimeException("地块未找到"));

        // 更新面积
        if (area <= 0) {
            throw new IllegalArgumentException("面积必须大于0");
        }
        plot.setArea(area);

        return plotDao.save(plot);
    }


}

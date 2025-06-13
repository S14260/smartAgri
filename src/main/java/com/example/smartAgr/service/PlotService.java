package com.example.smartAgr.service;

import com.example.smartAgr.dao.PlotDao;
import com.example.smartAgr.model.Plot;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class PlotService {

    @Autowired
    private PlotDao plotDao;

    public Plot savePlot(Plot plot) {
        return plotDao.save(plot); // 保存地块
    }

    public List<Plot> getAllPlots() {
        return plotDao.findAll(); // 获取所有地块
    }

    public void deletePlotsByIds(List<Long> ids) {
        plotDao.deleteAllById(ids);
    }


}

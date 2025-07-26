package com.example.smartAgr.service.admin;

import com.example.smartAgr.dao.admin.AdminPlotDao;
import com.example.smartAgr.model.AdminPlot;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class AdminPlotService {

    @Autowired
    private AdminPlotDao adminPlotDao;

    public AdminPlot savePlot(AdminPlot adminPlot) {
        return adminPlotDao.save(adminPlot); // 保存地块
    }

    public List<AdminPlot> getAllPlots() {
        return adminPlotDao.findAll(); // 获取所有地块
    }

    public void deletePlotsByIds(List<Long> ids) {
        adminPlotDao.deleteAllById(ids);
    }


}

package com.example.smartAgr.service.user;

import com.example.smartAgr.dao.user.UserPlotDao;
import com.example.smartAgr.model.UserPlot;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class UserPlotService {

    @Autowired
    private UserPlotDao userPlotDao;

    public UserPlot savePlot(UserPlot userPlot) {
        return userPlotDao.save(userPlot); // 保存地块
    }

    public List<UserPlot> getAllPlots() {
        return userPlotDao.findAll(); // 获取所有地块
    }

    public void deletePlotsByIds(List<Long> ids) {
        userPlotDao.deleteAllById(ids);
    }


}

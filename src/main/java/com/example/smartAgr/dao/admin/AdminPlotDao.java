package com.example.smartAgr.dao.admin;

import com.example.smartAgr.model.AdminPlot;
import com.example.smartAgr.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AdminPlotDao extends JpaRepository<AdminPlot, Long> {

    public List<AdminPlot> query();

    List<AdminPlot> findByRegion(String region);
}

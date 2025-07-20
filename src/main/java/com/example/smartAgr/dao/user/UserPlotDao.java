package com.example.smartAgr.dao.user;

import com.example.smartAgr.model.UserPlot;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface UserPlotDao extends JpaRepository<UserPlot, Long> {

    public List<UserPlot> query();
    public List<UserPlot> findByUserId(Long id);
}

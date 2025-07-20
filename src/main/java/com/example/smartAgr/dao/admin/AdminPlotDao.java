package com.example.smartAgr.dao.admin;

import com.example.smartAgr.model.Plot;
import com.example.smartAgr.model.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AdminPlotDao extends JpaRepository<Plot, Long> {

    public List<Plot> query();
}

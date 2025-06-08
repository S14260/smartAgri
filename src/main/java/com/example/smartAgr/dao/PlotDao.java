package com.example.smartAgr.dao;

import com.example.smartAgr.model.Plot;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PlotDao extends JpaRepository<Plot, Long> {

    public List<Plot> query();
}

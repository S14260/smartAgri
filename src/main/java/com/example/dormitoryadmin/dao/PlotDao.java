package com.example.dormitoryadmin.dao;

import com.example.dormitoryadmin.model.Plot;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface PlotDao extends JpaRepository<Plot, Long> {

    public List<Plot> query();
}

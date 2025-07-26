package com.example.smartAgr.dao.admin;

import com.example.smartAgr.model.AdminPlot;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;

import org.springframework.stereotype.Repository;

import java.util.List;
@Repository
public class AdminPlotDaoImpl {
    @Autowired
    private JdbcTemplate jdbcTemplate;


    public List<AdminPlot> query(){
        return jdbcTemplate.query("select * from admin_plots",new BeanPropertyRowMapper<>(AdminPlot.class));
    }
}

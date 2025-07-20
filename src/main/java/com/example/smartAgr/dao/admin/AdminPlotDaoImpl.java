package com.example.smartAgr.dao.admin;

import com.example.smartAgr.model.Plot;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;

import org.springframework.stereotype.Repository;

import java.util.List;
@Repository
public class AdminPlotDaoImpl {
    @Autowired
    private JdbcTemplate jdbcTemplate;


    public List<Plot> query(){
        return jdbcTemplate.query("select * from plots",new BeanPropertyRowMapper<>(Plot.class));
    }
}

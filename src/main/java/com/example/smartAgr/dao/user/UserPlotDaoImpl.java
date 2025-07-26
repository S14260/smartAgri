package com.example.smartAgr.dao.user;

import com.example.smartAgr.model.UserPlot;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;
@Repository
public class UserPlotDaoImpl {
    @Autowired
    private JdbcTemplate jdbcTemplate;


    public List<UserPlot> query(){
        return jdbcTemplate.query("select * from user_plots",new BeanPropertyRowMapper<>(UserPlot.class));
    }
}

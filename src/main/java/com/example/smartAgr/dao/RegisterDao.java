package com.example.smartAgr.dao;

import com.example.smartAgr.model.Register;

import java.util.List;

public interface RegisterDao {
    public Integer addRegister(Register d) ;
    public Integer updateRegister(Register d) ;
    public Integer deleteRegister(Integer id) ;
    public List<Register> query() ;
    public Register get(Integer id);
}

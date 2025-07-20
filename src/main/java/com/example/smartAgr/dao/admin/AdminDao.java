package com.example.smartAgr.dao.admin;

import com.example.smartAgr.model.Admin;

import java.util.List;

public interface AdminDao {
    public Integer addAdmin(Admin d) ;
    public Integer updateAdmin(Admin d) ;
    public Integer deleteAdmin(Integer id) ;
    public List<Admin> query() ;
    public Admin get(String username);
}

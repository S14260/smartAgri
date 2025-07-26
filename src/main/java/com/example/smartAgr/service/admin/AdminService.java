package com.example.smartAgr.service.admin;

import com.example.smartAgr.model.Admin;
import org.springframework.stereotype.Service;

import java.util.List;
public interface AdminService {
    public Integer addAdmin(Admin d) ;
    public Integer updateAdmin(Admin d) ;
    public Integer deleteAdmin(Integer id) ;
    public List<Admin> query() ;
    public Admin get(String username);
    boolean login(Admin admin);

}

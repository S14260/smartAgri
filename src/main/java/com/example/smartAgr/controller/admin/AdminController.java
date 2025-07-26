package com.example.smartAgr.controller.admin;

import com.example.smartAgr.model.Admin;
import com.example.smartAgr.service.admin.AdminService;
import com.example.smartAgr.utils.PageUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/admin")
public class AdminController {
    @Autowired
    AdminService adminservice;
    @PostMapping("/add")
    public Integer addDormitory(Admin s) {
        return adminservice.addAdmin(s);
    }
    @PostMapping("/update")
    public Integer updateDormitory(Admin s) {
        return adminservice.updateAdmin(s);
    }
    @GetMapping("/delete")
    public Integer deleteDormitory( Integer id) {return adminservice.deleteAdmin(id);}
    @GetMapping("/query")
    public List<Admin> query() {return adminservice.query();}
    @GetMapping("/get")
    public Admin get(String username){
        return adminservice.get(username);
    }
    @GetMapping("/getListByPage")
    public List<Admin> getListByPage(@RequestParam int pageNo, @RequestParam int pageSize) {
        List<Admin> allAdmins = adminservice.query();  // get student list from service
        return PageUtil.getAdminByPage(allAdmins, pageSize, pageNo);
    }
    @GetMapping("/getTotalCount")
    public int getTotalCount() {
        int totalCount = adminservice.query().size();
        return totalCount;
    }
}


package com.example.smartAgr.controller.admin;

import com.example.smartAgr.properties.JwtProperties;
import com.example.smartAgr.result.Result;
import com.example.smartAgr.model.Admin;
import com.example.smartAgr.service.admin.AdminService;
import com.example.smartAgr.utils.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/admin")
public class AdminLoginController {

    @Autowired
    private AdminService adminService;

    @Autowired
    private JwtProperties jwtProperties;

    @PostMapping("/login")
    public Result<String> login(@RequestParam String username, @RequestParam String password) {
        // 根据用户名查找管理员
        Admin admin = adminService.get(username);
        if (admin == null) {
            return Result.error("管理员不存在");
        }

        // 校验密码
        if (!admin.getPassword().equals(password)) {
            return Result.error("密码错误");
        }

        // 构造JWT payload
        Map<String, Object> claims = new HashMap<>();
        claims.put("username", admin.getUsername());
        claims.put("adminId", admin.getId());

        String token = JwtUtil.createJWT(jwtProperties.getAdminSecretKey(), jwtProperties.getAdminTtl(), claims);
        return Result.success(token);
    }
}

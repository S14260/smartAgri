package com.example.smartAgr.controller.user;

import com.example.smartAgr.properties.JwtProperties;
import com.example.smartAgr.result.Result;
import com.example.smartAgr.model.User;
import com.example.smartAgr.service.user.UserService;
import com.example.smartAgr.utils.JwtUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/user")
public class UserLoginController {

    @Autowired
    private UserService userService;
    @Autowired
    private JwtProperties jwtProperties;


    @PostMapping("/login")
    public Result<String> login(@RequestParam String username, @RequestParam String password) {
        // 根据用户名查找用户
        User user = userService.findByUsername(username);

        if (user == null) {
            return Result.error("用户不存在");
        }

        // 校验密码
        if (!user.getPassword().equals(password)) {
            return Result.error("密码错误");
        }

        // 构造JWT payload
        Map<String, Object> claims = new HashMap<>();
        claims.put("username", user.getUsername());
        claims.put("userId", user.getId());

        String token = JwtUtil.createJWT(jwtProperties.getUserSecretKey(), jwtProperties.getUserTtl(), claims);
        return Result.success(token);
    }

}

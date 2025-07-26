package com.example.smartAgr.controller.user;

import com.example.smartAgr.model.User;
import com.example.smartAgr.service.user.UserService;
import com.example.smartAgr.utils.PageUtil;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/user")
public class UserController {

    @Autowired
    UserService userservice;
    @PostMapping("/add")
    public Integer addDormitory(User s) {
        return userservice.addUser(s);
    }
    @PostMapping("/update")
    public Integer updateDormitory(User s) {
        return userservice.updateUser(s);
    }
    @GetMapping("/delete")
    public Integer deleteDormitory( Integer id) {return userservice.deleteUser(id);}
    @GetMapping("/query")
    public List<User> query() {return userservice.query();}
    @GetMapping("/get")
    public User get(String username){
        return userservice.get(username);
    }
    @GetMapping("/getTotalCount")
    public int getTotalCount() {
        int totalCount = userservice.query().size();
        return totalCount;
    }
}


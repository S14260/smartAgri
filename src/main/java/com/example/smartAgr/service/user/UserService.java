package com.example.smartAgr.service.user;

import com.example.smartAgr.model.User;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public interface UserService {
    public Integer addUser(User user);
    public Integer updateUser(User user);
    public Integer deleteUser(Integer id);
    public List<User> query();
    public User get(String username);
    boolean login(User user);
    User findByUsername(String username);
}

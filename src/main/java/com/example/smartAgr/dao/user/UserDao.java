package com.example.smartAgr.dao.user;

import com.example.smartAgr.model.User;
import java.util.List;

public interface UserDao {
    Integer addUser(User user);
    Integer updateUser(User user);
    Integer deleteUser(Integer id);
    List<User> query();
    User get(String username);
}

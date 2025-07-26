package com.example.smartAgr.service.user;

import com.example.smartAgr.dao.user.UserDao;
import com.example.smartAgr.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
public class UserServiceImpl implements UserService {
    @Autowired
    private UserDao userDao;

    @Override
    public Integer addUser(User user) {
        return userDao.addUser(user);
    }

    @Override
    public Integer updateUser(User user) {
        return userDao.updateUser(user);
    }

    @Override
    public Integer deleteUser(Integer id) {
        return userDao.deleteUser(id);
    }

    @Override
    public List<User> query() {
        return userDao.query();
    }

    @Override
    public User get(String username) {
        return userDao.get(username);
    }

    @Override
    public boolean login(User user) {
        User foundUser = userDao.get(user.getUsername());
        if (foundUser == null) {
            return false;
        }
        return foundUser.getPassword().equals(user.getPassword());
    }

    @Override
    public User findByUsername(String username) {
        return userDao.get(username);
    }
}

package com.example.smartAgr.dao.user;

import com.example.smartAgr.model.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.BeanPropertyRowMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public class UserDaoImpl implements UserDao {
    @Autowired
    JdbcTemplate jdbcTemplate;

    @Override
    public Integer addUser(User user) {
        return jdbcTemplate.update("INSERT INTO user(username,password,sex,age,phone) VALUES (?,?,?,?,?)",
                user.getUsername(), user.getPassword(), user.getSex(), user.getAge(), user.getPhone());
    }

    @Override
    public Integer updateUser(User user) {
        return jdbcTemplate.update("UPDATE user SET username=?, password=?, sex=?, age=?, phone=? WHERE id=?",
                user.getUsername(), user.getPassword(), user.getSex(), user.getAge(), user.getPhone(), user.getId());
    }

    @Override
    public Integer deleteUser(Integer id) {
        return jdbcTemplate.update("DELETE FROM user WHERE id=?", id);
    }

    @Override
    public List<User> query() {
        return jdbcTemplate.query("SELECT * FROM user", new BeanPropertyRowMapper<>(User.class));
    }

    @Override
    public User get(String username) {
        return jdbcTemplate.queryForObject("SELECT * FROM user WHERE username=?",
                new BeanPropertyRowMapper<>(User.class), username);
    }

    @Override
    public String getUserNameById(Long userId) {
        return jdbcTemplate.queryForObject(
                "SELECT username FROM user WHERE id = ?",
                new Object[]{userId},
                String.class
        );
    }

}

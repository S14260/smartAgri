package com.example.dormitoryadmin;

import com.example.dormitoryadmin.dao.AdminDao;
import com.example.dormitoryadmin.dao.StudentDao;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import java.nio.charset.StandardCharsets;

@SpringBootTest
class DormitoryAdminApplicationTests {
    @Autowired
    AdminDao adminDao;
    @Autowired
    StudentDao studentDao;
    @Test
    void contextLoads() {
        System.out.println(studentDao.get(2020111182).getStudentname());
        System.out.println("-------------------");
    }
    @Test
    void query() {

        System.out.println(studentDao.queryPlot().get(2));
    }
}

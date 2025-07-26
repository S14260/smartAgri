package com.example.smartAgr;

import com.example.smartAgr.dao.admin.AdminDao;
import com.example.smartAgr.dao.StudentDao;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

@SpringBootTest
class SmartAgrApplicationTests {
    @Autowired
    AdminDao adminDao;

    @Autowired
    StudentDao studentDao;
    @Test
    void contextLoads() {
        System.out.println(studentDao.get(2020111182).getStudentname());
        System.out.println("-------------------");
    }
}



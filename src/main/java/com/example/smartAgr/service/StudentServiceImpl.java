package com.example.smartAgr.service;

import com.example.smartAgr.dao.StudentDao;
import com.example.smartAgr.model.Plot;
import com.example.smartAgr.model.Student;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
@Transactional
public class StudentServiceImpl implements StudentService {
    @Autowired
    StudentDao studentdao;

    @Override
    public Integer addStudent(Student s) {
        return studentdao.addStudent(s);
    }

    @Override
    public Integer updateStudent(Student s) {
        return studentdao.updateStudent(s);
    }

    @Override
    public Integer deleteStudent(Integer id) {
        return studentdao.deleteStudent(id);
    }

    @Override
    public List<Student> query() {
        return studentdao.query();
    }

    @Override
    public Student get(Integer studentid) {
        return studentdao.get(studentid);
    }

    @Override
    public List<Student> getAllstudent(String dormitory) {
        return studentdao.getAllstudent(dormitory);
    }


    @Override
    public List<Plot> queryPlot() {
        return studentdao.queryPlot();
    }
}

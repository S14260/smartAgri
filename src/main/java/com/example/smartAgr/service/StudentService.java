package com.example.smartAgr.service;

import com.example.smartAgr.model.Plot;
import com.example.smartAgr.model.Student;

import java.util.List;

public interface StudentService {
    public  Integer addStudent(Student s) ;
    public  Integer updateStudent(Student s) ;
    public Integer deleteStudent(Integer studentid) ;
    public List<Student> query() ;
    public Student get(Integer studentid);
    public List<Student> getAllstudent(String dormitory) ;
    public List<Plot> queryPlot() ;
}


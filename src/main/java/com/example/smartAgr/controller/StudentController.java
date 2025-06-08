package com.example.smartAgr.controller;


import com.example.smartAgr.model.Plot;
import com.example.smartAgr.model.Student;
import com.example.smartAgr.utils.PageUtil;
import com.example.smartAgr.service.StudentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController

@RequestMapping("/student")
public class StudentController {
    @Autowired
    private StudentService StudentService;
    @PostMapping("/add")
    public Integer addStudent(Student s) {
        return StudentService.addStudent(s);
    }
    @PostMapping("/update")
    public Integer updateStudent(Student s) {
        return StudentService.updateStudent(s);
    }
    @GetMapping("/delete")
    public Integer delete( Integer id) {return StudentService.deleteStudent(id);}
    @GetMapping("/query")
    public List<Student> query() {return StudentService.query();}
    @GetMapping("/get")
    public Student get(Integer studentid){
        return StudentService.get(studentid);
    }
    @GetMapping("/getstudentall")
    public List<Student> getAllstudent(String dormitory) {return StudentService.getAllstudent(dormitory);}

    @GetMapping("/getListByPage")
    public List<Student> getListByPage(@RequestParam int pageNo, @RequestParam int pageSize) {
        List<Student> allStudents = StudentService.query();  // get student list from service
        return PageUtil.getPersonsByPage(allStudents, pageSize, pageNo);
    }
    @GetMapping("/getTotalCount")
    public int getTotalCount() {
        int totalCount = StudentService.query().size();
        return totalCount;
    }


    @GetMapping("/queryPlot")
    public List<Plot> queryPlot() {return StudentService.queryPlot();}
}


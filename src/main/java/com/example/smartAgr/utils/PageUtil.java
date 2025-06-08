package com.example.smartAgr.utils;

import com.example.smartAgr.model.Admin;
import com.example.smartAgr.model.Dormitory;
import com.example.smartAgr.model.Register;
import com.example.smartAgr.model.Student;

import java.util.List;

public class PageUtil {
    public static List<Student> getPersonsByPage(List<Student> list, int pageSize, int pageNo) {
        int totalCount = list.size();
        int pageCount = 0;
        if (totalCount % pageSize == 0){
            pageCount = totalCount/pageSize;
        } else {
            pageCount = totalCount/pageSize + 1;
        }

        int fromIndex = 0;
        int toIndex = 0;
        if (pageNo == pageCount) {
            fromIndex = (pageNo - 1)*pageSize;
            toIndex = totalCount;
        } else {
            fromIndex = (pageNo - 1)*pageSize;
            toIndex = fromIndex + pageSize;
        }
        return list.subList(fromIndex, toIndex);
    }


    public static List<Dormitory> getDormitoryByPage(List<Dormitory> list, int pageSize, int pageNo) {
        int totalCount = list.size();
        int pageCount = 0;
        if (totalCount % pageSize == 0){
            pageCount = totalCount/pageSize;
        } else {
            pageCount = totalCount/pageSize + 1;
        }

        int fromIndex = 0;
        int toIndex = 0;
        if (pageNo == pageCount) {
            fromIndex = (pageNo - 1)*pageSize;
            toIndex = totalCount;
        } else {
            fromIndex = (pageNo - 1)*pageSize;
            toIndex = fromIndex + pageSize;
        }
        return list.subList(fromIndex, toIndex);
    }
    //Register
    public static List<Register> getRegisterByPage(List<Register> list, int pageSize, int pageNo) {
        int totalCount = list.size();
        int pageCount = 0;
        if (totalCount % pageSize == 0){
            pageCount = totalCount/pageSize;
        } else {
            pageCount = totalCount/pageSize + 1;
        }

        int fromIndex = 0;
        int toIndex = 0;
        if (pageNo == pageCount) {
            fromIndex = (pageNo - 1)*pageSize;
            toIndex = totalCount;
        } else {
            fromIndex = (pageNo - 1)*pageSize;
            toIndex = fromIndex + pageSize;
        }
        return list.subList(fromIndex, toIndex);
    }

//    Admin
public static List<Admin> getAdminByPage(List<Admin> list, int pageSize, int pageNo) {
    int totalCount = list.size();
    int pageCount = 0;
    if (totalCount % pageSize == 0){
        pageCount = totalCount/pageSize;
    } else {
        pageCount = totalCount/pageSize + 1;
    }

    int fromIndex = 0;
    int toIndex = 0;
    if (pageNo == pageCount) {
        fromIndex = (pageNo - 1)*pageSize;
        toIndex = totalCount;
    } else {
        fromIndex = (pageNo - 1)*pageSize;
        toIndex = fromIndex + pageSize;
    }
    return list.subList(fromIndex, toIndex);
}

}
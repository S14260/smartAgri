package com.example.smartAgr.model;

import lombok.Data;

// src/main/java/com/yourpackage/entity/Location.java
@Data  // Lombok自动生成getter/setter（确保已引入Lombok依赖）
public class Location {
    private String name;
    private double lat;
    private double lng;

    // 新增带参数的构造函数
    public Location(String name, double lat, double lng) {
        this.name = name;
        this.lat = lat;
        this.lng = lng;
    }

    // 如果已有其他代码（如无参构造或setter），保留它们
}

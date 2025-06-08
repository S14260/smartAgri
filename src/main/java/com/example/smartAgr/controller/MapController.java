package com.example.smartAgr.controller;

import com.example.smartAgr.model.Location;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Arrays;
import java.util.List;

// src/main/java/com/yourpackage/controller/MapController.java
@RestController
@RequestMapping("/api")
public class MapController {

    @GetMapping("/locations")
    public List<Location> getLocations() {
        // 示例数据（可替换为数据库查询）
        return Arrays.asList(
                new Location("天安门", 39.90923, 116.397428),
                new Location("故宫", 39.916345, 116.397155)
        );
    }
}

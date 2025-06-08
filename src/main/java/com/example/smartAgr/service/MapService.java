package com.example.smartAgr.service;

import com.example.smartAgr.model.Location;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class MapService {
    @Autowired  // 确保已注入
    private RestTemplate restTemplate;
//    @Value("${amap.key}") // 高德API密钥（在application.properties中配置）
    private String apiKey;

    // 调用高德API获取路径规划
    public String getDrivingRoute(Location origin, Location destination) {
        String originStr = origin.getLng() + "," + origin.getLat();
        String destStr = destination.getLng() + "," + destination.getLat();
        String url = "https://restapi.amap.com/v3/direction/driving?" +
                "origin=" + originStr +
                "&destination=" + destStr +
                "&key=" + "2bb60e433f5d43d8401f3ee270749f17";
        return restTemplate.getForObject(url, String.class); // 返回JSON结果
    }
}

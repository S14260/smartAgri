package com.example.smartAgr.model;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class PunchRecord {
    private Long id;
    private Long plotId;
    private String plotName;
    private Double longitude;
    private Double latitude;
    private LocalDateTime punchTime;
    private Long userId;
    private String remark;
    private Integer status; //状态 1有效 2无效

}

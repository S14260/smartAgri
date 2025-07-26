package com.example.smartAgr.model;


import lombok.Data;

import javax.persistence.*;

@Entity
@Table(name = "admin_plots")
@Data
public class AdminPlot {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String plotName;
    private String lastCrop;
    private String currentCrop;
    private String contactPerson;
    private String phone;
    private String soilType;
    private String irrigationType;
    private String landType;
    private String shapeType;
    @Lob
    @Column(columnDefinition = "TEXT")
    private String coordinates;
    private Double area;
    private String address;

    // 如果你需要自定义构造器，可以保留，但无参构造器必须在
    public AdminPlot() {}
}

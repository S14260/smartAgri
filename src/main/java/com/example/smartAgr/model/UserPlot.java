package com.example.smartAgr.model;

import lombok.Data;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import javax.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "user_plots")
@Data
public class UserPlot {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "user_id", nullable = false)
    private Long userId;  // 所属用户ID

    private String userName;

    private String plotName;

    @Column(name = "last_crop")
    private String lastCrop;

    @Column(name = "current_crop")
    private String currentCrop;

    @Column(name = "contact_person")
    private String contactPerson;

    private String phone;

    @Column(name = "soil_type")
    private String soilType;

    @Column(name = "irrigation_type")
    private String irrigationType;

    @Column(name = "land_type")
    private String landType;

    @Column(name = "shape_type")
    private String shapeType;

    @Lob
    @Column(columnDefinition = "TEXT")
    private String coordinates;

    private Double area;

    private String address;

    @CreationTimestamp
    @Column(name = "create_time", updatable = false)
    private LocalDateTime createTime;

    @UpdateTimestamp
    @Column(name = "update_time")
    private LocalDateTime updateTime;

    public UserPlot() {}

}

package com.example.smartAgr.model;


import lombok.Data;

import javax.persistence.*;

@Entity
@Table(name = "plots")
@Data
public class Plot {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String name; // 地块名称
    private String lastCrop; // 上季作物
    private String currentCrop; // 本季作物
    private String contactPerson; // 联系人
    private String phone; // 电话
    private String soilType; // 土壤类型
    private String irrigationType; // 灌溉条件
    private String landType; // 土地类型
    private String shapeType; // 图形类型（polygon 或 circle）
    @Lob
    @Column(columnDefinition = "TEXT")
    private String coordinates; // 坐标数据（JSON字符串）
    private Double area; // 面积
    private String address;






    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getLastCrop() {
        return lastCrop;
    }

    public void setLastCrop(String lastCrop) {
        this.lastCrop = lastCrop;
    }

    public String getCurrentCrop() {
        return currentCrop;
    }

    public void setCurrentCrop(String currentCrop) {
        this.currentCrop = currentCrop;
    }

    public String getContactPerson() {
        return contactPerson;
    }

    public void setContactPerson(String contactPerson) {
        this.contactPerson = contactPerson;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getSoilType() {
        return soilType;
    }

    public void setSoilType(String soilType) {
        this.soilType = soilType;
    }

    public String getIrrigationType() {
        return irrigationType;
    }

    public void setIrrigationType(String irrigationType) {
        this.irrigationType = irrigationType;
    }

    public String getLandType() {
        return landType;
    }

    public void setLandType(String landType) {
        this.landType = landType;
    }

    public String getShapeType() {
        return shapeType;
    }

    public void setShapeType(String shapeType) {
        this.shapeType = shapeType;
    }

    public String getCoordinates() {
        return coordinates;
    }

    public void setCoordinates(String coordinates) {
        this.coordinates = coordinates;
    }

    public Double getArea() {
        return area;
    }

    public void setArea(Double area) {
        this.area = area;
    }

    public Plot(Long id, String name, String lastCrop, String currentCrop, String contactPerson, String phone, String soilType, String irrigationType, String landType, String shapeType, String coordinates, Double area) {
        this.id = id;
        this.name = name;
        this.lastCrop = lastCrop;
        this.currentCrop = currentCrop;
        this.contactPerson = contactPerson;
        this.phone = phone;
        this.soilType = soilType;
        this.irrigationType = irrigationType;
        this.landType = landType;
        this.shapeType = shapeType;
        this.coordinates = coordinates;
        this.area = area;
    }

    public Plot() {
    }
}

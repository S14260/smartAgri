package com.example.smartAgr.model;

import lombok.Data;
import java.util.List;

@Data
public class AnomalyRecordDTO {

    // 基本信息
    private String plot;
    private String plot_id;
    private String date;

    // 异常信息
    private String anomaly_type;
    private String anomaly_category;
    private Integer global_suggest_order;
    private Double priority;
    private Double score;
    private Double multi_index_score;
    private Double severity;

    // 面积信息
    private Double area_m2;
    private Double area_ratio_delta;
    private Double edge_ratio;

    // 多指数均值
    private Double mean_ndvi;
    private Double mean_evi;
    private Double mean_savi;
    private Double mean_ndwi;

    // 多指数增量
    private Double delta_ndvi;
    private Double delta_evi;
    private Double delta_savi;
    private Double delta_ndwi;

    // 图片资源
    private String report_png;
    private String anomaly_map_png;

    // 中心点坐标
    private List<Double> centroid;

    // 可选辅助信息（JSON 中可能没有，但未来可加）
    private String last_crop;
    private String current_crop;
    private String contact_person;
    private String phone;
}

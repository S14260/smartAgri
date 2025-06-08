package com.example.smartAgr.dao;

import com.example.smartAgr.model.PunchRecord;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

@Mapper
public interface PunchRecordMapper{


    /**
     * 插入一条打卡数据
     * @param punchRecord
     */
    @Insert("insert into punch_record(plot_id, plot_name, longitude, latitude, punch_time, user_id, remark,status) values(#{plotId}, #{plotName}, #{longitude}, #{latitude}, #{punchTime}, #{userId}, #{remark},#{status})")
    void insert(PunchRecord punchRecord);

    @Select("select * from punch_record")
    List<PunchRecord> getAllPunchRecords();
}


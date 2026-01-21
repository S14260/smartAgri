package com.example.smartAgr.service.admin;

import com.example.smartAgr.model.AnomalyRecordDTO;

public interface LlmService {

    /**
     * 根据巡田异常工单生成智能解释
     *
     * @param anomalyRecord JSON 对象（地图工单记录）
     * @return 智能体解释文本
     * @throws Exception 调用 LLM 失败
     */
    String explainAnomaly(AnomalyRecordDTO anomalyRecord) throws Exception;
}

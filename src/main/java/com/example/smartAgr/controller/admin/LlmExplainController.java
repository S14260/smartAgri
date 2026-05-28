package com.example.smartAgr.controller.admin;

import com.example.smartAgr.model.AnomalyRecordDTO;
import com.example.smartAgr.result.Result;
import com.example.smartAgr.service.admin.LlmService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/admin/ai")
@RequiredArgsConstructor
public class LlmExplainController {

    private final LlmService llmService;

    @PostMapping("/explain")
    public Result<String> explain(@RequestBody AnomalyRecordDTO anomalyRecord) {
        try {
            String explanation = llmService.explainAnomaly(anomalyRecord);
            return Result.success(explanation);
        } catch (Exception e) {
            return Result.error("AI 解释失败: " + e.getMessage());
        }
    }

}

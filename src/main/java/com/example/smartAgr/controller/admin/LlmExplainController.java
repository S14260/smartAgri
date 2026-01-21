package com.example.smartAgr.controller.admin;

import com.example.smartAgr.model.AnomalyRecordDTO;
import com.example.smartAgr.service.admin.LlmService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/admin/ai")
@RequiredArgsConstructor
public class LlmExplainController {

    private final LlmService llmService;

    @PostMapping("/explain")
    public String explain(@RequestBody AnomalyRecordDTO anomalyRecord) throws Exception {
        return llmService.explainAnomaly(anomalyRecord);
    }

}

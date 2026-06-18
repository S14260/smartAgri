# 第二阶段补充：Bug修复与功能打磨

> 时间：2026-06-08
> 目标：巡田报告页改造 + LLM集成修复 + AI助手Bug修复 + 驾驶舱/登录页修复

---

## 一、任务清单

| # | 任务 | 状态 | 工作量 |
|---|------|------|--------|
| 1 | 巡田报告页重新设计（路线图+异常图片） | ✅ 完成 | ~30min |
| 2 | LLM接口切换（MiMo → DeepSeek） | ✅ 完成 | ~10min |
| 3 | AI助手工具调用死循环修复 | ✅ 完成 | ~30min |
| 4 | AI助手思维链可视化重复修复 | ✅ 完成 | ~15min |
| 5 | CORS配置冲突修复 | ✅ 完成 | ~10min |
| 6 | 登录页字段名不匹配修复 | ✅ 完成 | ~5min |
| 7 | 驾驶舱401处理 + 快捷入口修复 | ✅ 完成 | ~10min |

**总工作量**：约 2 小时

---

## 二、改动详情

### 2.1 巡田报告页重新设计

**修改文件**：
- `static/admin-report.html`
- `static/css/report.css`

**改动内容**：

#### 按钮统一
- 生成任务单：`layui-btn layui-btn-normal`（蓝色主色调）
- 打印/关闭：`layui-btn layui-btn-sm`（小号）
- 刷新：`layui-btn layui-btn-normal layui-btn-sm`

#### 路线图区域
- 生成报告后自动调用 Flask `/xuntian/patrol/plan` 获取路线图
- 显示总里程、途经地块数、路线可视化图片
- 路线建议文本（LLM生成 + Flask路线建议合并）
- 路线规划API参数：`report_path`（工单URL），非 `plot_names`
- 添加 loading 动画、onload/onerror 处理、120秒超时

#### 异常缩略图
- 从 `report_info.visual_report_dir` 构建前端图片URL
- URL构造逻辑：提取 `xuntian_results/...` 相对路径，拼接 `FLASK_BASE/static/...`
- 每个任务项右侧显示 80x80 异常检测缩略图
- hover 时显示放大镜遮罩
- 点击打开 `layer.photos` 大图弹窗
- 图片加载失败时自动隐藏
- 任务头部增加"查看异常图"按钮

#### 任务项优化
- 面积和NDVI指标加了图标
- 联系人信息加了电话图标
- 左右布局：左侧文字 + 右侧缩略图

#### 打印样式
- 路线图和缩略图在打印时保留
- 放大镜遮罩和"查看异常图"按钮在打印时隐藏

---

### 2.2 LLM接口配置

**修改文件**：
- `src/main/resources/application.yml`

**改动内容**：

#### MiMo配置（已废弃）
- `base-url`: `https://token-plan-cn.xiaomimimo.com/v1`
- `model`: `mimo-v2.5-pro`
- `chat-endpoint`: `/chat/completions`（修复了 `/v1/chat/completions` 导致的双 `/v1` 问题）

#### DeepSeek配置（当前）
- `base-url`: `https://api.deepseek.com/v1`
- `model`: `deepseek-chat`
- `api-key`: `sk-fdf066b5724d4c31a7f68c1095aa22cd`
- `chat-endpoint`: `/chat/completions`

#### System Prompt增强
新增工具使用指南，指导LLM正确调用工具：
- `query_plots`：按 region/crop_type/name 筛选
- `get_anomaly_records`：先 action=list 获取列表，再 action=detail 查看详情
- `explain_anomaly`：需要 plot 和 anomaly_category
- `trigger_anomaly_detection`：需要 plot_ids、start_date、end_date、region
- `generate_patrol_route`：需要 report_path（工单URL）
- 重要：不要重复调用同一工具

---

### 2.3 AI助手工具调用修复

**修改文件**：
- `src/main/java/com/example/smartAgr/service/ai/AgentService.java`
- `src/main/java/com/example/smartAgr/service/ai/tools/GetAnomalyRecordsTool.java`
- `src/main/java/com/example/smartAgr/service/ai/tools/QueryPlotsTool.java`
- `src/main/java/com/example/smartAgr/service/ai/tools/ExplainAnomalyTool.java`
- `src/main/java/com/example/smartAgr/service/ai/tools/TriggerAnomalyDetectionTool.java`
- `src/main/java/com/example/smartAgr/service/ai/tools/GeneratePatrolRouteTool.java`

**改动内容**：

#### 工具Schema修复（所有5个工具）
- 添加 `required` 字段到 `getParametersSchema()`
- `GetAnomalyRecordsTool`: `required: ["action"]`
- `GeneratePatrolRouteTool`: `required: ["report_path"]`
- `TriggerAnomalyDetectionTool`: `required: ["plot_ids", "start_date", "end_date", "region"]`
- `ExplainAnomalyTool`: `required: ["plot", "anomaly_category"]`
- `QueryPlotsTool`: 无必填参数（所有参数均可选）
- 添加缺失的 `ArrayNode` import

#### GetAnomalyRecordsTool优化
- `action=detail` 时验证 `report_path` 必填
- `action=list` 返回精简格式（只保留 `generate_time`, `total_anomaly_count`, `report_url`）
- `action=detail` 返回精简格式（去掉 geojson 等大字段）

#### AgentService流式解析修复
- `function.name` 可能在后续 SSE chunk 中到达，添加延迟捕获逻辑
- 流式结束后过滤掉 name 为 null 的无效 tool_call
- JSON 参数解析失败时降级为空对象 `{}`
- 非流式模式 `parseResponse` 同样加了 try-catch

---

### 2.4 AI助手思维链可视化修复

**修改文件**：
- `static/admin-patrol-cesium.html`

**改动内容**：

#### 思考内容重复问题
- `token` 事件把思考内容渲染到回答气泡
- `thought` 事件又把同样内容加到推理链面板
- 修复：`thought` 事件到达时清空回答气泡中的 `accumulatedMarkdown`

#### tool_start ID冲突
- 同一工具多次调用时 `id="action-{tool_name}"` 冲突
- 修复：用唯一计数器 `toolCallCounter` 生成 `id="action-{counter}"`
- `tool_result` 用 `querySelectorAll` + `dataset.toolName` 查找匹配元素

#### 新增步骤时重置计数器
- 每个新步骤开始时 `toolCallCounter = 0`

---

### 2.5 CORS配置冲突修复

**修改文件**：
- `src/main/java/com/example/smartAgr/config/CorsConfig.java`（已删除）
- `src/main/java/com/example/smartAgr/interceptor/WebMvcConfig.java`
- `src/main/java/com/example/smartAgr/controller/admin/DashboardController.java`
- `src/main/java/com/example/smartAgr/controller/admin/AdminPlotController.java`
- `src/main/java/com/example/smartAgr/controller/admin/ReportController.java`
- `src/main/java/com/example/smartAgr/controller/user/UserPlotController.java`

**改动内容**：
- 删除 `CorsConfig.java`（与 `WebMvcConfig` 的 CORS 配置冲突）
- `WebMvcConfig` 改用 `allowedOriginPatterns("*")`（兼容 `allowCredentials(true)`）
- 移除所有控制器上的 `@CrossOrigin` 注解（全局配置已覆盖）

---

### 2.6 登录页修复

**修改文件**：
- `static/login.html`

**改动内容**：
- `res.message` 改为 `res.msg`（与 `Result.java` 的 `msg` 字段一致）
- 修复前：登录失败时永远显示兜底文案"账号或密码错误"
- 修复后：显示后端返回的真正错误信息（如"管理员不存在"、"密码错误"）

---

### 2.7 驾驶舱修复

**修改文件**：
- `static/welcome.html`

**改动内容**：

#### 401处理
- 新增 `handleAuthError(xhr)` 函数
- Dashboard API 返回 401 时自动跳转登录页
- 清除本地 token 并提示"登录已过期"

#### 快捷入口修复
- 所有 `add_tab` 调用补上第4个参数 `'adminTab'`
- 修复前：默认 `layFilter='xbs_tab'`，与实际 tab 容器 `lay-filter="adminTab"` 不匹配，按钮完全没反应
- 修复后：正确匹配，点击可打开对应页面

---

## 三、已知遗留问题

| 问题 | 优先级 | 说明 |
|------|--------|------|
| Flask外部服务依赖 | P1 | 驾驶舱的工单数、异常数、遥感影像依赖 `123.56.228.32:8000`，不可达时显示0或"--" |
| AI助手链接指向 | P2 | 快捷入口"AI助手"指向 `admin-patrol-cesium.html`（Cesium页面），非独立AI页面 |
| AdminPlotDao.query() | P2 | 无 `@Query` 注解，JPA 可能尝试自动生成查询实现 |
| 密码明文存储 | P2 | 已知安全问题，未修复 |

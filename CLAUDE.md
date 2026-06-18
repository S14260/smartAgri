# CLAUDE.md

Smart Agriculture Management System（智慧农业管理系统）— 双服务架构：
- Java/Spring Boot 后端 (port 8080)：核心 CRUD、认证、地块管理、AI Agent
- Python/Flask 微服务 (port 8000)：NDVI 卫星图像处理、巡检分析、路线规划
- 前端：服务端渲染 HTML（LayUI/X-admin/Leaflet/Cesium）

---

## 工作流程

修改代码或执行命令前，先说明：

1. **任务目标** — 要解决什么问题
2. **涉及文件** — 哪些文件会被修改
3. **实现方案** — 具体怎么改
4. **影响范围** — 改动会影响哪些模块
5. **验证方法** — 如何确认改动正确

除非明确要求"直接执行"，否则不跳过计划阶段。

---

## 开发原则

- 先阅读相关代码，再修改
- 保持现有项目结构和代码风格
- 只修改与任务直接相关的文件
- 不进行无关重构、无关格式化、无关依赖调整
- 优先局部修复，避免一次性大改多个模块

---

## 高风险操作

以下操作必须先说明原因、影响和回滚方式，并等待确认：

- 安装、升级或删除依赖
- 修改 Python / Java / Node / CUDA / torch / conda / pip 等环境
- 删除文件或目录
- 修改数据库结构或迁移脚本
- 执行长时间训练、下载、构建或批处理任务
- 执行 git commit、git push、git reset --hard、git clean
- 执行可能破坏数据的 shell 命令

---

## 修改后汇报

每次修改后必须说明：

- 修改了哪些文件
- 为什么这样改
- 影响哪些模块
- 是否运行验证
- 验证命令和结果
- 仍然存在的风险

---

## 项目信息

### 构建运行

```bash
# Java 后端（需要 MySQL localhost:3306，数据库 mydb）
./mvnw clean package
./mvnw spring-boot:run        # 端口 8080

# Python API（单独终端）
cd api
pip install -r requirements.txt
python app.py                 # 端口 8000
```

数据库：导入 `src/main/resources/mydb.sql`，默认凭证 root/root。

### 架构

**Java 后端 (`com.example.smartAgr`)**
- 双 JWT 认证：admin 用 header `token` (secret `smartArgAdmin`)，user 用 header `authentication` (secret `smartArgUser`)
- 混合数据访问：JdbcTemplate（旧实体）、JPA（地块）、MyBatis-Plus（打卡记录）— 不要混用
- 控制器分 `controller/admin/` 和 `controller/user/`
- AI Agent：`service/ai/AgentService.java` 实现 ReAct 循环 + function calling，支持 SSE 流式
- 统一返回格式：`result/Result.java`（`code`/`msg`/`data`）

**Python Flask API (`api/`)**
- `app.py` — 主应用，异步任务跟踪
- `cut_smooth_cutEdge.py` — NDVI 图像裁剪/平滑
- `xuntian_subregion.py` — 巡检子区域分析
- `services/patrol_planning.py` — 路线规划

**前端 (`src/main/resources/static/`)**
- Leaflet 2D 地图（`admin-patrol.html`, `admin-map.html`）
- Cesium 3D 地球（`admin-patrol-cesium.html`）— 地块渲染、NDVI 叠加、异常检测、路线规划、AI 对话

### 关键约定

- Java 1.8, Spring Boot 2.6.13
- 地块坐标以 JSON TEXT 存储在 MySQL
- 分页是内存级（`PageUtil`），不是数据库级
- 密码明文存储（已知问题）

### 常见坑

- `LLMConfig` 需要设置 `LLM_API_KEY` 环境变量
- Drools 依赖声明了但没用
- `LlmGatewayService` 和 `PlotAddressUpdateTask` 完全注释掉
- Agent 对话历史存在内存中，重启丢失

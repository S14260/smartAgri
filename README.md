# 智慧农业遥感监测与巡田决策平台

面向精准农业的一站式管理系统，集成地块全生命周期管理、多源遥感影像分析、AI 智能诊断与巡田路径规划，实现从卫星数据采集到田间决策执行的完整业务闭环。

## 系统架构

采用 **"Java 业务层 + Python 计算层 + 前端可视化层"三层分离架构**：

```
┌─────────────────────────────────────────────────────────┐
│                   前端可视化层                            │
│   Cesium 3D 地球 · Leaflet 2D 地图 · ECharts · LayUI    │
├─────────────────────────────────────────────────────────┤
│                   Java 业务层 (Spring Boot :8080)         │
│   用户认证(JWT) · 地块CRUD · 巡田管理 · AI Agent 调度     │
├─────────────────────────────────────────────────────────┤
│                   Python 计算层 (Flask :8000)             │
│   GDAL 影像裁剪 · NDVI 异常检测 · 子区域分析 · 路径规划   │
└─────────────────────────────────────────────────────────┘
```

## 功能展示

### 登陆界面
![登陆界面](photos_png/登陆界面.png)

### 数据驾驶舱
![数据驾驶舱](photos_png/我的桌面.png)

### 地图圈地
![地图圈地](photos_png/AI圈地.png)

### 异常检测
![异常检测](photos_png/异常检测结果面板.png)

### 巡田报告
![巡田报告](photos_png/巡田报告.png)

### 巡田任务单
![巡田任务单](photos_png/巡田任务单.png)

### 路径规划
![路径规划](photos_png/路径规划.png)

### AI 农业助手
![AI农业助手](photos_png/Agent农业助手.png)

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端 | Spring Boot 2.6 · Spring Data JPA · MyBatis-Plus · JWT · OkHttp |
| 计算 | Python 3 · Flask · GDAL · GeoTIFF · Shapely · Rasterio · NumPy · SciPy |
| 前端 | Leaflet · Cesium 3D · ECharts · LayUI · SSE |
| AI | DeepSeek LLM · ReAct Agent · Function Calling |
| 数据 | MySQL · JSON 空间数据 |

## 核心模块

### AI Agent 服务

基于 ReAct（Reasoning + Acting）模式的智能助手框架：

- **工具自动注册**：Spring DI 自动发现 `AgentTool` 实现类，运行时动态注册 5 个工具
- **流式推理链**：SSE 实时输出思考过程、工具调用状态、最终回答
- **多轮对话**：ConcurrentHashMap 维护会话历史，支持上下文连续对话
- **异常降级**：参数解析失败降级为空对象、LLM 畸形 JSON 自动过滤

### 遥感数据处理

#### NDVI 影像裁剪与平滑 (`cut_smooth_cutEdge.py`)

核心算法流程：

1. **NDVI 文件下载与缓存**：根据日期和区域从远程服务器下载 GeoTIFF 格式的 NDVI 卫星影像，本地缓存避免重复下载
2. **坐标系重投影**：自动检测原始影像坐标系，若非 WGS84 (EPSG:4326) 则进行重投影转换
3. **矢量裁剪**：使用地块多边形矢量边界对 NDVI 栅格进行精确裁剪
4. **Lanczos 超分辨率插值**：对裁剪后的影像进行 6 倍上采样，采用 Lanczos 插值算法提升视觉清晰度
5. **精确裁边**：二次裁剪去除插值引入的边界伪影，确保输出严格贴合地块边界
6. **NDVI 配色方案**：将 NDVI 值映射为 13 级颜色梯度（深红→深绿），直观反映植被长势
7. **边缘抗锯齿**：基于欧氏距离变换（EDT）的边缘软化处理，消除锯齿感

支持的光谱指数：
- **NDVI**（归一化植被指数）：反映植被覆盖密度
- **EVI**（增强植被指数）：在高植被覆盖区更敏感
- **SAVI**（土壤调节植被指数）：适用于裸土较多的区域
- **NDWI**（归一化水体指数）：用于识别积水/水渍

#### 子区域异常检测 (`xuntian_subregion.py`)

基于 NDVI 分级的多时相异常检测算法：

**第一阶段：子区域分割**
- 按 NDVI 值将地块划分为 7 个等级（重度干旱/中度干旱/轻度干旱/病虫害/已收割/正常/长势良好）
- 对每个等级进行连通区分析（Connected Component Analysis），提取空间连续的子区域
- 过滤面积过小（<500 像素）或过大（>192000 像素）的噪声区域

**第二阶段：多指标异常判定**
- **静态异常**：基于 NDVI 分级 + 多指数联合判定
  - 积水/水渍：NDWI ≥ -0.2 且 NDVI ≤ 0.35
  - 病虫害：EVI < 0.30 且 SAVI < 0.25 且 NDVI > 0.35
  - 干旱：NDVI 低于对应阈值
- **时序异常**：多时相数据对比
  - Delta NDVI：当前期与上期 NDVI 差值 < -0.05
  - Z-Score：标准化偏离度 < -1.8
  - 线性回归斜率：NDVI 趋势斜率 < -0.004 且相关系数 < -0.5

**第三阶段：优先级排序**
- 综合权重 = 严重度权重(0.65) × 等级权重 + 面积权重(0.25) × 归一化面积 + 时序加成(0.1) - 边缘惩罚(0.05)
- 去重：10 米范围内的重复异常点合并

**输出产物**：
- 巡田最终工单（JSON）：包含所有异常子区域的坐标、面积、等级、优先级
- 异常地图（PNG）：NDVI 分级渲染 + 异常点标注
- 趋势图（PNG）：地块级 NDVI/EVI/NDWI 时序变化曲线
- GeoJSON：异常区域矢量数据，可用于 GIS 软件叠加分析

### 巡田路径规划 (`services/patrol_planning.py`)

异常驱动的分层巡田路径规划算法：

**核心思想**：优先巡检高权重异常地块，同时最小化总行驶距离

**算法流程**：

1. **异常权重计算**
   ```
   weight = 0.5 × priority + 0.3 × severity + 0.2 × log(area + 1)
   ```
   综合考虑异常优先级、严重程度和面积大小

2. **地块内路径生成**（最近邻算法）
   - 对每个地块内的异常点，使用最近邻算法生成局部巡检路径
   - 起点优化：选择最西端点（经度最小）作为起点，减少折返

3. **地块间路径规划**（异常驱动 + 距离联合决策）
   - 起点选择：异常权重最高的地块
   - 下一地块决策函数：
     ```
     cost = distance(current, next) / (weight(next) + ε)
     ```
     距离越近、权重越高的地块优先访问

4. **2-opt 局部优化**
   - 迭代交换路径中的边，消除交叉，减少总路径长度
   - 固定随机种子（seed=45）保证结果可复现
   - 默认 200 次迭代，平衡优化效果与计算时间

5. **球面距离计算**
   - 使用 Haversine 公式计算经纬度间的真实球面距离（米）
   - 替代欧氏距离，避免高纬度地区距离失真

**输出产物**：
- GeoJSON 路径文件：可直接在 GIS 软件或 Cesium 地球上叠加显示
- 路径可视化图（PNG）：全局路径 + 地块分区 + 质心标注
- 量化评估报告：分层规划 vs 全局最近邻的路径长度、计算耗时对比
- 双图对比：分层路径与全局最近邻路径的并排可视化

### 空间可视化

- **Cesium 3D 地球**：地块三维渲染、NDVI 热力图、异常标注、AI 聊天嵌入
- **Leaflet 2D 地图**：地块圈选编辑（Leaflet.draw）、坐标拾取
- **ECharts 图表**：作物分布饼图、地区分布柱状图、异常统计

## 项目结构

```
smart-agriculture-management/
├── src/main/java/com/example/smartAgr/
│   ├── config/                     # 配置类（LLM、CORS、JWT）
│   ├── controller/admin/           # 管理端接口
│   │   ├── AgentController.java    # AI Agent 对话
│   │   ├── DashboardController.java# 数据驾驶舱
│   │   └── ReportController.java   # 巡田报告
│   ├── service/ai/                 # AI 核心服务
│   │   ├── AgentService.java       # ReAct 循环引擎
│   │   └── tools/                  # 5 个内置工具
│   └── interceptor/                # JWT 拦截器
│
├── src/main/resources/
│   ├── application.yml             # 应用配置（需自行创建）
│   └── static/                     # 前端页面
│       ├── admin-patrol-cesium.html# 3D 地球 + AI 助手
│       ├── admin-patrol.html       # 巡田规划（Leaflet 2D）
│       ├── admin-report.html       # 巡田报告
│       ├── welcome.html            # 数据驾驶舱
│       └── css/                    # 样式文件
│
├── api/                            # Python Flask 微服务
│   ├── app.py                      # Flask 主应用（API 路由 + 异步任务管理）
│   ├── cut_smooth_cutEdge.py       # NDVI 影像裁剪/平滑/配色算法
│   ├── xuntian_subregion.py        # 子区域异常检测（多时相融合）
│   └── services/
│       └── patrol_planning.py      # 分层巡田路径规划算法
│
├── photos_png/                     # 系统截图
├── docs/                           # 开发文档
└── pom.xml
```

## 快速开始

### 环境要求

- JDK 1.8+
- Maven 3.6+
- MySQL 5.7+
- Python 3.8+

### 1. 数据库

```bash
mysql -u root -p -e "CREATE DATABASE mydb;"
mysql -u root -p mydb < src/main/resources/mydb.sql
```

### 2. 配置

创建 `src/main/resources/application.yml`，参考以下模板：

```yaml
spring:
  datasource:
    username: root
    password: your_password
    url: jdbc:mysql://localhost:3306/mydb?useUnicode=true&characterEncoding=UTF-8&autoReconnect=true&useSSL=false&serverTimezone=GMT
    driver-class-name: com.mysql.cj.jdbc.Driver

server:
  port: 8080

amap:
  key: your_amap_key  # 高德地图 API Key

jwt:
  admin-secret-key: your_admin_secret
  admin-ttl: 7200000
  admin-token-name: token
  user-secret-key: your_user_secret
  user-ttl: 7200000
  user-token-name: authentication

llm:
  api-key: ${LLM_API_KEY:your-api-key-here}
  base-url: ${LLM_BASE_URL:https://api.deepseek.com/v1}
  model: ${LLM_MODEL:deepseek-chat}
  chat-endpoint: /chat/completions
```

或通过环境变量设置 API Key：
```bash
export LLM_API_KEY=sk-xxx
```

### 3. 启动 Java 后端

```bash
./mvnw spring-boot:run
```

### 4. 启动 Flask 微服务

```bash
cd api
pip install -r requirements.txt
python app.py
```

### 5. 访问

- 地址：http://localhost:8080/
- 管理员：`admin` / `admin`

## API 接口

### Java 后端 (port 8080)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/admin/ai/chat/stream` | POST | SSE 流式 AI 对话 |
| `/admin/dashboard/overview` | GET | 驾驶舱概览数据 |
| `/admin/plots` | GET/POST | 地块 CRUD |
| `/admin/llm/explain` | POST | 异常智能分析 |

### Flask 微服务 (port 8000)

| 接口 | 方法 | 说明 |
|------|------|------|
| `/admin/ndvicut` | POST | NDVI 影像裁剪（管理端） |
| `/user/ndvicut` | POST | NDVI 影像裁剪（用户端） |
| `/admin/ndvilist` | GET | NDVI 文件列表 |
| `/xuntian/run` | POST | 启动巡田分析任务（多地块异步） |
| `/xuntian/status` | GET | 查询巡田任务进度 |
| `/xuntian/results` | GET | 获取巡田分析结果 |
| `/xuntian/reports` | GET | 历史巡田工单列表 |
| `/xuntian/report/detail` | GET | 指定工单详情 |
| `/xuntian/patrol/plan` | POST | 生成巡田路径规划 |

## 已知限制

- Agent 会话存储在内存中，重启丢失
- 分页为内存分页，大数据量需优化
- 密码明文存储（已知安全问题）

## 开发工具

- **IDE**: IntelliJ IDEA
- **AI 辅助**: Claude Code
- **版本控制**: Git

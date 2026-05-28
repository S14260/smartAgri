# Smart Agriculture Management System 智慧农业管理系统

基于 Spring Boot + Flask + Cesium 的智慧农业管理平台，集成卫星遥感分析、AI 智能对话、巡检路径规划等功能。

## 功能特性

### 核心功能
- **地块管理** — 地块圈定、编辑、删除，支持全屏模式和移动端
- **卫星遥感** — NDVI 植被指数图层加载、多时相对比、按地块裁剪
- **异常检测** — 基于 NDVI 的作物异常自动识别与可视化
- **巡检管理** — 巡检任务创建、路径规划、巡检报告生成
- **三维地球** — Cesium 3D 地球展示，支持地块渲染、图层叠加

### AI 能力
- **AI Agent 对话** — 基于 ReAct 循环的智能助手，支持 SSE 流式输出
- **Function Calling** — 5 个内置工具：查询地块、异常检测、生成路线等
- **异常解释** — 调用 DeepSeek LLM 自动生成异常分析报告

### 用户体系
- **双端分离** — 管理端 / 用户端独立页面和权限
- **JWT 认证** — 基于 Token 的身份验证和接口鉴权
- **多用户支持** — 用户注册、登录、个人信息管理

## 技术栈

### 后端
| 技术 | 说明 |
|------|------|
| Spring Boot 2.6 | Java Web 框架 |
| Spring Data JPA | 数据持久化 |
| MyBatis-Plus | ORM 框架 |
| JWT | 身份认证 |
| OkHttp | HTTP 客户端（调用 LLM） |
| Flask | Python 微服务框架 |
| Gunicorn | WSGI 服务器 |

### 前端
| 技术 | 说明 |
|------|------|
| Cesium | 三维地球引擎 |
| Leaflet | 二维地图引擎 |
| ECharts | 数据可视化 |
| LayUI | UI 组件库 |
| X-admin | 后台管理模板 |
| GeoRaster | 栅格影像渲染 |

### AI / 数据
| 技术 | 说明 |
|------|------|
| DeepSeek API | LLM 大语言模型 |
| NDVI | 归一化植被指数 |
| GeoTIFF | 卫星遥感影像格式 |

## 项目结构

```
smart-agriculture-management/
├── src/main/java/com/example/smartAgr/
│   ├── config/                    # 配置类
│   │   └── LLMConfig.java         # LLM API 配置
│   ├── controller/
│   │   ├── admin/                 # 管理端接口
│   │   │   ├── AgentController.java      # AI Agent 对话
│   │   │   └── LlmExplainController.java # LLM 解释
│   │   └── user/                  # 用户端接口
│   ├── model/                     # 数据模型
│   │   └── ai/                    # AI 相关模型
│   ├── service/
│   │   ├── admin/                 # 管理端服务
│   │   │   ├── LlmServiceImpl.java       # LLM 调用实现
│   │   │   └── LlmGatewayService.java    # LLM 网关
│   │   └── ai/                    # AI 核心服务
│   │       ├── AgentService.java         # ReAct 循环引擎
│   │       ├── AgentTool.java            # 工具接口
│   │       └── tools/                    # 内置工具
│   └── interceptor/               # JWT 拦截器
│
├── src/main/resources/
│   ├── application.yml            # 应用配置
│   ├── static/                    # 前端静态资源
│   │   ├── admin-*.html           # 管理端页面
│   │   ├── user-*.html            # 用户端页面
│   │   ├── css/                   # 样式文件
│   │   └── lib/                   # 第三方库
│   └── mydb.sql                   # 数据库脚本
│
├── api/                           # Python Flask 微服务
│   ├── app.py                     # Flask 主应用
│   ├── cut_smooth_cutEdge.py      # NDVI 裁剪算法
│   ├── xuntian_subregion.py       # 巡检子区域分析
│   └── services/
│       └── patrol_planning.py     # 路径规划算法
│
├── pom.xml                        # Maven 依赖
├── package.json                   # Node.js 依赖（可选）
└── README.md
```

## 快速开始

### 环境要求
- JDK 1.8+
- Maven 3.6+
- MySQL 5.7+
- Python 3.8+（Flask 微服务）

### 1. 数据库配置
```bash
# 登录 MySQL，创建数据库并导入脚本
mysql -u root -p
CREATE DATABASE mydb;
USE mydb;
SOURCE src/main/resources/mydb.sql;
```

### 2. 修改配置
编辑 `src/main/resources/application.yml`：
```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb?useSSL=false&serverTimezone=Asia/Shanghai
    username: root
    password: your_password  # 修改为你的密码

llm:
  api-key: ${LLM_API_KEY:sk-xxx}  # DeepSeek API Key
  base-url: https://api.deepseek.com
```

### 3. 启动 Java 后端
```bash
# 方式一：Maven 启动
./mvnw spring-boot:run

# 方式二：打包后运行
./mvnw clean package
java -jar target/smartAgr-0.0.1-SNAPSHOT.jar
```

后端启动在 http://123.56.228.32:8080

### 4. 启动 Flask 微服务（可选）
```bash
cd api
pip install -r requirements.txt
python app.py
```

Flask 服务启动在 http://localhost:8000

### 5. 访问系统
- 打开 http://123.56.228.32:8080/
- 默认管理员账号：`admin` / `admin`
- 管理端入口：`/admin-index.html`
- 用户端入口：`/user-index.html`

## 页面说明

### 管理端功能
| 页面 | 路径 | 功能 |
|------|------|------|
| 管理首页 | `/admin-index.html` | 地块管理、地图展示 |
| 三维地球 | `/admin-patrol-cesium.html` | Cesium 3D、AI 对话、NDVI 分析 |
| 地块列表 | `/admin-plot.html` | 地块 CRUD 操作 |
| 巡检管理 | `/admin-patrol.html` | 巡检任务和报告 |
| 用户管理 | `/admin-user.html` | 用户账号管理 |

### 用户端功能
| 页面 | 路径 | 功能 |
|------|------|------|
| 用户首页 | `/user-index.html` | 地图查看、打卡 |
| 打卡记录 | `/user-punch.html` | 打卡历史 |

## API 接口

### AI Agent
```
POST /admin/ai/chat          # 普通对话
POST /admin/ai/chat/stream   # SSE 流式对话
```

### 地块管理
```
GET    /admin/plot/list       # 获取地块列表
POST   /admin/plot/add        # 新增地块
PUT    /admin/plot/update     # 更新地块
DELETE /admin/plot/delete     # 删除地块
```

### LLM 解释
```
POST /admin/llm/explain       # 异常解释
```

### Flask 微服务
```
POST /ndvi/cut                # NDVI 裁剪
POST /patrol/analyze          # 巡检分析
POST /patrol/route            # 路径规划
```

## 已知限制

- 密码明文存储（生产环境需加密）
- 分页为内存分页（数据量大时需优化）
- Agent 会话存储在内存（重启丢失）
- JWT Secret 硬编码（建议使用环境变量）

## 开发工具

- **IDE**: IntelliJ IDEA
- **AI 辅助**: Claude Code (claude.ai/code)
- **版本控制**: Git + GitHub

## 许可证

本项目仅供学习交流使用。

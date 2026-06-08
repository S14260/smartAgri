# 第二阶段：功能深度提升

> 时间：2026-06-08
> 目标：地图页面产品化 + CRUD样式统一 + 巡田报告页 + Cesium样式提取 + Dashboard接口

---

## 一、任务清单

| # | 任务 | 状态 | 工作量 |
|---|------|------|--------|
| 1 | 提取Cesium内联样式 | ✅ 完成 | ~10min |
| 2 | CRUD页面样式统一 | ✅ 完成 | ~20min |
| 3 | 新增Dashboard接口 | ✅ 完成 | ~20min |
| 4 | 地图页面三栏布局 | ✅ 完成 | ~30min |
| 5 | 巡田报告页 | ✅ 完成 | ~20min |

**总工作量**：约 1.5 小时

---

## 二、改动详情

### 2.1 提取Cesium内联样式

**新建文件**：`css/admin-patrol-cesium.css`

**操作**：
- 将 `admin-patrol-cesium.html` 中318行内联 `<style>` 提取为独立CSS文件
- 包含：基础布局、工具栏、AI Chat、Agent推理链、NDVI对比分析、帮助面板、响应式断点
- HTML中替换为 `<link rel="stylesheet" href="./css/admin-patrol-cesium.css"/>`

---

### 2.2 CRUD页面样式统一

**修改文件**：
- `admin-plots-list.html` — 添加搜索框 + 操作按钮图标
- `admin-plot-add.html` — 修复CSS路径 `./layui/` → `./lib/layui/`，添加design-tokens引用，统一表单样式
- `admin-plot-update.html` — 修复CDN引用 → 本地路径，添加design-tokens引用，统一表单样式
- `user-plots-list.html` — 添加搜索框 + 操作按钮图标

**样式改动**：
- 表单页面：添加圆角卡片容器、蓝色聚焦边框、统一按钮颜色
- 表格页面：添加搜索过滤功能（按地块名/作物实时筛选）

---

### 2.3 新增Dashboard接口

**新建文件**：`DashboardController.java`

**接口清单**：

| 接口 | 方法 | 返回 |
|------|------|------|
| `/admin/dashboard/overview` | GET | `{ plotCount, totalArea, punchCount }` |
| `/admin/dashboard/plot-stats` | GET | `{ byCrop, byRegion, bySoil }` |

**修改文件**：`welcome.html`
- 将 `/admin/plots` 调用替换为 `/admin/dashboard/overview`
- 图表数据优先从 `/admin/dashboard/plot-stats` 获取，失败时降级到地块列表接口
- 提取 `renderCropPie()` 和 `renderRegionBar()` 公共函数

---

### 2.4 地图页面三栏布局

**修改文件**：
- `admin-patrol.html` — 添加左右浮动面板HTML + 交互JS
- `css/admin-patrol.css` — 添加面板样式

**左侧面板**（280px）：
- Tab切换：地块列表 / 异常记录
- 地块列表项：图标 + 名称 + 作物 + 面积
- 点击列表项 → 地图 `flyTo` 定位 + 显示右侧面板

**右侧面板**（320px）：
- 地块详情卡片：10个字段展示
- 操作按钮：修改面积 / 删除
- 关闭按钮

**新增CSS类**：
- `.side-panel` / `.left-panel` / `.right-panel`
- `.panel-tabs` / `.panel-content`
- `.plot-list-item` / `.anomaly-item`
- `.detail-card` / `.detail-row`

---

### 2.5 巡田报告页

**新建文件**：
- `admin-report.html` — 巡田报告页面
- `css/report.css` — 报告页面样式

**页面结构**：
- 概览卡片：工单总数、异常总数、高危异常、低危异常
- 工单选择器：下拉选择工单
- 异常详情表格：序号、地块、异常类型、严重程度、面积、说明
- 图表区：异常类型分布饼图 + 严重程度柱状图

**数据来源**：
- `GET /xuntian/reports` → 工单列表
- `GET /xuntian/report/detail?path=xxx` → 工单详情

**侧边栏菜单**：已添加到 `admin-index.html` 的巡田管理下

---

## 三、文件变更清单

### 新建文件
```
src/main/resources/static/css/admin-patrol-cesium.css
src/main/resources/static/admin-report.html
src/main/resources/static/css/report.css
src/main/java/com/example/smartAgr/controller/admin/DashboardController.java
```

### 修改文件
```
src/main/resources/static/admin-patrol-cesium.html
src/main/resources/static/admin-patrol.html
src/main/resources/static/css/admin-patrol.css
src/main/resources/static/admin-plots-list.html
src/main/resources/static/admin-plot-add.html
src/main/resources/static/admin-plot-update.html
src/main/resources/static/user-plots-list.html
src/main/resources/static/welcome.html
src/main/resources/static/admin-index.html
```

---

## 四、验证方式

1. 打开 `admin-patrol-cesium.html`，检查功能是否正常（样式提取后）
2. 打开 `admin-plots-list.html`，搜索框输入关键词，检查筛选是否生效
3. 打开 `admin-plot-add.html`，检查表单样式是否统一
4. 打开 `admin-patrol.html`，检查左右面板是否正确显示
5. 点击左侧面板地块列表项，地图是否定位，右侧面板是否显示详情
6. 打开 `admin-report.html`，选择工单，检查数据和图表
7. 浏览器控制台无 404 错误

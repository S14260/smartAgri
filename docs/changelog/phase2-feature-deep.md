# 第二阶段：功能深度提升

> 时间：待定
> 目标：地图页面产品化 + CRUD样式统一 + 巡田报告页 + Dashboard接口

---

## 一、任务清单

| # | 任务 | 状态 | 工作量 |
|---|------|------|--------|
| 1 | 地图页面三栏布局 | ⬜ 待开始 | ~6h |
| 2 | CRUD页面样式统一 | ⬜ 待开始 | ~4h |
| 3 | 巡田报告页 | ⬜ 待开始 | ~6h |
| 4 | 提取Cesium内联样式 | ⬜ 待开始 | ~2h |
| 5 | 新增Dashboard接口 | ⬜ 待开始 | ~3h |

**预计总工作量**：约 21 小时

---

## 二、任务详情

### 2.1 地图页面三栏布局

**目标文件**：`admin-patrol.html`

**设计方案**

```
┌──────────────────────────────────────────────────────────────┐
│ 顶部工具栏                                                    │
│ [系统名称]  [搜索地块]  [图层控制]  [全屏]        [AI助手]   │
├────────┬─────────────────────────────────────┬────────────────┤
│ 左侧    │ 中间地图区域                         │ 右侧           │
│ (280px) │ (flex: 1)                            │ (320px)        │
│         │                                      │                │
│ [Tab切换]│  ┌─────────────────────────────────┐ │ [AI分析面板]   │
│ 地块列表 │  │                                 │ │  或            │
│ 异常记录 │  │      Leaflet 地图               │ │ [地块详情面板] │
│ 巡田任务 │  │                                 │ │                │
│         │  └─────────────────────────────────┘ │ - 名称         │
│         │                                      │ - 面积         │
│ - 地块1 │  底部状态栏: [坐标] [缩放] [图层名]   │ - 作物         │
│ - 地块2 │                                      │ - 土壤         │
│ - 地块3 │                                      │ - 灌溉         │
├────────┴─────────────────────────────────────┴────────────────┤
│ 底部状态栏                                                    │
└──────────────────────────────────────────────────────────────┘
```

**实现要点**

- 左侧面板：`position: absolute` + `z-index` 浮动在地图上方
- 右侧面板：同理
- 地图区域保持 `100vh` 全屏
- 面板显示/隐藏用 JS 控制
- 复用现有 `ai-chat.css` 样式

**新增CSS**

- `.left-panel` — 左侧面板容器
- `.right-panel` — 右侧面板容器
- `.panel-tabs` — Tab切换
- `.plot-list-item` — 地块列表项
- `.anomaly-item` — 异常记录项（按严重程度分色）
- `.detail-card` — 地块详情卡片

---

### 2.2 CRUD页面样式统一

**目标文件**

- `admin-plots-list.html`
- `user-plots-list.html`
- `admin-plot-add.html`
- `admin-plot-update.html`
- `user-plot-add.html`（如存在）
- `user-plot-update.html`

**设计方案**

- 表格：圆角卡片容器，斑马纹，悬停高亮
- 表单：统一的输入框样式，聚焦蓝色边框
- 按钮：渐变背景，悬停效果
- 弹窗：毛玻璃遮罩，圆角卡片

**复用资源**

- `design-tokens.css` 已有的 LayUI 覆盖样式
- `.sa-card` / `.sa-btn-*` / `.sa-badge-*` 组件

---

### 2.3 巡田报告页

**新建文件**：`admin-report.html` + `css/report.css`

**页面布局**

```
┌──────────────────────────────────────────────────────────────┐
│ [报告列表]                                [导出] [打印]      │
├──────────────────────────────────────────────────────────────┤
│ 报告概览卡片                                                  │
│ [工单时间] [异常总数] [高危异常] [巡田建议]                  │
├──────────────────────────────────────────────────────────────┤
│ 异常详情表格                                                  │
│ | 序号 | 地块 | 异常类型 | 严重程度 | 面积 | NDVI变化 | 操作 │
├──────────────────────────────────────────────────────────────┤
│ 可视化区域                                                    │
│ [异常分布饼图]  [NDVI变化图]  [巡田路线图]                   │
└──────────────────────────────────────────────────────────────┘
```

**数据来源**

- `GET /xuntian/reports` → 工单列表
- `GET /xuntian/report/detail?path=xxx` → 工单详情
- `POST /xuntian/patrol/plan` → 巡田路线

---

### 2.4 提取Cesium内联样式

**目标文件**：`admin-patrol-cesium.html`

**操作**

- 将 `admin-patrol-cesium.html` 中的 `<style>` 标签（约300行）提取为独立CSS文件
- 新建 `css/admin-patrol-cesium.css`
- 在HTML中引用外部CSS

---

### 2.5 新增Dashboard接口

**新建文件**：`DashboardController.java`

**接口设计**

| 接口 | 方法 | 返回 |
|------|------|------|
| `/admin/dashboard/overview` | GET | `{ plotCount, totalArea, anomalyCount, reportCount, latestImage }` |
| `/admin/dashboard/plot-stats` | GET | `{ byCrop: [...], byRegion: [...], bySoil: [...] }` |
| `/admin/dashboard/punch-trend` | GET | `{ dates: [...], counts: [...] }` |

**优势**

- 减少前端多次请求
- 后端聚合计算性能更好
- 接口更专业

---

## 三、文件变更清单

### 待新建文件
```
src/main/resources/static/admin-report.html
src/main/resources/static/css/report.css
src/main/resources/static/css/admin-patrol-cesium.css
src/main/java/com/example/smartAgr/controller/admin/DashboardController.java
```

### 待修改文件
```
src/main/resources/static/admin-patrol.html
src/main/resources/static/admin-plots-list.html
src/main/resources/static/user-plots-list.html
src/main/resources/static/admin-plot-add.html
src/main/resources/static/admin-plot-update.html
src/main/resources/static/admin-patrol-cesium.html
```

---

## 四、验证方式

1. 打开地图页面，检查三栏布局是否正确
2. 左侧面板切换地块列表/异常记录/巡田任务
3. 右侧面板显示地块详情或AI分析
4. 打开CRUD页面，检查表格/表单样式一致性
5. 打开巡田报告页，检查数据展示和图表
6. 检查Cesium页面功能是否正常（样式提取后）
7. 浏览器控制台无 404 错误

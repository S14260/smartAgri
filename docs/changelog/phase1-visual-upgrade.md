# 第一阶段：视觉系统升级

> 时间：2026-06-08
> 目标：从"学生管理系统风格"提升为"农田智能监测平台"

---

## 一、任务清单

| # | 任务 | 状态 | 工作量 |
|---|------|------|--------|
| 1 | 清理遗留页面和内容 | ✅ 完成 | ~30min |
| 2 | 创建全局设计Token CSS | ✅ 完成 | ~20min |
| 3 | 重新设计登录页 | ✅ 完成 | ~40min |
| 4 | 首页驾驶舱改造 | ✅ 完成 | ~1h |
| 5 | 主框架视觉升级 | ✅ 完成 | ~40min |

**总工作量**：约 3 小时

---

## 二、改动详情

### 2.1 清理遗留内容

**删除的文件（18个）**

```
dormitory-admin-add.html
dormitory-admin-del.html
dormitory-admin-get.html
dormitory-admin-getstudentall.html
dormitory-admin-update.html
register-admin.html
register-admin-add.html
register-admin-del.html
register-admin-get.html
register-admin-update.html
admin-admin.html
admin-admin-add.html
admin-admin-del.html
admin-admin-get.html
admin-admin-update.html
plots-admin.html
admin-list.html
log.html
```

**修复的标题**

| 文件 | 修改前 | 修改后 |
|------|--------|--------|
| `admin-index.html` | 地块管理系统 | 农田智能监测与巡田决策平台 |
| `user-index.html` | 地块管理系统 | 农田智能监测与巡田决策平台 |
| `welcome.html` | 学生宿舍管理系统 | 农田智能监测与巡田决策平台 |
| `plot-admin-add-test.html` | 新增地块信息 - X-admin2.2 | 新增地块信息 |

**修复的链接**

| 文件 | 修改前 | 修改后 |
|------|--------|--------|
| `admin-index.html` | `xadmin.open('个人信息','https://www.baidu.com')` | `href="javascript:;"` |
| `user-index.html` | `xadmin.open('个人信息','https://www.baidu.com')` | `href="javascript:;"` |

---

### 2.2 创建设计Token

**新建文件**：`css/design-tokens.css`

**设计变量清单**

| 类别 | 变量 | 值 |
|------|------|-----|
| 主色调 | `--primary-color` | `#1E88E5` |
| 主色浅 | `--primary-light` | `#42A5F5` |
| 主色深 | `--primary-dark` | `#1565C0` |
| 辅助色 | `--secondary-color` | `#43A047` |
| 强调色 | `--accent-color` | `#FF6D00` |
| 成功色 | `--success-color` | `#67C23A` |
| 警告色 | `--warning-color` | `#E6A23C` |
| 危险色 | `--danger-color` | `#F56C6C` |
| 文本主色 | `--text-primary` | `#303133` |
| 文本次色 | `--text-regular` | `#606266` |
| 背景色 | `--bg-page` | `#f0f2f5` |
| 阴影-sm | `--shadow-sm` | `0 2px 8px rgba(0,0,0,0.06)` |
| 阴影-md | `--shadow-md` | `0 4px 16px rgba(0,0,0,0.1)` |
| 圆角-sm | `--radius-sm` | `4px` |
| 圆角-md | `--radius-md` | `8px` |
| 圆角-lg | `--radius-lg` | `12px` |
| 字体 | `--font-family` | `"PingFang SC", "Microsoft YaHei", ...` |
| 数据字体 | `--font-data` | `"DIN Alternate", ...` |

**通用组件样式**

- `.sa-card` — 通用卡片
- `.sa-btn-primary` / `.sa-btn-success` / `.sa-btn-outline` — 按钮系列
- `.sa-badge-primary` / `.sa-badge-danger` — 徽章系列
- `.sa-data-number` — 数据展示数字
- LayUI 样式覆盖（表格、输入框、按钮等）

---

### 2.3 登录页重设计

**修改文件**：`login.html` + `css/login.css`

**设计方案**

| 元素 | 修改前 | 修改后 |
|------|--------|--------|
| 背景 | 静态图片 `bg.png` | 蓝绿渐变 + 粒子动画 |
| 卡片 | 白色矩形 | 毛玻璃效果 + 圆角16px + 阴影 |
| 标题栏 | 青绿色 `#189F92` | 蓝色渐变 `#1E88E5 → #1565C0` |
| Logo | 无 | Font Awesome 叶子图标 |
| 输入框 | 灰色边框 | 浅灰背景 + 蓝色聚焦光晕 |
| 按钮 | 青绿色 | 蓝色渐变 + 悬停上浮 + 涟漪效果 |
| 标题 | 智慧农业管理系统 | 农田智能监测平台 |

**动画效果**

- `gradientShift` — 背景渐变流动（15s循环）
- `cardAppear` — 卡片入场动画（0.6s）
- 按钮 `transform: translateY(-1px)` — 悬停上浮
- 输入框 `box-shadow: 0 0 0 3px rgba(30,136,229,0.1)` — 聚焦光晕

---

### 2.4 首页驾驶舱

**修改文件**：`welcome.html` + 新建 `css/dashboard.css`

**页面结构**

```
┌─────────────────────────────────────────────────┐
│ 欢迎区（蓝色渐变背景）                            │
│ [欢迎回来，管理员]              [06月08日 星期日] │
│ [农田智能监测平台 · 数据概览]    [14:30:25]       │
├─────────┬─────────┬─────────┬─────────┬─────────┤
│ 地块总数 │ 总亩数   │ 异常地块 │ 巡田工单 │ 遥感影像 │
│ [图标]   │ [图标]   │ [图标]   │ [图标]   │ [图标]   │
│  [数字]  │  [数字]  │  [数字]  │  [数字]  │  [数字]  │
├─────────────────────┬───────────────────────────┤
│ 作物类型分布（饼图）  │ 地区地块分布（柱状图）     │
│ [ECharts]            │ [ECharts]                  │
├──────────┬──────────┴───────────────────────────┤
│ 快捷入口  │ 最新巡田工单                         │
│ [地块管理]│ [工单1] 高风险                       │
│ [地图圈地]│ [工单2] 中风险                       │
│ [巡田分析]│ [工单3] 低风险                       │
│ [3D地球]  │ ...                                  │
│ [AI助手]  │                                      │
│ [打卡记录]│                                      │
└──────────┴──────────────────────────────────────┘
```

**数据来源**

| 统计卡片 | API | 计算方式 |
|---------|-----|---------|
| 地块总数 | `GET /admin/plots` | `.length` |
| 总亩数 | `GET /admin/plots` | `sum(area)` |
| 异常地块 | `GET /xuntian/reports` | 最新工单 `total_anomaly_count` |
| 巡田工单 | `GET /xuntian/reports` | `.length` |
| 遥感影像 | `GET /admin/ndvilist` | 最新文件日期 |

| 图表 | API | 分组方式 |
|------|-----|---------|
| 作物分布饼图 | `GET /admin/plots` | 按 `currentCrop` 分组 |
| 地区分布柱状图 | `GET /admin/plots` | 按 `region` 分组 |

**快捷入口**

| 入口 | 跳转页面 |
|------|---------|
| 地块管理 | `admin-plots-list.html` |
| 地图圈地 | `admin-map.html` |
| 巡田分析 | `admin-patrol.html` |
| 3D地球 | `admin-patrol-cesium.html` |
| AI助手 | `admin-patrol-cesium.html` |
| 打卡记录 | `punch-record-list.html` |

---

### 2.5 主框架视觉升级

**修改文件**：`css/xadmin.css`、`admin-index.html`、`user-index.html`

**样式改动**

| 元素 | 修改前 | 修改后 |
|------|--------|--------|
| 顶栏背景 | `#222` 纯色 | `linear-gradient(135deg, #1a1a2e, #16213e)` |
| 顶栏高度 | 45px | 52px |
| Logo字体 | 18px 白色 | 16px 渐变色（蓝→绿） |
| 侧边栏背景 | `#EEEEEE` 灰色 | `linear-gradient(180deg, #1a1a2e, #16213e)` 深色 |
| 菜单文字 | 深色 | `rgba(255,255,255,0.65)` 半透明白 |
| 菜单悬停 | `#009688` 绿色 | `rgba(255,255,255,0.08)` + 蓝色左边框 |
| 菜单激活 | `#009688` 绿色 | `rgba(30,136,229,0.2)` + 蓝色左边框 |
| 标签栏背景 | `#EFEEF0` 灰色 | `#fff` 白色 |
| 标签激活 | 无颜色 | `--primary-color` 蓝色指示器 |
| 分页高亮 | `#009688` | `--primary-color` |
| 统计数字 | `#009688` | `--primary-color` + DIN字体 |
| body背景 | `#f1f1f1` | `--bg-page` `#f0f2f5` |
| 滚动条 | 默认 | 4px窄滚动条 + 深色侧边栏自定义 |

**新增依赖**

- `css/design-tokens.css` — 设计Token
- Font Awesome 4.7 — 图标库

---

## 三、设计规范

### 3.1 配色方案

```
主色（蓝）：#1E88E5 / #42A5F5 / #1565C0
辅色（绿）：#43A047 / #66BB6A / #2E7D32
强调（橙）：#FF6D00 / #FF9100
语义色：成功 #67C23A / 警告 #E6A23C / 危险 #F56C6C
```

### 3.2 字体规范

```
正文字体：PingFang SC / Microsoft YaHei / Helvetica Neue
数据字体：DIN Alternate / Helvetica Neue
图标库：Font Awesome 4.7
```

### 3.3 间距规范

```
卡片内边距：20px
卡片间距：16px
圆角：4px / 8px / 12px
阴影：0 2px 8px / 0 4px 16px / 0 8px 24px
```

---

## 四、文件变更清单

### 新建文件
```
src/main/resources/static/css/design-tokens.css
src/main/resources/static/css/dashboard.css
```

### 修改文件
```
src/main/resources/static/login.html
src/main/resources/static/css/login.css
src/main/resources/static/welcome.html
src/main/resources/static/css/xadmin.css
src/main/resources/static/admin-index.html
src/main/resources/static/user-index.html
src/main/resources/static/plot-admin-add-test.html
```

### 删除文件（18个）
```
src/main/resources/static/dormitory-admin-add.html
src/main/resources/static/dormitory-admin-del.html
src/main/resources/static/dormitory-admin-get.html
src/main/resources/static/dormitory-admin-getstudentall.html
src/main/resources/static/dormitory-admin-update.html
src/main/resources/static/register-admin.html
src/main/resources/static/register-admin-add.html
src/main/resources/static/register-admin-del.html
src/main/resources/static/register-admin-get.html
src/main/resources/static/register-admin-update.html
src/main/resources/static/admin-admin.html
src/main/resources/static/admin-admin-add.html
src/main/resources/static/admin-admin-del.html
src/main/resources/static/admin-admin-get.html
src/main/resources/static/admin-admin-update.html
src/main/resources/static/plots-admin.html
src/main/resources/static/admin-list.html
src/main/resources/static/log.html
```

---

## 五、验证方式

1. 打开 `http://localhost:8080`，检查登录页视觉效果
2. 登录后检查驾驶舱统计数据是否真实
3. 检查侧边栏深色风格是否生效
4. 检查标签栏蓝色指示器是否正常
5. 浏览器控制台无 404 错误

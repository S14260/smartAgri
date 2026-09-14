# 对外接口契约

本文件描述本系统当前**已经实现**的对外接口，供与其他组系统对接时作为共同依据。

契约的用法是：**先按本文件把接口定下来，两边各自用假数据并行开发，最后联调**。
不要等两边都写完了再凑——那时候字段名、鉴权头、错误码都对不上，返工量最大。

> 本文档按代码实际行为编写，不是理想设计稿。**已知不一致的地方集中列在最后一节**，
> 对接前先看那一节，避免踩坑。

---

## 一、服务与端口职责

| 服务 | 端口 | 技术栈 | 职责 |
|------|------|--------|------|
| Java 业务层 | 8080 | Spring Boot 2.6 | 用户/管理员认证、地块 CRUD、驾驶舱统计、巡田报告生成、AI Agent |
| Python 计算层 | 8000 | Flask | NDVI 影像裁剪、子区域异常检测、巡田工单、路径规划 |

约定：

- **业务数据以 Java 层为准**。地块、用户等数据只存在 MySQL 里，Python 层不直连数据库，
  需要地块数据时向 Java 层请求（见 `/admin/plots` 代理）。
- Python 层的输出是**文件产物**（JSON / PNG / GeoJSON），通过 HTTP 提供下载，不落库。
- 两个服务**相互独立部署**。Python 层被 Java 层或前端直接调用，二者之间没有强耦合。
  当前线上部署在 `123.56.228.32`（见 `api/ndvi/gunicorn_conf.py`）。

---

## 二、鉴权

系统有**两套独立 JWT**，互不通用。

| 身份 | 请求头名 | 签发密钥配置项 | 载荷字段 | 保护的路径 |
|------|----------|----------------|----------|------------|
| 管理员 | `token` | `jwt.admin-secret-key` | `adminId` | `/admin/**` |
| 普通用户 | `authentication` | `jwt.user-secret-key` | `userId` | `/user/**` |

规则（见 `interceptor/WebMvcConfig.java`）：

- `/admin/login` 和 `/user/login` **不需要**令牌，其余 `/admin/**`、`/user/**` 全部拦截。
- **校验失败返回 HTTP 401，响应体为空**——不是 JSON，拿不到失败原因。
  对接方不要靠解析响应体判断鉴权失败，要看状态码。
- 拦截器只对 `HandlerMethod` 生效，静态资源（HTML/CSS/JS）不拦截。
- **Python 层（8000）自身不做鉴权**。它的 `/user/**`、`/admin/**` 路径名只是为了和
  Java 层对称，不代表它会校验令牌。对外暴露时请在网关或反向代理上做控制。

跨域（Java 层 `WebMvcConfig.java`）：`allowedOriginPatterns("*")` +
`allowCredentials(true)`，允许 `GET/POST/PUT/DELETE/OPTIONS`，允许任意请求头。
即**任何来源都可以带凭证访问**。Python 层在 `before_request` 里手工处理 `OPTIONS` 预检。

---

## 三、返回格式

### 3.1 Java 层：`Result`（推荐对接方按此约定）

```java
public class Result<T> {
    private Integer code; // 1 成功；0 和其它数字为失败
    private String  msg;  // 错误信息，成功时为 null
    private T       data; // 业务数据
}
```

```json
{ "code": 1, "msg": null, "data": { "plotCount": 12, "totalArea": 3456.78 } }
```

**三个容易踩的点：**

1. **`code` 不是 HTTP 状态码**。`1` 表示成功、`0` 表示失败，不是 `200/500`。
2. **业务失败时 HTTP 状态码仍然是 200**。后端 `catch` 住异常后返回 `Result.error(...)`，
   所以判断成败必须看 `code`，不能只看 HTTP 状态码。
3. **`msg` 在成功时为 `null`**，不是空字符串。

### 3.2 Java 层的例外：地块接口不返回 `Result`

`/admin/plots` 和 `/user/plots` 系列**直接返回实体、数组或 `ResponseEntity`**，没有 `Result` 包装：

| 接口 | 成功时返回 | 失败时返回 |
|------|-----------|-----------|
| `GET /admin/plots` | `AdminPlot[]` | — |
| `POST /admin/plots` | `AdminPlot` | — |
| `PUT /admin/plots/{id}/area` | `AdminPlot` | 抛异常 → Spring 默认 500 |
| `POST /admin/plots/{id}/address` | 纯文本 `"地址更新成功"` | 404 + 纯文本 |
| `DELETE /admin/plots/{id}` | 空 | — |
| `DELETE /admin/plots/deleteBatch` | 纯文本 `"删除成功"` | 500 + 纯文本 |
| `GET /user/plots` | `UserPlot[]` | — |
| `DELETE /user/plots/{id}` | 纯文本 `"删除成功"` | 403 + 纯文本 |

**对接建议**：需要自己的系统读地块数据时，`GET /admin/plots` 是唯一稳定的入口，
它返回一个数组，字段见 `model/AdminPlot.java`。**不要依赖 `msg` 字段**——这些接口根本没有。

### 3.3 Python 层：直接返回 JSON / 文件

没有 `Result` 包装，成功失败靠 **HTTP 状态码 + 响应体里的 `status`/`error` 字段**共同判断：
`{"status": "success", ...}`、`{"status": "error", "message": "..."}`、`{"error": "..."}` 三种都在用。
具体字段见下面每个接口的说明。

---

## 四、Java 层接口（8080）

| 接口 | 方法 | 说明 | 返回 |
|------|------|------|------|
| `/admin/login` | POST | 管理员登录，**唯一免鉴权** | `Result`（含 JWT） |
| `/user/login` | POST | 用户登录，**唯一免鉴权** | `Result`（含 JWT） |
| `/admin/plots` | GET | 全部地块；带 `?region=xxx` 按地区筛选 | `AdminPlot[]` |
| `/admin/plots` | POST | 新增地块 | `AdminPlot` |
| `/admin/plots/{id}` | PUT | 修改地块属性 | `AdminPlot` |
| `/admin/plots/{id}` | DELETE | 删除单个地块 | 空 |
| `/admin/plots/{id}/area` | PUT | 修改面积，body `{"area": 123.4}` | `AdminPlot` |
| `/admin/plots/{id}/address` | POST | 修改地址，body `{"address": "..."}` | 纯文本 |
| `/admin/plots/deleteBatch` | DELETE | 批量删除，body 为 id 数组 | 纯文本 |
| `/user/plots` | GET | 当前用户地块（用户令牌） | `UserPlot[]` |
| `/user/plots` | POST | 新增用户地块 | `UserPlot` |
| `/user/plots/{id}` | PUT | 修改，含归属校验 | `UserPlot` |
| `/user/plots/{id}` | DELETE | 删除，含归属校验，非本人返回 403 | 纯文本 |
| `/user/plots/deleteBatch` | DELETE | 批量删除，只删自己的 | 纯文本 |
| `/admin/dashboard/overview` | GET | 概览：`plotCount` / `totalArea` / `punchCount` | `Result` |
| `/admin/dashboard/plot-stats` | GET | 统计：`byCrop` / `byRegion` / `bySoil` | `Result` |
| `/admin/report/generate` | POST | 生成巡田任务单（调 LLM，失败自动降级为模板） | `Result` |
| `/admin/ai/explain` | POST | 单条异常智能解释 | `Result<String>` |
| `/admin/ai/chat` | POST | Agent 非流式对话，body `{sessionId, message}` | `Result<String>` |
| `/admin/ai/chat/stream` | POST | Agent 流式对话（**SSE**） | `text/event-stream` |
| `/admin/ai/tools` | GET | 列出 Agent 可用工具 | `Result` |
| `/admin/ai/conversation` | DELETE | 清除会话，`?sessionId=xxx` | `Result` |

`/admin/report/generate` 的请求体是上游巡田工单里的异常数组：

```json
{
  "report_time": "2026-09-14",
  "anomaly_subregions": [
    { "plot_name": "1号地", "anomaly_category": "干旱", "ndvi_grade_label": "中度干旱",
      "area_m2": 8300.0, "mean_ndvi": 0.21, "priority": 3, "severity": 4,
      "contact_person": "张三", "phone": "13800000000" }
  ]
}
```

返回 `data` 含 `total_anomaly` / `high_count` / `medium_count` / `low_count` /
`generated_time` / `summary` / `risk_level`（`高`/`中`/`低`）/ `route_suggestion` / `tasks[]`。

> 字段名注意：输入用 `mean_ndvi`，输出任务里叫 `ndvi_mean`；输入 `area_m2`（平方米），
> 输出 `area_mu`（亩，按 `area_m2 / 666.67` 换算）。对接时别串。

---

## 五、Python 层接口（8000）

### 5.1 地块查询代理

| 接口 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/admin/plots` | GET | — | 转发到 Java `:8080/admin/plots` |
| `/user/plots` | GET | — | 转发到 Java `:8080/user/plots` |

### 5.2 NDVI 影像裁剪

| 接口 | 方法 | 说明 |
|------|------|------|
| `/admin/ndvicut` | POST | 管理端裁剪 |
| `/user/ndvicut` | POST | 用户端裁剪 |
| `/admin/ndvilist` | GET | NDVI 文件列表，**必须带 `?region=`** |
| `/user/ndvilist` | GET | 同上（用户端） |
| `/ndvi_files/<region>/<filename>` | GET | 取裁剪后的影像文件 |
| `/ndvi_files/<filename>` | GET | 旧路径，无 region 兼容用 |

### 5.3 巡田分析

| 接口 | 方法 | 参数 | 说明 |
|------|------|------|------|
| `/xuntian/run` | POST | 见下 | 启动分析任务，**异步** |
| `/xuntian/status` | GET | `timestamp`（必填） | 查询进度 |
| `/xuntian/results` | GET | `timestamp`（可选） | 取分析结果 |
| `/xuntian/reports` | GET | — | 历史工单列表 |
| `/xuntian/report/detail` | GET | `path`（必填） | 取指定工单内容 |
| `/xuntian/results/files/<filename>` | GET | — | 取巡田产物文件 |
| `/xuntian/patrol/plan` | POST | 见下 | 生成巡田路径规划 |

**`/xuntian/run` 请求体**（单个地块传对象，多个传数组）：

```json
[{ "plot_id": "P001", "start_date": "2026-08-01", "end_date": "2026-09-01",
   "ndvi_folder": "./ndvi_files" }]
```

`plot_id` / `start_date` / `end_date` 必填；`ndvi_folder` 可选。
返回：

```json
{ "status": "success", "timestamp": "20260914_103000",
  "message": "已启动 3 个巡田分析任务（后台运行）",
  "tasks": [{ "plot_id": "P001", "status": "已提交" }],
  "notice": "所有任务完成后将自动生成最终统一工单..." }
```

**`timestamp` 是后续所有查询的句柄**，拿到后要立刻存下来传给 `/xuntian/status`、`/xuntian/results`。

**`/xuntian/results?timestamp=xxx` 的返回不唯一**，按优先级依次尝试：任务内存结果 →
最新最终工单 `{type:"final_report", generate_time, data}` → 临时结果数组 →
`{"message":"暂无巡田结果"}`。对接方需要判断响应形状，不能假设固定结构。

**`/xuntian/reports` 返回数组**，元素：

```json
{ "timestamp": "20260914_103000", "generate_time": "20260914_103000",
  "total_anomaly_count": 7, "report_file": "巡田最终工单_20260914_103000.json",
  "base_path": "http://<host>/static/xuntian_results/reports_20260914_103000",
  "report_url": "http://<host>/static/xuntian_results/reports_20260914_103000/巡田最终工单_20260914_103000.json" }
```

> `base_path` / `report_url` 里的 host 取自配置 `XUNTIAN_RESULT_BASE`，
> 当前硬编码为 `http://123.56.228.32:8000`。换部署环境必须改。

**`/xuntian/report/detail` 的参数名是 `path`**（不是 `report_path`），
可传上一步的完整 `report_url`，也兼容相对路径。

**`/xuntian/patrol/plan` 请求体**：

```json
{ "report_path": "<report_url 或本地路径>", "enable_2opt": true }
```

`report_path` 必填，`enable_2opt` 可选（默认 `true`，控制是否做 2-opt 局部优化）。
失败时返回 `{"status":"error","message":"..."}` 并以 400/404 响应。

---

## 六、版本化与变更流程

- **改接口在路径上加版本号**：`/v1/...`。现有接口暂时没有版本号，属于历史遗留；
  新开的对外接口一律带 `/v1`。
- **新接口上线后旧接口先保留**，确认对方已切换再下线，避免对方突然挂掉。
- **任何字段增删改，在本文件的同一次 PR 里更新**，并在 PR 描述里写明改动点和迁移方式。
- 加字段是兼容的，改字段名和删字段不是。前者可以直接上，后者走版本号。

---

## 七、已知不一致（对接前务必先读）

这些是代码当前的真实状态，不是设计意图。对接时要么绕开，要么先改代码。

1. **返回格式不统一**。`Result{code,msg,data}` 和裸实体/纯文本混用，同一组路径下都可能不一致
   （见 3.2）。对接方最省事的做法：只依赖 `GET /admin/plots` 取数据，其余走 Java 层新接口时
   按 `Result` 解析。

2. **`msg` 语义模糊**。`Result.msg` 在 `Result.error()` 里是错误原因，但在 `Result.success()`
   里恒为 `null`，并非"提示信息"。不要把它当成功提示展示。

3. **Python 层 `/admin/plots` 代理的鉴权头名对不上**。
   `api/ndvi/app.py:64` 把收到的 `token` 头改名成 `authentication` 再转发给 Java，
   而 Java 的 `/admin/**` 拦截器读的是 `token` 头——按当前代码这个代理会拿到 401。
   `/user/plots`（`app.py:56`）转发的头名是对的。**对接管理端数据请直接连 Java 的 8080**，
   不要走这个代理，或者先把这个头名改一致。

4. **`/xuntian/status` 必传 `timestamp`**，不传直接返回 400。它不接受"查当前任务"这种用法。

5. **Python 层无鉴权**，且 `/xuntian/report/detail` 与 `/xuntian/patrol/plan` 接受任意路径参数，
   分别用于读文件和定位工单。对外网暴露前必须加访问控制，否则存在任意文件读取风险。

6. **全局任务状态是单例**。`run_xuntian` 用模块级全局变量统计 `total_task_count` /
   `completed_task_count`（`api/ndvi/app.py` 顶部），**同一时刻只支持一个分析批次**。
   两个系统并发调 `/xuntian/run` 会互相污染进度。对接方需自行串行化，或先改造为按任务隔离。

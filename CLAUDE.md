# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Smart Agriculture Management System (智慧农业管理系统). A dual-service application:
- **Java/Spring Boot backend** (port 8080) — core CRUD, auth, plot management, AI Agent
- **Python/Flask microservice** (port 8000) — NDVI satellite image processing, patrol/inspection analysis, route planning

Frontend is server-rendered HTML using LayUI/X-admin/Leaflet/Cesium (not a SPA).

## Build & Run

```bash
# Java backend (requires MySQL on localhost:3306, database "mydb")
./mvnw clean package          # build
./mvnw spring-boot:run        # run on port 8080

# Python API (separate terminal)
cd api
pip install -r requirements.txt
python app.py                 # runs on port 8000
```

Database setup: import `src/main/resources/mydb.sql` into MySQL. Default credentials in `application.yml` are root/root.

## Architecture

### Java Backend (`com.example.smartAgr`)

- **Dual JWT auth**: admin tokens use header `token` (secret `smartArgAdmin`), user tokens use header `authentication` (secret `smartArgUser`). Interceptors in `interceptor/` validate and set `BaseContext` (ThreadLocal).
- **Hybrid data access**: JdbcTemplate for legacy entities (Admin, User, Student, Dormitory, Register), Spring Data JPA for plot entities (AdminPlot, UserPlot), MyBatis-Plus for PunchRecord. This inconsistency is intentional/existing — don't mix further.
- **Controllers** split into `controller/admin/` and `controller/user/` with role-specific endpoints.
- **Legacy code**: Student, Dormitory, Register models/controllers/services are from the original dormitory management template and coexist with agriculture-specific code.
- **LLM integration**: `LlmServiceImpl` calls DeepSeek API via OkHttp for anomaly explanation. Config in `LLMConfig.java` binds `llm.*` properties.
- **AI Agent**: `service/ai/AgentService.java` implements a ReAct (Reasoning + Acting) loop with function calling. Tools are `AgentTool` implementations auto-registered via Spring DI. Supports both non-streaming (`/admin/ai/chat`) and SSE streaming (`/admin/ai/chat/stream`). Tools: `QueryPlotsTool`, `GetAnomalyRecordsTool`, `TriggerAnomalyDetectionTool`, `ExplainAnomalyTool`, `GeneratePatrolRouteTool`.
- **Result wrapper**: `result/Result.java` is the standard API response format (`code`/`msg`/`data`). There's a duplicate in `utils/Result.java` — use the one in `result/`.

### Python Flask API (`api/`)

- `app.py` — main Flask app, async task tracking for patrol analysis
- `cut_smooth_cutEdge.py` — NDVI image clipping/smoothing to plot boundaries
- `xuntian_subregion.py` — patrol subregion analysis
- `services/patrol_planning.py` — route planning algorithm
- Proxies plot data requests to the Java backend

### Frontend (`src/main/resources/static/`)

- HTML pages served by Spring Boot, using LayUI + X-admin templates
- Leaflet for 2D map rendering (`admin-patrol.html`, `admin-map.html`)
- **Cesium 3D globe** (`admin-patrol-cesium.html`) — full-featured: plot rendering, NDVI overlay, anomaly detection, historical reports, route planning, address search, and AI chat assistant
- AI Chat widget embedded in Cesium page — uses SSE streaming to `/admin/ai/chat/stream`
- Entry point: `/` redirects to `login.html`

## Key Conventions

- Java 1.8, Spring Boot 2.6.13
- Package base: `com.example.smartAgr`
- Plot coordinates stored as JSON TEXT in MySQL (not PostGIS)
- Pagination is in-memory via `PageUtil` (fetches all, slices) — not database-level
- Passwords are stored in plaintext (known issue)
- CORS configured for 123.56.228.32:8080 in both `CorsConfig` and `WebMvcConfig`

## Common Gotchas

- `LLMConfig` properties are in `application.yml` with env var overrides (`${LLM_API_KEY:sk-xxx}`) — set `LLM_API_KEY` env var for real usage
- Drools dependencies are declared in `pom.xml` but completely unused
- `LlmGatewayService` and `PlotAddressUpdateTask` are entirely commented out
- The `api/` directory and `node_modules/` are git-tracked or untracked differently — check `git status` before committing
- Agent conversation history is in-memory (`ConcurrentHashMap`) — lost on restart

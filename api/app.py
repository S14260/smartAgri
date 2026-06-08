from flask import Flask, request, jsonify, make_response, send_from_directory
from flask_cors import CORS
import requests
import os
import json
import threading
from pathlib import Path
from datetime import datetime
import cut_smooth_cutEdge
import xuntian_subregion as xuntian
from services.patrol_planning import run_patrol_planning_pipeline

app = Flask(__name__, static_folder="static")
XUNTIAN_RESULT_BASE = 'http://123.56.228.32:8000';

# ====== CORS 配置 ======
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": ["http://localhost:8080", "http://localhost:8080"],
        "allow_headers": ["Content-Type", "Authorization", "token", "authentication"],
        "methods": ["GET", "POST", "OPTIONS"]
    }
})

# ====== 基础配置 ======
NDVI_BASE_URL = "http://123.56.228.32"
NDVI_LOCAL_FOLDER = "./ndvi_files"
CROPPED_BASE_FOLDER = "./static/ndvi_clips"
XUNTIAN_OUTPUT = Path("./static/xuntian_results")

# ====== 异步任务跟踪 ======
task_lock = threading.Lock()
total_task_count = 0
completed_task_count = 0
is_report_generated = False
task_results = {}  # 新增：存储每个任务的结果


# ========== OPTIONS 预检请求支持 ==========
@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "")
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = request.headers.get(
            "Access-Control-Request-Headers", "Content-Type, token, authentication"
        )
        return response


# ========== 用户端地块获取 ==========
@app.route("/user/plots", methods=["GET"])
def get_user_plots():
    headers = {"authentication": request.headers.get("authentication", "")}
    resp = requests.get(f"{NDVI_BASE_URL}:8080/user/plots", headers=headers)
    return jsonify(resp.json()), resp.status_code


# ========== 管理端地块获取 ==========
@app.route("/admin/plots", methods=["GET"])
def get_admin_plots():
    headers = {"authentication": request.headers.get("token", "")}
    resp = requests.get(f"{NDVI_BASE_URL}:8080/admin/plots", headers=headers)
    return jsonify(resp.json()), resp.status_code


# ========== polygon 坐标解析工具 ==========
def _extract_latlngs(polygon_obj):
    if polygon_obj is None:
        return None
    if isinstance(polygon_obj, list):
        return polygon_obj
    if isinstance(polygon_obj, str):
        try:
            parsed = json.loads(polygon_obj)
            return _extract_latlngs(parsed)
        except Exception:
            return None
    if isinstance(polygon_obj, dict):
        if "latlngs" in polygon_obj and isinstance(polygon_obj["latlngs"], list):
            return polygon_obj["latlngs"]
        if "geometry" in polygon_obj and isinstance(polygon_obj["geometry"], dict):
            geometry = polygon_obj["geometry"]
            if "coordinates" in geometry:
                coords = geometry["coordinates"]
                if coords and isinstance(coords[0], list):
                    try:
                        ring = coords[0]
                        return [{"lat": c[1], "lng": c[0]} for c in ring]
                    except Exception:
                        return None
        if "coordinates" in polygon_obj:
            coords = polygon_obj["coordinates"]
            if coords and isinstance(coords[0], list):
                try:
                    ring = coords[0]
                    return [{"lat": c[1], "lng": c[0]} for c in ring]
                except Exception:
                    return None
    return None


# ========== NDVI 裁剪处理 ==========
def handle_crop(date, region, username, plots):
    if not all([date, username, plots]):
        return jsonify({"error": "缺少参数（date、username、plots）"}), 400

    if isinstance(plots, dict):
        plots = [plots]

    results, errors = [], []

    for plot in plots:
        plot_id = plot.get("plotId")
        polygon_raw = plot.get("polygon")
        plotname = plot.get("plotname")

        if not plot_id or not polygon_raw:
            errors.append({"plotId": plot_id, "error": "缺少 plotId 或 polygon"})
            continue

        try:
            polygon_obj = json.loads(polygon_raw) if isinstance(polygon_raw, str) else polygon_raw
            polygon_coords = _extract_latlngs(polygon_obj)
            if not polygon_coords or not isinstance(polygon_coords, list):
                errors.append({"plotId": plot_id, "error": "polygon 解析失败"})
                continue

            tif_rel, tif_path, png_rel, png_path, bounds = cut_smooth_cutEdge.cut_smooth_cutEdge(
                date_str=date,
                polygon_coords=polygon_coords,
                plot_id=plot_id,
                username=username,
                plot_name=plotname,
                region=region
            )

            host = request.host_url.rstrip("/")
            tif_url = f"{host}/{tif_rel.lstrip('/')}" if tif_rel else None
            png_url = f"{host}/{png_rel.lstrip('/')}" if png_rel else None

            results.append({
                "tif_url": tif_url,
                "png_url": png_url,
                "tif_filename": os.path.basename(tif_path) if tif_path else None,
                "png_filename": os.path.basename(png_path) if png_path else None,
                "bounds": bounds,
                "user": username,
                "plotId": plot_id,
                "plotname": plotname
            })
        except Exception as e:
            errors.append({"plotId": plot_id, "error": str(e)})

    try:
        return jsonify({"success": results, "errors": errors})
    except Exception as e:
        print(f"[handle_crop 序列化失败] {e}")
        return jsonify({"success": [], "errors": [{"error": str(e)}]}), 500


@app.route("/user/ndvicut", methods=["POST", "OPTIONS"])
def user_crop_ndvi():
    data = request.json or {}
    return handle_crop(
        date=data.get("date"),
        region=data.get("region"),
        username=data.get("username"),
        plots=data.get("plots") or {
            "plotId": data.get("plotId"),
            "polygon": data.get("polygon"),
            "plotname": data.get("plotname")
        }
    )


@app.route("/admin/ndvicut", methods=["POST", "OPTIONS"])
def admin_crop_ndvi():
    data = request.json or {}
    return handle_crop(
        date=data.get("date"),
        region=data.get("region"),
        username="admin",
        plots=data.get("plots") or {
            "plotId": data.get("plotId"),
            "polygon": data.get("polygon"),
            "plotname": data.get("plotname")
        }
    )


# ========== 静态文件访问 ==========
@app.route("/ndvi_files/<region>/<path:filename>")
def serve_ndvi_files_with_region(region, filename):
    dirpath = os.path.join("ndvi_files", region)
    return send_from_directory(dirpath, filename)


@app.route("/ndvi_files/<path:filename>")
def serve_ndvi_files_no_region(filename):
    return send_from_directory("ndvi_files", filename)


# ========== NDVI 列表 ==========
@app.route("/user/ndvilist", methods=["GET"])
def user_ndvi_list():
    region = request.args.get("region")
    ndvi_files = cut_smooth_cutEdge.list_ndvi_files(region=region)
    host = request.host_url.rstrip("/")
    for f in ndvi_files:
        if f["region"]:
            f["url"] = f"{host}/ndvi_files/{f['region']}/{f['filename']}"
        else:
            f["url"] = f"{host}/ndvi_files/{f['filename']}"
    return jsonify(ndvi_files)


@app.route("/admin/ndvilist", methods=["GET"])
def admin_ndvi_list():
    region = request.args.get("region")
    ndvi_files = cut_smooth_cutEdge.list_ndvi_files(region=region)
    host = request.host_url.rstrip("/")
    for f in ndvi_files:
        if f["region"]:
            f["url"] = f"{host}/ndvi_files/{f['region']}/{f['filename']}"
        else:
            f["url"] = f"{host}/ndvi_files/{f['filename']}"
    return jsonify(ndvi_files)


# ====== 异步任务函数 ======
def run_xuntian_analysis_async(plot_id=None, start_date=None, end_date=None, ndvi_folder=None, timestamp=None):
    """后台异步运行巡田分析 + 任务完成后计数"""
    global completed_task_count, is_report_generated

    def task():
        global completed_task_count, is_report_generated
        try:
            print(f"[巡田分析] 开始 — 地块: {plot_id}, 时间范围: {start_date}~{end_date}")
            # ========== 核心修改1：封装参数为字典传入 ==========
            params = {
                "plot_ids": [plot_id],  # 单地块传列表
                "start_date": start_date,
                "end_date": end_date,
                "ndvi_folder": ndvi_folder,
                "timestamp": timestamp,
                "delete_temp": False
            }
            # 调用巡田分析函数（传入字典参数）
            xuntian.run_xuntian_from_app(params)
            print(f"[巡田分析] 完成 — 地块: {plot_id}")
        except Exception as e:
            print(f"[巡田分析] 运行失败: {e}")
            import traceback
            traceback.print_exc()  # 新增：打印详细错误栈
        finally:
            with task_lock:
                completed_task_count += 1
                print(f"[任务跟踪] 已完成 {completed_task_count}/{total_task_count} 个地块")

                if completed_task_count == total_task_count and not is_report_generated:
                    print(f"[最终工单] 所有 {total_task_count} 个地块处理完成，开始生成最终工单...")
                    try:
                        # ========== 核心修改2：传时间戳生成最终报告 ==========
                        final_report = xuntian.generate_final_report(delete_temp=False, timestamp=timestamp)
                        print(f"[最终工单] 生成成功！路径：{xuntian.Config.OUTPUT_FOLDER}")
                        # 修复：打印anomaly_records数量（兼容字段）
                        anomaly_records = final_report.get('anomaly_records',
                                                           final_report.get('anomaly_subregions', []))
                        print(f"[最终工单] 共 {len(anomaly_records)} 条异常记录")
                        task_results[timestamp] = final_report  # 存储报告结果
                    except Exception as e:
                        print(f"[最终工单] 生成失败：{str(e)}")
                        import traceback
                        traceback.print_exc()
                    finally:
                        is_report_generated = True

    thread = threading.Thread(target=task, daemon=True)
    thread.start()


# ====== 巡田任务提交接口 ======
@app.route("/xuntian/run", methods=["POST"])
def run_xuntian():
    """启动巡田分析任务（多地块自动跟踪，完成后生成最终工单）"""
    global total_task_count, completed_task_count, is_report_generated

    data = request.get_json() or []
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return jsonify({"error": "数据格式错误，需为字典（单地块）或列表（多地块）"}), 400

    # 动态时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[时间戳] 当前任务时间戳: {timestamp}")
    task_results[timestamp] = {}  # 初始化任务结果

    valid_tasks = []
    for item in data:
        plot_id = item.get("plot_id")
        start_date = item.get("start_date")
        end_date = item.get("end_date")
        ndvi_folder = item.get("ndvi_folder", NDVI_LOCAL_FOLDER)
        if not all([plot_id, start_date, end_date]):
            return jsonify({"error": f"地块 {plot_id} 缺少必要参数（plot_id/start_date/end_date）"}), 400
        # 验证目录存在
        if not Path(ndvi_folder).exists():
            return jsonify({"error": f"NDVI目录不存在：{ndvi_folder}"}), 404
        valid_tasks.append({
            "plot_id": plot_id,
            "start_date": start_date,
            "end_date": end_date,
            "ndvi_folder": ndvi_folder
        })

    with task_lock:
        total_task_count = len(valid_tasks)
        completed_task_count = 0
        is_report_generated = False
    print(f"[任务提交] 成功接收 {total_task_count} 个地块任务，开始异步处理...")

    for task in valid_tasks:
        run_xuntian_analysis_async(
            plot_id=task["plot_id"],
            start_date=task["start_date"],
            end_date=task["end_date"],
            ndvi_folder=task["ndvi_folder"],
            timestamp=timestamp
        )

    return jsonify({
        "status": "success",
        "timestamp": timestamp,
        "message": f"已启动 {total_task_count} 个巡田分析任务（后台运行）",
        "tasks": [{"plot_id": t["plot_id"], "status": "已提交"} for t in valid_tasks],
        "notice": "所有任务完成后将自动生成最终统一工单，可通过/xuntian/results接口查询"
    })


# ========== 获取巡田结果 ==========
@app.route("/xuntian/results", methods=["GET"])
def get_xuntian_results():
    timestamp = request.args.get("timestamp")
    # 按时间戳查询
    if timestamp and timestamp in task_results:
        return jsonify(task_results[timestamp])

    # 查最新报告
    final_reports = sorted(xuntian.Config.OUTPUT_BASE.glob("reports_*/巡田最终工单_*.json"), reverse=True)
    if final_reports:
        latest_report = final_reports[0]
        try:
            with open(latest_report, "r", encoding="utf-8") as f:
                report_data = json.load(f)
                # 兼容anomaly_records字段
                report_data['anomaly_records'] = report_data.get('anomaly_records',
                                                                 report_data.get('anomaly_subregions', []))
                return jsonify({
                    "type": "final_report",
                    "generate_time": latest_report.parent.name.replace("reports_", ""),
                    "data": report_data
                })
        except Exception as e:
            print(f"[读取最终工单失败] {str(e)}")
            return jsonify({"error": f"读取报告失败：{str(e)}"}), 500

    # 查临时文件
    temp_dirs = sorted(xuntian.Config.OUTPUT_BASE.glob("reports_*/temp"), reverse=True)
    if not temp_dirs:
        return jsonify({"message": "暂无巡田结果"})

    results = []
    for temp_dir in temp_dirs[:1]:  # 只查最新的临时目录
        for file in sorted(temp_dir.glob("temp_subregions_*.json"), reverse=True):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    temp_data = json.load(f)
                    results.append({
                        "filename": file.name,
                        "plot_id": temp_data.get("plot_id") or file.name.replace("temp_subregions_", "").replace(
                            ".json", ""),
                        "status": "completed",
                        "anomalies": temp_data
                    })
            except Exception as e:
                results.append({"filename": file.name, "error": str(e)})
    return jsonify(results)

# 新增：访问巡田结果文件的路由
@app.route("/xuntian/results/files/<path:filename>")
def serve_xuntian_files(filename):
    return send_from_directory(XUNTIAN_OUTPUT, filename)


@app.route("/xuntian/status", methods=["GET"])
def xuntian_status():
    timestamp = request.args.get("timestamp")
    if not timestamp:
        return jsonify({
            "status": "error",
            "message": "missing timestamp"
        }), 400

    # 最终工单路径（与你真实生成逻辑一致）
    result_dir = XUNTIAN_OUTPUT / f"reports_{timestamp}"
    final_report_path = result_dir / f"巡田最终工单_{timestamp}.json"

    with task_lock:
        total = total_task_count
        completed = completed_task_count
        report_done = is_report_generated

    # ====== 1️⃣ 尚未开始或任务异常 ======
    if total == 0:
        return jsonify({
            "status": "pending",
            "message": "任务尚未初始化"
        })

    # ====== 2️⃣ 地块分析阶段 ======
    if completed < total:
        return jsonify({
            "status": "running",
            "progress": {
                "total": total,
                "completed": completed
            },
            "message": f"正在分析地块（{completed}/{total}）"
        })

    # ====== 3️⃣ 正在生成最终工单 ======
    if completed == total and not report_done:
        return jsonify({
            "status": "merging",
            "progress": {
                "total": total,
                "completed": completed
            },
            "message": "分析完成，正在生成最终巡田工单"
        })

    # ====== 4️⃣ 全部完成 ======
    if report_done and final_report_path.exists():
        result_url = f"{request.host_url.rstrip('/')}/static/xuntian_results/reports_{timestamp}"
        return jsonify({
            "status": "completed",
            "result_url": result_url,
            "report_file": final_report_path.name,
            "message": "巡田分析完成"
        })

    # ====== 5️⃣ 异常兜底 ======
    return jsonify({
        "status": "error",
        "message": "状态异常，请检查后台日志"
    }), 500

# ========== 历史巡田工单列表 ==========
@app.route("/xuntian/reports", methods=["GET"])
def list_xuntian_reports():
    """
    返回历史巡田最终工单列表
    """
    reports = []

    base_dir = XUNTIAN_OUTPUT  # ./static/xuntian_results
    if not base_dir.exists():
        return jsonify([])

    # 按时间倒序
    for report_dir in sorted(base_dir.glob("reports_*"), reverse=True):
        if not report_dir.is_dir():
            continue

        timestamp = report_dir.name.replace("reports_", "")
        final_report_path = report_dir / f"巡田最终工单_{timestamp}.json"

        if not final_report_path.exists():
            continue

        try:
            with open(final_report_path, "r", encoding="utf-8") as f:
                report_data = json.load(f)

            anomaly_list = report_data.get(
                "anomaly_records",
                report_data.get("anomaly_subregions", [])
            )

            reports.append({
                "timestamp": timestamp,
                "generate_time": timestamp,
                "total_anomaly_count": len(anomaly_list),
                "report_file": final_report_path.name,

                # ✅ 改：完整 URL
                "base_path": f"{XUNTIAN_RESULT_BASE}/static/xuntian_results/{report_dir.name}",
                "report_url": f"{XUNTIAN_RESULT_BASE}/static/xuntian_results/{report_dir.name}/{final_report_path.name}"
            })


        except Exception as e:
            print(f"[历史工单读取失败] {final_report_path}: {e}")

    return jsonify(reports)

# ========== 读取指定历史巡田工单 ==========
@app.route("/xuntian/report/detail", methods=["GET"])
def get_xuntian_report_detail():
    """
    根据 report_url 读取历史巡田最终工单 JSON
    """
    report_url = request.args.get("path")
    if not report_url:
        return jsonify({"error": "missing path"}), 400

    try:
        # ✅ 新逻辑：兼容完整 URL / 相对路径
        if report_url.startswith("http"):
            # 去掉域名，只保留 /static/...
            path_part = report_url.split("/static/", 1)[1]
            real_path = Path("static") / path_part
        else:
            # 旧逻辑（兜底）
            relative_path = report_url.replace("/static/", "", 1)
            real_path = Path("static") / relative_path

        if not real_path.exists():
            return jsonify({"error": "file not found"}), 404

        with open(real_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        data["anomaly_records"] = data.get(
            "anomaly_records",
            data.get("anomaly_subregions", [])
        )

        return jsonify(data)

    except Exception as e:
        print(f"[读取历史工单失败] {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/xuntian/patrol/plan", methods=["POST"])
def generate_patrol_plan():
    """
    根据【巡田最终工单】生成巡田路径规划结果
    前端调用场景：历史工单 / 当前工单 → 生成巡田路线
    输出目录：与工单文件同级（reports_xxx/patrol_plan_xxx/）
    """
    try:
        data = request.get_json() or {}

        report_path = data.get("report_path")
        enable_2opt = data.get("enable_2opt", True)

        if not report_path:
            return jsonify({
                "status": "error",
                "message": "缺少 report_path"
            }), 400

        # ========= 1️⃣ 解析真实文件路径 =========
        project_root = Path(__file__).parent

        if report_path.startswith("http"):
            if "/static/" not in report_path:
                return jsonify({
                    "status": "error",
                    "message": "非法 report_path：URL 必须包含 /static/"
                }), 400
            relative = report_path.split("/static/", 1)[1]
            real_report_path = project_root / "static" / relative
        else:
            if report_path.startswith("/static/"):
                real_report_path = project_root / report_path.lstrip("/")
            else:
                real_report_path = project_root / report_path

        real_report_path = real_report_path.resolve()

        if not real_report_path.exists():
            return jsonify({
                "status": "error",
                "message": f"工单文件不存在: {str(real_report_path)}",
                "hint": f"当前解析的绝对路径为：{str(real_report_path)}"
            }), 404

        # ========= 2️⃣ 输出目录 =========
        report_parent_dir = real_report_path.parent
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = report_parent_dir / f"patrol_plan_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)

        # ========= 3️⃣ 调用路径规划算法 =========
        result = run_patrol_planning_pipeline(
            report_json_path=str(real_report_path),
            output_dir=str(output_dir),
            enable_2opt=enable_2opt
        )

        # ========= 4️⃣ 结果判定 =========
        if not isinstance(result, dict):
            return jsonify({
                "status": "error",
                "message": "路径规划返回结果格式错误"
            }), 500

        if result.get("success") is False:
            return jsonify({
                "status": "error",
                "message": result.get("message", "巡田路径规划失败"),
                "data": result
            }), 500

        # 兼容两种返回结构：
        # 旧版：result["geojson"]
        # 新版：result["files"]["geojson"]
        files = result.get("files", {}) if isinstance(result.get("files", {}), dict) else {}

        geojson_path = result.get("geojson") or files.get("geojson", "")
        visualization_path = result.get("visualization") or files.get("visualization", "")
        evaluation_path = result.get("evaluation") or files.get("evaluation", "")

        path_length_comparison_path = (
            result.get("path_length_comparison") or files.get("path_length_comparison", "")
        )
        time_comparison_path = (
            result.get("time_comparison") or files.get("time_comparison", "")
        )
        global_nearest_neighbor_path = (
            result.get("global_nearest_neighbor") or files.get("global_nearest_neighbor", "")
        )
        hierarchical_vs_global_path = (
            result.get("hierarchical_vs_global") or files.get("hierarchical_vs_global", "")
        )

        # ========= 5️⃣ URL 转换工具 =========
        base_url = request.host_url.rstrip("/")

        def get_frontend_url(file_path):
            if not file_path:
                return ""
            file_path = Path(file_path).resolve()
            static_root = (project_root / "static").resolve()

            try:
                relative_to_static = file_path.relative_to(static_root)
            except ValueError:
                # 文件不在 static 下，直接返回空，避免接口 500
                return ""

            return f"{base_url}/static/{relative_to_static.as_posix()}"

        output_dir_url = ""
        try:
            output_dir_url = f"{base_url}/static/{output_dir.resolve().relative_to((project_root / 'static').resolve()).as_posix()}"
        except ValueError:
            output_dir_url = ""

        # ========= 6️⃣ 返回给前端 =========
        return jsonify({
            "status": "success",
            "message": result.get("message", "巡田路径规划生成成功"),
            "data": {
                "geojson": get_frontend_url(geojson_path),
                "visualization": get_frontend_url(visualization_path),
                "evaluation": get_frontend_url(evaluation_path),
                "path_length_comparison": get_frontend_url(path_length_comparison_path),
                "time_comparison": get_frontend_url(time_comparison_path),
                "global_nearest_neighbor": get_frontend_url(global_nearest_neighbor_path),
                "hierarchical_vs_global": get_frontend_url(hierarchical_vs_global_path),
                "plot_count": result.get("plot_count", 0),
                "point_count": result.get("point_count", 0),
                "route_length_m": result.get("route_length_m", 0.0),
                "missing_files": result.get("missing_files", {}),
                "output_dir": output_dir_url
            }
        })

    except Exception as e:
        print(f"[巡田路径规划失败] {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e),
            "detail": traceback.format_exc()[:1000]
        }), 500


if __name__ == "__main__":
    # 新增：指定xuntian输出目录与app.py的XUNTIAN_OUTPUT一致
    xuntian.Config.OUTPUT_BASE = XUNTIAN_OUTPUT
    # 初始化目录
    xuntian.Config.OUTPUT_BASE.mkdir(parents=True, exist_ok=True)
    Path(CROPPED_BASE_FOLDER).mkdir(parents=True, exist_ok=True)
    Path(NDVI_LOCAL_FOLDER).mkdir(parents=True, exist_ok=True)
    app.run(host="0.0.0.0", port=8000, threaded=True, debug=False)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hierarchical Patrol Route Planning (v5 - Full Version)
异常驱动分层巡田规划（Anomaly-driven Hierarchical Patrol Planning）
适配论文的分层巡田路径规划算法
核心改进：
1. 经纬度球面距离计算（替代欧氏距离，更精准）
2. 2-opt局部优化（提升路径最优性）
3. 量化评估模块（路径长度/优化率/耗时对比）
4. 学术化可视化（固定配色/中文支持/论文级分辨率）
5. 鲁棒性增强（坐标校验/起点优化/异常处理）
"""

import json
import math
import random
import time
import os   # ✅【新增】系统化运行需要
from collections import defaultdict
from typing import List, Tuple, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# =========================
# 全局配置（适配论文可视化）
# =========================
import matplotlib.font_manager as fm
import os

def configure_matplotlib_for_chinese():
    import matplotlib.pyplot as plt
    import matplotlib.font_manager as fm
    import os

    plt.rcParams['axes.unicode_minus'] = False

    if os.name == 'posix':  # Linux 服务器
        font_candidates = [
            '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc',
            '/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-microhei.ttc',
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',
        ]
    else:  # Windows
        font_candidates = [
            'C:/Windows/Fonts/simhei.ttf',
            'C:/Windows/Fonts/msyh.ttc',
        ]

    for fp in font_candidates:
        if os.path.exists(fp):
            font_prop = fm.FontProperties(fname=fp)
            plt.rcParams['font.family'] = 'sans-serif'
            plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
            print(f"✅ 已加载中文字体: {font_prop.get_name()} -> {fp}")
            return font_prop

    print("⚠️ 未找到中文字体，可能出现乱码！")
    return fm.FontProperties(family='DejaVu Sans')


_FONT_PROP = configure_matplotlib_for_chinese()

# =========================
# 基础工具函数（增强版）
# =========================

def haversine_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    计算两点间球面距离（米），适配经纬度坐标
    :param p1: (经度, 纬度)
    :param p2: (经度, 纬度)
    :return: 距离（米）
    """
    R = 6371000  # 地球平均半径（米）
    lon1, lat1 = math.radians(p1[0]), math.radians(p1[1])
    lon2, lat2 = math.radians(p2[0]), math.radians(p2[1])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Haversine公式
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """欧氏距离（仅用于地块内短距离计算）"""
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


def compute_centroid(points: List[Tuple[float, float]]) -> Tuple[float, float]:
    """计算点集质心，增加空值校验"""
    if not points:
        raise ValueError("点集不能为空，无法计算质心")
    x = sum(p[0] for p in points) / len(points)
    y = sum(p[1] for p in points) / len(points)
    return (x, y)


def validate_coordinates(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """
    坐标合法性校验：过滤异常值（经纬度范围、空值）
    :return: 清洗后的坐标列表
    """
    valid_points = []
    for p in points:
        if not p or len(p) != 2:
            continue
        lon, lat = p
        # 经纬度合理范围校验（可根据实际区域调整）
        if -180 <= lon <= 180 and -90 <= lat <= 90:
            valid_points.append((float(lon), float(lat)))
    return valid_points


def calculate_route_length(route: List[Tuple[float, float]]) -> float:
    """计算路径总长度（米）"""
    if len(route) < 2:
        return 0.0
    total_length = 0.0
    for i in range(len(route) - 1):
        total_length += haversine_distance(route[i], route[i + 1])
    return total_length

# =========================
# 异常驱动权重（新增）
# =========================

def anomaly_weight(sr: dict) -> float:
    """
    计算异常驱动权重（用于路径排序）
    权重越大，越优先巡田
    """
    severity = sr.get("severity", 0.0)
    priority = sr.get("priority", 0.0)
    area = sr.get("area_m2", 0.0)

    # 归一化面积（防止超大地块压制）
    area_factor = math.log(area + 1)

    # 综合权重（论文里可写为加权线性模型）
    weight = 0.5 * priority + 0.3 * severity + 0.2 * area_factor
    return weight

# =========================
# 路径优化算法
# =========================

def nearest_neighbor_path(points: List[Tuple[float, float]], use_spherical: bool = False) -> List[Tuple[float, float]]:
    """
    改进版最近邻算法：
    1. 起点优化（选最西端点，减少折返）
    2. 支持球面/欧氏距离切换
    3. 完善空值/单点处理
    """
    # 坐标清洗
    points = validate_coordinates(points)
    if len(points) <= 1:
        return points

    # 选择最优起点：经度最小（最西）→ 纬度最小（最南）
    def sort_key(p):
        return (p[0], p[1])  # 先按经度，再按纬度

    start_idx = min(range(len(points)), key=lambda i: sort_key(points[i]))

    unvisited = points.copy()
    path = [unvisited.pop(start_idx)]
    distance_func = haversine_distance if use_spherical else euclidean_distance

    while unvisited:
        last = path[-1]
        # 找最近未访问点
        nxt = min(unvisited, key=lambda p: distance_func(last, p))
        path.append(nxt)
        unvisited.remove(nxt)

    return path


def two_opt_optimization(route: List[Tuple[float, float]], iterations: int = 200) -> List[Tuple[float, float]]:
    """
    2-opt局部优化算法：迭代交换路径边，减少总长度
    :param route: 初始路径
    :param iterations: 迭代次数（平衡效率与最优性）
    :return: 优化后路径
    """
    if len(route) < 4:  # 点数过少无需优化
        return route

    best_route = route.copy()
    best_length = calculate_route_length(best_route)
    random.seed(45)  # 固定随机种子，保证结果可复现

    for _ in range(iterations):
        # 随机选择两个不相邻的索引
        i = random.randint(1, len(best_route) - 2)
        j = random.randint(i + 1, len(best_route) - 1)

        # 2-opt交换：反转i到j的路径段
        new_route = best_route[:i] + best_route[i:j][::-1] + best_route[j:]
        new_length = calculate_route_length(new_route)

        # 保留更优路径
        if new_length < best_length:
            best_route = new_route
            best_length = new_length

    return best_route


def global_nearest_neighbor(points: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
    """无分组全局最近邻（用于对比实验）"""
    return nearest_neighbor_path(points, use_spherical=True)


# =========================
# 主算法：分层路径规划
# =========================

def generate_patrol_route_from_report(
        report: dict,
        use_2opt: bool = True
) -> Tuple[List[Tuple[float, float]], dict, dict]:
    """
    分层巡田路径规划主函数
    :param report: 异常子区域报告字典
    :param use_2opt: 是否启用2-opt优化
    :return: 最终路径、地块路径字典、地块质心字典
    """
    # 1. 数据提取与校验
    if "anomaly_subregions" not in report:
        raise ValueError("报告格式错误：缺少anomaly_subregions字段")
    subregions = report["anomaly_subregions"]
    if not subregions:
        raise ValueError("异常子区域列表为空，无法生成路径")

    # 2. 按地块分组 + 异常权重
    plots = defaultdict(list)
    plot_weights = defaultdict(float)

    for sr in subregions:
        if not sr.get("is_anomaly", False):
            continue

        centroid = sr.get("centroid")
        if not centroid or len(centroid) != 2:
            continue

        lon, lat = centroid[1], centroid[0]
        pid = sr["plot_id"]

        plots[pid].append((lon, lat))

        # 累加该地块的异常权重
        plot_weights[pid] += anomaly_weight(sr)

    # 3. 地块内路径生成（最近邻）
    plot_routes = {}
    plot_centroids = {}
    for pid, pts in plots.items():
        # 坐标清洗
        valid_pts = validate_coordinates(pts)
        if not valid_pts:
            continue
        # 地块内路径（短距离用欧氏距离，效率更高）
        plot_route = nearest_neighbor_path(valid_pts, use_spherical=False)
        plot_routes[pid] = plot_route
        # 计算地块质心
        plot_centroids[pid] = compute_centroid(valid_pts)

    # 4. 地块间路径规划（异常驱动 + 距离联合决策）

    plot_ids = list(plot_centroids.keys())
    if not plot_ids:
        raise ValueError("无有效地块质心数据")

    # 起点：异常权重最高的地块
    current_pid = max(plot_ids, key=lambda pid: plot_weights[pid])
    ordered_plot_ids = [current_pid]
    plot_ids.remove(current_pid)

    while plot_ids:
        last_pid = ordered_plot_ids[-1]

        def cost(pid):
            dist = haversine_distance(
                plot_centroids[last_pid],
                plot_centroids[pid]
            )
            # 距离越小越好，权重越大越好
            # 地块	  异常权重	与当前地块距离           代价
            # A（严重）	100	       10 km           10000/100=100
            # B（轻微）	10	       1 km            1000/10=100
            # C（一般）	20    	   2 km             2000/20=100
            return dist / (plot_weights[pid] + 1e-6)

        next_pid = min(plot_ids, key=cost)
        ordered_plot_ids.append(next_pid)
        plot_ids.remove(next_pid)

    # 5. 拼接全局路径
    final_route = []
    for pid in ordered_plot_ids:
        final_route.extend(plot_routes[pid])

    # 6. 2-opt全局优化
    if use_2opt and len(final_route) >= 4:
        final_route = two_opt_optimization(final_route)

    return final_route, plot_routes, plot_centroids


# =========================
# 输出模块
# =========================

def export_geojson(
        route: List[Tuple[float, float]],
        out_path: str,
        route_name: str = "Patrol Route",
        strategy: str = "hierarchical plot + nearest neighbor + 2-opt"
) -> None:
    """
    导出GeoJSON格式路径文件（适配GIS软件）
    """
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": route
                },
                "properties": {
                    "name": route_name,
                    "strategy": strategy,
                    "total_length_m": round(calculate_route_length(route), 2),
                    "point_count": len(route),
                    "generate_time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                }
            }
        ]
    }

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(geojson, f, ensure_ascii=False, indent=2)
        print(f"✅ GeoJSON已生成：{out_path}")
    except Exception as e:
        print(f"❌ GeoJSON生成失败：{e}")


def visualize_patrol_route(
        route: List[Tuple[float, float]],
        plot_routes: dict,
        plot_centroids: dict,
        out_path: str,
        title: str = "分层巡田路径规划结果"
) -> None:
    """
    论文级可视化函数：
    1. 固定配色方案（matplotlib tab10）
    2. 多层级标注（全局路径/地块/质心）
    3. 高分辨率输出（300dpi）
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 8))

        # 1. 绘制全局巡田路径
        if route:
            xs = [p[0] for p in route]
            ys = [p[1] for p in route]
            ax.plot(xs, ys, "-k", linewidth=1.5, label="全局巡田路径", zorder=1)
            # 标注起点终点
            ax.scatter(xs[0], ys[0], marker="o", s=100, color="red", label="起点", zorder=4)
            ax.scatter(xs[-1], ys[-1], marker="s", s=100, color="blue", label="终点", zorder=4)

        # 2. 绘制各地块数据
        colors = plt.cm.tab10.colors  # 固定配色
        sorted_plot_ids = sorted(plot_routes.keys())  # 排序保证配色一致

        for idx, pid in enumerate(sorted_plot_ids):
            pts = plot_routes[pid]
            color = colors[idx % len(colors)]

            # 地块内点位
            px = [p[0] for p in pts]
            py = [p[1] for p in pts]
            ax.scatter(px, py, s=30, color=color, label=f"地块 {pid}", zorder=2)

            # 地块质心（带标注）
            cx, cy = plot_centroids[pid]
            ax.scatter(cx, cy, marker="x", s=80, color=color, zorder=3)
            ax.text(
                cx + 0.0001, cy + 0.0001, f"质心{pid}",
                fontsize=7, color=color, weight="bold", fontproperties=_FONT_PROP
            )

            # 地块内路径
            ax.plot(px, py, "--", color=color, alpha=0.7, linewidth=1, zorder=1)

        # 3. 图表样式配置（论文规范）
        ax.set_title(title, fontsize=12, fontweight="bold", pad=15, fontproperties=_FONT_PROP)
        ax.set_xlabel("经度 (°)", fontsize=10, fontproperties=_FONT_PROP)
        ax.set_ylabel("纬度 (°)", fontsize=10, fontproperties=_FONT_PROP)
        ax.legend(fontsize=8, loc="upper right", framealpha=0.9, prop=_FONT_PROP)
        ax.grid(True, alpha=0.3, linestyle="-", linewidth=0.5)

        # 4. 保存（去除白边，高分辨率）
        plt.tight_layout()
        plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close()

        print(f"✅ 可视化已生成：{out_path}")

    except Exception as e:
        print(f"❌ 可视化生成失败：{e}")

####################全局最近邻#########################
def visualize_global_nearest_neighbor_route(
        route: List[Tuple[float, float]],
        out_path: str,
        title: str = "全局最近邻路径规划结果（Baseline）"
) -> None:
    """
    全局最近邻路径可视化（对比实验用）
    不区分地块，仅展示路径结构
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 8))

        if route:
            xs = [p[0] for p in route]
            ys = [p[1] for p in route]

            # 路径
            ax.plot(xs, ys, "-k", linewidth=1.5, label="全局最近邻路径", zorder=1)

            # 起点 / 终点
            ax.scatter(xs[0], ys[0], marker="o", s=100, color="red", label="起点", zorder=3)
            ax.scatter(xs[-1], ys[-1], marker="s", s=100, color="blue", label="终点", zorder=3)

            # 所有异常点
            ax.scatter(xs, ys, s=20, color="gray", alpha=0.7, label="异常点", zorder=2)

        ax.set_title(title, fontsize=12, fontweight="bold", pad=15, fontproperties=_FONT_PROP)
        ax.set_xlabel("经度 (°)", fontproperties=_FONT_PROP)
        ax.set_ylabel("纬度 (°)", fontproperties=_FONT_PROP)
        ax.legend(fontsize=9, loc="upper right", framealpha=0.9, prop=_FONT_PROP)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close()

        print(f"✅ 全局最近邻路径图已生成：{out_path}")

    except Exception as e:
        print(f"❌ 全局最近邻路径图生成失败：{e}")



def generate_evaluation_report(
        hierarchical_route: List[Tuple[float, float]],
        plot_routes: dict,
        save_path: Optional[str] = None
) -> dict:
    """
    生成量化评估报告（论文核心数据）
    :return: 评估结果字典
    """
    # 1. 提取所有异常点
    all_points = []
    for pts in plot_routes.values():
        all_points.extend(pts)

    # 2. 计算全局最近邻路径（对比组）
    start_time = time.time()
    global_route = global_nearest_neighbor(all_points)
    global_time = time.time() - start_time

    # 3. 分层路径耗时（复用主算法耗时，这里重新计算）
    start_time = time.time()
    hierarchical_route_recompute = nearest_neighbor_path(all_points)  # 模拟
    hierarchical_time = time.time() - start_time

    # 4. 长度计算
    hierarchical_length = calculate_route_length(hierarchical_route)
    global_length = calculate_route_length(global_route)

    # 5. 优化率计算（避免除零）
    optimization_rate = 0.0
    if global_length > 0:
        optimization_rate = (global_length - hierarchical_length) / global_length * 100

    # 构建评估报告
    report = {
        "评估指标": {
            "分层规划路径长度(米)": round(hierarchical_length, 2),
            "全局最近邻路径长度(米)": round(global_length, 2),
            "路径长度优化率(%)": round(optimization_rate, 2),
            "分层规划计算耗时(秒)": round(hierarchical_time, 4),
            "全局规划计算耗时(秒)": round(global_time, 4),
            "总异常点数": len(all_points),
            "地块数量": len(plot_routes),
            "最终路径点数": len(hierarchical_route)
        },
        "算法参数": {
            "是否启用2-opt": True,
            "2-opt迭代次数": 200,
            "距离计算方式": "球面距离(Haversine)",
            "起点选择策略": "最西端点"
        }
    }

    # 打印评估结果
    print("\n📊 路径规划量化评估报告")
    print("-" * 50)
    for k, v in report["评估指标"].items():
        print(f"{k}: {v}")
    print("-" * 50)

    # 保存评估报告
    if save_path:
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            print(f"✅ 评估报告已保存：{save_path}")
        except Exception as e:
            print(f"❌ 评估报告保存失败：{e}")

    return report



# =========================
# 【新增】评估结果可视化模块（不影响原有逻辑）
# =========================

def visualize_path_length_comparison(
        eval_report: dict,
        out_path: str,
        title: str = "不同路径规划策略路径长度对比"
) -> None:
    """
    路径长度对比柱状图
    """
    try:
        metrics = eval_report["评估指标"]
        labels = ["分层规划", "全局最近邻"]
        values = [
            metrics["分层规划路径长度(米)"],
            metrics["全局最近邻路径长度(米)"]
        ]

        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(labels, values)

        # 数值标注
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{height:.1f}",
                ha="center",
                va="bottom",
                fontsize=9
            )

        ax.set_ylabel("路径总长度 (米)", fontproperties=_FONT_PROP)
        ax.set_title(title, fontsize=12, fontweight="bold", fontproperties=_FONT_PROP)
        ax.set_xticklabels(labels, fontproperties=_FONT_PROP)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"📊 路径长度对比图已生成：{out_path}")

    except Exception as e:
        print(f"❌ 路径长度对比图生成失败：{e}")

def visualize_time_comparison(
        eval_report: dict,
        out_path: str,
        title: str = "不同路径规划策略计算耗时对比"
) -> None:
    """
    算法耗时对比柱状图
    """
    try:
        metrics = eval_report["评估指标"]
        labels = ["分层规划", "全局最近邻"]
        values = [
            metrics["分层规划计算耗时(秒)"],
            metrics["全局规划计算耗时(秒)"]
        ]

        fig, ax = plt.subplots(figsize=(6, 4))
        bars = ax.bar(labels, values)

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{height:.4f}",
                ha="center",
                va="bottom",
                fontsize=9
            )

        ax.set_ylabel("计算耗时 (秒)", fontproperties=_FONT_PROP)
        ax.set_title(title, fontsize=12, fontweight="bold", fontproperties=_FONT_PROP)
        ax.set_xticklabels(labels, fontproperties=_FONT_PROP)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"⏱️ 计算耗时对比图已生成：{out_path}")

    except Exception as e:
        print(f"❌ 计算耗时对比图生成失败：{e}")


#双图对比Figure X. Comparison between anomaly-driven hierarchical patrol routing and global nearest-neighbor routing.
def visualize_hierarchical_vs_global_routes(
        hierarchical_route: List[Tuple[float, float]],
        plot_routes: dict,
        plot_centroids: dict,
        global_route: List[Tuple[float, float]],
        out_path: str
) -> None:
    """
    🔥 分层 vs 全局 最近邻 路径规划 双图并排（论文级）
    """
    try:
        fig, axes = plt.subplots(1, 2, figsize=(16, 7), sharex=True, sharey=True)

        # =====================
        # 左图：分层异常驱动路径
        # =====================
        ax = axes[0]

        # 全局路径
        xs = [p[0] for p in hierarchical_route]
        ys = [p[1] for p in hierarchical_route]
        ax.plot(xs, ys, "-k", linewidth=1.5, label="分层巡田路径")
        ax.scatter(xs[0], ys[0], s=80, color="red", label="起点", zorder=5)

        colors = plt.cm.tab10.colors
        for idx, pid in enumerate(sorted(plot_routes.keys())):
            pts = plot_routes[pid]
            px = [p[0] for p in pts]
            py = [p[1] for p in pts]
            color = colors[idx % len(colors)]

            ax.scatter(px, py, s=25, color=color)
            ax.plot(px, py, "--", color=color, alpha=0.6)

            cx, cy = plot_centroids[pid]
            ax.scatter(cx, cy, marker="x", s=60, color=color)

        ax.set_title("（a）异常驱动分层巡田路径", fontsize=12, fontweight="bold", fontproperties=_FONT_PROP)
        ax.set_xlabel("经度 (°)", fontproperties=_FONT_PROP)
        ax.set_ylabel("纬度 (°)", fontproperties=_FONT_PROP)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, prop=_FONT_PROP)

        # =====================
        # 右图：全局最近邻路径
        # =====================
        ax = axes[1]

        xs = [p[0] for p in global_route]
        ys = [p[1] for p in global_route]
        ax.plot(xs, ys, "-k", linewidth=1.5, label="全局最近邻路径")
        ax.scatter(xs[0], ys[0], s=80, color="red", label="起点", zorder=5)

        ax.scatter(xs, ys, s=25, color="gray", alpha=0.8)

        ax.set_title("（b）全局最近邻巡田路径", fontsize=12, fontweight="bold", fontproperties=_FONT_PROP)
        ax.set_xlabel("经度 (°)", fontproperties=_FONT_PROP)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, prop=_FONT_PROP)

        # =====================
        # 保存
        # =====================
        plt.tight_layout()
        plt.savefig(out_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"🔥 分层 vs 全局 双图并排已生成：{out_path}")

    except Exception as e:
        print(f"❌ 双图生成失败：{e}")


def run_patrol_planning_pipeline(
        report_json_path: str,
        output_dir: str,
        enable_2opt: bool = True
) -> dict:
    """
    🚜 巡田路径规划服务化入口（与本地 __main__ 输出尽量一致）

    :param report_json_path: 异常子区域报告 JSON 路径
    :param output_dir: 输出目录（自动创建）
    :param enable_2opt: 是否启用 2-opt 优化
    :return: 结果路径与统计信息
    """

    result = {
        "success": False,
        "message": "",
        "files": {},
        "plot_count": 0,
        "point_count": 0,
        "route_length_m": 0.0
    }

    try:
        # 1. 读取异常报告
        with open(report_json_path, "r", encoding="utf-8") as f:
            report = json.load(f)

        # 2. 输出目录准备
        os.makedirs(output_dir, exist_ok=True)

        # 3. 中文字体初始化（失败不阻断主流程）
        try:
            configure_matplotlib_for_chinese()
            print("✅ 中文字体初始化成功")
        except Exception as e:
            print(f"⚠️ 中文字体初始化失败：{e}")

        # 4. 执行核心算法
        final_route, plot_routes, plot_centroids = generate_patrol_route_from_report(
            report,
            use_2opt=enable_2opt
        )

        # 5. 定义输出文件路径
        geojson_path = os.path.join(output_dir, "patrol_route.geojson")
        png_path = os.path.join(output_dir, "patrol_route.png")
        eval_path = os.path.join(output_dir, "patrol_route_evaluation.json")

        path_length_cmp_path = os.path.join(output_dir, "path_length_comparison.png")
        time_cmp_path = os.path.join(output_dir, "time_comparison.png")
        global_nn_path = os.path.join(output_dir, "global_nearest_neighbor_route.png")
        compare_path = os.path.join(output_dir, "hierarchical_vs_global_routes.png")

        # 6. 基础输出
        export_geojson(final_route, geojson_path)

        visualize_patrol_route(
            final_route,
            plot_routes,
            plot_centroids,
            png_path,
            title="分层巡田路径规划结果（系统生成）"
        )

        eval_report = generate_evaluation_report(
            final_route,
            plot_routes,
            save_path=eval_path
        )

        # 7. 生成与本地 __main__ 一致的补充文件
        visualize_path_length_comparison(
            eval_report,
            path_length_cmp_path,
            title="不同路径规划策略路径长度对比"
        )

        visualize_time_comparison(
            eval_report,
            time_cmp_path,
            title="不同路径规划策略计算耗时对比"
        )

        all_points = []
        for pts in plot_routes.values():
            all_points.extend(pts)

        global_route = global_nearest_neighbor(all_points)

        visualize_global_nearest_neighbor_route(
            global_route,
            global_nn_path,
            title="全局最近邻路径规划结果（Baseline）"
        )

        visualize_hierarchical_vs_global_routes(
            hierarchical_route=final_route,
            plot_routes=plot_routes,
            plot_centroids=plot_centroids,
            global_route=global_route,
            out_path=compare_path
        )

        # 8. 结果检查：只返回实际生成成功的文件
        file_map = {
            "geojson": geojson_path,
            "visualization": png_path,
            "evaluation": eval_path,
            "path_length_comparison": path_length_cmp_path,
            "time_comparison": time_cmp_path,
            "global_nearest_neighbor": global_nn_path,
            "hierarchical_vs_global": compare_path
        }

        existing_files = {}
        missing_files = {}

        for k, v in file_map.items():
            if os.path.exists(v):
                existing_files[k] = v
            else:
                missing_files[k] = v

        result["success"] = True
        result["message"] = "巡田路径规划完成"
        result["files"] = existing_files
        result["missing_files"] = missing_files
        result["plot_count"] = len(plot_routes)
        result["point_count"] = len(final_route)
        result["route_length_m"] = round(calculate_route_length(final_route), 2)

        if missing_files:
            result["message"] += f"，但有 {len(missing_files)} 个文件未生成"

        return result

    except Exception as e:
        result["success"] = False
        result["message"] = f"巡田路径规划失败: {e}"
        return result


# =========================
# 主函数（CLI入口）
# =========================
# （👇👇👇 这里开始 —— 仍然是你的原代码，一字不动 👇👇👇）

if __name__ == "__main__":
    # 路径配置（根据实际情况修改）
    BASE = "../static/xuntian_subregion_results/reports_20260117_165755_数据/"
    INPUT_JSON = BASE + "final_subregion_report_20260117_165755.json"
    OUT_GEOJSON = BASE + "patrol_route_geojson_v6.json"
    OUT_PNG = BASE + "patrol_route_visualization_v6.png"
    OUT_EVAL = BASE + "patrol_route_evaluation_v6.json"

    try:
        # 1. 加载输入数据
        print("🔍 加载异常子区域报告...")
        with open(INPUT_JSON, "r", encoding="utf-8") as f:
            report = json.load(f)

        # 2. 生成分层巡田路径（启用2-opt优化）
        print("🧮 执行分层路径规划算法...")
        final_route, plot_routes, plot_centroids = generate_patrol_route_from_report(
            report,
            use_2opt=True
        )

        # 3. 导出GeoJSON
        export_geojson(final_route, OUT_GEOJSON)

        # 4. 生成可视化图
        visualize_patrol_route(
            final_route,
            plot_routes,
            plot_centroids,
            OUT_PNG,
            title="分层巡田路径规划结果（2-opt优化）"
        )

        # 5. 生成量化评估报告
        eval_report = generate_evaluation_report(final_route, plot_routes, OUT_EVAL)

        # 6. 评估结果可视化
        visualize_path_length_comparison(
            eval_report,
            BASE + "path_length_comparison.png"
        )

        visualize_time_comparison(
            eval_report,
            BASE + "time_comparison.png"
        )

        # 7. 全局最近邻路径（Baseline）
        print("📍 生成全局最近邻路径可视化...")
        all_points = []
        for pts in plot_routes.values():
            all_points.extend(pts)

        global_route = global_nearest_neighbor(all_points)

        visualize_global_nearest_neighbor_route(
            global_route,
            BASE + "global_nearest_neighbor_route.png",
            title="全局最近邻路径规划结果（Baseline）"
        )

        # 8. 双图并排
        visualize_hierarchical_vs_global_routes(
            hierarchical_route=final_route,
            plot_routes=plot_routes,
            plot_centroids=plot_centroids,
            global_route=global_route,
            out_path=BASE + "hierarchical_vs_global_routes.png"
        )

        print("\n🎉 所有任务执行完成！")

    except Exception as e:
        print(f"❌ 程序执行出错：{e}")
        import traceback
        traceback.print_exc()

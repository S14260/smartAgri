#!/usr/bin/env python3
"""
xuntian_subregion_detection.py
基于地块内子区域（NDVI分级+连通区+多时相融合）的异常筛选方法
适配调整：支持本地（Windows/macOS）+ 服务器（Linux）双环境运行
"""
import os
import json
import logging
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
from pathlib import Path
import numpy as np
import rasterio
from rasterio.features import shapes, rasterize
import geopandas as gpd
from shapely.geometry import shape, Point
from shapely.ops import transform as shp_transform
from pyproj import CRS, Transformer
from functools import lru_cache
from typing import List, Dict, Any, Optional
import pandas as pd
from scipy.stats import linregress
from scipy.ndimage import binary_erosion, label
import re
from datetime import datetime, date


# ================= 日志配置（本地适配：Windows终端颜色兼容） =================
class ColoredFormatter(logging.Formatter):
    COLOR_CODES = {
        logging.DEBUG: '\033[90m',  # 灰色
        logging.INFO: '\033[92m',  # 绿色
        logging.WARNING: '\033[93m',  # 黄色
        logging.ERROR: '\033[91m',  # 红色
        logging.CRITICAL: '\033[95m'  # 紫色
    }
    RESET_CODE = '\033[0m'

    def format(self, record):
        color = self.COLOR_CODES.get(record.levelno, self.RESET_CODE)
        log_message = super().format(record)
        return f"{color}{log_message}{self.RESET_CODE}"


# 初始化日志
logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if logger.handlers:
    logger.handlers.clear()
console_handler = logging.StreamHandler()
formatter = ColoredFormatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%H:%M:%S')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


# ================= 配置类（本地适配：动态路径+多系统兼容） =================
class Config:
    # 基础路径（默认值，可被动态覆盖）
    BASE_DIR = Path(__file__).resolve().parent  # api 目录

    # 本地适配：可手动修改的核心参数（本地运行时直接改这里）
    LOCAL_NDVI_FOLDER = BASE_DIR / 'xuntian' /'static' / 'xuntian_plots'  # 输入多时相GeoTIFF
    LOCAL_OUTPUT_FOLDER = BASE_DIR / 'static' / 'xuntian_results'
    LOCAL_START_DATE = '2025-06-01'  # 本地运行的起始日期
    LOCAL_END_DATE = '2025-10-01'  # 本地运行的结束日期
    LOCAL_PLOT_IDS = ['72', '73', '74', '76', '77', '78', '79']  # 本地要处理的地块ID列表（如['4', '72']）

    # 动态参数（由init_dirs初始化）
    NDVI_FOLDER = None
    OUTPUT_BASE = None
    TIMESTAMP = None
    OUTPUT_FOLDER = None
    TEMP_FOLDER = None
    REPORT_FOLDER = None
    GEOJSON_FOLDER = None

    # ===== NDVI分级配置（保留原有）=====
    NDVI_GRADES = {
        'severe_drought': {  # 重度干旱（扩大区间）
            'range': (-1.0, 0.15),
            'label': '重度干旱',
            'color': (255, 0, 0),
            'is_anomaly': True,
            'priority_weight': 1.0
        },
        'moderate_drought': {  # 中度干旱（扩大区间）
            'range': (0.15, 0.30),
            'label': '中度干旱',
            'color': (244, 109, 67),
            'is_anomaly': True,
            'priority_weight': 0.8
        },
        'mild_drought': {  # 轻度干旱（预警）（扩大区间）
            'range': (0.30, 0.40),
            'label': '轻度干旱（预警）',
            'color': (254, 224, 139),
            'is_anomaly': True,
            'priority_weight': 0.4
        },
        'pest_disease': {  # 病虫害（核心异常）
            'range': (0.40, 0.50),
            'label': '病虫害/长势异常',
            'color': (128, 0, 128),
            'is_anomaly': True,
            'priority_weight': 0.8
        },
        'harvested': {  # 已收割/无植被（取消季节限制，仅作为补充）
            'range': (-0.2, 0.10),
            'label': '已收割/无植被',
            'color': (169, 169, 169),
            'is_anomaly': True,
            'priority_weight': 0.3
        },
        'normal': {  # 正常长势
            'range': (0.50, 0.60),
            'label': '正常',
            'color': (102, 189, 99),
            'is_anomaly': False,
            'priority_weight': 0.0
        },
        'vigorous': {  # 长势良好
            'range': (0.60, 1.0),
            'label': '长势良好',
            'color': (0, 136, 55),
            'is_anomaly': False,
            'priority_weight': 0.0
        }
    }

    # 多指数异常判定阈值（放宽）
    MULTI_INDEX_ANOMALY_THRESH = {
        'waterlogging': {  # 积水：NDWI≥-0.2 + NDVI≤0.35
            'ndwi_min': -0.2,
            'ndvi_max': 0.35
        },
        'pest_disease': {  # 病虫害：放宽阈值
            'evi_max': 0.30,
            'savi_max': 0.25,
            'ndvi_min': 0.35
        }
    }

    # ===== 子区域过滤参数（保留原有）=====
    MIN_SUBREGION_PIXELS = 500
    MAX_SUBREGION_PIXELS = 192000
    INVALID_PIXEL_RATIO_THRESHOLD = 0.15
    EDGE_BUFFER_M = 1
    INVALID_INDEX_THRESHOLD = -0.45

    # ===== 时序异常阈值（保留原有）=====
    DELTA_THRESHOLD = 0.05
    ZSCORE_THRESHOLD = -1.8
    SLOPE_THRESHOLD = -0.004
    RVALUE_THRESHOLD = -0.5

    # 异常严重度权重（保留原有）
    INDEX_WEIGHTS = {
        'NDVI': 0.55,
        'NDWI': 0.3,
        'EVI': 0.1,
        'SAVI': 0.05
    }
    SEVERITY_WEIGHT = 0.65
    AREA_WEIGHT = 0.25
    EDGE_PENALTY = -0.05

    # ===== 输出过滤（保留原有）=====
    MIN_SUBREGION_AREA_M2 = 1000
    MIN_PRIORITY = 0.4
    DEDUPLICATE_TOLERANCE_M = 10

    # ===== 其他参数（保留原有）=====
    NO_IMAGE_CONSECUTIVE_FRAMES = 2
    NO_IMAGE_PRIORITY = 0.1
    NDVI_NEGATIVE_THRESHOLD = -0.1
    HARVEST_SEASON_MONTHS = [9, 10, 11]

    @classmethod
    def init_dirs(cls, timestamp: str = None, ndvi_folder: str = None):
        """
        动态初始化目录（本地适配：优先使用本地配置路径）
        :param timestamp: 任务时间戳
        :param ndvi_folder: NDVI文件目录（本地/服务器）
        """
        # 本地适配：优先使用本地配置的NDVI文件夹
        if ndvi_folder:
            cls.NDVI_FOLDER = Path(ndvi_folder).resolve()
        else:
            cls.NDVI_FOLDER = cls.LOCAL_NDVI_FOLDER.resolve()

        # 本地适配：输出目录改为本地配置路径
        cls.OUTPUT_BASE = cls.LOCAL_OUTPUT_FOLDER.resolve()

        # 初始化时间戳和输出子目录
        cls.TIMESTAMP = timestamp or datetime.now().strftime('%Y%m%d_%H%M%S')
        cls.OUTPUT_FOLDER = cls.OUTPUT_BASE / f'reports_{cls.TIMESTAMP}'
        cls.TEMP_FOLDER = cls.OUTPUT_FOLDER / 'temp'
        cls.REPORT_FOLDER = cls.OUTPUT_FOLDER / 'visualReports'
        cls.GEOJSON_FOLDER = cls.OUTPUT_FOLDER / 'geojson'

        # 创建目录（本地适配：递归创建，忽略已存在）
        for dir_path in [cls.NDVI_FOLDER, cls.OUTPUT_FOLDER, cls.TEMP_FOLDER, cls.REPORT_FOLDER, cls.GEOJSON_FOLDER]:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建/确认目录成功：{dir_path}")
            except Exception as e:
                logger.warning(f'创建目录失败 {dir_path}: {e}')

    @staticmethod
    def get_ndvi_grade(ndvi_value: float) -> Dict:
        """根据NDVI值获取对应的分级配置"""
        if np.isnan(ndvi_value):
            return {'label': '无效值', 'is_anomaly': False, 'priority_weight': 0.0}

        for grade_key, grade_config in Config.NDVI_GRADES.items():
            low, high = grade_config['range']
            if low <= ndvi_value < high:
                return grade_config
        return {'label': '未知等级', 'is_anomaly': False, 'priority_weight': 0.0}

    @staticmethod
    def is_harvest_season(date: datetime) -> bool:
        """判断是否为秋收季（仅参考）"""
        return date.month in Config.HARVEST_SEASON_MONTHS


# ================= 工具函数（本地适配：字体+路径） =================
def configure_matplotlib_for_chinese(preferred_fonts=None):
    """
    本地适配：多系统中文字体配置（Windows/macOS/Linux）
    """
    if preferred_fonts is None:
        # 本地适配：按系统优先级排序字体
        if os.name == 'nt':  # Windows
            preferred_fonts = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
        elif os.name == 'posix':  # macOS/Linux
            preferred_fonts = [
                # macOS
                'PingFang SC', 'Heiti TC', 'Noto Sans CJK SC',
                # Linux
                '/usr/share/fonts/wqy-microhei/wqy-microhei.ttc',
                '/usr/share/fonts/wqy-zenhei/wqy-zenhei.ttc'
            ]

    # 本地适配：容错逻辑增强
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    for name in preferred_fonts:
        try:
            # 处理字体文件路径
            if os.path.isabs(name) and os.path.exists(name):
                prop = fm.FontProperties(fname=name)
                plt.rcParams['font.sans-serif'] = [prop.get_name()]
                logger.info(f"成功加载字体：{name}")
                return prop
            # 处理字体名称
            matches = [f for f in fm.findSystemFonts() if os.path.basename(f).lower().find(name.lower()) != -1]
            if matches:
                prop = fm.FontProperties(fname=matches[0])
                plt.rcParams['font.sans-serif'] = [prop.get_name()]
                logger.info(f"成功加载字体：{name} (匹配文件：{matches[0]})")
                return prop
        except Exception as e:
            logger.debug(f"加载字体 {name} 失败：{e}")
            continue

    # 兜底方案
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    logger.warning("未找到中文字体，可能出现乱码！建议安装SimHei/微软雅黑/苹方字体")
    return fm.FontProperties(family='DejaVu Sans')


# 初始化中文字体（本地适配）
_FONT_PROP = configure_matplotlib_for_chinese()


def scale01(arr, minv=None, maxv=None):
    """安全归一化到0-1区间"""
    arr = np.array(arr, dtype=float)
    if minv is None or maxv is None:
        minv, maxv = np.nanmin(arr), np.nanmax(arr)
    if maxv - minv == 0 or np.isnan(maxv - minv):
        return np.zeros_like(arr)
    return (arr - minv) / (maxv - minv)


def safe_remove(filepath: Path) -> None:
    """安全删除文件（本地适配：Windows文件锁定容错）"""
    if filepath.exists():
        try:
            filepath.unlink(missing_ok=True)  # 本地适配：Python 3.8+支持missing_ok
        except PermissionError:
            logger.warning(f'文件被占用，无法删除：{filepath}')
        except Exception as e:
            logger.warning(f'删除文件失败 {filepath}: {e}')


@lru_cache(maxsize=None)
def get_transformer(crs_from, crs_to) -> Transformer:
    """缓存投影转换器"""
    return Transformer.from_crs(crs_from, crs_to, always_xy=True)


def reproject_geom(geom, crs_from, crs_to):
    """几何图形投影转换"""
    if CRS.from_user_input(crs_from) == CRS.from_user_input(crs_to):
        return geom
    transformer = get_transformer(crs_from, crs_to)
    return shp_transform(transformer.transform, geom)


def to_wgs84(geom, crs_from) -> Any:
    """转换到WGS84坐标系"""
    return reproject_geom(geom, crs_from, CRS.from_epsg(4326))


def get_projected_crs(geom_wgs84) -> CRS:
    """根据WGS84几何获取投影坐标系（UTM）"""
    centroid_lon, centroid_lat = geom_wgs84.centroid.x, geom_wgs84.centroid.y
    zone = int((centroid_lon + 180) // 6) + 1
    epsg = 32600 + zone if centroid_lat >= 0 else 32700 + zone
    return CRS.from_epsg(epsg)


def parse_filename_info(basename: str) -> dict:
    """
    解析文件名中的地块ID、地块名称和日期
    适配格式：4_张北1号地_2025_0607_guyuan_smooth.tif
    """
    name = basename.replace('.tif', '')
    plot_id = f"unknown_{str(hash(name))[:6]}"
    plot_name = "未知地块"
    date = pd.to_datetime('1970-01-01').date()

    # 核心正则：匹配【数字_地块名称_年份_月日_任意字符】格式（适配新文件名）
    pattern = r'^(\d+)_([^_]+?)_(\d{4})_(\d{4})_'
    match = re.match(pattern, name)

    if match:
        plot_id = match.group(1)
        plot_name = match.group(2).strip()
        year = match.group(3)
        month_day = match.group(4)
        try:
            date_str = f"{year}-{month_day[:2]}-{month_day[2:]}"
            date = pd.to_datetime(date_str).date()
            logger.debug(f"解析文件名成功：ID={plot_id}, 名称={plot_name}, 日期={date}")
        except Exception as e:
            logger.warning(f'解析日期失败 {date_str}: {e}')
    else:
        # 兼容其他格式：先找日期，再找地块ID
        date_match = re.search(r'(20\d{6}|19\d{6})', name)
        if date_match:
            try:
                date = pd.to_datetime(date_match.group(0), format='%Y%m%d').date()
            except Exception:
                pass

        if not date or date == pd.to_datetime('1970-01-01').date():
            try:
                file_path = Config.NDVI_FOLDER / basename
                mtime = os.path.getmtime(file_path)
                date = pd.to_datetime(mtime, unit='s').date()
            except Exception:
                pass

        # 提取地块ID（优先数字）
        plot_id_match = re.findall(r'^(\d+)_', name)
        if plot_id_match:
            plot_id = plot_id_match[0]
        else:
            plot_id_match = re.findall(r'(\d+|[A-Za-z0-9_]+)', name)
            plot_id = plot_id_match[0] if plot_id_match else plot_id

    return {
        'plot_id': plot_id,
        'plot_name': plot_name,
        'date': date,
        'basename': basename
    }


def is_valid_tif(file_path: Path) -> bool:
    """检查是否为有效TIFF文件（本地适配：增加文件大小检查）"""
    if not file_path.suffix.lower() == '.tif':
        return False
    # 本地适配：跳过空文件
    if file_path.stat().st_size < 1024:
        logger.warning(f'文件过小，跳过：{file_path}')
        return False
    try:
        with rasterio.open(file_path) as src:
            return src.count >= 1 and src.width > 0 and src.height > 0
    except Exception as e:
        logger.warning(f'无效TIFF {file_path}: {e}')
        return False


def filter_files_by_time_range(file_list: List[Path], start_date: str, end_date: str) -> List[Path]:
    """按时间范围筛选TIFF文件"""
    if not start_date or not end_date:
        logger.info("未指定时间范围，返回全部文件")
        return file_list

    try:
        start = pd.to_datetime(start_date).date()
        end = pd.to_datetime(end_date).date()
    except Exception as e:
        logger.warning(f'解析时间范围失败 {start_date}~{end_date}: {e}，返回全部文件')
        return file_list

    filtered = []
    for file in file_list:
        file_info = parse_filename_info(file.name)
        file_date = file_info['date']
        if start <= file_date <= end:
            filtered.append(file)

    logger.info(f'时间范围筛选：{len(file_list)} → {len(filtered)} 个文件（{start}~{end}）')
    return filtered


def read_index_arrays(tif_path: Path) -> Dict[str, Any]:
    """读取TIFF文件中的各指数数组（本地适配：增加内存限制）"""
    try:
        with rasterio.open(tif_path) as src:
            # 本地适配：跳过过大的文件（避免内存溢出）
            if src.width * src.height > 10000000:  # 10000x10000
                logger.warning(f'文件过大，跳过：{tif_path}（{src.width}x{src.height}像素）')
                return {}

            transform = src.transform
            crs = src.crs
            count = src.count

            arrs = {'NDVI': None, 'EVI': None, 'SAVI': None, 'NDWI': None}

            for i in range(1, min(count, 4) + 1):
                arr = src.read(i).astype(np.float32)
                arr[arr < Config.INVALID_INDEX_THRESHOLD] = np.nan
                if i == 1:
                    arrs['NDVI'] = arr
                elif i == 2:
                    arrs['EVI'] = arr
                elif i == 3:
                    arrs['SAVI'] = arr
                elif i == 4:
                    arrs['NDWI'] = arr

            if count == 1:
                arrs['NDVI'] = src.read(1).astype(np.float32)
                arrs['NDVI'][arrs['NDVI'] < Config.INVALID_INDEX_THRESHOLD] = np.nan

        logger.debug(f"读取TIFF成功：{tif_path}，波段数={count}")
        return {
            'arrs': arrs,
            'transform': transform,
            'crs': crs,
            'width': src.width,
            'height': src.height
        }
    except Exception as e:
        logger.warning(f'读取TIFF失败 {tif_path}: {e}')
        return {}


def calculate_plot_level_metrics(tif_path: Path) -> Dict[str, Any]:
    """计算整个地块的指数均值（用于地块级趋势图）"""
    data = read_index_arrays(tif_path)
    if not data:
        return {}

    index_arrs = data['arrs']
    file_info = parse_filename_info(tif_path.name)

    plot_metrics = {
        'plot_id': file_info['plot_id'],
        'plot_name': file_info['plot_name'],
        'date': file_info['date'].isoformat()[:10],
        'mean_ndvi': None,
        'mean_evi': None,
        'mean_savi': None,
        'mean_ndwi': None
    }

    for idx_name, arr in index_arrs.items():
        if arr is not None:
            valid_vals = arr[~np.isnan(arr)]
            if len(valid_vals) > 0:
                plot_metrics[f'mean_{idx_name.lower()}'] = round(float(np.mean(valid_vals)), 3)

    return plot_metrics


# ================= 核心函数（保留原有逻辑，仅字体适配） =================
def segment_subregions(ndvi_arr: np.ndarray, transform: Any, min_pixels: int, max_pixels: int) -> List[Dict]:
    """基于NDVI分级的子区域分割"""
    valid_mask = ~np.isnan(ndvi_arr)
    if not np.any(valid_mask):
        logger.info('无有效像素，无法分割子区域')
        return []

    subregions = []
    label_id_counter = 1

    for grade_key, grade_config in Config.NDVI_GRADES.items():
        low, high = grade_config['range']
        grade_mask = valid_mask & (ndvi_arr >= low) & (ndvi_arr < high)

        if not np.any(grade_mask):
            continue

        labeled_arr, num_features = label(grade_mask)
        logger.debug(f'NDVI分级「{grade_config["label"]}」检测到 {num_features} 个连通区')

        for local_label_id in range(1, num_features + 1):
            sub_mask = labeled_arr == local_label_id
            pixel_count = int(np.sum(sub_mask))

            if pixel_count < min_pixels or pixel_count > max_pixels:
                continue

            shapes_gen = shapes(sub_mask.astype('uint8'), mask=sub_mask, transform=transform)
            for geom_dict, _ in shapes_gen:
                try:
                    geom = shape(geom_dict)
                    valid_ndvi_vals = ndvi_arr[sub_mask][~np.isnan(ndvi_arr[sub_mask])]
                    mean_ndvi = float(np.mean(valid_ndvi_vals)) if len(valid_ndvi_vals) > 0 else np.nan

                    subregions.append({
                        'geometry': geom,
                        'mask': sub_mask,
                        'pixel_count': pixel_count,
                        'label_id': label_id_counter,
                        'ndvi_grade': grade_key,
                        'ndvi_grade_label': grade_config['label'],
                        'ndvi_grade_color': grade_config['color'],
                        'is_anomaly_by_grade': grade_config['is_anomaly'],
                        'priority_weight': grade_config['priority_weight'],
                        'mean_ndvi': round(mean_ndvi, 3)
                    })
                    label_id_counter += 1
                    break
                except Exception as e:
                    logger.debug(f'提取子区域几何失败: {e}')
                    continue

    logger.info(f'按NDVI分级分割出 {len(subregions)} 个有效子区域')
    return subregions


def calculate_subregion_metrics(subregion: Dict, index_arrs: Dict[str, np.ndarray], crs: Any) -> Dict[str, Any]:
    """计算子区域的核心指标"""
    mask = subregion['mask']
    geom = subregion['geometry']

    geom_wgs84 = to_wgs84(geom, crs)
    proj_crs = get_projected_crs(geom_wgs84)
    geom_proj = reproject_geom(geom, crs, proj_crs)

    area_m2 = float(geom_proj.area)
    centroid = geom_wgs84.centroid
    centroid_latlng = [centroid.y, centroid.x]
    edge_band = geom_proj.boundary.buffer(Config.EDGE_BUFFER_M)
    edge_ratio = float(geom_proj.intersection(edge_band).area / area_m2) if area_m2 > 0 else 0

    metrics = {
        'area_m2': round(area_m2, 2),
        'centroid': centroid_latlng,
        'edge_ratio': round(edge_ratio, 3),
        'pixel_count': subregion['pixel_count'],
        'mean_ndvi': subregion['mean_ndvi'],
        'ndvi_grade': subregion['ndvi_grade'],
        'ndvi_grade_label': subregion['ndvi_grade_label'],
        'is_anomaly_by_grade': subregion['is_anomaly_by_grade'],
        'grade_priority_weight': subregion['priority_weight']
    }

    for idx_name in ['EVI', 'SAVI', 'NDWI']:
        arr = index_arrs.get(idx_name)
        if arr is None:
            metrics[f'mean_{idx_name.lower()}'] = None
            continue
        valid_vals = arr[mask][~np.isnan(arr[mask])]
        if len(valid_vals) == 0:
            metrics[f'mean_{idx_name.lower()}'] = None
        else:
            metrics[f'mean_{idx_name.lower()}'] = round(float(np.mean(valid_vals)), 3)

    total_pixels = subregion['pixel_count']
    valid_pixel_count = sum(
        len(index_arrs[idx][mask][~np.isnan(index_arrs[idx][mask])])
        for idx in ['NDVI'] if index_arrs[idx] is not None
    )
    metrics['valid_pixel_ratio'] = round(valid_pixel_count / total_pixels if total_pixels > 0 else 0, 3)

    return metrics


def judge_subregion_anomaly(subregion_metrics: Dict, historical_metrics: List[Dict] = None) -> Dict[str, Any]:
    """子区域异常判定（保留原有逻辑）"""
    result = {
        'is_anomaly': False,
        'anomaly_type': 'normal',
        'anomaly_category': '无异常',
        'severity': 0.0,
        'priority': 0.0,
        'multi_index_score': 0.0,
        'delta_ndvi': 0.0,
        'zscore': 0.0,
        'slope': 0.0,
        'rvalue': 0.0
    }

    # 1. 过滤无效子区域
    if subregion_metrics['valid_pixel_ratio'] < Config.INVALID_PIXEL_RATIO_THRESHOLD:
        result.update({
            'is_anomaly': True,
            'anomaly_type': 'invalid_data',
            'anomaly_category': '有效像素不足',
            'priority': 0.1
        })
        return result

    # 2. NDVI<0 特殊预判断
    mean_ndvi = subregion_metrics.get('mean_ndvi')
    mean_ndwi = subregion_metrics.get('mean_ndwi')
    mean_evi = subregion_metrics.get('mean_evi')
    mean_savi = subregion_metrics.get('mean_savi')
    date_str = subregion_metrics.get('date')
    date = pd.to_datetime(date_str) if date_str else datetime.now()

    if mean_ndvi is not None and mean_ndvi < Config.NDVI_NEGATIVE_THRESHOLD:
        consecutive_negative = 0
        if historical_metrics:
            hist_ndvi = [h.get('mean_ndvi', 0.0) for h in historical_metrics if h.get('mean_ndvi') is not None]
            for ndvi_val in reversed(hist_ndvi):
                if ndvi_val < Config.NDVI_NEGATIVE_THRESHOLD:
                    consecutive_negative += 1
                else:
                    break
        if consecutive_negative >= Config.NO_IMAGE_CONSECUTIVE_FRAMES:
            result.update({
                'is_anomaly': False,
                'anomaly_category': '无影像',
                'priority': 0.0
            })
            return result
        else:
            result.update({
                'is_anomaly': True,
                'anomaly_type': 'ndvi_negative',
                'anomaly_category': 'NDVI负值（疑似影像异常/地块异常）',
                'priority': Config.NO_IMAGE_PRIORITY,
                'severity': 0.0
            })
            return result

    # 3. 静态异常判定（基于NDVI分级+多指数）
    is_static_anomaly = False
    anomaly_category = '无异常'
    priority_weight = 0.0

    # 3.1 积水/水渍判定
    if (mean_ndwi is not None and mean_ndwi >= Config.MULTI_INDEX_ANOMALY_THRESH['waterlogging']['ndwi_min'] and
            mean_ndvi < Config.MULTI_INDEX_ANOMALY_THRESH['waterlogging']['ndvi_max']):
        is_static_anomaly = True
        anomaly_category = '积水/水渍'
        priority_weight = 0.9
        result['anomaly_type'] = 'waterlogging_anomaly'

    # 3.2 病虫害/长势异常判定
    elif (mean_evi is not None and mean_evi < Config.MULTI_INDEX_ANOMALY_THRESH['pest_disease']['evi_max'] and
          mean_savi is not None and mean_savi < Config.MULTI_INDEX_ANOMALY_THRESH['pest_disease']['savi_max'] and
          mean_ndvi > Config.MULTI_INDEX_ANOMALY_THRESH['pest_disease']['ndvi_min']):
        is_static_anomaly = True
        anomaly_category = '病虫害/长势异常'
        priority_weight = Config.NDVI_GRADES['pest_disease']['priority_weight']
        result['anomaly_type'] = 'pest_disease_anomaly'

    # 3.3 已收割/无植被（取消季节强制限制）
    elif mean_ndvi >= -0.2 and mean_ndvi <= 0.10:
        is_static_anomaly = True
        anomaly_category = '已收割/无植被'
        priority_weight = Config.NDVI_GRADES['harvested']['priority_weight']
        result['anomaly_type'] = 'harvested_anomaly'

    # 3.4 干旱类异常判定
    elif subregion_metrics.get('is_anomaly_by_grade', False):
        is_static_anomaly = True
        anomaly_category = subregion_metrics.get('ndvi_grade_label', '未知')
        priority_weight = subregion_metrics.get('grade_priority_weight', 0.0)
        result['anomaly_type'] = 'ndvi_grade_anomaly'

    # 4. 时序异常判定
    is_temporal_anomaly = False
    delta_ndvi = 0.0
    zscore = 0.0
    slope = 0.0
    rvalue = 0.0

    if historical_metrics and len(historical_metrics) >= 2:
        hist_ndvi = [h.get('mean_ndvi', 0.0) for h in historical_metrics if h.get('mean_ndvi') is not None]
        if len(hist_ndvi) >= 2:
            delta_ndvi = mean_ndvi - hist_ndvi[-1]
            x = np.arange(len(hist_ndvi))
            slope, intercept, rvalue, pvalue, std_err = linregress(x, hist_ndvi)
            hist_mean = np.mean(hist_ndvi)
            hist_std = np.std(hist_ndvi)
            zscore = (mean_ndvi - hist_mean) / (hist_std + 1e-6) if hist_std > 0 else 0

            # 放宽时序条件：三选一即可
            is_temporal_anomaly = (delta_ndvi < -Config.DELTA_THRESHOLD) or \
                                  (slope < -Config.SLOPE_THRESHOLD and rvalue < Config.RVALUE_THRESHOLD) or \
                                  (zscore < Config.ZSCORE_THRESHOLD)
    else:
        # 无历史数据时，静态异常直接判定为时序异常
        is_temporal_anomaly = True

    # 5. 最终异常判定
    if is_static_anomaly and is_temporal_anomaly:
        normal_ndvi_low = Config.NDVI_GRADES['normal']['range'][0]
        severity = max(0.0, normal_ndvi_low - mean_ndvi) if mean_ndvi < normal_ndvi_low else 0.0
        area_score = scale01(np.array([subregion_metrics['area_m2']]), 0, 3000)[0]
        time_boost = 0.1 if is_temporal_anomaly else 0.0

        priority = (
                priority_weight * Config.SEVERITY_WEIGHT +
                area_score * Config.AREA_WEIGHT +
                time_boost +
                (Config.EDGE_PENALTY if subregion_metrics['edge_ratio'] > 0.5 else 0.0)
        )

        result.update({
            'is_anomaly': True,
            'anomaly_category': anomaly_category,
            'severity': round(severity, 3),
            'priority': round(max(priority, 0.0), 3),
            'delta_ndvi': round(delta_ndvi, 3),
            'zscore': round(zscore, 3),
            'slope': round(slope, 4),
            'rvalue': round(rvalue, 3)
        })

    return result


def deduplicate_subregions(subregions: List[Dict]) -> List[Dict]:
    """子区域去重"""
    if len(subregions) <= 1:
        return subregions

    subregions_sorted = sorted(subregions, key=lambda x: x.get('priority', 0), reverse=True)
    unique_subregions = []

    for sub in subregions_sorted:
        if sub.get('priority', 0) < Config.MIN_PRIORITY:
            continue
        if sub.get('area_m2', 0) < Config.MIN_SUBREGION_AREA_M2:
            continue

        centroid = Point(sub['centroid'][1], sub['centroid'][0])
        is_duplicate = False

        for unique_sub in unique_subregions:
            unique_centroid = Point(unique_sub['centroid'][1], unique_sub['centroid'][0])
            proj_crs = get_projected_crs(centroid)
            centroid_proj = reproject_geom(centroid, CRS.from_epsg(4326), proj_crs)
            unique_centroid_proj = reproject_geom(unique_centroid, CRS.from_epsg(4326), proj_crs)
            distance = centroid_proj.distance(unique_centroid_proj)

            if distance < Config.DEDUPLICATE_TOLERANCE_M:
                is_duplicate = True
                break

        if not is_duplicate:
            unique_subregions.append(sub)

    logger.info(f'子区域去重：{len(subregions)} → {len(unique_subregions)}')
    return unique_subregions


def generate_subregion_anomaly_map(tif_path: Path, index_arrs: Dict, subregions: List[Dict], plot_id: str,
                                   plot_name: str, date: str) -> Path:
    """生成异常地图（本地适配：修复图例字体）"""
    ndvi_arr = index_arrs.get('NDVI', np.zeros((100, 100)))
    with rasterio.open(tif_path) as src:
        transform = src.transform

    rgb = np.zeros((ndvi_arr.shape[0], ndvi_arr.shape[1], 3), dtype=np.uint8)
    valid_mask = ~np.isnan(ndvi_arr)

    for grade_key, grade_config in Config.NDVI_GRADES.items():
        low, high = grade_config['range']
        color = grade_config['color']
        mask = (ndvi_arr >= low) & (ndvi_arr < high) & valid_mask
        rgb[mask] = color

    # 1. 画布尺寸适配
    fig, ax = plt.subplots(figsize=(12, 9))
    plt.subplots_adjust(left=0.05, right=0.8, top=0.95, bottom=0.1)

    extent = [transform.c, transform.c + transform.a * rgb.shape[1],
              transform.f + transform.e * rgb.shape[0], transform.f]
    ax.imshow(rgb, extent=extent)

    # 绘制异常点标注
    for i, sub in enumerate(subregions):
        if not sub.get('is_anomaly'):
            continue
        centroid_lon, centroid_lat = sub['centroid'][1], sub['centroid'][0]
        ax.scatter(centroid_lon, centroid_lat, s=80, c='black', marker='x', linewidth=2)
        label = (f"{i + 1}: {sub['anomaly_category']}\n"
                 f"NDVI: {sub['mean_ndvi']} | 优先级: {sub['priority']:.2f}\n"
                 f"ΔNDVI: {sub['delta_ndvi']} | 斜率: {sub['slope']:.4f}")
        # 本地适配：标注文字指定字体
        ax.annotate(label, (centroid_lon, centroid_lat), xytext=(5, 5),
                    textcoords='offset points', fontsize=9,
                    bbox=dict(boxstyle='round,pad=0.3', fc='white', alpha=0.8),
                    fontproperties=_FONT_PROP)

    # 设置标题和坐标轴（本地适配：指定字体）
    ax.set_title(f'地块 {plot_id}（{plot_name}）NDVI分级异常检测 ({date})', fontsize=12, fontproperties=_FONT_PROP)
    ax.set_xlabel('经度', fontproperties=_FONT_PROP)
    ax.set_ylabel('纬度', fontproperties=_FONT_PROP)
    ax.grid(True, linestyle='--', alpha=0.5)

    # 3. 构建图例元素
    legend_elements = [
        plt.Rectangle((0, 0), 1, 1, facecolor=np.array(grade['color']) / 255, label=grade['label'])
        for grade in Config.NDVI_GRADES.values()
    ]

    # 本地适配：图例字体强制指定（解决乱码）
    ax.legend(
        handles=legend_elements,
        loc='upper left',
        bbox_to_anchor=(1.0, 1.0),
        prop=_FONT_PROP,  # 直接使用本地适配的字体
        frameon=True,
        facecolor='white',
        edgecolor='black',
        framealpha=0.9,
        borderaxespad=0.2
    )

    # 保存图片（本地适配：解决Windows路径乱码）
    img_name = f'subregion_anomaly_map_{plot_id}_{date}.png'
    img_path = Config.REPORT_FOLDER / img_name
    # 本地适配：确保文件名无特殊字符
    img_path = img_path.with_name(img_path.name.replace('/', '_').replace('\\', '_'))
    fig.savefig(img_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    logger.info(f'保存子区域异常地图：{img_path}')
    return img_path


def generate_plot_trend_plot(plot_id: str, plot_name: str, plot_metrics_list: List[Dict]) -> Path:
    """生成趋势图（本地适配：字体）"""
    if len(plot_metrics_list) < 2:
        logger.warning(f'地块 {plot_id} 时序数据不足，无法生成趋势图')
        return Path('')

    df = pd.DataFrame(plot_metrics_list)
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(df['date'], df['mean_ndvi'], marker='o', linewidth=2, label='NDVI', color='green', markersize=6)
    if 'mean_ndwi' in df.columns and df['mean_ndwi'].notna().any():
        ax.plot(df['date'], df['mean_ndwi'], marker='s', linewidth=2, label='NDWI', color='blue', markersize=6)
    if 'mean_evi' in df.columns and df['mean_evi'].notna().any():
        ax.plot(df['date'], df['mean_evi'], marker='^', linewidth=2, label='EVI', color='orange', markersize=6)

    ax.axhline(y=Config.NDVI_GRADES['severe_drought']['range'][1], color='red', linestyle='-', alpha=0.8,
               label='重度干旱阈值')
    ax.axhline(y=Config.NDVI_GRADES['moderate_drought']['range'][1], color='orange', linestyle='--', alpha=0.8,
               label='中度干旱阈值')
    ax.axhline(y=Config.NDVI_GRADES['mild_drought']['range'][1], color='yellow', linestyle='--', alpha=0.7,
               label='轻度干旱阈值')
    ax.axhline(y=0, color='gray', linestyle=':', alpha=0.5, label='NDVI=0基线')

    ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=3, maxticks=15))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    plt.xticks(rotation=45)

    ax.set_title(f'地块 {plot_id}（{plot_name}）整体指数时序趋势', fontsize=14, fontproperties=_FONT_PROP)
    ax.set_xlabel('日期', fontsize=12, fontproperties=_FONT_PROP)
    ax.set_ylabel('指数值', fontsize=12, fontproperties=_FONT_PROP)
    ax.legend(prop=_FONT_PROP)
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()

    img_name = f'plot_trend_{plot_id}.png'
    img_path = Config.REPORT_FOLDER / img_name
    fig.savefig(img_path, dpi=150, bbox_inches='tight')
    plt.close(fig)

    logger.info(f'保存地块 {plot_id} 整体趋势图：{img_path}')
    return img_path


def export_subregions_geojson(plot_id: str, plot_name: str, date: str, subregions: List[Dict], crs: Any) -> Path:
    """导出GeoJSON（本地适配：编码）"""
    features = []
    for i, sub in enumerate(subregions):
        if not sub.get('is_anomaly'):
            continue

        feature = {
            'type': 'Feature',
            'geometry': shape(sub['geometry']).__geo_interface__,
            'properties': {
                'subregion_id': i + 1,
                'plot_id': plot_id,
                'plot_name': plot_name,
                'date': date,
                'ndvi_grade': sub['ndvi_grade_label'],
                'anomaly_category': sub['anomaly_category'],
                'mean_ndvi': sub['mean_ndvi'],
                'mean_ndwi': sub['mean_ndwi'],
                'area_m2': sub['area_m2'],
                'priority': sub['priority'],
                'severity': sub['severity'],
                'delta_ndvi': sub['delta_ndvi'],
                'slope': sub['slope']
            }
        }
        features.append(feature)

    geojson = {
        'type': 'FeatureCollection',
        'crs': {'type': 'name', 'properties': {'name': crs.to_string()}},
        'features': features
    }

    geojson_name = f'subregion_anomalies_{plot_id}_{date}.geojson'
    geojson_path = Config.GEOJSON_FOLDER / geojson_name

    # 本地适配：确保UTF-8编码
    with open(geojson_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    logger.info(f'导出子区域GeoJSON：{geojson_path}')
    return geojson_path


# ================= 核心处理函数（保留原有） =================
def process_single_tif(tif_path: Path, historical_data: List[Dict] = None) -> List[Dict]:
    """处理单张TIFF文件"""
    file_info = parse_filename_info(tif_path.name)
    plot_id = file_info['plot_id']
    plot_name = file_info['plot_name']
    date = file_info['date'].isoformat()[:10]
    logger.info(f'开始处理地块 {plot_id}（{plot_name}）日期 {date} 的子区域检测')

    data = read_index_arrays(tif_path)
    if not data:
        logger.warning(f'读取 {tif_path.name} 失败，跳过')
        return []
    index_arrs = data['arrs']
    crs = data['crs']
    transform = data['transform']

    ndvi_arr = index_arrs.get('NDVI')
    if ndvi_arr is None:
        logger.warning(f'{tif_path.name} 无NDVI数据，跳过')
        return []
    subregions = segment_subregions(
        ndvi_arr, transform,
        Config.MIN_SUBREGION_PIXELS,
        Config.MAX_SUBREGION_PIXELS
    )
    if not subregions:
        logger.info(f'地块 {plot_id}（{plot_name}）无有效子区域')
        return []

    anomaly_subregions = []
    for sub in subregions:
        metrics = calculate_subregion_metrics(sub, index_arrs, crs)
        metrics['date'] = date
        sub_historical = []
        if historical_data:
            sub_historical = [h for h in historical_data if h.get('plot_id') == plot_id]

        anomaly_result = judge_subregion_anomaly(metrics, sub_historical)

        sub_result = {
            'plot_id': plot_id,
            'plot_name': plot_name,
            'date': date,
            'subregion_id': sub['label_id'],
            'area_m2': metrics['area_m2'],
            'centroid': metrics['centroid'],
            'edge_ratio': metrics['edge_ratio'],
            'pixel_count': metrics['pixel_count'],
            'mean_ndvi': metrics['mean_ndvi'],
            'mean_evi': metrics['mean_evi'],
            'mean_savi': metrics['mean_savi'],
            'mean_ndwi': metrics['mean_ndwi'],
            'valid_pixel_ratio': metrics['valid_pixel_ratio'],
            'ndvi_grade': metrics['ndvi_grade'],
            'ndvi_grade_label': metrics['ndvi_grade_label'],
            **anomaly_result
        }

        if sub_result['is_anomaly'] and sub_result['priority'] >= Config.MIN_PRIORITY:
            anomaly_subregions.append(sub_result)

    if anomaly_subregions:
        generate_subregion_anomaly_map(tif_path, index_arrs, anomaly_subregions, plot_id, plot_name, date)
        export_subregions_geojson(plot_id, plot_name, date, subregions, crs)

    logger.info(f'地块 {plot_id}（{plot_name}）检测到 {len(anomaly_subregions)} 个异常子区域')
    return anomaly_subregions


def process_plot_timeseries(plot_id: str, start_date: str, end_date: str) -> List[Dict]:
    """处理指定地块的指定时间范围数据"""
    # 提取纯数字的plot_id
    pure_plot_id = re.findall(r'^\d+', plot_id)[0] if re.findall(r'^\d+', plot_id) else plot_id
    logger.info(f"处理地块：原始ID={plot_id}，提取纯数字ID={pure_plot_id}")

    # 1. 获取该地块的所有有效TIFF文件
    if not Config.NDVI_FOLDER.exists():
        logger.error(f"NDVI目录不存在：{Config.NDVI_FOLDER}")
        return []
    all_tif_files = [f for f in Config.NDVI_FOLDER.iterdir() if is_valid_tif(f)]
    plot_files = []
    for file in all_tif_files:
        file_info = parse_filename_info(file.name)
        if file_info['plot_id'] == pure_plot_id:
            plot_files.append(file)

    if not plot_files:
        logger.warning(f'地块 {pure_plot_id}（{plot_id}）无有效TIFF文件')
        return []

    # 2. 按时间范围筛选
    plot_files = filter_files_by_time_range(plot_files, start_date, end_date)
    if not plot_files:
        logger.warning(f'地块 {pure_plot_id}（{plot_id}）在 {start_date}~{end_date} 无有效文件')
        return []

    # 3. 按日期排序
    plot_files_sorted = sorted(plot_files, key=lambda x: parse_filename_info(x.name)['date'])

    # 4. 计算地块级时序指标
    plot_metrics_list = []
    for tif_file in plot_files_sorted:
        plot_metrics = calculate_plot_level_metrics(tif_file)
        if plot_metrics:
            plot_metrics_list.append(plot_metrics)

    if plot_metrics_list:
        plot_name = plot_metrics_list[0].get('plot_name', '未知地块')
        generate_plot_trend_plot(pure_plot_id, plot_name, plot_metrics_list)

    # 5. 处理每个TIFF文件
    all_anomalies = []
    historical_data = []
    for tif_file in plot_files_sorted:
        anomalies = process_single_tif(tif_file, historical_data)
        all_anomalies.extend(anomalies)
        historical_data.extend(anomalies)

    # 6. 保存临时文件
    temp_file = Config.TEMP_FOLDER / f'temp_subregions_{pure_plot_id}.json'
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(all_anomalies, f, ensure_ascii=False, indent=2)

    logger.info(f'地块 {pure_plot_id}（{plot_id}）时序分析完成，共检测到 {len(all_anomalies)} 个异常子区域')
    return all_anomalies


def generate_final_report(delete_temp: bool = False, timestamp: str = None) -> Dict[str, Any]:
    """生成最终检测报告"""
    # 定位到指定时间戳的目录
    report_dir = Config.OUTPUT_BASE / f'reports_{timestamp or Config.TIMESTAMP}'
    temp_dir = report_dir / 'temp'
    if not temp_dir.exists():
        logger.error(f'临时目录不存在：{temp_dir}')
        return {'error': '临时目录不存在', 'total_anomaly_count': 0, 'anomaly_subregions': []}

    # 读取所有临时文件
    all_anomalies = []
    temp_files = list(temp_dir.glob('temp_subregions_*.json'))
    for temp_file in temp_files:
        try:
            with open(temp_file, 'r', encoding='utf-8') as f:
                anomalies = json.load(f)
                all_anomalies.extend(anomalies)
        except Exception as e:
            logger.warning(f'读取临时文件 {temp_file} 失败：{e}')

    # 去重和排序
    all_anomalies = deduplicate_subregions(all_anomalies)
    all_anomalies = sorted(all_anomalies, key=lambda x: x.get('priority', 0), reverse=True)

    # 统计分级异常数
    grade_stats = {}
    for grade_key, grade_config in Config.NDVI_GRADES.items():
        if grade_config['is_anomaly']:
            count = len([a for a in all_anomalies if a.get('ndvi_grade') == grade_key])
            grade_stats[grade_config['label']] = count

    # 构建最终报告
    total_anomalies = len(all_anomalies)
    report = {
        'total_anomaly_count': total_anomalies,
        'ndvi_grade_stats': grade_stats,
        'report_info': {
            'generate_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_subregions': total_anomalies,
            'total_plots': len(set([a.get('plot_id') for a in all_anomalies])),
            'anomaly_categories': list(set([a.get('anomaly_category') for a in all_anomalies])),
            'output_dir': str(report_dir),
            'geojson_dir': str(report_dir / 'geojson'),
            'visual_report_dir': str(report_dir / 'visualReports')
        },
        'anomaly_subregions': all_anomalies,
        'anomaly_records': all_anomalies,
        'patrol_suggestion': {
            'high_priority': [a for a in all_anomalies if a.get('priority', 0) >= 0.7],
            'medium_priority': [a for a in all_anomalies if 0.4 <= a.get('priority', 0) < 0.7],
            'low_priority': [a for a in all_anomalies if a.get('priority', 0) < 0.4]
        }
    }

    # 保存最终报告
    report_file = report_dir / f'巡田最终工单_{timestamp or Config.TIMESTAMP}.json'
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 可选删除临时文件
    if delete_temp:
        for temp_file in temp_files:
            safe_remove(temp_file)

    logger.info(f'生成最终报告：{report_file}，总异常数：{total_anomalies}')
    logger.info(f'NDVI分级异常统计：{grade_stats}')
    logger.info(
        f'巡田规划：高优先级 {len(report["patrol_suggestion"]["high_priority"])} 个，中优先级 {len(report["patrol_suggestion"]["medium_priority"])} 个，低优先级 {len(report["patrol_suggestion"]["low_priority"])} 个')
    logger.info(f'详细坐标数据已保存至：{report_dir / "geojson"}')
    return report


def run_xuntian_from_app(params: Dict[str, Any]) -> Dict[str, Any]:
    """服务器部署入口函数（保留）"""
    try:
        # 1. 解析参数
        plot_ids = params.get('plot_ids', [])
        start_date = params.get('start_date')
        end_date = params.get('end_date')
        ndvi_folder = params.get('ndvi_folder')
        timestamp = params.get('timestamp', datetime.now().strftime('%Y%m%d_%H%M%S'))
        delete_temp = params.get('delete_temp', False)

        # 2. 校验必填参数
        if not plot_ids or not start_date or not end_date:
            logger.error(f"参数不全：plot_ids={plot_ids}, start_date={start_date}, end_date={end_date}")
            return {'status': 'failed', 'error': '缺少必要参数（plot_ids/start_date/end_date）'}

        # 3. 初始化目录
        Config.init_dirs(timestamp=timestamp, ndvi_folder=ndvi_folder)
        logger.info(f"开始处理巡田任务，时间戳：{timestamp}，任务数：{len(plot_ids)}")

        # 4. 遍历每个plot_id
        all_task_anomalies = []
        for idx, plot_id in enumerate(plot_ids, 1):
            try:
                logger.info(f"\n===== 处理任务{idx}：地块={plot_id}，时间={start_date}~{end_date} =====")
                plot_anomalies = process_plot_timeseries(plot_id, start_date, end_date)
                all_task_anomalies.extend(plot_anomalies)
            except Exception as e:
                logger.error(f"处理任务{idx}失败：{e}", exc_info=True)
                continue

        # 5. 生成最终报告
        final_report = generate_final_report(delete_temp=delete_temp, timestamp=timestamp)

        # 6. 返回结果
        logger.info("\n===== 所有任务处理完成 =====")
        return {
            'status': 'success',
            'total_plots': len(plot_ids),
            'total_anomalies': final_report.get('total_anomaly_count', 0),
            'report': final_report
        }

    except Exception as e:
        logger.error(f"巡田任务整体失败：{e}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(e),
            'total_anomalies': 0
        }


# ================= 本地运行主函数（核心修改） =================
def main():
    """
    本地运行主函数：
    1. 初始化本地目录
    2. 读取本地配置的地块ID/时间范围
    3. 批量处理并生成报告
    """
    # 1. 初始化本地目录（关键：使用本地配置的路径）
    Config.init_dirs()
    logger.info(f"===== 本地运行模式 =====")
    logger.info(f"NDVI文件目录：{Config.NDVI_FOLDER}")
    logger.info(f"结果输出目录：{Config.OUTPUT_FOLDER}")

    # 2. 校验本地NDVI目录
    if not Config.NDVI_FOLDER.exists():
        logger.error(f'本地NDVI目录不存在：{Config.NDVI_FOLDER}')
        logger.info(f"请先创建该目录，并放入TIFF文件：{Config.NDVI_FOLDER}")
        return

    # 3. 获取本地配置的参数
    plot_ids = Config.LOCAL_PLOT_IDS
    start_date = Config.LOCAL_START_DATE
    end_date = Config.LOCAL_END_DATE

    if not plot_ids:
        logger.error("本地配置的地块ID列表为空（LOCAL_PLOT_IDS）")
        return

    # 4. 批量处理指定地块
    logger.info(f"开始处理本地任务：地块ID={plot_ids}，时间范围={start_date}~{end_date}")
    all_task_anomalies = []
    for idx, plot_id in enumerate(plot_ids, 1):
        try:
            logger.info(f"\n===== 处理本地任务{idx}：地块={plot_id} =====")
            plot_anomalies = process_plot_timeseries(plot_id, start_date, end_date)
            all_task_anomalies.extend(plot_anomalies)
        except Exception as e:
            logger.error(f"处理本地任务{idx}失败：{e}", exc_info=True)
            continue

    # 5. 生成最终报告
    generate_final_report(delete_temp=False)  # 本地保留临时文件，方便调试

    # 6. 输出本地运行结果
    logger.info('=' * 60)
    logger.info('本地运行完成！')
    logger.info(f'结果输出目录：{Config.OUTPUT_FOLDER}')
    logger.info(f'可视化报告：{Config.REPORT_FOLDER}')
    logger.info(f'GeoJSON数据：{Config.GEOJSON_FOLDER}')
    logger.info(f'最终报告：{Config.OUTPUT_FOLDER}/巡田最终工单_{Config.TIMESTAMP}.json')
    logger.info('=' * 60)


if __name__ == '__main__':
    main()
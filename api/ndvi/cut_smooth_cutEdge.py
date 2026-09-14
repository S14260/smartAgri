import os
import requests
from shapely.geometry import Polygon, mapping
import rasterio
from rasterio.mask import mask
from rasterio.enums import Resampling
from rasterio.warp import calculate_default_transform, reproject
import numpy as np
from PIL import Image
from rasterio.io import MemoryFile

# ========== 配置 ========== 
NDVI_BASE_URL = "http://123.56.228.32"
NDVI_LOCAL_FOLDER = "./ndvi_files"
CROPPED_BASE_FOLDER = "./static/ndvi_clips"

os.makedirs(NDVI_LOCAL_FOLDER, exist_ok=True)
os.makedirs(CROPPED_BASE_FOLDER, exist_ok=True)

# ========== 下载 ========== 
def get_local_ndvi_path(date_str, region=None):
    filename = f"{date_str}_NDVI.tif"
    base_folder = os.path.join(NDVI_LOCAL_FOLDER, region) if region else NDVI_LOCAL_FOLDER
    os.makedirs(base_folder, exist_ok=True)

    local_path = os.path.join(base_folder, filename)

    if not os.path.exists(local_path):
        url = f"{NDVI_BASE_URL}/{region}/{filename}" if region else f"{NDVI_BASE_URL}/{filename}"
        print(f"[下载] {url}")
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r.content)

    return local_path


# ========== 名称安全 ========== 
def _safe_plot_name(name):
    if not name:
        return "noname"
    for ch in ['/', '\\', ':', '*', '?', '"', '<', '>', '|']:
        name = name.replace(ch, "_")
    return name.strip().replace(" ", "_")


# ========== 日期格式化函数 ==========
def _format_date_parts(date_str):
    """
    支持:
    20250620 -> 2025, 0620
    2025_0620 -> 2025, 0620
    """
    s = str(date_str).strip().replace("-", "").replace("_", "")
    if len(s) >= 8 and s[:8].isdigit():
        return s[:4], s[4:8]
    return str(date_str), ""


# ========== 文件名格式化 ==========
def _format_output_basename(plot_id, plot_name, date_str, region=None, suffix="smooth"):
    safe_name = _safe_plot_name(plot_name)
    year, mmdd = _format_date_parts(date_str)

    parts = [str(plot_id), safe_name, year]
    if mmdd:
        parts.append(mmdd)
    if region:
        parts.append(_safe_plot_name(region))
    if suffix:
        parts.append(suffix)

    return "_".join(parts)


# ========== 重投影 ========== 
def _ensure_tif_in_4326(path):
    with rasterio.open(path) as src:
        if src.crs and src.crs.to_string().upper() == "EPSG:4326":
            return path

    new_path = path.replace(".tif", "_4326.tif")

    if os.path.exists(new_path):
        return new_path

    with rasterio.open(path) as src:
        transform, w, h = calculate_default_transform(
            src.crs, "EPSG:4326", src.width, src.height, *src.bounds
        )

        meta = src.meta.copy()
        meta.update({
            "crs": "EPSG:4326",
            "transform": transform,
            "width": w,
            "height": h,
            "nodata": src.nodata if src.nodata else -9999
        })

        with rasterio.open(new_path, "w", **meta) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    rasterio.band(src, i),
                    rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs="EPSG:4326",
                    resampling=Resampling.bilinear
                )

    return new_path


# ========== PNG（平滑 + 精确裁边） ==========
def _save_png_smooth(original_tif_path, png_path, polygon_coords, scale_factor=6):

    polygon = Polygon([(p['lng'], p['lat']) for p in polygon_coords])

    with rasterio.open(original_tif_path) as src:

        data = src.read(1).astype(np.float32)

        nodata = src.nodata
        if nodata is not None:
            data = np.where(data == nodata, np.nan, data)

        # ===== ❗关键修复1：先mask（只保留地块）=====
        mask_img, _ = mask(
            src,
            [mapping(polygon)],
            crop=False,
            filled=True,
            nodata=np.nan
        )

        data = mask_img[0]

        # ===== ❗关键修复2：避免NaN参与插值 =====
        data = np.where(np.isnan(data), -9999, data)

        h, w = data.shape
        new_h, new_w = h * scale_factor, w * scale_factor

        data_up = np.empty((new_h, new_w), dtype=np.float32)

        new_transform = src.transform * src.transform.scale(w/new_w, h/new_h)

        # ===== 插值 =====
        reproject(
            source=data,
            destination=data_up,
            src_transform=src.transform,
            src_crs=src.crs,
            dst_transform=new_transform,
            dst_crs=src.crs,
            src_nodata=-9999,
            dst_nodata=np.nan,
            resampling=Resampling.lanczos
        )

        # ===== ❗关键修复3：最后再裁边 =====
        with MemoryFile() as memfile:
            with memfile.open(
                driver='GTiff',
                height=new_h,
                width=new_w,
                count=1,
                dtype='float32',
                crs=src.crs,
                transform=new_transform,
                nodata=np.nan
            ) as dataset:

                dataset.write(data_up, 1)

                mask_img2, mask_transform = mask(
                    dataset,
                    [mapping(polygon)],
                    crop=True,
                    filled=True,
                    nodata=np.nan
                )

        data_up = mask_img2[0]

        # ===== NDVI配色 =====
        h2, w2 = data_up.shape
        rgba = np.zeros((h2, w2, 4), dtype=np.uint8)

        mask_transparent = np.isnan(data_up) | (data_up <= -0.2)
        rgba[mask_transparent] = (0, 0, 0, 0)

        ranges = [
            (0.05, (215, 48, 39, 255)),
            (0.1,  (244, 109, 67, 255)),
            (0.15, (253, 174, 97, 255)),
            (0.2,  (254, 224, 139, 255)),
            (0.25, (255, 255, 191, 255)),
            (0.3,  (217, 239, 139, 255)),
            (0.35, (166, 217, 106, 255)),
            (0.4,  (102, 189, 99, 255)),
            (0.45, (26, 152, 80, 255)),
            (0.55, (0, 136, 55, 255)),
            (0.65, (0, 104, 55, 255)),
            (0.75, (0, 68, 27, 255)),
            (1.0,  (0, 51, 0, 255))
        ]

        prev = -np.inf
        for upper, color in ranges:
            mask_range = (data_up > prev) & (data_up <= upper)
            rgba[mask_range] = color
            prev = upper

        # ===== ✅ 边缘抗锯齿（核心补丁）=====
        from scipy.ndimage import distance_transform_edt

        alpha_mask = (~np.isnan(data_up)).astype(np.uint8)

        dist_in = distance_transform_edt(alpha_mask)
        dist_out = distance_transform_edt(1 - alpha_mask)

        edge_width = 2  # 👈 可调：2~4

        soft_alpha = dist_in / (dist_in + dist_out + 1e-6)
        soft_alpha = np.clip(soft_alpha * edge_width, 0, 1)

        rgba[..., 3] = (rgba[..., 3] * soft_alpha).astype(np.uint8)

        Image.fromarray(rgba, "RGBA").save(png_path)

        bounds = rasterio.transform.array_bounds(h2, w2, mask_transform)
        minx, miny, maxx, maxy = bounds

        return [[miny, minx], [maxy, maxx]]


# ========== 核心 ========== 
def cut_smooth_cutEdge(date_str, polygon_coords, plot_id, username, plot_name=None, region=None):

    ndvi_path = get_local_ndvi_path(date_str, region)
    ndvi_path = _ensure_tif_in_4326(ndvi_path)

    safe_name = _safe_plot_name(plot_name)

    user_folder = os.path.join(CROPPED_BASE_FOLDER, region, username) if region else os.path.join(CROPPED_BASE_FOLDER, username)
    os.makedirs(user_folder, exist_ok=True)

    # 使用新的文件名格式
    base_name = _format_output_basename(plot_id=plot_id, plot_name=plot_name, date_str=date_str, region=region, suffix="smooth")
    tif_name = f"{base_name}.tif"
    png_name = f"{base_name}.png"

    tif_path = os.path.join(user_folder, tif_name)
    png_path = os.path.join(user_folder, png_name)

    polygon = Polygon([(p['lng'], p['lat']) for p in polygon_coords])

    # ===== 第一次裁剪 =====
    with rasterio.open(ndvi_path) as src:
        out_img, out_trans = mask(src, [mapping(polygon)], crop=True)

        meta = src.meta.copy()
        meta.update({
            "height": out_img.shape[1],
            "width": out_img.shape[2],
            "transform": out_trans,
            "nodata": src.nodata if src.nodata else -9999
        })

    # ===== ✅ 第二次裁边（核心修复）=====
    with MemoryFile() as memfile:
        with memfile.open(**meta) as tmp_ds:
            tmp_ds.write(out_img)

            out_img_clean, out_trans_clean = mask(
                tmp_ds,
                [mapping(polygon)],
                crop=False,
                filled=True,
                nodata=meta["nodata"]
            )

    meta.update({
        "transform": out_trans_clean
    })

    # ===== 保存干净TIF =====
    with rasterio.open(tif_path, "w", **meta) as dst:
        dst.write(out_img_clean)

        band_names = ["NDVI", "EVI", "SAVI"]
        for i, name in enumerate(band_names, 1):
            if i <= dst.count:
                dst.set_band_description(i, name)

    print("✅ TIF完成（已裁边干净）")

    # ===== PNG =====
    bounds = _save_png_smooth(tif_path, png_path, polygon_coords)

    print("✅ PNG完成（平滑+干净裁边）")

    tif_rel = f"/static/ndvi_clips/{region}/{username}/{tif_name}" if region else f"/static/ndvi_clips/{username}/{tif_name}"
    png_rel = tif_rel.replace(".tif", ".png")

    return tif_rel, tif_path, png_rel, png_path, bounds

# ========== 列出本地 NDVI 文件 ========== 
def list_ndvi_files(region=None):
    """
    返回本地 NDVI 文件列表，按日期倒序排列
    :param region: 区域名 (字符串)，对应目录名
    """
    base_folder = NDVI_LOCAL_FOLDER if not region else os.path.join(NDVI_LOCAL_FOLDER, region)

    if not os.path.exists(base_folder):
        return []

    files = []
    for fname in os.listdir(base_folder):
        if fname.endswith("_NDVI.tif") and len(fname) >= 13:
            try:
                year, date, _ = fname.split("_", 2)
                files.append({
                    "filename": fname,
                    "year": year,
                    "date": date,
                    "region": region or "",
                    "path": os.path.join(base_folder, fname)
                })
            except Exception:
                continue

    # 按日期倒序
    files.sort(key=lambda x: (x["year"], x["date"]), reverse=True)
    return files
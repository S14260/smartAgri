"""
Auto Land Plotting API
======================

这是一个基于 FastAPI 的后端服务，
用于调用训练好的 YOLO 分割模型，实现“AI 自动圈地”功能。
前端可上传当前地图截图与边界坐标，返回地块多边形坐标（可用于 Leaflet 显示与编辑）。

Author: Abner
"""

from fastapi import FastAPI, UploadFile, Form, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import numpy as np
import cv2
from PIL import Image
import io
import json

# ------------------------------
# 初始化 FastAPI 应用
# ------------------------------
app = FastAPI(title="Auto Land Plotting API", description="AI 自动圈地后端接口", version="1.0")

# 允许跨域（前端网页端口可能不同）
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或 ["http://123.56.228.32:8080"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# 加载 YOLO 分割模型（只需一次）
# ------------------------------
model = YOLO("best.pt")

# ------------------------------
# 像素坐标 → 经纬度坐标转换函数
# ------------------------------
def pixel_to_latlng(polygon, img_width, img_height, bounds):
    (lat1, lng1), (lat2, lng2) = bounds  # 左上、右下
    latlngs = []
    for x, y in polygon:
        lng = lng1 + (x / img_width) * (lng2 - lng1)
        lat = lat1 + (y / img_height) * (lat2 - lat1)
        latlngs.append([lat, lng])
    return latlngs


# ------------------------------
# 捕获客户端中断（避免连接关闭报错）
# ------------------------------
@app.middleware("http")
async def catch_client_disconnect(request: Request, call_next):
    try:
        return await call_next(request)
    except ConnectionResetError:
        return JSONResponse({"error": "Client disconnected"}, status_code=499)


# ------------------------------
# 核心接口：AI 自动圈地预测
# ------------------------------
@app.post("/predict")
async def predict(file: UploadFile, bounds: str = Form(...)):
    """
    上传一张地图截图（file） + 当前地图的经纬度范围（bounds），
    返回模型预测的地块边界多边形（经纬度格式）。
    """
    try:
        # 读取上传图片
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

        # 模型推理
        results = model.predict(img_cv, imgsz=640, conf=0.3)

        polygons_latlng = []
        for r in results:
            if hasattr(r, "masks") and r.masks is not None:
                for m in r.masks.xy:
                    polygon = [(float(x), float(y)) for x, y in m]
                    latlngs = pixel_to_latlng(
                        polygon,
                        img.width,
                        img.height,
                        json.loads(bounds)  # 安全解析 JSON
                    )
                    polygons_latlng.append(latlngs)

        return JSONResponse({"polygons": polygons_latlng})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)


# ------------------------------
# 启动服务
# ------------------------------
if __name__ == "__main__":
    import uvicorn
    print("🚀 Auto Land Plotting API is starting at http://127.0.0.1:8002 ...")
    uvicorn.run("auto_land_plotting_api:app", host="0.0.0.0", port=8002, timeout_keep_alive=120)

# app.py
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from ultralytics import YOLO
import numpy as np
import cv2
from PIL import Image
import io
import json

app = FastAPI()


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或 ["http://123.56.228.32:8080"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载模型
model = YOLO("best.pt")

def pixel_to_latlng(polygon, img_width, img_height, bounds):
    (lat1, lng1), (lat2, lng2) = bounds
    latlngs = []
    for x, y in polygon:
        lng = lng1 + (x / img_width) * (lng2 - lng1)
        lat = lat1 + (y / img_height) * (lat2 - lat1)
        latlngs.append([lat, lng])
    return latlngs

@app.post("/predict")
async def predict(file: UploadFile = Form(...), bounds: str = Form(...)):
    try:
        contents = await file.read()
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        results = model.predict(img_cv, imgsz=640, conf=0.3)

        polygons_latlng = []
        for r in results:
            if hasattr(r, "masks") and r.masks is not None:
                for m in r.masks.xy:
                    polygon = [(float(x), float(y)) for x, y in m]
                    latlngs = pixel_to_latlng(polygon, img.width, img.height, json.loads(bounds))
                    polygons_latlng.append(latlngs)

        return JSONResponse({"polygons": polygons_latlng})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8001, timeout_keep_alive=120)

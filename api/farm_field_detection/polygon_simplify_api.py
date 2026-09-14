# polygon_simplify_api.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from shapely.geometry import Polygon
import json

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 或 ["http://123.56.228.32:8080"]
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/simplify")
async def simplify_polygon(request: Request):
    try:
        data = await request.json()
        polygons = data.get("polygons", [])
        tolerance = data.get("tolerance", 0.00005)  # 滑块控制
        simplified_polygons = []

        for coords in polygons:
            if len(coords) < 4:
                simplified_polygons.append(coords)
                continue
            poly = Polygon(coords)
            simple_poly = poly.simplify(tolerance, preserve_topology=True)
            simplified_polygons.append(list(simple_poly.exterior.coords))

        return JSONResponse({"simplified_polygons": simplified_polygons})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("polygon_simplify_api:app", host="0.0.0.0", port=8003)

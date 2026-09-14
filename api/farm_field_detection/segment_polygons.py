import os
import cv2
import json
import numpy as np
from ultralytics import YOLO


def main():
    # 1. 加载训练好的 YOLO 分割模型
    model = YOLO("best.pt")

    # 2. 推理，返回结果对象
    results = model.predict(
        #source="DST1052/images/valid",  # 你的验证集/测试集路径
        source="predict/images",
        imgsz=640,
        conf=0.3,
        iou=0.5,
        classes=[0],   # 只预测耕地
        device="0"     # GPU
    )

    # 3. 创建保存目录
    #save_dir = "runs/segment_polygons"
    save_dir="predict/predictions"
    os.makedirs(save_dir, exist_ok=True)

    # 4. 遍历结果
    for result in results:
        img = result.orig_img.copy()  # 原始图像
        polygons_data = []  # 存放多边形坐标的 JSON 数据

        if result.masks is not None:
            for poly in result.masks.xy:  # 每个 polygon 是 Nx2 数组
                poly = poly.astype(np.int32)

                # 绘制多边形边界线（绿色）
                cv2.polylines(img, [poly], isClosed=True, color=(0, 255, 0), thickness=2)

                # 存储 polygon 坐标
                polygons_data.append(poly.tolist())

        # 5. 保存可视化图像
        img_name = os.path.basename(result.path)
        save_img_path = os.path.join(save_dir, img_name)
        cv2.imwrite(save_img_path, img)

        # 6. 保存多边形坐标为 JSON
        json_name = os.path.splitext(img_name)[0] + ".json"
        save_json_path = os.path.join(save_dir, json_name)
        with open(save_json_path, "w", encoding="utf-8") as f:
            json.dump(polygons_data, f, ensure_ascii=False, indent=2)

        print(f"已保存结果：{save_img_path} 和 {save_json_path}")


if __name__ == "__main__":
    main()

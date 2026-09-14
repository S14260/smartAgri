import os
import cv2
from ultralytics import YOLO


def predict_images_in_folder():
    # ====================== 在这里修改你的参数 ======================
    # 分割模型修改：模型路径指向分割模型的best.pt
    model_path = "runs/segment/field_segmentation/weights/best.pt"  # 分割模型路径
    folder_path = "predict/images"  # 图片文件夹路径
    output_dir = "predict/predictions"  # 结果保存目录
    conf_threshold = 0.3  # 置信度阈值
    # ==============================================================

    # 创建输出目录（分割模型修改：恢复目录创建，避免保存失败）
    os.makedirs(output_dir, exist_ok=True)

    # 加载分割模型
    print(f"加载分割模型: {model_path}")
    model = YOLO(model_path)

    # 获取文件夹中所有支持的图片文件（无需修改）
    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')
    image_files = [
        f for f in os.listdir(folder_path)
        if f.lower().endswith(supported_formats)
    ]

    if not image_files:
        print(f"警告：在 {folder_path} 中未找到任何图片文件")
        return

    # 遍历并预测每张图片
    for img_file in image_files:
        image_path = os.path.join(folder_path, img_file)
        print(f"\n预测图片: {image_path}")

        # 执行预测（分割模型会返回掩码信息）
        results = model(image_path, conf=conf_threshold)

        # 处理并保存结果
        for result in results:
            img = result.orig_img  # 获取原始图片

            # 分割模型修改：遍历掩码（masks）而非边界框（boxes），绘制多边形
            # zip(result.masks.xy, result.boxes)：同时获取多边形和类别信息
            for mask, box in zip(result.masks.xy, result.boxes):
                # 获取类别和置信度（仍用box信息，无需修改）
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = model.names[cls]

                # 分割模型修改：绘制多边形轮廓（替代矩形框）
                mask = mask.astype(int)  # 转换为整数坐标
                cv2.polylines(
                    img,
                    [mask],  # 多边形顶点坐标列表
                    isClosed=True,  # 闭合多边形（关键）
                    color=(0, 255, 0),  # 绿色轮廓
                    thickness=2  # 线宽
                )

                # 绘制类别标签（位置仍用边界框左上角，无需修改）
                x1, y1 = int(box.xyxy[0][0]), int(box.xyxy[0][1])
                label = f"{class_name} {conf:.2f}"
                cv2.putText(img, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # 保存带标注的图片（无需修改）
            output_path = os.path.join(output_dir, f"pred_{img_file}")
            cv2.imwrite(output_path, cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
            print(f"预测结果已保存到: {output_path}")

    print(f"\n所有图片预测完成，结果保存在: {output_dir}")


if __name__ == "__main__":
    predict_images_in_folder()
import os
import shutil
import yaml
import json
from sklearn.model_selection import train_test_split
from ultralytics import YOLO


# 🔥 新增：导入 new_data -> labelme_annotations 的函数
import os
import shutil
import json
import random


def import_new_dataset(new_data_dir, labelme_dir, class_names=None, mode="copy",
                       split_ratio=(0.7, 0.2, 0.1), seed=42):
    """
    将 new_data 中的数据导入到 labelme_annotations/ 下，并自动划分 train/val/test
    :param new_data_dir: 新数据目录 (含 json+图片)
    :param labelme_dir: 主数据集目录 (labelme_annotations)
    :param class_names: 类别列表
    :param mode: "copy" or "move" 是否保留 new_data
    :param split_ratio: (train, val, test) 比例，和为 1
    :param seed: 随机种子，保证划分可复现
    """
    if class_names is None:
        class_names = ["field"]

    # 保证比例正确
    assert abs(sum(split_ratio) - 1.0) < 1e-6, "split_ratio 必须和为 1"

    # 找所有 json 文件
    json_files = [f for f in os.listdir(new_data_dir) if f.endswith(".json")]
    if not json_files:
        print("⚠️ new_data 中没有 JSON 文件")
        return

    random.seed(seed)
    random.shuffle(json_files)

    n_total = len(json_files)
    n_train = int(n_total * split_ratio[0])
    n_val = int(n_total * split_ratio[1])
    splits = {
        "train": json_files[:n_train],
        "val": json_files[n_train:n_train + n_val],
        "test": json_files[n_train + n_val:]
    }

    for split, files in splits.items():
        img_dir = os.path.join(labelme_dir, "images", split)
        label_dir = os.path.join(labelme_dir, "labels", split)
        backup_dir = os.path.join(labelme_dir, "json_backup", split)
        os.makedirs(img_dir, exist_ok=True)
        os.makedirs(label_dir, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)

        for json_file in files:
            json_path = os.path.join(new_data_dir, json_file)
            img_name = os.path.splitext(json_file)[0]

            # 找图片
            img_extensions = [".jpg", ".jpeg", ".png", ".bmp"]
            img_src = None
            for ext in img_extensions:
                candidate = os.path.join(new_data_dir, img_name + ext)
                if os.path.exists(candidate):
                    img_src = candidate
                    break
            if not img_src:
                print(f"⚠️ {json_file} 缺少对应图片，跳过")
                continue

            # 移动/复制图片
            img_dst = os.path.join(img_dir, os.path.basename(img_src))
            if mode == "move":
                shutil.move(img_src, img_dst)
            else:
                shutil.copy(img_src, img_dst)

            # 转换 JSON -> YOLO txt
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            img_h = data["imageHeight"]
            img_w = data["imageWidth"]
            label_lines = []

            for shape in data["shapes"]:
                cls_name = shape["label"]
                if cls_name not in class_names:
                    print(f"⚠️ 未知类别 {cls_name}，跳过")
                    continue

                cls_id = class_names.index(cls_name)
                points = shape["points"]

                normalized_points = []
                for (x, y) in points:
                    nx = x / img_w
                    ny = y / img_h
                    normalized_points.append(f"{nx:.6f} {ny:.6f}")

                label_lines.append(f"{cls_id} " + " ".join(normalized_points))

            label_path = os.path.join(label_dir, img_name + ".txt")
            with open(label_path, "w") as f:
                f.write("\n".join(label_lines))

            # 备份 JSON
            if mode == "move":
                shutil.move(json_path, os.path.join(backup_dir, json_file))
            else:
                shutil.copy(json_path, os.path.join(backup_dir, json_file))

        print(f"✅ {split} 集导入完成: {len(files)} 个样本")

    print(f"\n🎯 总计导入: {n_total} 个样本 -> train {n_train}, val {n_val}, test {n_total - n_train - n_val}")


def create_yaml_config(labelme_dir, class_names):
    """创建 dataset.yaml 配置文件"""
    config = {
        'path': os.path.abspath(labelme_dir),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'nc': len(class_names),
        'names': class_names
    }

    config_path = os.path.join(labelme_dir, 'dataset.yaml')
    with open(config_path, 'w') as f:
        yaml.dump(config, f, sort_keys=False)

    return config_path


def main():
    # 🔥 修改：项目目录结构
    LABELME_DIR = r"D:\PyCharm\farm_field_detection\data\labelme_annotations"
    NEW_DATA_DIR = r"D:\PyCharm\farm_field_detection\data\new_data"
    CLASS_NAMES = ["field"]

    EPOCHS = 200
    IMAGE_SIZE = 1024
    BATCH_SIZE = 8
    DEVICE = "0"
    MODEL_SAVE_DIR = "runs/segment/field_segmentation"

    # 🔥 新增：导入 new_data
    print("===== 导入新数据 =====")
    import_new_dataset(NEW_DATA_DIR, LABELME_DIR,class_names=CLASS_NAMES, mode="copy")

    # 创建 dataset.yaml
    print("\n===== 创建配置文件 =====")
    config_path = create_yaml_config(LABELME_DIR, CLASS_NAMES)
    print(f"配置文件已保存到: {config_path}")

    # 🔥 修改：训练直接用 labelme_annotations
    print("\n===== 开始训练分割模型 =====")
    model = YOLO("yolo11s-seg.pt")
    results = model.train(
        data=config_path,
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        device=DEVICE,
        project=os.path.dirname(MODEL_SAVE_DIR),
        name=os.path.basename(MODEL_SAVE_DIR),
        exist_ok=True,
        task='segment',
        patience=50,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10,
        translate=0.1,
        scale=0.5,
        shear=0.2,
        flipud=0.3,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1
    )

    print("\n===== 分割模型训练完成 =====")
    print(f"模型保存路径: {MODEL_SAVE_DIR}")
    print(f"最佳模型路径: {os.path.join(MODEL_SAVE_DIR, 'weights', 'best.pt')}")


if __name__ == "__main__":
    main()

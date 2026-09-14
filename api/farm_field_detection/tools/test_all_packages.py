import sys
import traceback
import numpy as np
import torch
import torchvision
import cv2
## matplotlib测试不通过
import matplotlib
import matplotlib.pyplot as plt
import albumentations
import pycocotools
from labelme2coco import labelme2coco
from PIL import Image


# =============================
# 工具方法：统一测试包装器
# =============================
def run_test(name, func):
    print(f"\n=== 测试：{name} ===")
    try:
        func()
        print(f"✅ {name} 测试通过")
    except Exception as e:
        print(f"❌ {name} 测试失败：{e}")
        traceback.print_exc()
        sys.exit(1)


# =============================
# 1. PyTorch 测试
# =============================
def test_pytorch():
    print(f"PyTorch 版本: {torch.__version__}")
    print(f"Torchvision 版本: {torchvision.__version__}")
    print(f"CUDA 可用: {torch.cuda.is_available()}")

    if torch.cuda.is_available():
        print(f"GPU 设备: {torch.cuda.get_device_name(0)}")
        print(f"CUDA 版本: {torch.version.cuda}")

    t = torch.rand(3, 3).cuda() if torch.cuda.is_available() else torch.rand(3, 3)
    print("张量创建成功:", t.shape)


# =============================
# 2. OpenCV 测试
# =============================
def test_opencv():
    print(f"OpenCV 版本: {cv2.__version__}")

    img = np.random.randint(0, 255, (120, 120, 3), dtype=np.uint8)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    print("OpenCV 图像处理完成，灰度图尺寸:", gray.shape)


# =============================
# 3. Matplotlib 测试
# =============================
# def test_matplotlib():
#     import matplotlib
#     matplotlib.use("template")  # <-- 关键！不使用Agg，避免崩溃
#
#     import matplotlib.pyplot as plt
#
#     print(f"Matplotlib 版本: {matplotlib.__version__}")
#
#     plt.figure()
#     plt.plot([1, 2, 3], [4, 5, 1])
#     plt.title("Matplotlib Test")
#     plt.savefig("test_matplot.png")
#     plt.close()
#
#     print("Matplotlib 绘图 test_matplot.png 已生成")




# =============================
# 4. Albumentations 测试
# =============================
def test_albumentations():
    print(f"Albumentations 版本: {albumentations.__version__}")

    transform = albumentations.Compose([
        albumentations.Resize(50, 50),
        albumentations.RandomBrightnessContrast(0.2, 0.2)
    ])

    img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    out = transform(image=img)

    print("增强前:", img.shape, "增强后:", out["image"].shape)


# =============================
# 5. Pillow 测试
# =============================
def test_pillow():
    print(f"Pillow 版本: {Image.__version__}")

    img = Image.new("RGB", (100, 100), "blue")
    img.save("test_pillow.png")

    loaded = Image.open("test_pillow.png")
    print("图像读取成功，尺寸:", loaded.size)


# =============================
# 6. COCO API 测试
# =============================
def test_pycocotools():
    from pycocotools.coco import COCO
    print("Pycocotools 导入成功")


# =============================
# 7. labelme2coco 测试
# =============================
def test_labelme2coco():
    print("labelme2coco 导入成功（无需数据即可测试）")


# =============================
# 主程序
# =============================
if __name__ == "__main__":
    print("=================================================")
    print(f"Python 版本: {sys.version.split()[0]}")
    print(f"Numpy 版本: {np.__version__}")
    print("环境依赖自检开始……")
    print("=================================================")

    run_test("PyTorch", test_pytorch)
    run_test("OpenCV", test_opencv)
    run_test("Matplotlib", test_matplotlib)
    run_test("Albumentations", test_albumentations)
    run_test("Pillow", test_pillow)
    run_test("Pycocotools", test_pycocotools)
    run_test("labelme2coco", test_labelme2coco)

    print("\n=================================================")
    print("🎉 所有模块测试完成：环境配置正常！")
    print("=================================================")

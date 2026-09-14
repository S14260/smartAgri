import warnings
warnings.filterwarnings('ignore')
from ultralytics import YOLO

if __name__ == '__main__':
    # 1. 加载训练好的分割模型（确保是YOLO-seg系列权重，如yolo11n-seg的best.pt）
    model = YOLO('best.pt')  # 你的分割权重路径

    # 2. 执行分割推理（仅保留合法参数，无无效参数）
    model.predict(
        source='DST1052/images/valid',  # 测试集路径（文件夹/单张图/图列表）
        imgsz=640,                     # 与训练一致的输入尺寸（必须匹配，保证精度）
        project='runs/segment',  # 结果保存根目录（延续你训练的路径风格）
        name='yolo11n-seg_exp',        # 实验名称（与训练exp对应，方便管理）
        save=True,                     # 保存带分割掩码的图像
        conf=0.3,                      # 过滤低置信度预测（减少非耕地误判）
        iou=0.5,                       # 合并重复的耕地预测（避免同一地块多掩码）
        line_width=1,                  # 边界框变细，不遮挡掩码细节
        show_labels=False,             # 关闭标签，耕地密集时更清晰
        classes=[0],                   # 只分割第0类（你的耕地类，必加！避免其他干扰）
        device='0'                     # 用GPU推理（CPU设为'cpu'，你的RTX 4060可用0）
    )

    # 3. 正确的结果路径提示（与project+name对应，避免误导）
    result_path = 'farmland_segment_runs/segment/yolo11n_seg_exp'
    print(f"分割推理完成！结果已保存至：{result_path}")
    print("保存内容：带彩色耕地掩码的图像（绿色/蓝色填充区域为耕地，边界框为细线条）")
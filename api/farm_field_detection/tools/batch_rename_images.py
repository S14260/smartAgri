import os


def batch_rename_images(input_dir, prefix="field", start_index=1, output_dir=None):
    """
    批量重命名文件夹中的图片

    参数:
        input_dir (str): 输入图片文件夹路径
        prefix (str): 新文件名前缀 (默认 "field")
        start_index (int): 起始编号 (默认 1)
        output_dir (str): 输出文件夹路径 (默认 None，表示直接覆盖重命名)
    """
    # 支持的图片后缀
    supported_exts = (".jpg", ".jpeg", ".png", ".bmp", ".tiff")

    # 如果没有指定输出目录，就在原目录里操作
    if output_dir is None:
        output_dir = input_dir
    else:
        os.makedirs(output_dir, exist_ok=True)

    # 遍历所有图片
    count = start_index
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_exts):
            ext = os.path.splitext(filename)[1]  # 保留原始后缀
            new_name = f"{prefix}_{count:03d}{ext}"  # 例如 field_001.jpg
            src_path = os.path.join(input_dir, filename)
            dst_path = os.path.join(output_dir, new_name)
            os.rename(src_path, dst_path)
            print(f"重命名: {filename} -> {new_name}")
            count += 1

    print("\n批量重命名完成！")


# ==================== 使用示例 ====================
if __name__ == "__main__":
    input_folder = r"C:\Users\marve\Pictures\Screenshots"  # 你的图片目录
    batch_rename_images(input_folder, prefix="TileMatrix18", start_index=1)

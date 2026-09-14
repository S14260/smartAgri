import subprocess

processes = [
    subprocess.Popen(["python3", "app.py"]),
    subprocess.Popen(["python3", "auto_land_plotting_api.py"]),
    subprocess.Popen(["python3", "polygon_simplify_api.py"]),
]

# 防止脚本退出
for p in processes:
    p.wait()

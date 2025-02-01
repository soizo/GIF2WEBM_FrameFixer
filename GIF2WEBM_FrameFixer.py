import imageio
import numpy as np
import os
import subprocess
from PIL import Image, ImageSequence  # 用於調整尺寸


def gif_to_webm(input_gif, output_webm, target_fps=60, target_duration=3, target_size=(512, 512)):
    # 讀取 GIF 使用 PIL 以更好地處理透明通道
    with Image.open(input_gif) as im:
        frames = []
        durations = []

        for frame in ImageSequence.Iterator(im):
            frame = frame.convert("RGBA")  # 確保使用 RGBA 模式
            durations.append(frame.info.get('duration', 100))  # 預設持續時間 100ms
            frames.append(np.array(frame))

    # 計算原始平均幀率
    total_duration = sum(durations)
    if total_duration == 0:
        raise ValueError("GIF 總持續時間為 0，無法計算幀率")

    average_duration = total_duration / len(durations)
    original_fps = 1000 / average_duration
    print(f"原始 GIF 平均幀率: {original_fps:.2f} FPS")

    # 計算需要重複的次數以達到目標時長
    original_duration = total_duration / 1000  # 轉換為秒
    repeat_times = int(np.ceil(target_duration / original_duration))
    print(f"原始動畫時長: {original_duration:.2f} 秒，將重複 {repeat_times} 次以達到 ≥{target_duration} 秒")

    # 重複幀以達到目標時長
    frames = frames * repeat_times

    # 調整尺寸為 512x512
    resized_frames = []
    for frame in frames:
        img = Image.fromarray(frame).resize(target_size, Image.Resampling.LANCZOS)
        resized_frames.append(np.array(img))

    # 存儲中間格式
    temp_frames_dir = "temp_frames"
    os.makedirs(temp_frames_dir, exist_ok=True)
    frame_paths = []

    for i, frame in enumerate(resized_frames):
        frame_path = os.path.join(temp_frames_dir, f"frame_{i:03d}.png")
        imageio.imwrite(frame_path, frame)
        frame_paths.append(frame_path)

    # 使用 FFmpeg 轉換
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-framerate", f"{original_fps:.2f}",
        "-i", os.path.join(temp_frames_dir, "frame_%03d.png"),
        "-r", str(target_fps),
        "-c:v", "libvpx-vp9",
        "-b:v", "500K",
        "-pix_fmt", "yuva420p",  # 支援透明通道
        "-auto-alt-ref", "0",
        output_webm
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg 轉換失敗: {e}")
        raise
    finally:
        for file in frame_paths:
            if os.path.exists(file):
                os.remove(file)
        if os.path.exists(temp_frames_dir):
            os.rmdir(temp_frames_dir)

    print(f"轉換完成: {output_webm}")


# 使用示例
input_folder = "input"
output_folder = "output"

# 如果輸出文件夾不存在，則創建
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 遍注input文件夾中的所有GIF文件
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".gif"):
        input_path = os.path.join(input_folder, filename)
        output_filename = os.path.splitext(filename)[0] + ".webm"
        output_path = os.path.join(output_folder, output_filename)

        print(f"正在轉換: {input_path} -> {output_path}")
        gif_to_webm(input_path, output_path)

print("所有轉換完成!")
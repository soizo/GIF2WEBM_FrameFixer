import argparse
import imageio
import numpy as np
import os
import subprocess
from PIL import Image, ImageSequence


def gif_to_webm(input_gif, output_webm, target_fps=60, target_duration=2, target_size=(512, 512)):
    """Convert a GIF animation to a WebM video with VP9 codec and transparency support.

    Args:
        input_gif: Path to the input GIF file.
        output_webm: Path for the output WebM file.
        target_fps: Output frame rate (default: 60).
        target_duration: Minimum output duration in seconds (default: 2).
        target_size: Output resolution as (width, height) tuple (default: 512x512).
    """
    # Read GIF using PIL to preserve transparency
    with Image.open(input_gif) as im:
        frames = []
        durations = []

        for frame in ImageSequence.Iterator(im):
            frame = frame.convert("RGBA")
            durations.append(frame.info.get('duration', 100))  # default 100ms if missing
            frames.append(np.array(frame))

    # Calculate original average frame rate
    total_duration = sum(durations)
    if total_duration == 0:
        raise ValueError("GIF total duration is 0, cannot calculate frame rate")

    average_duration = total_duration / len(durations)
    original_fps = 1000 / average_duration
    print(f"Original GIF average FPS: {original_fps:.2f}")

    # Calculate how many times to repeat frames to reach target duration
    original_duration = total_duration / 1000  # convert to seconds
    repeat_times = int(np.ceil(target_duration / original_duration))
    print(f"Original duration: {original_duration:.2f}s — repeating {repeat_times}x to reach ≥{target_duration}s")

    # Repeat frames to meet target duration
    frames = frames * repeat_times

    # Resize all frames to target size
    resized_frames = []
    for frame in frames:
        img = Image.fromarray(frame).resize(target_size, Image.Resampling.LANCZOS)
        resized_frames.append(np.array(img))

    # Write frames to a temporary directory
    temp_frames_dir = "temp_frames"
    os.makedirs(temp_frames_dir, exist_ok=True)
    frame_paths = []

    for i, frame in enumerate(resized_frames):
        frame_path = os.path.join(temp_frames_dir, f"frame_{i:03d}.png")
        imageio.imwrite(frame_path, frame)
        frame_paths.append(frame_path)

    # Run FFmpeg to encode WebM with VP9 and alpha channel
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-framerate", f"{original_fps:.2f}",
        "-i", os.path.join(temp_frames_dir, "frame_%03d.png"),
        "-r", str(target_fps),
        "-c:v", "libvpx-vp9",
        "-b:v", "500K",
        "-pix_fmt", "yuva420p",  # preserve alpha channel
        "-auto-alt-ref", "0",
        output_webm
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"FFmpeg conversion failed: {e}")
        raise
    finally:
        for file in frame_paths:
            if os.path.exists(file):
                os.remove(file)
        if os.path.exists(temp_frames_dir):
            os.rmdir(temp_frames_dir)

    print(f"Done: {output_webm}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert GIF animations to WebM (VP9, with transparency)"
    )
    parser.add_argument(
        "--input", default="input",
        help="Folder containing input GIF files (default: ./input)"
    )
    parser.add_argument(
        "--output", default="output",
        help="Folder for output WebM files (default: ./output)"
    )
    parser.add_argument(
        "--fps", type=int, default=60,
        help="Output frame rate (default: 60)"
    )
    parser.add_argument(
        "--min-duration", type=float, default=2.0,
        help="Minimum output duration in seconds (default: 2.0)"
    )
    parser.add_argument(
        "--size", type=int, default=512,
        help="Output width and height in pixels (default: 512)"
    )
    args = parser.parse_args()

    input_folder = args.input
    output_folder = args.output
    target_size = (args.size, args.size)

    os.makedirs(output_folder, exist_ok=True)

    gif_files = [f for f in os.listdir(input_folder) if f.lower().endswith(".gif")]
    if not gif_files:
        print(f"No GIF files found in '{input_folder}'.")
        return

    for filename in gif_files:
        input_path = os.path.join(input_folder, filename)
        output_filename = os.path.splitext(filename)[0] + ".webm"
        output_path = os.path.join(output_folder, output_filename)

        print(f"Converting: {input_path} -> {output_path}")
        gif_to_webm(
            input_path, output_path,
            target_fps=args.fps,
            target_duration=args.min_duration,
            target_size=target_size
        )

    print("All conversions complete.")


if __name__ == "__main__":
    main()

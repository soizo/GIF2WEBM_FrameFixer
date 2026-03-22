import argparse
import logging
import os
import shutil
import subprocess

import imageio
import numpy as np
from PIL import Image, ImageSequence

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def gif_to_webm(
    input_gif: str,
    output_webm: str,
    target_fps: int = 60,
    target_duration: float = 2.0,
    target_size: tuple[int, int] = (512, 512),
) -> None:
    """Convert a GIF animation to WebM format with frame standardization.

    Reads the input GIF, repeats frames to meet the target duration,
    resizes all frames to the target size, then encodes to VP9 WebM
    with alpha channel support via FFmpeg.

    Args:
        input_gif: Path to the input GIF file.
        output_webm: Path for the output WebM file.
        target_fps: Output frame rate in frames per second.
        target_duration: Minimum output duration in seconds.
        target_size: Output frame dimensions as (width, height).
    """
    if not os.path.isfile(input_gif):
        raise FileNotFoundError(f"Input GIF not found: {input_gif}")

    with Image.open(input_gif) as im:
        frames = []
        durations = []
        for frame in ImageSequence.Iterator(im):
            frame = frame.convert("RGBA")
            durations.append(frame.info.get("duration", 100))
            frames.append(np.array(frame))

    if not frames:
        raise ValueError(f"No frames found in GIF: {input_gif}")

    total_duration_ms = sum(durations)
    if total_duration_ms == 0:
        raise ValueError(f"GIF total duration is 0: {input_gif}")

    average_duration_ms = total_duration_ms / len(durations)
    original_fps = 1000 / average_duration_ms
    original_duration_s = total_duration_ms / 1000
    logger.info("Original GIF: %.2f FPS, %.2f s", original_fps, original_duration_s)

    repeat_times = int(np.ceil(target_duration / original_duration_s))
    logger.info(
        "Repeating %d time(s) to reach >= %.1f s", repeat_times, target_duration
    )
    frames = frames * repeat_times

    resized_frames = [
        np.array(Image.fromarray(f).resize(target_size, Image.Resampling.LANCZOS))
        for f in frames
    ]

    temp_dir = output_webm + ".tmp_frames"
    os.makedirs(temp_dir, exist_ok=True)
    try:
        frame_paths = []
        for i, frame in enumerate(resized_frames):
            path = os.path.join(temp_dir, f"frame_{i:04d}.png")
            imageio.imwrite(path, frame)
            frame_paths.append(path)

        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-framerate", f"{original_fps:.2f}",
            "-i", os.path.join(temp_dir, "frame_%04d.png"),
            "-r", str(target_fps),
            "-c:v", "libvpx-vp9",
            "-b:v", "500K",
            "-pix_fmt", "yuva420p",
            "-auto-alt-ref", "0",
            output_webm,
        ]
        subprocess.run(ffmpeg_cmd, check=True, capture_output=True)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    logger.info("Done: %s", output_webm)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert GIF animations to WebM (VP9) with frame standardization."
    )
    parser.add_argument(
        "-i", "--input", default="input",
        help="Input folder containing GIF files (default: input)"
    )
    parser.add_argument(
        "-o", "--output", default="output",
        help="Output folder for WebM files (default: output)"
    )
    parser.add_argument(
        "--fps", type=int, default=60,
        help="Output frame rate (default: 60)"
    )
    parser.add_argument(
        "--duration", type=float, default=2.0,
        help="Minimum output duration in seconds (default: 2.0)"
    )
    parser.add_argument(
        "--size", type=int, nargs=2, metavar=("W", "H"), default=[512, 512],
        help="Output frame size: width height (default: 512 512)"
    )
    args = parser.parse_args()

    if not os.path.isdir(args.input):
        logger.error("Input folder not found: %s", args.input)
        raise SystemExit(1)

    os.makedirs(args.output, exist_ok=True)
    target_size = tuple(args.size)

    gif_files = [f for f in os.listdir(args.input) if f.lower().endswith(".gif")]
    if not gif_files:
        logger.warning("No GIF files found in: %s", args.input)
        return

    for filename in gif_files:
        input_path = os.path.join(args.input, filename)
        output_path = os.path.join(args.output, os.path.splitext(filename)[0] + ".webm")
        logger.info("Converting: %s -> %s", input_path, output_path)
        try:
            gif_to_webm(input_path, output_path, args.fps, args.duration, target_size)
        except Exception as exc:
            logger.error("Failed to convert %s: %s", filename, exc)

    logger.info("All conversions complete.")


if __name__ == "__main__":
    main()

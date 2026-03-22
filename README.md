# GIF2WEBM FrameFixer

Convert animated GIFs to WebM video using the VP9 codec, with full alpha-channel (transparency) support. Useful for creating Telegram stickers or any context requiring transparent WebM animations.

## Features

- Preserves transparency (RGBA → VP9 + yuva420p)
- Loops short GIFs to meet a minimum duration (default 2 s)
- Resizes output to a target resolution (default 512×512)
- Batch-converts all GIFs in an input folder
- Supports CLI arguments for full customization

## Prerequisites

- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) installed and available on your `PATH`

## Installation

```bash
# Clone the repo
git clone https://github.com/soizo/GIF2WEBM_FrameFixer.git
cd GIF2WEBM_FrameFixer

# (Optional) Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

## Usage

1. Place your `.gif` files in the `input/` folder (create it if it doesn't exist).
2. Run the script:

```bash
python GIF2WEBM_FrameFixer.py
```

Output `.webm` files will be saved to the `output/` folder.

### Options

| Flag | Default | Description |
|---|---|---|
| `-i, --input DIR` | `input` | Input folder containing GIF files |
| `-o, --output DIR` | `output` | Output folder for WebM files |
| `--fps N` | `60` | Output frame rate |
| `--duration SECS` | `2.0` | Minimum output duration in seconds |
| `--size W H` | `512 512` | Output frame dimensions |

**Examples:**

```bash
# Custom output: 30 FPS, 3 seconds, 720×720
python GIF2WEBM_FrameFixer.py --fps 30 --duration 3 --size 720 720

# Custom input/output folders
python GIF2WEBM_FrameFixer.py -i my_gifs -o my_webms
```

## Output Format

| Property | Value |
|---|---|
| Container | WebM |
| Video codec | VP9 (`libvpx-vp9`) |
| Pixel format | `yuva420p` (alpha channel preserved) |
| Bitrate | 500 Kbps |

## License

MIT — see [LICENSE](LICENSE).

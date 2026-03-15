# GIF2WEBM FrameFixer

將透明 GIF 動畫轉換為 WebM (VP9) 格式，並標準化幀數、時長與解析度。

> 原始教學：[免費將透明底動態GIF添加到貼紙方法](https://telegra.ph/%E5%85%8D%E8%B2%BB%E5%B0%87%E9%80%8F%E6%98%8E%E5%BA%95%E5%8B%95%E6%85%8BGIF%E6%B7%BB%E5%8A%A0%E5%88%B0%E8%B2%BC%E7%B4%99%E6%96%B9%E6%B3%95-01-30)

## 功能

- 保留 GIF 透明通道（RGBA → yuva420p）
- 自動重複幀以達到目標時長
- 調整輸出解析度（預設 512×512）
- 自訂輸出幀率（預設 60 FPS）
- 支援命令列參數

## 依賴

- **Python** >= 3.10
- **FFmpeg**（需在系統 PATH 中）

安裝 Python 依賴：

```bash
pip install -r requirements.txt
```

## 使用方法

### 基本用法

1. 建立 `input/` 資料夾並放入 GIF 檔案
2. 執行腳本：

```bash
python GIF2WEBM_FrameFixer.py
```

轉換結果會輸出至 `output/` 資料夾。

### 進階用法

```bash
python GIF2WEBM_FrameFixer.py [選項]

選項：
  -i, --input DIR       輸入資料夾（預設：input）
  -o, --output DIR      輸出資料夾（預設：output）
  --fps N               輸出幀率（預設：60）
  --duration SECS       最短輸出時長，秒（預設：2.0）
  --size W H            輸出解析度（預設：512 512）
```

**範例：**

```bash
# 自訂輸出為 30 FPS、3 秒、720×720
python GIF2WEBM_FrameFixer.py --fps 30 --duration 3 --size 720 720

# 自訂輸入輸出資料夾
python GIF2WEBM_FrameFixer.py -i my_gifs -o my_webms
```

## 授權

MIT License

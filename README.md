# 專案名稱

PathGuard 路徑守護者

# 專案簡介

PathGuard 是一款「即時 AI 路徑安全助理」，透過即時影像理解與動態偵測，輸出可中斷、可執行的短句語音指引，協助使用者在街道環境中更安全地通行。

# 功能列表

- 即時影像擷取：支援 `--source 0`（攝影機）或 `--source <video_path>`（影片檔）或 `--source synthetic`（合成測試來源）
- 場景語意理解（Gemini 2.0 Flash）：以時鐘方位輸出精簡指令，分析間隔預設 3 秒
- 動態危險偵測（OpenCV Optical Flow）：聚焦中央走道區域，偵測快速接近與顯著位移，危險事件可插播中斷語音
- 路徑對齊（OpenCV 邊界推定）：估計安全走廊中心偏移，輸出「Veering Left / Veering Right」修正提示
- 風險仲裁（Risk Arbitration）：優先順序為「危險 > 偏移 > 一般描述」
- 跨平台語音輸出：macOS 使用 `say`，Windows/Linux 使用 `pyttsx3`

# 技術架構

`Camera`（即時影像）→ `MotionEngine`（光流動態）與 `PathAlignmentEngine`（走廊偏移）→ `VisionEngine`（Gemini 場景理解）→ `RiskArbiter`（風險優先序）→ `AudioEngine`（TTS 與可中斷播報）

# 專案結構

- `demo.py`：主程式（整合影像、動態偵測、路徑對齊、Gemini、語音、風險仲裁）
- `camera.py`：攝影機來源與 `SyntheticCamera`
- `vision.py`：Gemini 影像分析
- `motion.py`：OpenCV 光流動態偵測
- `path_alignment.py`：OpenCV 路徑對齊
- `risk.py`：風險仲裁與優先序事件
- `audio.py`：TTS 與 `interrupt=True` 中斷機制
- `requirements.txt`：Python 依賴
- `.env.example`：環境變數範例

# 本地測試教學

以下流程已在 macOS（Python 3.13）驗證可執行。

1. 安裝依賴

```bash
python3 -m pip install -r requirements.txt
```

2. 離線快速自測（不需要攝影機、不需要 `GEMINI_API_KEY`）

```bash
python3 demo.py --source synthetic --offline --headless --seconds 2
```

3. 啟用光流偵測（離線、合成來源）

```bash
python3 demo.py --source synthetic --offline --headless --seconds 2 --motion
```

## 參數說明

- `--source`：影像來源，支援 `0`（預設攝影機）、影片檔路徑、或 `synthetic`（合成來源）
- `--offline`：不呼叫 Gemini（不需要 `GEMINI_API_KEY`）
- `--lang`：語言，支援 `zh` 或 `en`
- `--motion` / `--no-motion`：啟用/停用光流動態警示
- `--headless`：不開啟視窗（適合做快速 smoke test）
- `--seconds`：執行 N 秒後自動結束（`0` 代表直到手動退出）

# 環境變數

- `GEMINI_API_KEY`：Gemini API 金鑰（需要啟用雲端場景理解時才必填）

範例請參考 `.env.example`，自行建立 `.env` 並設定 `GEMINI_API_KEY`。

# Coolify 部署教學

本專案目前未提供已驗證的 Coolify 部署流程。

# 前端 / 後端詳細文件連結

- 前端：無（目前為單一 Python 原型）
- 後端：無（目前為單一 Python 原型）

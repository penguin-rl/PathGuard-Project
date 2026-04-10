# PathGuard (路徑守護者)

**PathGuard (路徑守護者)** 是一款即時 AI 導航助理，旨在幫助所有人，尤其是視障人士，安全且自信地在世界中導航。

應用程式運用 **Google's Gemini 2.0 Flash API** 與 **OpenCV**，透過分析即時攝影機畫面來辨識障礙物、人行道邊界、行人穿越道號誌，以及危險的快速移動物體，並提供即時的語音回饋來引導使用者。

## 展示影片

[請在此處放置您的展示影片]

---

## 靈感來源

本專案的靈感來自於 **WalkVLM** (arXiv:2412.20903)，該研究探討了如何使用視覺語言模型 (VLMs) 為視障人士提供步行輔助。如同 WalkVLM，**PathGuard** 運用了多模態 AI (Gemini 2.0) 的推理能力來理解複雜場景，並即時提供簡潔、可操作的指引。

## 主要功能

*   **即時障礙物偵測**：使用時鐘方位識別車輛、行人、柱子與其他危險物（例如：「兩點鐘方向有車輛」）。
*   **路徑對齊**：引導使用者走在人行道上，並在偏離路線時發出警告。
*   **行人穿越道辨識**：偵測行人穿越道號誌（可通行/禁止通行）與交通號誌。
*   **快速移動警告**（可選功能）：使用光流法 (Optical Flow) 偵測快速接近的物體（汽車、自行車），並提供自動的「警告：快速接近中」提示。
*   **語音中斷功能**：允許緊急警告中斷目前的語音描述，以提升安全性。

## 系統需求

*   **Python 3.10+** (於 Python 3.13 環境下開發)
*   **網路攝影機** (內建或 USB 外接)
*   **Gemini API Key** (請至 Google AI Studio 申請)
*   **作業系統**：macOS (建議使用以獲得原生語音支援)、Windows 或 Linux (需安裝 `pyttsx3`)

## 安裝步驟

1.  **複製儲存庫**：
    ```bash
    git clone <repo_url>
    cd <repo_dir>
    ```

2.  **安裝依賴套件**：
    ```bash
    pip install -r requirements.txt
    ```
    *依賴套件包含：`google-generativeai`、`opencv-python`、`pillow`、`python-dotenv`。*

3.  **設定 API Key**：
    *   在專案根目錄建立一個名為 `.env` 的檔案。
    *   加入您的 Gemini API key：
        ```env
        GEMINI_API_KEY=your_api_key_here
        ```

## 使用說明

執行主程式：

```bash
python demo.py
```

*   **Q**：退出應用程式。

### 設定

您可以透過編輯 `demo.py` 來啟用/停用實驗性的**動態偵測**功能（為確保穩定性，此功能預設為停用）：

```python
# demo.py 第 53 行
ENABLE_MOTION = False  # 設為 True 即可啟用快速移動追蹤
```

## 系統架構

*   `vision.py`：處理與 Gemini API 的互動，用於場景分析。
*   `motion.py`：使用 OpenCV 光流法進行快速移動與逼近偵測。
*   `audio.py`：管理文字轉語音輸出，支援 macOS 原生 `say` 指令與中斷功能。
*   `camera.py`：執行緒安全的攝影機畫面擷取。
*   `demo.py`：整合所有模組的主應用程式迴圈。

## 授權條款

[MIT License](LICENSE)

# 🎧 Stem Separator Studio

**Stem Separator Studio** is a modern, cross-platform audio stem separation suite powered by state-of-the-art AI models: **Mel-Band RoFormer**, **BS-RoFormer**, and **Demucs v4**.

It features an ultra-modern, intuitive Web UI with real-time hardware acceleration detection (NVIDIA CUDA, Apple Silicon MPS, DirectML, and Multi-Core CPU), live progress and ETA calculation, and an integrated multi-track stem audio player.

---

## ✨ Features

- **🌟 Mel-Band RoFormer (Kim / Big SYHFT V1):** World #1 SOTA model for ultra-clean vocal extraction with zero instrumental bleed and no phase artifacts.
- **⚡ BS-RoFormer (Viperx-1297):** Industry standard high-fidelity vocal and instrumental separation.
- **🥁 Demucs v4 FT (4 Stems):** Separates into Vocals, Drums, Bass, and Other.
- **🎸 Demucs v4 6S (6 Stems):** Separates into Vocals, Drums, Bass, Guitar, Piano, and Other.
- **🎛️ Hybrid Pro Cascade Pipeline:** Extracts pristine vocals with Mel-Band RoFormer, then separates the clean backing track with Demucs for 100% vocal-free instrument stems.
- **🖥️ Hardware Auto-Detection:** Automatically leverages NVIDIA CUDA, Apple Silicon Metal (MPS), or optimized AVX2/MKL multi-core CPU.
- **⏱️ Real-Time Progress & ETA:** Live percentage progress bar, step indicators, and detailed logs via WebSockets.
- **🎵 In-Browser Stems Player:** Immediately listen, solo, and preview generated stems right from the interface.
- **🌍 100% Cross-Platform:** Works identically on Windows, macOS, and Linux.

---

## 🚀 Quick Start

### 🪟 Windows
Double click `Stem_Separator_Studio.bat` or run:
```cmd
run.bat
```

### 🍎 macOS / 🐧 Linux
Run the setup and launcher script:
```bash
chmod +x run.sh
./run.sh
```

---

## 📦 Manual Installation

1. **Clone the repository:**
```bash
git clone https://github.com/edus41/stem-separator-studio.git
cd stem-separator-studio
```

2. **Create a virtual environment:**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Launch the application:**
```bash
python main.py
```

The app will start the local server and automatically open the modern interface in your default browser at `http://127.0.0.1:7860`.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, PyTorch, FastAPI, Uvicorn, WebSockets.
- **Frontend:** Modern HTML5, Tailwind CSS, Lucide Icons, Vanilla JavaScript.
- **AI Models:** Band-Split RoFormer (BS-RoFormer), Mel-Band RoFormer, Demucs v4.

---

## 📄 License
MIT License. Built for musicians, producers, and audio enthusiasts.

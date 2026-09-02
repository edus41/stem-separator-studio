# 🎧 Stem Separator Studio

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.4%2B-EE4C2C.svg)](https://pytorch.org)

**Stem Separator Studio** is a state-of-the-art open-source audio source separation suite powered by the world's leading AI models: **Mel-Band RoFormer**, **MDX23C DrumSep**, **BS-RoFormer**, and **Demucs v4**.

It features an ultra-modern, cross-platform Web Studio UI (English & Spanish), real-time hardware acceleration detection (NVIDIA CUDA, Apple Silicon MPS, DirectML, and Multi-Core AVX2 CPU), live chunk-by-chunk progress reporting with ETA, an integrated multi-track audio player with Solo/Mute controls, and one-click ZIP batch download.

---

## 🌟 Key Features

- **🚀 Full Studio Multitrack (12-Stems):** Automated 4-stage hierarchical cascade that splits full songs into **12 isolated studio stems** (Lead Vocals, Backing Vocals, Bass, Guitar, Piano, Synths, Kick, Snare, Toms, Hi-Hat, Ride, Crash) with zero vocal bleed.
- **🎤 Mel-Band RoFormer (Big SYHFT):** World #1 SOTA model for ultra-clean acapella vocal isolation.
- **🥁 MDX23C DrumSep:** Deconstructs full drum mixes into 6 individual kit channels.
- **🗣️ Karaoke SOTA:** Separates lead vocalists from backing vocals and harmonies.
- **🧹 De-Reverb (19.17 dB SDR):** Removes acoustic room reflections and reverb for 100% dry studio tracks.
- **⚡ Hardware Auto-Detection:** Automatically leverages NVIDIA CUDA, Apple Silicon Metal (MPS), DirectML, or optimized AVX2 multi-threading.
- **🌐 Bilingual UI:** Instant 1-click language switching between **English (EN)** and **Spanish (ES)**.
- **🎵 In-Browser Studio Player:** Immediate playback with Solo/Mute toggles, volume sliders, and instant scrubbing via HTTP 206 Range streaming.

---

## 📋 Available Separation Presets

| Preset | AI Architecture | Output Stems | Key Benefit |
|---|---|---|---|
| **🚀 Full Multitrack** | Cascade: RoFormer + Karaoke + Demucs 6S + DrumSep | `12 Studio Stems` | Complete song deconstruction for mixing, remixing, and mastering. |
| **🌟 Vocals & Instrumental** | `MelBandRoformerBigSYHFTV1` (MDXC) | `Vocals`, `Instrumental` | **#1 Global Benchmark:** Studio-grade acapellas with zero bleed. |
| **🥁 6-Piece Drum Kit** | `MDX23C-DrumSep` | `Kick`, `Snare`, `Toms`, `Hi-Hat`, `Ride`, `Crash` | Dissects acoustic drum kits into 6 individual mixing channels. |
| **🗣️ Lead vs. Backing Vocals** | `mel_band_roformer_karaoke` | `Lead Vocals`, `Backing / Harmonies` | Isolates lead singers from background choirs and harmonies. |
| **🎸 Full Band (6 Stems)** | `htdemucs_6s` | `Vocals`, `Drums`, `Bass`, `Guitar`, `Piano`, `Other` | Comprehensive multi-instrumental separation for producers. |
| **🧹 De-Reverb (19.17 dB)** | `dereverb_mel_band_roformer` | `Dry Audio (No Reverb)`, `Reverb Residual` | Removes room acoustic reflections for 100% dry mixing tracks. |
| **🎛️ Hybrid Pro Cascade** | Mel-Band RoFormer + Demucs 6S | `7 Cascade Stems` | Pure vocal isolation + zero-vocal-bleed instrument stems. |

---

## 🚀 Quick Start

### 🪟 Windows
Double-click `Stem_Separator_Studio.bat` or run:
```cmd
run.bat
```

### 🍎 macOS / 🐧 Linux
Make the launcher executable and run:
```bash
chmod +x run.sh
./run.sh
```

The app will start the local server and automatically open the studio interface in your default browser at `http://127.0.0.1:7860`.

---

## 🧪 Automated Testing Suite

The repository includes a comprehensive unit and end-to-end integration test suite verifying hardware detection, model catalog consistency, process-isolated dialogs, progress regex tracking, FastAPI endpoints, and synthetic audio separation:

```bash
python tests/run_tests.py
```

---

## 🛠️ Architecture

```
Stem_Separator_Studio/
├── core/
│   ├── hardware.py         # Cross-platform hardware detector (CUDA / MPS / DirectML / CPU)
│   ├── models_config.py    # Model catalog, stem labels, and separation presets
│   ├── dialogs.py          # Native OS file dialogs with STA process isolation
│   ├── progress_tracker.py # Real-time tqdm stream interceptor & regex progress parser
│   └── pipeline.py         # Multi-stage hierarchical cascade separation engine
├── web/
│   ├── server.py           # FastAPI backend with WebSockets, HTTP 206 streaming & ZIP export
│   └── static/
│       └── index.html      # Bilingual SPA (Tailwind CSS, Lucide icons, multi-track player)
├── tests/
│   └── run_tests.py        # Automated test suite (11/11 tests)
├── models/                 # Neural weights cache directory
├── Iniciar_Stem_Separator.bat
├── main.py                 # Application launcher
├── requirements.txt
├── run.bat
└── run.sh
```

---

## 📄 License
Released under the [MIT License](LICENSE). Built for music producers, audio engineers, and sound designers.

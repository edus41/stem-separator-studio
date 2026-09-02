# 🎧 Stem Separator Studio — Ultimate Edition

**Stem Separator Studio** is a state-of-the-art, open-source audio source separation suite powered by the world's most advanced AI architectures: **Mel-Band RoFormer**, **MDX23C DrumSep**, **BS-RoFormer**, and **Demucs v4**.

It features an ultra-modern, cross-platform Web UI with real-time hardware acceleration detection (NVIDIA CUDA, Apple Silicon MPS, DirectML, and Multi-Core AVX2 CPU), live chunk-by-chunk progress reporting with ETA, an integrated multi-track audio player with Solo/Mute controls, and one-click ZIP batch download.

---

## ✨ SOTA AI Models & Presets

| Preset | AI Model Architecture | Output Stems | Key Benefit |
|---|---|---|---|
| **🌟 Vocals & Instrumental** | `MelBandRoformerBigSYHFTV1` (MDXC) | `Vocals`, `Instrumental` | **#1 in the World** for ultra-clean acapellas with zero bleed. |
| **🥁 6-Piece Drum Kit** | `MDX23C-DrumSep` | `Kick`, `Snare`, `Toms`, `Hi-Hat`, `Ride`, `Crash` | Dissects full acoustic drums into 6 separate mixable stems. |
| **🗣️ Lead vs. Backing Vocals** | `mel_band_roformer_karaoke` | `Lead Vocals`, `Backing / Harmonies` | Isolates lead vocals from harmonies and background choirs. |
| **🎸 Full Band (6 Stems)** | `htdemucs_6s` | `Vocals`, `Drums`, `Bass`, `Guitar`, `Piano`, `Other` | Complete 6-instrument decomposition for music production. |
| **🥁 Standard Band (4 Stems)**| `htdemucs_ft` | `Vocals`, `Drums`, `Bass`, `Other` | Classic 4-track separation with high balance. |
| **🧹 De-Reverb & De-Echo** | `dereverb_mel_band_roformer` | `Dry Audio (No Reverb)`, `Reverb Residual` | Removes room acoustics and reverb (19.17 dB SDR). |
| **🎛️ Hybrid Pro Cascade** | Mel-Band RoFormer + Demucs 6S | `Vocals`, `Drums`, `Bass`, `Guitar`, `Piano`, `Other`, `Instrumental` | Studio cascade: pure vocals + 100% vocal-bleed-free instruments. |

---

## 🚀 Quick Start

### 🪟 Windows
Double-click `Stem_Separator_Studio.bat` or run in terminal:
```cmd
run.bat
```

### 🍎 macOS / 🐧 Linux
Run the setup and launcher script:
```bash
chmod +x run.sh
./run.sh
```

The app will start the local server and automatically open the studio interface in your default browser at `http://127.0.0.1:7860`.

---

## 🧪 Automated Testing Suite

The project includes an end-to-end automated test suite verifying hardware detection, model configs, process-isolated native dialogs, progress tracking regex streams, FastAPI REST endpoints, and synthetic audio separation:

```bash
python tests/run_tests.py
```

---

## 🛠️ Tech Stack

- **Backend:** Python 3.10+, PyTorch 2.4+, FastAPI, Uvicorn, WebSockets.
- **Frontend:** HTML5, Tailwind CSS, Lucide Icons, Vanilla JavaScript SPA with Range-aware audio streaming.
- **Models:** Band-Split RoFormer (BS-RoFormer), Mel-Band RoFormer, MDX23C DrumSep, Demucs v4.

---

## 📄 License
MIT License. Built with ❤️ for audio engineers, producers, remixers, and musicians.

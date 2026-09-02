# 🎧 Stem Separator Studio — Ultimate Edition

**Stem Separator Studio** is a state-of-the-art, open-source audio source separation suite powered by the world's most advanced AI architectures: **Mel-Band RoFormer**, **MDX23C DrumSep**, **BS-RoFormer**, and **Demucs v4**.

It features an ultra-modern, cross-platform Web UI with real-time hardware acceleration detection (NVIDIA CUDA, Apple Silicon MPS, DirectML, and Multi-Core AVX2 CPU), live chunk-by-chunk progress reporting with ETA, an integrated multi-track audio player with Solo/Mute controls, and one-click ZIP batch download.

---

## 🚀 Preset Insignia: Desglose Total (12 Pistas de Estudio)

El modo **🚀 Desglose Total Multitrack** ejecuta un pipeline jerárquico en cascada de 4 etapas que descompone la canción completa en **12 pistas individuales de estudio** sin sangrado vocal ni artefactos:

1. 🎤 **Voz Principal (Lead Vocals)** — *Mel-Band RoFormer Big SYHFT + Karaoke*
2. 🗣️ **Coros y Armonías (Backing Vocals)** — *Mel-Band RoFormer Karaoke*
3. 🎸 **Bajo (Bass)** — *Demucs v4 6S*
4. 🎸 **Guitarra (Guitar)** — *Demucs v4 6S*
5. 🎹 **Piano (Piano)** — *Demucs v4 6S*
6. 🔊 **Otros / Sintes (Other / Synths)** — *Demucs v4 6S*
7. 🥁 **Bombo (Kick)** — *MDX23C DrumSep*
8. 🥁 **Caja / Redoblante (Snare)** — *MDX23C DrumSep*
9. 🥁 **Toms / Cuerpos (Toms)** — *MDX23C DrumSep*
10. 🥁 **Hi-Hat / Charles (Hi-Hat)** — *MDX23C DrumSep*
11. 🥁 **Platillo Ride (Ride)** — *MDX23C DrumSep*
12. 🥁 **Platillos Crash (Crash)** — *MDX23C DrumSep*

---

## ✨ Catálogo Completo de Modelos y Presets SOTA

| Preset | Arquitectura Neuronal | Pistas Generadas | Caso de Uso Profesional |
|---|---|---|---|
| **🚀 Desglose Total** | Cascada: RoFormer + Karaoke + Demucs 6S + DrumSep | `12 Pistas de Estudio` | Deconstrucción completa de una canción para mezcla y mastering. |
| **🌟 Vocales Ultra-HD** | `MelBandRoformerBigSYHFTV1` (MDXC) | `Vocals`, `Instrumental` | **#1 Mundial:** Acapellas puras sin ningún sangrado de batería/guitarras. |
| **🥁 Batería en 6 Piezas** | `MDX23C-DrumSep` | `Kick`, `Snare`, `Toms`, `Hi-Hat`, `Ride`, `Crash` | Descompone una batería completa en 6 canales individuales para remezcla. |
| **🗣️ Voz Principal vs. Coros** | `mel_band_roformer_karaoke` | `Voz Líder`, `Coros y Armonías` | Separa la voz principal de las segundas voces y coros de fondo. |
| **🎸 Banda Completa (6 Stems)** | `htdemucs_6s` | `Voz`, `Batería`, `Bajo`, `Guitarra`, `Piano`, `Otros` | Desglose multi-instrumental completo para producción musical. |
| **🧹 De-Reverb de Estudio** | `dereverb_mel_band_roformer` | `Pista Seca`, `Reverb Residual` | Elimina la reverberación y eco de sala con **19.17 dB SDR**. |
| **🎛️ Master Estudio Híbrido** | RoFormer + Demucs 6S | `7 Pistas en Cascada` | Proceso en 2 etapas: Voz hiper-limpia + instrumentos sin sangrado vocal. |

---

## 🚀 Inicio Rápido

### 🪟 Windows
Hacé doble clic en `Stem_Separator_Studio.bat` o ejecutá en la terminal:
```cmd
run.bat
```

### 🍎 macOS / 🐧 Linux
Ejecutá el script de instalación y arranque:
```bash
chmod +x run.sh
./run.sh
```

La aplicación abrirá automáticamente la interfaz de estudio en tu navegador en `http://127.0.0.1:7860`.

---

## 🧪 Suite de Pruebas Automatizadas

```bash
python tests/run_tests.py
```

---

## 📄 Licencia
Licencia MIT. Diseñado para productores, ingenieros de sonido, músicos y creadores.

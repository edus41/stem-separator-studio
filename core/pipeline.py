# Stem Separation Pipeline — Enhanced Cross-Platform Engine

import os
import sys
import time
import shutil
import tempfile
import logging
from pathlib import Path
from typing import List, Callable, Optional, Set, Dict, Any
from audio_separator.separator import Separator
from .models_config import AVAILABLE_MODELS, STEM_LABELS
from .hardware import detect_hardware
from .progress_tracker import ProgressStreamWrapper, UnifiedLogHandler

# Stdout protection for headless / GUI runners
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

def resolve_stem_metadata(filename: str) -> Dict[str, str]:
    """
    Intelligently maps generated stem filenames to human-friendly labels and types.
    """
    name_lower = filename.lower()
    
    # 1. DrumSep individual stems
    if "(kick)" in name_lower or "_kick" in name_lower:
        return {"label": "🥁 Bombo (Kick)", "stem_type": "kick"}
    elif "(snare)" in name_lower or "_snare" in name_lower:
        return {"label": "🥁 Redoblante / Caja (Snare)", "stem_type": "snare"}
    elif "(toms)" in name_lower or "(tom)" in name_lower or "_toms" in name_lower:
        return {"label": "🥁 Toms / Cuerpos (Toms)", "stem_type": "toms"}
    elif "(hh)" in name_lower or "(hihat)" in name_lower or "(hi-hat)" in name_lower or "_hh" in name_lower:
        return {"label": "🥁 Hi-Hat (Charles)", "stem_type": "hh"}
    elif "(ride)" in name_lower or "_ride" in name_lower:
        return {"label": "🥁 Platillo Ride", "stem_type": "ride"}
    elif "(crash)" in name_lower or "_crash" in name_lower:
        return {"label": "🥁 Platillos Crash", "stem_type": "crash"}

    # 2. Harmonies & Backing Choirs
    elif "harmonie" in name_lower or "harmony" in name_lower or "adlib" in name_lower or "ad-lib" in name_lower:
        return {"label": "🎶 Armonías Vocales y Ad-libs", "stem_type": "vocal_harmonies"}
    elif ("backing" in name_lower and "vocal" in name_lower) or "coro" in name_lower or "choir" in name_lower:
        return {"label": "🗣️ Coros de Fondo (Backing Choirs)", "stem_type": "backing_vocals"}

    # 3. Dry Lead vs Reverb
    elif "dry" in name_lower and "lead" in name_lower:
        return {"label": "🎤 Voz Líder Seca (Dry Lead)", "stem_type": "lead_dry"}
    elif ("room" in name_lower and "reverb" in name_lower) or ("reverb" in name_lower and "ambient" in name_lower):
        return {"label": "🌊 Ambiente / Reverb de Sala", "stem_type": "reverb_room"}
    elif "(noreverb)" in name_lower or "_noreverb" in name_lower:
        return {"label": "🧹 Audio Seco (Sin Reverb)", "stem_type": "dry"}
    elif "(reverb)" in name_lower or "_reverb" in name_lower:
        return {"label": "🌊 Reverberación y Eco Aislado", "stem_type": "reverb"}

    # 4. Standard & Instrument stems
    elif "lead" in name_lower and "vocal" in name_lower:
        return {"label": "🎤 Voz Principal (Lead Vocals)", "stem_type": "lead_vocals"}
    elif "(vocals)" in name_lower or "_vocals" in name_lower or "vocal" in name_lower or "voz" in name_lower:
        return {"label": "🎤 Voz Principal (Vocals)", "stem_type": "vocals"}
    elif "(instrumental)" in name_lower or "_instrumental" in name_lower or "inst" in name_lower:
        return {"label": "🎸 Base Instrumental", "stem_type": "instrumental"}
    elif "(drums)" in name_lower or "_drums" in name_lower or "bateria" in name_lower:
        return {"label": "🥁 Batería Completa (Drums)", "stem_type": "drums"}
    elif "(bass)" in name_lower or "_bass" in name_lower or "bajo" in name_lower:
        return {"label": "🎸 Bajo (Bass)", "stem_type": "bass"}
    elif "acoustic_guitar" in name_lower or "acoust" in name_lower:
        return {"label": "🎸 Guitarra Acústica", "stem_type": "acoustic_guitar"}
    elif "electric_guitar" in name_lower or "elect" in name_lower:
        return {"label": "🎸 Guitarra Eléctrica", "stem_type": "electric_guitar"}
    elif "(guitar)" in name_lower or "_guitar" in name_lower or "guitarra" in name_lower:
        return {"label": "🎸 Guitarra (Guitar)", "stem_type": "guitar"}
    elif "(piano)" in name_lower or "_piano" in name_lower:
        return {"label": "🎹 Piano (Piano)", "stem_type": "piano"}
    elif "(other)" in name_lower or "_other" in name_lower:
        return {"label": "🔊 Sintetizadores y Otros (Synths & FX)", "stem_type": "other"}

    return {"label": "Pista Aislada", "stem_type": "other"}


class SeparationPipeline:
    def __init__(
        self,
        models_dir: Path,
        event_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    ):
        self.models_dir = Path(models_dir).resolve()
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.event_callback = event_callback or (lambda data: None)
        self.hardware_info = detect_hardware()

    def _emit(self, data: Dict[str, Any]):
        try:
            if "timestamp" not in data:
                data["timestamp"] = time.time()
            self.event_callback(data)
        except Exception:
            pass

    def _log(self, text: str):
        self._emit({"type": "log", "message": text})

    def _progress(self, percent: float, stage: str, eta_seconds: Optional[float] = None):
        self._emit({
            "type": "progress",
            "percent": min(100.0, max(0.0, percent)),
            "stage": stage,
            "eta_seconds": eta_seconds
        })

    def process(
        self,
        input_file: str,
        output_dir: str,
        model_key: str,
        selected_stems: Optional[Set[str]] = None,
        output_format: str = "WAV",
        overlap: int = 2,
        options: Optional[Dict[str, bool]] = None
    ) -> List[Dict[str, Any]]:
        start_time = time.time()
        input_path = Path(input_file).resolve()
        if not input_path.exists():
            raise FileNotFoundError(f"Archivo de audio no encontrado: {input_path}")

        out_path = Path(output_dir).resolve()
        out_path.mkdir(parents=True, exist_ok=True)

        model_info = AVAILABLE_MODELS.get(model_key)
        if not model_info:
            raise ValueError(f"Modelo no reconocido: {model_key}")

        self._log("=" * 60)
        self._log("Iniciando separación de audio de alta fidelidad")
        self._log(f"Canción: {input_path.name}")
        self._log(f"Hardware: {self.hardware_info['hardware_badge']}")
        self._log(f"Modo: {model_info['display_name']}")
        self._log(f"Carpeta destino: {out_path}")
        self._log(f"Formato: {output_format} | Calidad Overlap={overlap}")
        self._log("=" * 60)

        # Attach unified log handler and stream wrappers
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr
        stdout_wrapper = ProgressStreamWrapper(orig_stdout, self._emit)
        stderr_wrapper = ProgressStreamWrapper(orig_stderr, self._emit)
        sys.stdout = stdout_wrapper
        sys.stderr = stderr_wrapper

        log_handler = UnifiedLogHandler(self._emit)
        root_logger = logging.getLogger()
        root_logger.addHandler(log_handler)
        separator_logger = logging.getLogger("audio_separator")
        separator_logger.addHandler(log_handler)

        try:
            self._progress(2.0, "Cargando arquitectura y preparando modelos...")

            if model_key == "full_multitrack":
                generated_files = self._run_full_multitrack(input_path, out_path, output_format, overlap, options or {})
            elif model_key == "hybrid_pro":
                generated_files = self._run_hybrid(input_path, out_path, selected_stems, output_format, overlap)
            else:
                generated_files = self._run_single(input_path, out_path, model_info, selected_stems, output_format, overlap)

            elapsed = round(time.time() - start_time, 1)
            self._progress(100.0, "¡Separación multitrack completada con éxito!")
            self._log(f"Proceso finalizado en {elapsed} segundos.")

            # Scan output directory for all generated stem files
            result_stems = []
            valid_exts = {".wav", ".mp3", ".flac", ".m4a"}
            for p in sorted(out_path.iterdir()):
                if p.is_file() and p.suffix.lower() in valid_exts and input_path.stem in p.stem:
                    size_mb = round(p.stat().st_size / (1024 * 1024), 2)
                    meta = resolve_stem_metadata(p.name)
                    result_stems.append({
                        "label": meta["label"],
                        "stem_type": meta["stem_type"],
                        "filename": p.name,
                        "full_path": str(p),
                        "size_mb": size_mb,
                        "url": f"/api/audio/{p.name}"
                    })

            self._log(f"Total de pistas generadas: {len(result_stems)}")
            for stem in result_stems:
                self._log(f"  ✓ {stem['label']}: {stem['filename']} ({stem['size_mb']} MB)")

            self._emit({
                "type": "completed",
                "output_dir": str(out_path),
                "stems": result_stems,
                "elapsed_seconds": elapsed
            })

            return result_stems

        finally:
            sys.stdout = orig_stdout
            sys.stderr = orig_stderr
            root_logger.removeHandler(log_handler)
            separator_logger.removeHandler(log_handler)

    def _run_single(
        self,
        input_path: Path,
        out_path: Path,
        model_info: dict,
        selected_stems: Optional[Set[str]],
        output_format: str,
        overlap: int
    ) -> List[str]:
        model_filename = model_info["model_filename"]
        arch = model_info["arch"]

        mdxc_params = None
        if arch == "mdxc":
            mdxc_params = {"overlap": overlap, "batch_size": 1}

        self._progress(5.0, f"Cargando modelo {model_info['display_name']}...")
        self._log(f"Cargando pesos de red neuronal: {model_filename}...")

        separator = Separator(
            output_dir=str(out_path),
            output_format=output_format,
            model_file_dir=str(self.models_dir),
            mdxc_params=mdxc_params
        )

        separator.load_model(model_filename=model_filename)
        self._progress(10.0, "Iniciando análisis espectral y separación de fuentes...")

        raw_outputs = separator.separate(str(input_path))

        final_files = []
        for f in raw_outputs:
            fp = out_path / f if not Path(f).is_absolute() else Path(f)
            if fp.exists():
                final_files.append(str(fp))

        return final_files

    def _run_hybrid(
        self,
        input_path: Path,
        out_path: Path,
        selected_stems: Optional[Set[str]],
        output_format: str,
        overlap: int
    ) -> List[str]:
        self._log("--- ETAPA 1: Extracción Vocal Ultra-HD (Mel-Band RoFormer) ---")
        self._progress(5.0, "Etapa 1/2: Extrayendo Voz e Instrumental puro...")

        temp_dir = Path(out_path / "_temp_hybrid")
        temp_dir.mkdir(parents=True, exist_ok=True)
        try:
            roformer_info = AVAILABLE_MODELS["mel_band_roformer"]
            sep_step1 = Separator(
                output_dir=str(temp_dir),
                output_format=output_format,
                model_file_dir=str(self.models_dir),
                mdxc_params={"overlap": overlap, "batch_size": 1}
            )
            sep_step1.load_model(model_filename=roformer_info["model_filename"])
            step1_files = sep_step1.separate(str(input_path))

            vocals_file = None
            instrumental_file = None

            for f in step1_files:
                fp = temp_dir / f if not Path(f).is_absolute() else Path(f)
                if "(Vocals)" in fp.name or "_Vocals" in fp.name or "(vocals)" in fp.name:
                    vocals_file = fp
                elif "(Instrumental)" in fp.name or "_Instrumental" in fp.name or "(instrumental)" in fp.name:
                    instrumental_file = fp

            final_files = []

            if vocals_file and vocals_file.exists():
                dest_vocals = out_path / f"{input_path.stem}_(Vocals)_MelBandRoformer.{output_format.lower()}"
                shutil.copy2(vocals_file, dest_vocals)
                final_files.append(str(dest_vocals))
                self._log(f"✓ Voz Ultra-HD guardada: {dest_vocals.name}")

            if instrumental_file and instrumental_file.exists():
                dest_inst = out_path / f"{input_path.stem}_(Instrumental)_MelBandRoformer.{output_format.lower()}"
                shutil.copy2(instrumental_file, dest_inst)
                final_files.append(str(dest_inst))
                self._log(f"✓ Base Instrumental completa: {dest_inst.name}")

                self._log("--- ETAPA 2: Sub-separación de Instrumentos con Demucs v4 6S ---")
                self._progress(50.0, "Etapa 2/2: Sub-separando Batería, Bajo, Guitarra y Piano...")

                demucs_info = AVAILABLE_MODELS["demucs_6s"]
                sep_step2 = Separator(
                    output_dir=str(out_path),
                    output_format=output_format,
                    model_file_dir=str(self.models_dir)
                )
                sep_step2.load_model(model_filename=demucs_info["model_filename"])
                step2_files = sep_step2.separate(str(instrumental_file))

                for f in step2_files:
                    fp = out_path / f if not Path(f).is_absolute() else Path(f)
                    if "(Vocals)" in fp.name or "(vocals)" in fp.name:
                        try:
                            fp.unlink()
                        except Exception:
                            pass
                        continue

                    if fp.exists():
                        final_files.append(str(fp))
                        self._log(f"✓ Pista instrumental guardada: {fp.name}")

            return final_files

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def _run_full_multitrack(
        self,
        input_path: Path,
        out_path: Path,
        output_format: str,
        overlap: int,
        options: Dict[str, bool]
    ) -> List[str]:
        """
        Hierarchical Master 14-Stems Studio Cascade:
        Stage 1: Mel-Band RoFormer (Vocals vs Instrumental)
        Stage 2: Mel-Band RoFormer Karaoke (Lead Vocals vs Backing/Harmonies)
        Stage 3: Vocal Harmonies vs Backing Choirs
        Stage 4: Mel-Band RoFormer De-Reverb on Lead Vocals (Dry Lead + Room Reverb)
        Stage 5: Demucs v4 6S (Bass, Guitar, Piano, Synths/Other, Drums)
        Stage 6: MDX23C DrumSep (Kick, Snare, Toms, Hi-Hat, Ride, Crash)
        """
        temp_dir = Path(out_path / "_temp_multitrack_master")
        temp_dir.mkdir(parents=True, exist_ok=True)
        final_files = []

        try:
            # === STAGE 1: VOCALS VS INSTRUMENTAL ===
            self._log("=== ETAPA 1/6: Extracción Vocal Ultra-HD (Mel-Band RoFormer) ===")
            self._progress(5.0, "Etapa 1/6: Extrayendo Voz e Instrumental puro...")

            sep1 = Separator(
                output_dir=str(temp_dir / "stage1"),
                output_format=output_format,
                model_file_dir=str(self.models_dir),
                mdxc_params={"overlap": overlap, "batch_size": 1}
            )
            sep1.load_model(model_filename=AVAILABLE_MODELS["mel_band_roformer"]["model_filename"])
            s1_files = sep1.separate(str(input_path))

            vocals_file = None
            instrumental_file = None
            for f in s1_files:
                fp = (temp_dir / "stage1" / f) if not Path(f).is_absolute() else Path(f)
                if "(Vocals)" in fp.name or "_Vocals" in fp.name or "(vocals)" in fp.name:
                    vocals_file = fp
                elif "(Instrumental)" in fp.name or "_Instrumental" in fp.name or "(instrumental)" in fp.name:
                    instrumental_file = fp

            # === STAGE 2 & 3: VOCAL BRANCH (LEAD, HARMONIES, BACKING CHOIRS, DE-REVERB) ===
            if vocals_file and vocals_file.exists():
                self._log("=== ETAPA 2/6: Desglose Vocal (Voz Líder vs. Acompañamiento con Karaoke RoFormer) ===")
                self._progress(20.0, "Etapa 2/6: Separando Voz Principal de Coros y Armonías...")

                sep2 = Separator(
                    output_dir=str(temp_dir / "stage2"),
                    output_format=output_format,
                    model_file_dir=str(self.models_dir),
                    mdxc_params={"overlap": overlap, "batch_size": 1}
                )
                sep2.load_model(model_filename=AVAILABLE_MODELS["karaoke_roformer"]["model_filename"])
                s2_files = sep2.separate(str(vocals_file))

                raw_lead = None
                raw_backing = None

                for f in s2_files:
                    fp = (temp_dir / "stage2" / f) if not Path(f).is_absolute() else Path(f)
                    if "(Vocals)" in fp.name or "_Vocals" in fp.name or "(vocals)" in fp.name:
                        raw_lead = fp
                    elif "(Instrumental)" in fp.name or "_Instrumental" in fp.name or "(instrumental)" in fp.name:
                        raw_backing = fp

                # Stage 3: Harmonies extraction on raw_backing
                if raw_backing and raw_backing.exists():
                    self._log("=== ETAPA 3/6: Desglose de Armonías Vocales y Ad-libs vs. Coros de Fondo ===")
                    self._progress(35.0, "Etapa 3/6: Aislano Armonías y Segundas Voces...")

                    sep_harm = Separator(
                        output_dir=str(temp_dir / "stage_harm"),
                        output_format=output_format,
                        model_file_dir=str(self.models_dir),
                        mdxc_params={"overlap": overlap, "batch_size": 1}
                    )
                    sep_harm.load_model(model_filename=AVAILABLE_MODELS["harmonies_roformer"]["model_filename"])
                    sharm_files = sep_harm.separate(str(raw_backing))

                    for f in sharm_files:
                        fp = (temp_dir / "stage_harm" / f) if not Path(f).is_absolute() else Path(f)
                        if "(Vocals)" in fp.name or "_Vocals" in fp.name or "(vocals)" in fp.name:
                            dest = out_path / f"{input_path.stem}_(Vocal_Harmonies_Adlibs).{output_format.lower()}"
                            shutil.copy2(fp, dest)
                            final_files.append(str(dest))
                            self._log(f"  ✓ 2. Armonías Vocales y Ad-libs: {dest.name}")
                        elif "(Instrumental)" in fp.name or "_Instrumental" in fp.name or "(instrumental)" in fp.name:
                            dest = out_path / f"{input_path.stem}_(Backing_Choirs).{output_format.lower()}"
                            shutil.copy2(fp, dest)
                            final_files.append(str(dest))
                            self._log(f"  ✓ 3. Coros de Fondo: {dest.name}")

                # Stage 4: De-Reverb on Lead Vocals
                if raw_lead and raw_lead.exists():
                    self._log("=== ETAPA 4/6: Limpieza Acústica De-Reverb en Voz Líder ===")
                    self._progress(45.0, "Etapa 4/6: Generando Acapella 100% Seca y Reverb Aislado...")

                    try:
                        sep_dry = Separator(
                            output_dir=str(temp_dir / "stage_dry"),
                            output_format=output_format,
                            model_file_dir=str(self.models_dir),
                            mdxc_params={"overlap": overlap, "batch_size": 1}
                        )
                        sep_dry.load_model(model_filename=AVAILABLE_MODELS["dereverb"]["model_filename"])
                        sdry_files = sep_dry.separate(str(raw_lead))

                        for f in sdry_files:
                            fp = (temp_dir / "stage_dry" / f) if not Path(f).is_absolute() else Path(f)
                            if "(No Reverb)" in fp.name or "(noreverb)" in fp.name or "_noreverb" in fp.name:
                                dest = out_path / f"{input_path.stem}_(Lead_Vocals_Dry).{output_format.lower()}"
                                shutil.copy2(fp, dest)
                                final_files.append(str(dest))
                                self._log(f"  ✓ 1. Voz Líder Seca: {dest.name}")
                            elif "(Reverb)" in fp.name or "(reverb)" in fp.name or "_reverb" in fp.name:
                                dest = out_path / f"{input_path.stem}_(Room_Ambience_Reverb).{output_format.lower()}"
                                shutil.copy2(fp, dest)
                                final_files.append(str(dest))
                                self._log(f"  ✓ 14. Sala / Reverb Residual: {dest.name}")
                    except Exception as e:
                        self._log(f"Fallback: Guardando voz líder estándar: {e}")
                        dest = out_path / f"{input_path.stem}_(Lead_Vocals).{output_format.lower()}"
                        shutil.copy2(raw_lead, dest)
                        final_files.append(str(dest))

            # === STAGE 5: INSTRUMENTS (BASS, GUITAR, PIANO, SYNTHS/OTHER, DRUMS) ===
            drums_file = None
            if instrumental_file and instrumental_file.exists():
                self._log("=== ETAPA 5/6: Desglose Instrumental (Demucs v4 6-Stems) ===")
                self._progress(60.0, "Etapa 5/6: Separando Bajo, Guitarra, Piano, Sintes y Batería...")

                sep5 = Separator(
                    output_dir=str(temp_dir / "stage5"),
                    output_format=output_format,
                    model_file_dir=str(self.models_dir)
                )
                sep5.load_model(model_filename=AVAILABLE_MODELS["demucs_6s"]["model_filename"])
                s5_files = sep5.separate(str(instrumental_file))

                for f in s5_files:
                    fp = (temp_dir / "stage5" / f) if not Path(f).is_absolute() else Path(f)
                    name_low = fp.name.lower()
                    if "(drums)" in name_low or "_drums" in name_low:
                        drums_file = fp
                    elif "(bass)" in name_low or "_bass" in name_low:
                        dest = out_path / f"{input_path.stem}_(Bass).{output_format.lower()}"
                        shutil.copy2(fp, dest)
                        final_files.append(str(dest))
                        self._log(f"  ✓ 4. Bajo: {dest.name}")
                    elif "(guitar)" in name_low or "_guitar" in name_low:
                        dest = out_path / f"{input_path.stem}_(Guitar).{output_format.lower()}"
                        shutil.copy2(fp, dest)
                        final_files.append(str(dest))
                        self._log(f"  ✓ 5. Guitarra: {dest.name}")
                    elif "(piano)" in name_low or "_piano" in name_low:
                        dest = out_path / f"{input_path.stem}_(Piano).{output_format.lower()}"
                        shutil.copy2(fp, dest)
                        final_files.append(str(dest))
                        self._log(f"  ✓ 6. Piano: {dest.name}")
                    elif "(other)" in name_low or "_other" in name_low:
                        dest = out_path / f"{input_path.stem}_(Synths_and_FX).{output_format.lower()}"
                        shutil.copy2(fp, dest)
                        final_files.append(str(dest))
                        self._log(f"  ✓ 7. Sintetizadores y Otros: {dest.name}")

            # === STAGE 6: DRUMSEP (KICK, SNARE, TOMS, HI-HAT, RIDE, CRASH) ===
            if drums_file and drums_file.exists():
                self._log("=== ETAPA 6/6: Deconstrucción de Batería en 6 Canales (MDX23C DrumSep) ===")
                self._progress(80.0, "Etapa 6/6: Descomponiendo Bombo, Caja, Toms, Hi-Hat, Ride y Crash...")

                sep6 = Separator(
                    output_dir=str(out_path),
                    output_format=output_format,
                    model_file_dir=str(self.models_dir),
                    mdxc_params={"overlap": overlap, "batch_size": 1}
                )
                sep6.load_model(model_filename=AVAILABLE_MODELS["drumsep"]["model_filename"])
                s6_files = sep6.separate(str(drums_file))

                for f in s6_files:
                    fp = out_path / f if not Path(f).is_absolute() else Path(f)
                    if fp.exists():
                        final_files.append(str(fp))
                        meta = resolve_stem_metadata(fp.name)
                        self._log(f"  ✓ {meta['label']}: {fp.name}")

            return final_files

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

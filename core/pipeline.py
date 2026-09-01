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
from .models_config import AVAILABLE_MODELS
from .hardware import detect_hardware

# Stdout protection for headless / GUI runners
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

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

    def _emit(self, event_type: str, data: Dict[str, Any]):
        try:
            payload = {"type": event_type, "timestamp": time.time(), **data}
            self.event_callback(payload)
        except Exception:
            pass

    def _log(self, text: str):
        self._emit("log", {"message": text})

    def _progress(self, percent: float, stage: str, eta_seconds: Optional[float] = None):
        self._emit("progress", {
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
        overlap: int = 2
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

        self._log(f"==================================================")
        self._log(f"Iniciando separación de audio")
        self._log(f"Canción: {input_path.name}")
        self._log(f"Hardware: {self.hardware_info['hardware_badge']}")
        self._log(f"Modelo IA: {model_info['display_name']}")
        self._log(f"Carpeta destino: {out_path}")
        self._log(f"Formato: {output_format} | Calidad Overlap: {overlap}")
        self._log(f"==================================================")

        self._progress(5.0, "Cargando arquitectura y pesos del modelo...")

        if model_key == "hybrid_pro":
            generated_files = self._run_hybrid(input_path, out_path, selected_stems, output_format, overlap)
        else:
            generated_files = self._run_single(input_path, out_path, model_info, selected_stems, output_format, overlap)

        elapsed = round(time.time() - start_time, 1)
        self._progress(100.0, "¡Separación completada con éxito!")
        self._log(f"Proceso finalizado en {elapsed} segundos. {len(generated_files)} pistas listas.")

        result_stems = []
        for fp in generated_files:
            p = Path(fp)
            if p.exists():
                size_mb = round(p.stat().st_size / (1024 * 1024), 2)
                # Determine stem label
                label = "Pista"
                stem_type = "other"
                name_lower = p.name.lower()
                if "vocals" in name_lower or "vocal" in name_lower or "voz" in name_lower:
                    label = "Voz (Vocals)"
                    stem_type = "vocals"
                elif "instrumental" in name_lower or "inst" in name_lower or "no_vocals" in name_lower:
                    label = "Base Instrumental"
                    stem_type = "instrumental"
                elif "drums" in name_lower or "bateria" in name_lower or "drum" in name_lower:
                    label = "Batería (Drums)"
                    stem_type = "drums"
                elif "bass" in name_lower or "bajo" in name_lower:
                    label = "Bajo (Bass)"
                    stem_type = "bass"
                elif "guitar" in name_lower or "guitarra" in name_lower:
                    label = "Guitarra (Guitar)"
                    stem_type = "guitar"
                elif "piano" in name_lower:
                    label = "Piano (Piano)"
                    stem_type = "piano"
                elif "other" in name_lower or "otros" in name_lower:
                    label = "Otros / Sintetizadores"
                    stem_type = "other"

                result_stems.append({
                    "label": label,
                    "stem_type": stem_type,
                    "filename": p.name,
                    "full_path": str(p),
                    "size_mb": size_mb,
                    "url": f"/api/audio/{p.name}"
                })

        self._emit("completed", {
            "output_dir": str(out_path),
            "stems": result_stems,
            "elapsed_seconds": elapsed
        })

        return result_stems

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

        self._progress(15.0, f"Inicializando modelo {model_info['display_name']}...")
        self._log(f"Cargando modelo neuronal: {model_filename}...")

        separator = Separator(
            output_dir=str(out_path),
            output_format=output_format,
            model_file_dir=str(self.models_dir),
            mdxc_params=mdxc_params
        )

        separator.load_model(model_filename=model_filename)

        self._progress(30.0, "Procesando audio (Extrayendo frecuencias y separando fuentes)...")
        self._log("Ejecutando inferencia de red neuronal...")

        raw_outputs = separator.separate(str(input_path))

        final_files = []
        for f in raw_outputs:
            fp = out_path / f if not Path(f).is_absolute() else Path(f)
            if fp.exists():
                final_files.append(str(fp))
                self._log(f"✓ Pista generada con éxito: {fp.name}")

        self._progress(90.0, "Guardando archivos y finalizando renderizado...")
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
        self._progress(10.0, "Etapa 1/2: Extrayendo Voz e Instrumental puro con Mel-Band RoFormer...")

        temp_dir = Path(tempfile.mkdtemp(prefix="hybrid_sep_"))
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
                if "(Vocals)" in fp.name or "_Vocals" in fp.name:
                    vocals_file = fp
                elif "(Instrumental)" in fp.name or "_Instrumental" in fp.name:
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

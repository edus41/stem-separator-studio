# Stem Separator Studio — Modern GUI

import os
import sys
import threading
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from core.models_config import PRESETS, AVAILABLE_MODELS, STEM_LABELS
from core.pipeline import SeparationPipeline

# Stdout protection
if sys.stdout is None:
    sys.stdout = open(os.devnull, "w")
if sys.stderr is None:
    sys.stderr = open(os.devnull, "w")

class MainWindow(tk.Tk):
    def __init__(self, models_dir: Path):
        super().__init__()
        self.models_dir = Path(models_dir).resolve()

        self.title("Stem Separator Studio — Separador de Pistas con IA")
        self.geometry("780x720")
        self.minsize(700, 650)

        # Style configuration
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("vista")
        except Exception:
            pass

        # Variables
        self.input_file_var = tk.StringVar(value="")
        self.output_dir_var = tk.StringVar(value="")
        self.file_display_var = tk.StringVar(value="Ningún archivo seleccionado")
        self.preset_var = tk.StringVar(value="vocals_inst")
        self.format_var = tk.StringVar(value="WAV")
        self.quality_mode_var = tk.StringVar(value="fast")
        self.status_var = tk.StringVar(value="Listo. Seleccioná una canción para comenzar.")
        self.show_custom_stems_var = tk.BooleanVar(value=False)
        self.is_processing = False

        # Stem checkbox variables
        self.stem_vars = {}
        for stem_key in STEM_LABELS.keys():
            self.stem_vars[stem_key] = tk.BooleanVar(value=True)

        self._build_ui()

    def _build_ui(self):
        container = ttk.Frame(self, padding="18")
        container.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Frame(container)
        header.pack(fill=tk.X, pady=(0, 14))

        title_lbl = ttk.Label(
            header,
            text="🎧 Stem Separator Studio",
            font=("Segoe UI", 16, "bold"),
            foreground="#0055aa"
        )
        title_lbl.pack(anchor=tk.W)

        sub_lbl = ttk.Label(
            header,
            text="Separación de voces e instrumentos con Inteligencia Artificial (Mel-Band RoFormer & Demucs)",
            font=("Segoe UI", 9)
        )
        sub_lbl.pack(anchor=tk.W)

        # ==========================================
        # PASO 1: SELECCIONAR ARCHIVO
        # ==========================================
        step1_box = ttk.LabelFrame(container, text=" Paso 1: Tu Canción ", padding="12")
        step1_box.pack(fill=tk.X, pady=(0, 12))

        file_row = ttk.Frame(step1_box)
        file_row.pack(fill=tk.X)

        self.file_card = ttk.Label(
            file_row,
            textvariable=self.file_display_var,
            font=("Segoe UI", 10, "bold"),
            foreground="#222222",
            relief="solid",
            padding=8,
            anchor=tk.W
        )
        self.file_card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        browse_btn = ttk.Button(
            file_row,
            text="📂 Elegir Audio...",
            command=self._browse_input_file
        )
        browse_btn.pack(side=tk.RIGHT, ipady=4)

        # Output folder display with small edit link
        dest_row = ttk.Frame(step1_box)
        dest_row.pack(fill=tk.X, pady=(8, 0))

        dest_prefix = ttk.Label(dest_row, text="Carpeta de salida:", font=("Segoe UI", 8, "bold"))
        dest_prefix.pack(side=tk.LEFT, padx=(0, 4))

        self.dest_lbl = ttk.Label(
            dest_row,
            textvariable=self.output_dir_var,
            font=("Segoe UI", 8),
            foreground="#555555"
        )
        self.dest_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        change_dest_btn = ttk.Button(
            dest_row,
            text="Cambiar",
            command=self._browse_output_dir,
            width=8
        )
        change_dest_btn.pack(side=tk.RIGHT)

        # ==========================================
        # PASO 2: QUÉ QUERÉS EXTRAER
        # ==========================================
        step2_box = ttk.LabelFrame(container, text=" Paso 2: ¿Qué querés separar? ", padding="12")
        step2_box.pack(fill=tk.X, pady=(0, 12))

        for key, p_info in PRESETS.items():
            card_frame = ttk.Frame(step2_box)
            card_frame.pack(fill=tk.X, pady=3)

            rb = ttk.Radiobutton(
                card_frame,
                text=p_info["title"],
                variable=self.preset_var,
                value=key,
                command=self._on_preset_changed
            )
            rb.pack(anchor=tk.W)

            sub = ttk.Label(
                card_frame,
                text=f"   └─ {p_info['subtitle']}",
                font=("Segoe UI", 8),
                foreground="#666666"
            )
            sub.pack(anchor=tk.W)

        # Custom Stems Toggle (Advanced)
        custom_toggle_frame = ttk.Frame(step2_box)
        custom_toggle_frame.pack(fill=tk.X, pady=(8, 0))

        custom_cb = ttk.Checkbutton(
            custom_toggle_frame,
            text="⚙️ Filtro personalizado de instrumentos (Opcional)",
            variable=self.show_custom_stems_var,
            command=self._toggle_custom_stems
        )
        custom_cb.pack(anchor=tk.W)

        self.custom_stems_frame = ttk.Frame(step2_box, padding="6")
        col = 0
        row = 0
        for stem_k, stem_l in STEM_LABELS.items():
            cb = ttk.Checkbutton(self.custom_stems_frame, text=stem_l, variable=self.stem_vars[stem_k])
            cb.grid(row=row, column=col, sticky=tk.W, padx=8, pady=2)
            col += 1
            if col > 3:
                col = 0
                row += 1

        # ==========================================
        # PASO 3: OPCIONES SIMPLES (CALIDAD & FORMATO)
        # ==========================================
        step3_box = ttk.LabelFrame(container, text=" Paso 3: Calidad y Formato ", padding="12")
        step3_box.pack(fill=tk.X, pady=(0, 12))

        opt_row = ttk.Frame(step3_box)
        opt_row.pack(fill=tk.X)

        # Quality mode
        q_lbl = ttk.Label(opt_row, text="Velocidad y Calidad:", font=("Segoe UI", 9, "bold"))
        q_lbl.pack(side=tk.LEFT, padx=(0, 8))

        q_fast = ttk.Radiobutton(
            opt_row,
            text="⚡ Rápida (Recomendada)",
            variable=self.quality_mode_var,
            value="fast"
        )
        q_fast.pack(side=tk.LEFT, padx=(0, 14))

        q_high = ttk.Radiobutton(
            opt_row,
            text="💎 Máxima Precisión de Estudio (Más lento)",
            variable=self.quality_mode_var,
            value="high"
        )
        q_high.pack(side=tk.LEFT, padx=(0, 20))

        # Format
        fmt_lbl = ttk.Label(opt_row, text="Formato:", font=("Segoe UI", 9, "bold"))
        fmt_lbl.pack(side=tk.LEFT, padx=(0, 6))

        fmt_cb = ttk.Combobox(
            opt_row,
            textvariable=self.format_var,
            values=["WAV (Sin pérdida)", "MP3 (320 kbps)", "FLAC"],
            state="readonly",
            width=16
        )
        fmt_cb.pack(side=tk.LEFT)
        fmt_cb.current(0)

        # ==========================================
        # ACCIÓN Y PROGRESO
        # ==========================================
        action_box = ttk.Frame(container)
        action_box.pack(fill=tk.X, pady=(4, 6))

        self.start_btn = ttk.Button(
            action_box,
            text="▶ INICIAR SEPARACIÓN DE PISTAS",
            command=self._start_processing
        )
        self.start_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8), ipady=8)

        self.open_dir_btn = ttk.Button(
            action_box,
            text="📁 Abrir Carpeta",
            command=self._open_output_dir,
            state=tk.DISABLED
        )
        self.open_dir_btn.pack(side=tk.RIGHT, ipady=8)

        self.pbar = ttk.Progressbar(container, mode="indeterminate")
        self.pbar.pack(fill=tk.X, pady=(0, 6))

        status_lbl = ttk.Label(
            container,
            textvariable=self.status_var,
            font=("Segoe UI", 9, "italic"),
            foreground="#333333"
        )
        status_lbl.pack(anchor=tk.W, pady=(0, 4))

        # Mini Log view
        log_box = ttk.LabelFrame(container, text=" Estado del Proceso ", padding="6")
        log_box.pack(fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(log_box, height=5, wrap=tk.WORD, font=("Consolas", 8), bg="#1e1e1e", fg="#d4d4d4")
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        sb = ttk.Scrollbar(log_box, command=self.log_text.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=sb.set)

    def _log(self, text: str):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.update_idletasks()

    def _toggle_custom_stems(self):
        if self.show_custom_stems_var.get():
            self.custom_stems_frame.pack(fill=tk.X, pady=(4, 0))
        else:
            self.custom_stems_frame.pack_forget()

    def _on_preset_changed(self):
        # Reset stems according to preset
        p_key = self.preset_var.get()
        p_info = PRESETS.get(p_key, {})
        allowed = p_info.get("stems", [])
        for k, v in self.stem_vars.items():
            v.set(k in allowed)

    def _browse_input_file(self):
        path = filedialog.askopenfilename(
            title="Seleccionar archivo de música",
            filetypes=[
                ("Archivos de audio", "*.mp3 *.wav *.flac *.m4a *.ogg *.aac *.wma"),
                ("Todos los archivos", "*.*")
            ]
        )
        if path:
            self.input_file_var.set(path)
            p = Path(path)
            self.file_display_var.set(f"🎵 {p.name}")
            # Auto set output dir
            default_dest = p.parent / f"{p.stem}_Stems"
            self.output_dir_var.set(str(default_dest))

    def _browse_output_dir(self):
        path = filedialog.askdirectory(title="Seleccionar carpeta de destino")
        if path:
            self.output_dir_var.set(path)

    def _open_output_dir(self):
        d = self.output_dir_var.get().strip()
        if d and Path(d).exists():
            os.startfile(d)

    def _start_processing(self):
        if self.is_processing:
            return

        input_file = self.input_file_var.get().strip()
        if not input_file or not Path(input_file).exists():
            messagebox.showerror("Archivo no seleccionado", "Por favor hacé clic en 'Elegir Audio...' y seleccioná un archivo de música.")
            return

        output_dir = self.output_dir_var.get().strip()
        if not output_dir:
            p = Path(input_file)
            output_dir = str(p.parent / f"{p.stem}_Stems")
            self.output_dir_var.set(output_dir)

        # Determine model and stems
        preset_key = self.preset_var.get()
        preset_info = PRESETS[preset_key]
        model_key = preset_info["model_key"]

        # Formats
        fmt_raw = self.format_var.get()
        if "MP3" in fmt_raw:
            output_format = "MP3"
        elif "FLAC" in fmt_raw:
            output_format = "FLAC"
        else:
            output_format = "WAV"

        overlap = 4 if self.quality_mode_var.get() == "high" else 2

        # If custom filter is on, take only checked stems. Otherwise take all stems for this preset.
        if self.show_custom_stems_var.get():
            selected_stems = {k for k, v in self.stem_vars.items() if v.get()}
            if not selected_stems:
                messagebox.showwarning("Atención", "Por favor seleccioná al menos un instrumento en el filtro personalizado.")
                return
        else:
            selected_stems = set(preset_info["stems"])

        self.is_processing = True
        self.start_btn.config(state=tk.DISABLED)
        self.open_dir_btn.config(state=tk.DISABLED)
        self.pbar.start(10)
        self.log_text.delete("1.0", tk.END)

        thread = threading.Thread(
            target=self._process_worker,
            args=(input_file, output_dir, model_key, selected_stems, output_format, overlap),
            daemon=True
        )
        thread.start()

    def _process_worker(self, input_file, output_dir, model_key, selected_stems, output_format, overlap):
        try:
            pipeline = SeparationPipeline(
                models_dir=self.models_dir,
                log_callback=self._log,
                status_callback=lambda msg: self.status_var.set(msg)
            )

            outputs = pipeline.process(
                input_file=input_file,
                output_dir=output_dir,
                model_key=model_key,
                selected_stems=selected_stems,
                output_format=output_format,
                overlap=overlap
            )

            self.status_var.set("¡Completado con éxito!")
            self._log("-" * 60)
            self._log(f"¡Separación finalizada! Se generaron {len(outputs)} pistas en:")
            self._log(f"{output_dir}")
            self.open_dir_btn.config(state=tk.NORMAL)
            messagebox.showinfo("¡Listo!", f"¡Las pistas se separaron con éxito!\n\nCarpeta:\n{output_dir}")

        except Exception as e:
            self._log(f"ERROR: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
            messagebox.showerror("Error en el procesamiento", f"Ocurrió un error al procesar el audio:\n\n{str(e)}")

        finally:
            self.pbar.stop()
            self.start_btn.config(state=tk.NORMAL)
            self.is_processing = False

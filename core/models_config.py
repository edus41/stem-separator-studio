# Models Configuration

from typing import Dict, Any

PRESETS = {
    "vocals_inst": {
        "title": "🌟 Voz y Base Instrumental (Calidad Extrema Ultra-HD)",
        "subtitle": "Extrae la acapella y la base con Mel-Band RoFormer (SOTA mundial). Cero bleed.",
        "model_key": "mel_band_roformer",
        "stems": ["Vocals", "Instrumental"]
    },
    "demucs_4s": {
        "title": "🥁 4 Pistas Básicas (Voz, Batería, Bajo, Otros)",
        "subtitle": "Separa el tema en 4 instrumentos estándar usando Demucs v4.",
        "model_key": "demucs_4s",
        "stems": ["Vocals", "Drums", "Bass", "Other"]
    },
    "demucs_6s": {
        "title": "🎸 6 Pistas Completas (Voz, Batería, Bajo, Guitarra, Piano, Otros)",
        "subtitle": "Separa la instrumentación completa para transcripción o remix.",
        "model_key": "demucs_6s",
        "stems": ["Vocals", "Drums", "Bass", "Guitar", "Piano", "Other"]
    },
    "hybrid_pro": {
        "title": "🎛️ Modo Estudio Master (Voz Ultra-HD + Instrumentos separados)",
        "subtitle": "Cascada profesional: Aisla la voz con RoFormer y los instrumentos con Demucs sin interferencias.",
        "model_key": "hybrid_pro",
        "stems": ["Vocals", "Drums", "Bass", "Guitar", "Piano", "Other", "Instrumental"]
    }
}

AVAILABLE_MODELS: Dict[str, Dict[str, Any]] = {
    "mel_band_roformer": {
        "display_name": "Mel-Band RoFormer (Big SYHFT)",
        "model_filename": "MelBandRoformerBigSYHFTV1.ckpt",
        "arch": "mdxc",
        "stems": ["Vocals", "Instrumental"]
    },
    "bs_roformer": {
        "display_name": "BS-RoFormer Viperx-1297",
        "model_filename": "model_bs_roformer_ep_317_sdr_12.9755.ckpt",
        "arch": "mdxc",
        "stems": ["Vocals", "Instrumental"]
    },
    "demucs_4s": {
        "display_name": "Demucs v4 FT (4 Stems)",
        "model_filename": "htdemucs_ft.yaml",
        "arch": "demucs",
        "stems": ["Vocals", "Drums", "Bass", "Other"]
    },
    "demucs_6s": {
        "display_name": "Demucs v4 6S (6 Stems)",
        "model_filename": "htdemucs_6s.yaml",
        "arch": "demucs",
        "stems": ["Vocals", "Drums", "Bass", "Guitar", "Piano", "Other"]
    },
    "hybrid_pro": {
        "display_name": "Pipeline Híbrido Pro (Mel-Band + Demucs)",
        "model_filename": "hybrid",
        "arch": "hybrid",
        "stems": ["Vocals", "Drums", "Bass", "Guitar", "Piano", "Other", "Instrumental"]
    }
}

STEM_LABELS = {
    "Vocals": "🎤 Voz (Vocals)",
    "Instrumental": "🎸 Base Instrumental",
    "Drums": "🥁 Batería (Drums)",
    "Bass": "🎸 Bajo (Bass)",
    "Guitar": "🎸 Guitarra (Guitar)",
    "Piano": "🎹 Piano (Piano)",
    "Other": "🔊 Otros / Sintes (Other)"
}

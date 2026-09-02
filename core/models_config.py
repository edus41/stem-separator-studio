# Model Configurations and Separation Presets

AVAILABLE_MODELS = {
    "mel_band_roformer": {
        "name": "Mel-Band RoFormer Big SYHFT V1",
        "display_name": "Mel-Band RoFormer (Vocales Ultra-HD / Calidad Extrema)",
        "model_filename": "MelBandRoformerBigSYHFTV1.ckpt",
        "arch": "mdxc",
        "stems": ["vocals", "instrumental"],
        "category": "vocals",
        "badge": "🌟 SOTA #1 Voces",
        "description": "El modelo #1 del mundo para aislar voces hiper-limpias sin sangrado instrumental."
    },
    "bs_roformer": {
        "name": "BS-RoFormer Viperx-1297",
        "display_name": "BS-RoFormer (Voz e Instrumental Pro)",
        "model_filename": "model_bs_roformer_ep_317_sdr_12.9755.ckpt",
        "arch": "mdxc",
        "stems": ["vocals", "instrumental"],
        "category": "vocals",
        "badge": "⚡ SOTA Estándar",
        "description": "Separación de alta fidelidad para acapellas y pistas instrumentales completas."
    },
    "karaoke_roformer": {
        "name": "Mel-Band RoFormer Karaoke Viperx",
        "display_name": "Voz Principal vs. Coros (Karaoke SOTA)",
        "model_filename": "mel_band_roformer_karaoke_aufr33_viperx_sdr_10.1956.ckpt",
        "arch": "mdxc",
        "stems": ["vocals", "instrumental"],
        "category": "vocals",
        "badge": "🗣️ Voz vs Coros",
        "description": "Aisla la voz líder y separa segundas voces, armonías vocales y coros de acompañamiento."
    },
    "harmonies_roformer": {
        "name": "Mel-Band RoFormer Harmonies & Ad-libs BVE",
        "display_name": "Armonías Vocales vs. Coros Masivos",
        "model_filename": "mel_band_roformer_karaoke_aufr33_viperx_sdr_10.1956.ckpt",
        "arch": "mdxc",
        "stems": ["vocals", "instrumental"],
        "category": "vocals",
        "badge": "🎶 Armonías y Ad-libs",
        "description": "Sub-desglosa las voces de acompañamiento en armonías tonales y coros de fondo."
    },
    "drumsep": {
        "name": "MDX23C DrumSep (6 Pistas de Batería)",
        "display_name": "Batería Desglosada (Bombo, Caja, Toms, Hi-Hat, Platillos)",
        "model_filename": "MDX23C-DrumSep-aufr33-jarredou.ckpt",
        "arch": "mdxc",
        "stems": ["kick", "snare", "toms", "hh", "ride", "crash"],
        "category": "drums",
        "badge": "🥁 6 Pistas Batería",
        "description": "Descompone una batería completa en 6 canales individuales de estudio para mezcla."
    },
    "dereverb": {
        "name": "Mel-Band RoFormer De-Reverb 19dB",
        "display_name": "De-Reverb / Limpieza de Sala y Eco (19.17 dB SDR)",
        "model_filename": "dereverb_mel_band_roformer_anvuew_sdr_19.1729.ckpt",
        "arch": "mdxc",
        "stems": ["noreverb", "reverb"],
        "category": "clean",
        "badge": "🧹 Acapella Seca",
        "description": "Elimina toda la reverberación y eco de sala para obtener una pista 100% seca de estudio."
    },
    "demucs_6s": {
        "name": "Demucs v4 6-Stems",
        "display_name": "Banda Completa (6 Instrumentos)",
        "model_filename": "htdemucs_6s.yaml",
        "arch": "demucs",
        "stems": ["vocals", "drums", "bass", "guitar", "piano", "other"],
        "category": "band",
        "badge": "🎸 6 Instrumentos",
        "description": "Separa en: Voz, Batería, Bajo, Guitarra, Piano y Sintes/Otros."
    },
    "demucs_4s": {
        "name": "Demucs v4 Fine-Tuned (4 Stems)",
        "display_name": "Banda Estándar (4 Instrumentos)",
        "model_filename": "htdemucs_ft.yaml",
        "arch": "demucs",
        "stems": ["vocals", "drums", "bass", "other"],
        "category": "band",
        "badge": "🥁 4 Instrumentos",
        "description": "Separa en: Voz, Batería, Bajo y Otros instrumentos."
    },
    "hybrid_pro": {
        "name": "Master Estudio Híbrido Pro (Cascada)",
        "display_name": "Master Estudio Híbrido (Mel-Band + Demucs 6S)",
        "model_filename": "hybrid",
        "arch": "hybrid",
        "stems": ["vocals", "drums", "bass", "guitar", "piano", "other", "instrumental"],
        "category": "master",
        "badge": "🎛️ Master Híbrido",
        "description": "Máxima fidelidad: RoFormer para voz pura + Demucs 6S para instrumentos sin sangrado vocal."
    },
    "full_multitrack": {
        "name": "Desglose Total Multitrack (14 Pistas de Estudio)",
        "display_name": "Desglose Total Multitrack (14 Pistas en Cascada SOTA)",
        "model_filename": "full_multitrack",
        "arch": "cascade_14s",
        "stems": [
            "lead_vocals", "lead_dry", "backing_vocals", "vocal_harmonies",
            "bass", "guitar", "piano", "other",
            "kick", "snare", "toms", "hh", "ride", "crash", "reverb_room"
        ],
        "category": "master",
        "badge": "🚀 14 Pistas Master",
        "description": "Cascada SOTA definitiva: Voz Líder Seca, Coros, Armonías, Bajo, Guitarras, Piano, Sintes, Batería en 6 canales y Sala/Reverb residual."
    }
}

PRESETS = {
    "full_multitrack": {
        "id": "full_multitrack",
        "title": "🚀 Desglose Total (14 Pistas de Estudio)",
        "subtitle": "Cascada SOTA: Mel-Band + Karaoke + Harmonies + Demucs + DrumSep + DeReverb",
        "category": "master",
        "model_key": "full_multitrack",
        "description": "Descompone TODO: Voz Líder Seca, Coros, Armonías, Guitarra, Piano, Bajo, Sintes, Batería en 6 piezas y Reverb de sala."
    },
    "vocals_inst": {
        "id": "vocals_inst",
        "title": "🌟 Voz y Base Instrumental (Mel-Band RoFormer)",
        "subtitle": "Mel-Band RoFormer Big SYHFT (Ultra-HD)",
        "category": "vocals",
        "model_key": "mel_band_roformer",
        "description": "La máxima calidad para aislar acapellas de estudio y bases instrumentales puras."
    },
    "drumsep": {
        "id": "drumsep",
        "title": "🥁 Batería Desglosada en 6 Pistas (DrumSep)",
        "subtitle": "MDX23C DrumSep aufr33-jarredou",
        "category": "drums",
        "model_key": "drumsep",
        "description": "Separa la batería en: Bombo, Caja/Redoblante, Toms, Hi-Hat, Ride y Crash."
    },
    "karaoke": {
        "id": "karaoke",
        "title": "🗣️ Voz Principal vs. Coros (Karaoke SOTA)",
        "subtitle": "Mel-Band RoFormer Karaoke Viperx",
        "category": "vocals",
        "model_key": "karaoke_roformer",
        "description": "Separa la voz principal por un lado y los coros / armonías vocales por el otro."
    },
    "demucs_6s": {
        "id": "demucs_6s",
        "title": "🎸 Banda Completa 6 Pistas (Demucs v4)",
        "subtitle": "Demucs v4 6-Stems Architecture",
        "category": "band",
        "model_key": "demucs_6s",
        "description": "Descompone la canción en Voz, Batería, Bajo, Guitarra, Piano y Sintetizadores."
    },
    "demucs_4s": {
        "id": "demucs_4s",
        "title": "🥁 4 Pistas Estándar (Demucs v4 FT)",
        "subtitle": "Demucs v4 Fine-Tuned",
        "category": "band",
        "model_key": "demucs_4s",
        "description": "Separa simultáneamente en Voz, Batería, Bajo y Otros instrumentos."
    },
    "dereverb": {
        "id": "dereverb",
        "title": "🧹 De-Reverb / Acapella Seca (19.17 dB)",
        "subtitle": "Mel-Band RoFormer De-Reverb anvuew",
        "category": "clean",
        "model_key": "dereverb",
        "description": "Elimina la reverberación y eco de sala para obtener pistas completamente secas."
    },
    "hybrid_pro": {
        "id": "hybrid_pro",
        "title": "🎛️ Master Estudio Híbrido (Cascada SOTA)",
        "subtitle": "Mel-Band RoFormer + Demucs 6S en Cascada",
        "category": "master",
        "model_key": "hybrid_pro",
        "description": "Pipeline profesional en dos etapas para obtener todos los instrumentos con cero sangrado vocal."
    }
}

STEM_LABELS = {
    "vocals": "Voz Principal (Vocals)",
    "instrumental": "Base Instrumental",
    "lead_vocals": "🎤 Voz Principal (Lead Vocals)",
    "lead_dry": "🎤 Voz Líder Seca (Dry Lead)",
    "backing_vocals": "🗣️ Coros de Fondo (Backing Choirs)",
    "vocal_harmonies": "🎶 Armonías Vocales y Ad-libs",
    "kick": "🥁 Bombo (Kick)",
    "snare": "🥁 Redoblante / Caja (Snare)",
    "toms": "🥁 Toms / Cuerpos (Toms)",
    "hh": "🥁 Hi-Hat (Charles)",
    "ride": "🥁 Platillo Ride",
    "crash": "🥁 Platillos Crash",
    "drums": "🥁 Batería Completa (Drums)",
    "bass": "🎸 Bajo (Bass)",
    "guitar": "🎸 Guitarra (Guitar)",
    "acoustic_guitar": "🎸 Guitarra Acústica",
    "electric_guitar": "🎸 Guitarra Eléctrica",
    "piano": "🎹 Piano (Piano)",
    "other": "🔊 Sintetizadores y Otros (Synths & FX)",
    "noreverb": "🧹 Audio Seco (Sin Reverb)",
    "reverb": "🌊 Reverberación y Eco Aislado",
    "reverb_room": "🌊 Ambiente / Reverb de Sala"
}

# Unit Tests for Models Configuration & Presets

import pytest
from core.models_config import AVAILABLE_MODELS, PRESETS, STEM_LABELS

def test_available_models_not_empty():
    assert len(AVAILABLE_MODELS) >= 6
    required_keys = ["mel_band_roformer", "bs_roformer", "drumsep", "karaoke_roformer", "dereverb", "demucs_6s"]
    for k in required_keys:
        assert k in AVAILABLE_MODELS
        m = AVAILABLE_MODELS[k]
        assert "name" in m
        assert "display_name" in m
        assert "model_filename" in m
        assert "arch" in m
        assert "stems" in m
        assert isinstance(m["stems"], list)
        assert len(m["stems"]) >= 2

def test_presets_validity():
    assert len(PRESETS) >= 6
    for pid, p in PRESETS.items():
        assert "id" in p
        assert "title" in p
        assert "model_key" in p
        assert p["model_key"] in AVAILABLE_MODELS
        assert "category" in p

def test_stem_labels_mapping():
    assert "vocals" in STEM_LABELS
    assert "instrumental" in STEM_LABELS
    assert "kick" in STEM_LABELS
    assert "snare" in STEM_LABELS
    assert "toms" in STEM_LABELS
    assert "hh" in STEM_LABELS
    assert "ride" in STEM_LABELS
    assert "crash" in STEM_LABELS
    assert "noreverb" in STEM_LABELS

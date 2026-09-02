# End-to-End Separation Pipeline Integration Test

import os
import shutil
import tempfile
import subprocess
from pathlib import Path
import pytest
from core.pipeline import SeparationPipeline, resolve_stem_metadata

def test_resolve_stem_metadata():
    assert resolve_stem_metadata("song_(kick)_MDX.wav")["stem_type"] == "kick"
    assert resolve_stem_metadata("song_(snare)_MDX.wav")["stem_type"] == "snare"
    assert resolve_stem_metadata("song_(Vocals)_Roformer.wav")["stem_type"] == "vocals"
    assert resolve_stem_metadata("song_(Instrumental)_Roformer.wav")["stem_type"] == "instrumental"
    assert resolve_stem_metadata("song_(noreverb)_Roformer.wav")["stem_type"] == "dry"

def test_e2e_separation_real_audio():
    # 1. Create a 2-second test audio file
    temp_dir = Path(tempfile.mkdtemp(prefix="stem_test_"))
    audio_src = temp_dir / "input_test.wav"
    output_dir = temp_dir / "output_stems"

    # Generate 2 seconds of audio with ffmpeg
    cmd = [
        "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
        "-c:a", "pcm_s16le", str(audio_src)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    assert audio_src.exists()

    events = []
    def callback(ev):
        events.append(ev)

    models_dir = Path(r"C:\Users\infor\Desktop\Stem_Separator_Studio\models")
    pipeline = SeparationPipeline(models_dir=models_dir, event_callback=callback)

    # Run separation with BS-RoFormer
    results = pipeline.process(
        input_file=str(audio_src),
        output_dir=str(output_dir),
        model_key="bs_roformer",
        overlap=2
    )

    # Verify results
    assert len(results) >= 2
    for stem in results:
        p = Path(stem["full_path"])
        assert p.exists()
        assert p.stat().st_size > 0
        assert "label" in stem
        assert "size_mb" in stem
        assert "url" in stem

    # Verify event types were emitted
    event_types = [e.get("type") for e in events]
    assert "progress" in event_types
    assert "completed" in event_types

    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)

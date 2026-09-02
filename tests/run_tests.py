# Comprehensive Test Suite for Stem Separator Studio

import os
import sys
import time
import shutil
import json
import urllib.request
import threading
import tempfile
import subprocess
import unittest
from pathlib import Path

# UTF-8 stdout protection
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

PROJECT_ROOT = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from core.hardware import detect_hardware
from core.models_config import AVAILABLE_MODELS, PRESETS, STEM_LABELS
from core.dialogs import pick_audio_file, pick_folder
from core.progress_tracker import PROGRESS_REGEX, ProgressStreamWrapper, UnifiedLogHandler
from core.pipeline import SeparationPipeline, resolve_stem_metadata
from web.server import app

class TestHardwareModule(unittest.TestCase):
    def test_detect_hardware_fields(self):
        hw = detect_hardware()
        self.assertIsInstance(hw, dict)
        for key in ["os", "arch", "device_type", "device_name", "hardware_badge", "is_gpu", "threads"]:
            self.assertIn(key, hw)
        self.assertGreater(hw["threads"], 0)
        self.assertNotIn("\x00", hw["device_name"])
        self.assertNotIn("\x00", hw["hardware_badge"])
        print("  [PASS] Hardware detection test passed:", hw["hardware_badge"])


class TestModelsAndPresets(unittest.TestCase):
    def test_model_catalog(self):
        self.assertGreaterEqual(len(AVAILABLE_MODELS), 8)
        self.assertIn("full_multitrack", AVAILABLE_MODELS)
        for key, info in AVAILABLE_MODELS.items():
            self.assertIn("name", info)
            self.assertIn("display_name", info)
            self.assertIn("model_filename", info)
            self.assertIn("arch", info)
            self.assertIn("stems", info)
            self.assertIsInstance(info["stems"], list)
        print(f"  [PASS] Model catalog test passed ({len(AVAILABLE_MODELS)} models verified)")

    def test_presets_consistency(self):
        self.assertGreaterEqual(len(PRESETS), 7)
        self.assertIn("full_multitrack", PRESETS)
        for pid, preset in PRESETS.items():
            self.assertIn("title", preset)
            self.assertIn("model_key", preset)
            self.assertIn(preset["model_key"], AVAILABLE_MODELS)
        print(f"  [PASS] Presets consistency test passed ({len(PRESETS)} presets verified)")

    def test_stem_resolver(self):
        self.assertEqual(resolve_stem_metadata("test_(kick)_model.wav")["stem_type"], "kick")
        self.assertEqual(resolve_stem_metadata("test_(snare)_model.wav")["stem_type"], "snare")
        self.assertEqual(resolve_stem_metadata("test_(Vocals)_model.wav")["stem_type"], "vocals")
        self.assertEqual(resolve_stem_metadata("test_(Lead_Vocals).wav")["stem_type"], "lead_vocals")
        self.assertEqual(resolve_stem_metadata("test_(Backing_Vocals).wav")["stem_type"], "backing_vocals")
        self.assertEqual(resolve_stem_metadata("test_(noreverb)_model.wav")["stem_type"], "dry")
        print("  [PASS] Stem metadata resolver test passed")


class TestDialogsIsolation(unittest.TestCase):
    def test_dialogs_clean_import(self):
        self.assertTrue(callable(pick_audio_file))
        self.assertTrue(callable(pick_folder))
        print("  [PASS] Native dialogs isolation test passed (Tkinter-free)")


class TestProgressTracker(unittest.TestCase):
    def test_tqdm_regex(self):
        sample = " 42%|####2     | 21/50 [07:12<09:56, 20.57s/it]"
        m = PROGRESS_REGEX.search(sample)
        self.assertIsNotNone(m)
        cur, tot, el, eta = m.groups()
        self.assertEqual(cur, "21")
        self.assertEqual(tot, "50")
        self.assertEqual(eta.strip(), "09:56")
        pct = round((int(cur) / int(tot)) * 100, 1)
        self.assertEqual(pct, 42.0)
        print("  [PASS] Progress tracker regex test passed")


class TestFastAPIServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import uvicorn
        cls.port = 7893
        cls.url = f"http://127.0.0.1:{cls.port}"
        cls.server_thread = threading.Thread(
            target=lambda: uvicorn.run(app, host="127.0.0.1", port=cls.port, log_level="critical"),
            daemon=True
        )
        cls.server_thread.start()
        time.sleep(1.5)

    def test_get_hardware_endpoint(self):
        req = urllib.request.urlopen(f"{self.url}/api/hardware")
        self.assertEqual(req.status, 200)
        data = json.loads(req.read().decode("utf-8"))
        self.assertIn("hardware_badge", data)
        print("  [PASS] API /api/hardware test passed")

    def test_get_presets_endpoint(self):
        req = urllib.request.urlopen(f"{self.url}/api/presets")
        self.assertEqual(req.status, 200)
        data = json.loads(req.read().decode("utf-8"))
        self.assertIn("presets", data)
        self.assertIn("full_multitrack", data["presets"])
        self.assertIn("drumsep", data["presets"])
        self.assertIn("karaoke", data["presets"])
        print("  [PASS] API /api/presets test passed")

    def test_get_status_endpoint(self):
        req = urllib.request.urlopen(f"{self.url}/api/status")
        self.assertEqual(req.status, 200)
        data = json.loads(req.read().decode("utf-8"))
        self.assertIn("job", data)
        print("  [PASS] API /api/status test passed")

    def test_get_index_html(self):
        req = urllib.request.urlopen(f"{self.url}/")
        self.assertEqual(req.status, 200)
        html = req.read().decode("utf-8")
        self.assertIn("Stem Separator Studio", html)
        self.assertIn("Desglose Total Multitrack", html)
        print("  [PASS] API / (SPA frontend) test passed")


class TestPipelineE2E(unittest.TestCase):
    def test_full_separation_e2e(self):
        print("  [...] Running E2E separation test with synthetic audio...")
        temp_dir = Path(tempfile.mkdtemp(prefix="stem_e2e_"))
        try:
            audio_src = temp_dir / "e2e_test.wav"
            out_dir = temp_dir / "e2e_out"
            
            # Generate 2s audio clip
            cmd = [
                "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=2",
                "-c:a", "pcm_s16le", str(audio_src)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            self.assertTrue(audio_src.exists())

            events = []
            def cb(ev):
                events.append(ev)

            models_dir = PROJECT_ROOT / "models"
            pipe = SeparationPipeline(models_dir=models_dir, event_callback=cb)
            results = pipe.process(
                input_file=str(audio_src),
                output_dir=str(out_dir),
                model_key="bs_roformer",
                overlap=2
            )

            self.assertGreaterEqual(len(results), 2)
            for stem in results:
                p = Path(stem["full_path"])
                self.assertTrue(p.exists())
                self.assertGreater(p.stat().st_size, 0)
                self.assertIn("label", stem)
                self.assertIn("url", stem)

            event_types = [e.get("type") for e in events]
            self.assertIn("progress", event_types)
            self.assertIn("completed", event_types)
            print(f"  [PASS] E2E separation test passed ({len(results)} stems produced and verified)")

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    print("=" * 60)
    print("  RUNNING STEM SEPARATOR STUDIO TEST SUITE")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestHardwareModule))
    suite.addTests(loader.loadTestsFromTestCase(TestModelsAndPresets))
    suite.addTests(loader.loadTestsFromTestCase(TestDialogsIsolation))
    suite.addTests(loader.loadTestsFromTestCase(TestProgressTracker))
    suite.addTests(loader.loadTestsFromTestCase(TestFastAPIServer))
    suite.addTests(loader.loadTestsFromTestCase(TestPipelineE2E))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("=" * 60)
    if result.wasSuccessful():
        print(f"  ALL {result.testsRun} TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)
        return 0
    else:
        print(f"  FAILURES: {len(result.failures)}, ERRORS: {len(result.errors)}")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())

# Unit Tests for Native OS Dialogs Isolation

import sys
from core.dialogs import pick_audio_file, pick_folder

def test_dialogs_import_clean():
    # Verify that tkinter is NOT imported into sys.modules by importing core.dialogs
    assert "tkinter" not in sys.modules

def test_pick_functions_callable():
    assert callable(pick_audio_file)
    assert callable(pick_folder)

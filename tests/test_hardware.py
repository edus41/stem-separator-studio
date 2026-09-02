# Unit Tests for Hardware Detection Module

import pytest
import platform
import torch
from core.hardware import detect_hardware

def test_detect_hardware_structure():
    hw = detect_hardware()
    assert isinstance(hw, dict)
    assert "os" in hw
    assert "arch" in hw
    assert "device_type" in hw
    assert "device_name" in hw
    assert "hardware_badge" in hw
    assert "is_gpu" in hw
    assert "threads" in hw
    assert isinstance(hw["threads"], int)
    assert hw["threads"] > 0

def test_detect_hardware_os_match():
    hw = detect_hardware()
    assert hw["os"] == platform.system()
    assert hw["arch"] == platform.machine()

def test_detect_hardware_badge_not_empty():
    hw = detect_hardware()
    assert len(hw["hardware_badge"]) > 0
    assert "\x00" not in hw["device_name"]
    assert "\x00" not in hw["hardware_badge"]

def test_detect_hardware_device_type_valid():
    hw = detect_hardware()
    assert hw["device_type"] in ["cuda", "mps", "directml", "cpu"]

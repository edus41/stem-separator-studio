# Hardware Detection & Device Optimizer

import os
import platform
import torch

def detect_hardware():
    """
    Detects available compute hardware across Windows, macOS, and Linux.
    Returns a structured dictionary with device type, friendly name, and recommendations.
    """
    info = {
        "os": platform.system(),
        "arch": platform.machine(),
        "device_type": "cpu",
        "device_name": "CPU",
        "hardware_badge": "CPU Multi-Core",
        "is_gpu": False,
        "details": "",
        "threads": os.cpu_count() or 4
    }

    # 1. Check NVIDIA CUDA
    if torch.cuda.is_available():
        info["device_type"] = "cuda"
        name = torch.cuda.get_device_name(0).replace("\x00", "").strip()
        info["device_name"] = name
        info["hardware_badge"] = f"NVIDIA GPU (CUDA {torch.version.cuda})"
        info["is_gpu"] = True
        info["details"] = f"Aceleración CUDA activada: {name}"
        return info

    # 2. Check Apple Silicon MPS (Metal Performance Shaders on macOS)
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        info["device_type"] = "mps"
        info["device_name"] = "Apple Silicon (Metal MPS)"
        info["hardware_badge"] = "Apple Silicon (GPU Metal)"
        info["is_gpu"] = True
        info["details"] = "Aceleración Apple Metal MPS activada"
        return info

    # 3. Check DirectML (Windows AMD/Intel/NVIDIA without CUDA)
    try:
        import torch_directml
        if torch_directml.is_available():
            info["device_type"] = "directml"
            try:
                raw_name = torch_directml.device_name(0).replace("\x00", "").strip()
            except Exception:
                raw_name = "DirectML GPU"
            info["device_name"] = raw_name
            info["hardware_badge"] = f"GPU ({raw_name})"
            info["is_gpu"] = True
            info["details"] = f"Aceleración DirectML disponible ({raw_name})"
            return info
    except Exception:
        pass

    # 4. Fallback to CPU with multi-threading optimization
    cpu_cores = os.cpu_count() or 4
    torch.set_num_threads(cpu_cores)
    info["device_type"] = "cpu"
    info["device_name"] = f"{platform.processor() or 'Procesador multi-núcleo'} ({cpu_cores} Hilos)"
    info["hardware_badge"] = f"CPU ({cpu_cores} Hilos AVX2)"
    info["is_gpu"] = False
    info["details"] = f"Ejecutando en CPU optimizada con {cpu_cores} hilos en paralelo."

    return info

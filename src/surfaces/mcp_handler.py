from src.contract import RegistryServiceAggregate

def _check_dependencies(shutil) -> dict:
    """Helper to verify all library and binary dependencies."""
    _unused = RegistryServiceAggregate
    deps = {
        "opencv": "cv2",
        "pillow": "PIL",
        "numpy": "numpy",
        "pytesseract": "pytesseract",
        "requests": "requests",
        "pyyaml": "yaml",
        "llama-cpp-python": "llama_cpp",
        "ffmpeg": None,  # binary check
    }
    res = {}
    for name, module in deps.items():
        if module:
            try:
                __import__(module)
                res[name] = "OK"
            except ImportError:
                res[name] = "MISSING"
        else:
            res[name] = "OK" if shutil.which(name) else "MISSING"
    return res


def _check_native_vlm(project_root, adapter_config) -> tuple[dict, bool]:
    """Helper to check VLM native GGUF and mmproj models availability."""
    native_cfg = adapter_config.get("native") if isinstance(adapter_config, dict) else {}
    if not isinstance(native_cfg, dict):
        native_cfg = {}
    model_rel_path = str(native_cfg.get("model_path", "models/MiniCPM-V-4_6-Q8_0.gguf"))
    mmproj_rel_path = str(native_cfg.get("mmproj_path", "models/mmproj-MiniCPM-V-4.6-F16.gguf"))
    
    model_path = project_root / model_rel_path
    mmproj_path = project_root / mmproj_rel_path
    
    model_exists = model_path.exists()
    mmproj_exists = mmproj_path.exists()
    
    files_status = {
        "model_file": "FOUND" if model_exists else "MISSING",
        "mmproj_file": "FOUND" if mmproj_exists else "MISSING"
    }
    return files_status, bool(model_exists and mmproj_exists)

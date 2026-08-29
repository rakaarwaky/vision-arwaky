def _check_dependencies(shutil) -> dict:
    """Helper to verify all library and binary dependencies."""
    deps = {
        "opencv": "cv2",
        "pillow": "PIL",
        "numpy": "numpy",
        "pytesseract": "pytesseract",
        "requests": "requests",
        "pyyaml": "yaml",
        "ffmpeg": None,
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

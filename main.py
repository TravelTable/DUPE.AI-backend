import importlib.util
import sys
from pathlib import Path

def _load_app():
    app_path = Path(__file__).resolve().parent / "dupe-ai-backend" / "app" / "main.py"
    sys.path.insert(0, str(app_path.parent.parent))
    spec = importlib.util.spec_from_file_location("dupe_ai_backend_app", app_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load backend app module.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.app

app = _load_app()

__all__ = ["app"]

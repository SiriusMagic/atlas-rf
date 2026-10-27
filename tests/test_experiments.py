"""Pruebas de humo de la carpeta experiments/ (no forma parte del paquete atlas_rf)."""
import importlib.util
import json
import math
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

ROOT = Path(__file__).resolve().parents[1]
SECRET = re.compile(r"AIza[0-9A-Za-z_\-]{35}|hf_[A-Za-z0-9]{30,}|sk-[A-Za-z0-9]{20,}|github_pat_\w+")


def _load_scheduler():
    path = ROOT / "experiments" / "beam_scheduler" / "beam_scheduler.py"
    spec = importlib.util.spec_from_file_location("beam_scheduler", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_beam_scheduler_produces_real_metrics():
    bs = _load_scheduler()
    angles = list(range(-60, 61, 10))
    for algorithm in ("fixed", "intelligent"):
        users = bs.generate_users(20, seed=1)
        served, total_time, _ = bs.run_simulation(users, angles, algorithm=algorithm)
        metrics = bs.evaluate_performance(served, total_time, False)
        assert total_time > 0
        assert not math.isnan(metrics["discovery_mean"]), "las métricas no deben salir NaN"
        assert 0 < metrics["fairness_index"] <= 1


def test_notebooks_are_clean():
    notebooks = list((ROOT / "experiments").rglob("*.ipynb"))
    assert notebooks
    for nb_path in notebooks:
        raw = nb_path.read_text(encoding="utf-8")
        assert not SECRET.search(raw), f"{nb_path.name} contiene algo que parece una llave"
        nb = json.loads(raw)
        assert nb["nbformat"] == 4
        for cell in nb["cells"]:
            if cell["cell_type"] == "code":
                assert not cell.get("outputs"), f"{nb_path.name} tiene resultados guardados"
            src = cell["source"] if isinstance(cell["source"], str) else "".join(cell["source"])
            assert "weights_only=False" not in src, f"{nb_path.name}: usa torch.load inseguro"

import importlib.util
from pathlib import Path

from whestbench import BaseEstimator


def test_estimator_entrypoint_is_valid_base_estimator() -> None:
    estimator_path = Path(__file__).resolve().parents[1] / "estimator.py"
    spec = importlib.util.spec_from_file_location("arc_whitebox_estimator", estimator_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert issubclass(module.Estimator, BaseEstimator)

from __future__ import annotations

import pytest

from scripts.e015_mz_diagnostic import instrument_v29_source


MINIMAL_V29 = '''import math

class Estimator:
    def predict(self):
        D3, D21 = self._dslices(x)

    def _dslices(self):
        if ka < k and STRASSEN_HUB > 0:
            D21 = self._hub2(bufs, apb4, ka, k, n)
            fnp.add(D21, fnp.matmul(inner, Qc.T, out=bufs["t1"]), out=D21)
        else:
            D21 = fnp.matmul(inner, Qc.T, out=bufs["d21"])
'''


def test_instrumentation_records_layer_old_and_young_without_replacing_output_path() -> None:
    patched = instrument_v29_source(MINIMAL_V29)

    assert "E015_TRACE = []" in patched
    assert "E015_LAYER[0] = li" in patched
    assert '"old": _e015_np.array(bufs["t1"], copy=True)' in patched
    assert '"young": _e015_np.array(D21, copy=True)' in patched
    assert "fnp.add(D21, bufs[\"t1\"], out=D21)" in patched


def test_instrumentation_rejects_unexpected_source_shape() -> None:
    with pytest.raises(ValueError, match="old-tier D21 marker"):
        instrument_v29_source("import math\n")

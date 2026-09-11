"""最小化学数据审计：标识、坐标、缺失、饱和与重复。"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
axis = np.linspace(400, 1800, 701)
X = rng.normal(size=(24, axis.size))
X[3, 120] = np.nan
X[8, 300:305] = 65535
meta = pd.DataFrame({
    "sample_id": [f"S{i//2:02d}" for i in range(24)],
    "replicate": [i % 2 + 1 for i in range(24)],
    "batch": ["A"] * 12 + ["B"] * 12,
})

report = {
    "rows": len(meta),
    "independent_samples": meta.sample_id.nunique(),
    "duplicate_sample_rows": int(meta.sample_id.duplicated(keep=False).sum()),
    "missing_points": int(np.isnan(X).sum()),
    "saturated_points": int((X >= 65535).sum()),
    "axis_monotonic": bool(np.all(np.diff(axis) > 0)),
    "axis_step_sd": float(np.std(np.diff(axis))),
}
for key, value in report.items():
    print(f"{key:24s}: {value}")


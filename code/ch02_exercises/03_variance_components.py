"""用随机效应模型估计批次、样品与扫描方差。"""
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

rng = np.random.default_rng(12)
rows = []
for batch in range(4):
    b = rng.normal(0, 1.2)
    for sample in range(8):
        s = rng.normal(0, 2.0)
        for scan in range(3):
            rows.append((batch, f"B{batch}_S{sample}", scan, 10+b+s+rng.normal(0, .35)))
df = pd.DataFrame(rows, columns=["batch", "sample", "scan", "response"])
model = smf.mixedlm("response ~ 1", df, groups=df["batch"],
                    vc_formula={"sample":"0 + C(sample)"})
fit = model.fit(reml=True)
print(fit.summary())


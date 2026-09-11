"""比较SNV、MSC与Savitzky-Golay；输出保峰诊断。"""
import numpy as np
from scipy.signal import savgol_filter

rng = np.random.default_rng(4)
x = np.linspace(400, 1800, 1401)
clean = np.exp(-0.5*((x-1000)/18)**2) + 0.45*np.exp(-0.5*((x-1250)/35)**2)
raw = 1.35*clean + 0.00025*(x-400) + rng.normal(0, 0.035, x.size)

snv = (raw - raw.mean()) / raw.std(ddof=1)
reference = clean
b, a = np.polyfit(reference, raw, 1)
msc = (raw - a) / b
sg = savgol_filter(raw, 31, 3)

def peak_metrics(y):
    i = np.argmax(y)
    half = y[i] / 2
    ids = np.flatnonzero(y >= half)
    return x[i], y[i], x[ids[-1]] - x[ids[0]]

for name, y in {"clean":clean, "raw":raw, "snv":snv, "msc":msc, "sg":sg}.items():
    print(name, "peak_position, height, apparent_FWHM =", peak_metrics(y))


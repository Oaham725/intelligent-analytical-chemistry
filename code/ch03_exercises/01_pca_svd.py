"""从SVD手工计算PCA，并验证得分、载荷和重构误差。"""
import numpy as np

rng = np.random.default_rng(1)
n, p = 80, 240
w = np.linspace(400, 1800, p)
S = np.c_[np.exp(-0.5*((w-850)/45)**2), np.exp(-0.5*((w-1200)/75)**2)]
C = rng.uniform(0, 1, (n, 2))
X = C @ S.T + rng.normal(0, .015, (n, p))
Xc = X - X.mean(axis=0)
U, singular, Vt = np.linalg.svd(Xc, full_matrices=False)
T = U[:, :2] * singular[:2]
P = Vt[:2].T
Xhat = T @ P.T
explained = singular**2 / np.sum(singular**2)
print("前5个解释方差比:", explained[:5])
print("保留2个主成分的相对重构误差:", np.linalg.norm(Xc-Xhat)/np.linalg.norm(Xc))
print("得分与真实浓度的相关矩阵:\n", np.corrcoef(T.T, C.T)[:2, 2:])


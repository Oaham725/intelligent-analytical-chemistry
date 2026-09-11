"""用PCA的Hotelling T2和Q残差识别两类域外样品。"""
import numpy as np
from sklearn.decomposition import PCA

rng = np.random.default_rng(3)
X = rng.normal(size=(100, 6)) @ rng.normal(size=(6, 80)) + rng.normal(0,.1,(100,80))
pca = PCA(6).fit(X)
T = pca.transform(X)
Xhat = pca.inverse_transform(T)
var_t = T.var(axis=0, ddof=1)
t2 = np.sum(T**2 / var_t, axis=1)
q = np.sum((X-Xhat)**2, axis=1)
t2_lim, q_lim = np.quantile(t2,.975), np.quantile(q,.975)

test = np.vstack([X[:4], X.mean(0)+4*pca.components_[0], X.mean(0)+5*rng.normal(size=80)])
Tt = pca.transform(test); Qt = np.sum((test-pca.inverse_transform(Tt))**2, axis=1)
T2t = np.sum(Tt**2/var_t, axis=1)
for i,(a,b) in enumerate(zip(T2t,Qt)):
    print(i, f"T2={a:.2f}", f"Q={b:.2f}", "inside=", a<=t2_lim and b<=q_lim)

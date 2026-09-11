"""在共线光谱上用嵌套交叉验证比较PCR与PLS潜变量数。"""
import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupKFold, GridSearchCV, cross_val_score

rng = np.random.default_rng(2)
n, p = 72, 120
w = np.linspace(900, 1700, p)
y = rng.uniform(8, 16, n)
batch = np.repeat(np.arange(12), 6)
X = y[:,None]*np.exp(-0.5*((w-1250)/80)**2) + 0.9*batch[:,None]
X += rng.normal(0, .8, (n,p))

outer = GroupKFold(3)
for name, estimator, grid in [
    ("PCR", make_pipeline(StandardScaler(), PCA(), LinearRegression()),
     {"pca__n_components":list(range(1, 7))}),
    ("PLS", make_pipeline(StandardScaler(), PLSRegression()),
     {"plsregression__n_components":list(range(1, 7))}),
]:
    inner = GroupKFold(3)
    search = GridSearchCV(estimator, grid, cv=inner, scoring="neg_root_mean_squared_error")
    score = -cross_val_score(search, X, y, groups=batch, cv=outer,
                             scoring="neg_root_mean_squared_error",
                             params={"groups":batch})
    print(name, "outer RMSE:", score, "mean=", score.mean())

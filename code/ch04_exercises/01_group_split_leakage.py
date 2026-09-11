"""演示把重复谱随机分折造成的性能泄漏。"""
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, GroupKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

rng = np.random.default_rng(4)
n_samples, repeats, p = 60, 5, 40
sample_pattern = rng.normal(size=(n_samples, p))
label = rng.integers(0, 2, n_samples)
X = np.repeat(sample_pattern, repeats, axis=0) + rng.normal(0,.08,(n_samples*repeats,p))
y = np.repeat(label, repeats); groups = np.repeat(np.arange(n_samples), repeats)
clf = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000))
random_cv = StratifiedKFold(5, shuffle=True, random_state=0)
group_cv = GroupKFold(5)
print("random-spectrum CV:", cross_val_score(clf,X,y,cv=random_cv).mean())
print("independent-sample CV:", cross_val_score(clf,X,y,cv=group_cv,groups=groups).mean())


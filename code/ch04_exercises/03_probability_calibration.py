"""校准分类概率，并按不同错误代价选择阈值。"""
import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, brier_score_loss

X,y=make_classification(n_samples=1200,n_features=20,weights=[.88,.12],flip_y=.04,random_state=5)
Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.35,stratify=y,random_state=3)
model=CalibratedClassifierCV(LogisticRegression(max_iter=2000),method="isotonic",cv=5).fit(Xtr,ytr)
p=model.predict_proba(Xte)[:,1]
print("Brier:",brier_score_loss(yte,p))
for cost_fn,cost_fp in [(1,1),(8,1)]:
    best=None
    for threshold in np.linspace(.01,.99,99):
        tn,fp,fn,tp=confusion_matrix(yte,p>=threshold).ravel()
        cost=cost_fn*fn+cost_fp*fp
        if best is None or cost<best[0]: best=(cost,threshold,tn,fp,fn,tp)
    print("FN/FP cost",cost_fn,cost_fp,"best",best)


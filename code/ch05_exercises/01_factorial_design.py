"""两水平全析因：从设计矩阵估计主效应和交互。"""
import itertools
import numpy as np
import statsmodels.api as sm

rng=np.random.default_rng(1)
X=np.array(list(itertools.product([-1,1],repeat=3)),float)
A,B,C=X.T
design=np.c_[A,B,C,A*B,A*C,B*C,A*B*C]
y=12+2*A-1.2*B+3*A*B+rng.normal(0,.25,len(A))
fit=sm.OLS(y,sm.add_constant(design)).fit()
print(fit.summary(xname=["const","A","B","C","AB","AC","BC","ABC"]))


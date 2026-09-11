"""拟合二次响应面并用Hessian判断驻点类型。"""
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression

rng=np.random.default_rng(2)
X=rng.uniform(-1.5,1.5,(40,2))
y=5+2*X[:,0]-X[:,1]-1.8*X[:,0]**2-1.1*X[:,1]**2+.8*X[:,0]*X[:,1]+rng.normal(0,.15,40)
poly=PolynomialFeatures(2,include_bias=False)
model=LinearRegression().fit(poly.fit_transform(X),y)
# features: x1,x2,x1^2,x1*x2,x2^2
b=model.coef_; H=np.array([[2*b[2],b[3]],[b[3],2*b[4]]]); g=b[:2]
stationary=-np.linalg.solve(H,g)
print("stationary point:",stationary)
print("Hessian eigenvalues:",np.linalg.eigvalsh(H),"=> max if both negative")
print("predicted response:",model.predict(poly.transform(stationary[None]))[0])


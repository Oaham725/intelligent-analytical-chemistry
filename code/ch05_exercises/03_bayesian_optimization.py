"""一维带噪实验的高斯过程+期望改进。"""
import numpy as np
from scipy.stats import norm
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel

rng=np.random.default_rng(8)
def experiment(x): return np.sin(3*x)+.45*np.cos(7*x)-.08*(x-2)**2+rng.normal(0,.05,np.shape(x))
X=np.array([[0.0],[2.0],[4.0]]); y=experiment(X[:,0])
grid=np.linspace(0,4,801)[:,None]
kernel=ConstantKernel(1,(1e-2,1e2))*Matern(length_scale=1,nu=2.5)+WhiteKernel(.01)
for step in range(12):
    gp=GaussianProcessRegressor(kernel=kernel,normalize_y=True,random_state=0).fit(X,y)
    mu,sd=gp.predict(grid,return_std=True); improvement=mu-y.max()-.01
    z=np.divide(improvement,sd,out=np.zeros_like(sd),where=sd>0)
    ei=improvement*norm.cdf(z)+sd*norm.pdf(z)
    x_next=grid[np.argmax(ei)]; y_next=experiment(x_next[0])
    X=np.vstack([X,x_next]); y=np.append(y,y_next)
    print(step, "x=",x_next[0].round(3),"y=",round(y_next,3),"best=",round(y.max(),3))


"""在统一嵌套外层下比较Ridge、SVM与随机森林。"""
from sklearn.datasets import make_regression
from sklearn.ensemble import RandomForestRegressor
from sklearn.kernel_ridge import KernelRidge
from sklearn.linear_model import Ridge
from sklearn.model_selection import KFold, GridSearchCV, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

X, y = make_regression(n_samples=180, n_features=70, n_informative=8,
                       effective_rank=12, noise=12, random_state=2)
outer = KFold(5, shuffle=True, random_state=10)
inner = KFold(4, shuffle=True, random_state=11)
models = {
 "Ridge": (make_pipeline(StandardScaler(),Ridge()), {"ridge__alpha":[.1,1,10,100]}),
 "RBF": (make_pipeline(StandardScaler(),KernelRidge(kernel="rbf")),
         {"kernelridge__alpha":[.1,1,10],"kernelridge__gamma":[.001,.01,.1]}),
 "RF": (RandomForestRegressor(random_state=1),
        {"max_depth":[3,6,None],"min_samples_leaf":[1,4,10]}),
}
for name,(model,grid) in models.items():
    search=GridSearchCV(model,grid,cv=inner,scoring="neg_root_mean_squared_error")
    rmse=-cross_val_score(search,X,y,cv=outer,scoring="neg_root_mean_squared_error")
    print(name, rmse.round(2), "mean=",rmse.mean().round(2))


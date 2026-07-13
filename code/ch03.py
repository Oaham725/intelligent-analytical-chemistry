"""第3章代码练习：化学计量学：从测量信号到化学信息

任务：从SVD实现PCA，比较MLR、PCR与PLS的校准、交叉验证和外部预测误差。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

X=rng.normal(size=(40,120))
k=5
Xc=X-X.mean(0)
U,S,Vt=np.linalg.svd(Xc,full_matrices=False)
T=U[:,:k]*S[:k]
P=Vt[:k].T
Xhat=T@P.T+X.mean(0)
q_residual=((X-Xhat)**2).sum(1)

# TODO 1: 用课程或开放数据替换合成输入，明确对象为近红外样品—变量矩阵及辛烷值参照。
# TODO 2: 实现按生产批次留出整组样品，并与随机划分或默认流程对照。
# TODO 3: 输出联合阅读得分、载荷、Q残差和预测残差，据此判断能否选择潜变量数并给出模型适用域。

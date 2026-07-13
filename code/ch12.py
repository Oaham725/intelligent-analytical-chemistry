"""第12章代码练习：生物分析、单细胞与多组学测量

任务：模拟共享潜变量的两组学数据，用CCA对齐并比较随机与留个体外验证。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

X=rng.normal(size=(50,20))
Y=X[:,:3]@rng.normal(size=(3,15))+rng.normal(scale=0.2,size=(50,15))
Xc=X-X.mean(0); Yc=Y-Y.mean(0)
U,S,Vt=np.linalg.svd(Xc.T@Yc,full_matrices=False)
X_score=Xc@U[:,0]; Y_score=Yc@Vt.T[:,0]

# TODO 1: 用课程或开放数据替换合成输入，明确对象为单细胞、成像表型与质谱参照组成的多组学样本。
# TODO 2: 实现按供体或患者完整留出，并与随机划分或默认流程对照。
# TODO 3: 输出区分生物重复、技术重复、批次效应和标签不确定性，据此判断能否说明不同模态贡献了互补证据还是共同偏差。

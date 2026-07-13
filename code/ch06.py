"""第6章代码练习：分子表征与结构—性质关系

任务：用简化分子图和路径指纹比较异构体，并执行骨架分组验证。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

atoms=['C','C','O','H']
bonds=[(0,1),(1,2),(0,3)]
adj=np.zeros((len(atoms),len(atoms)),dtype=int)
for i,j in bonds: adj[i,j]=adj[j,i]=1
fingerprint=(adj@np.arange(1,len(atoms)+1))%2

# TODO 1: 用课程或开放数据替换合成输入，明确对象为具有分子式、SMILES、指纹、二维图和构象的化合物。
# TODO 2: 实现按骨架而非随机分子留出测试集，并与随机划分或默认流程对照。
# TODO 3: 输出寻找异构体混淆、指纹碰撞和表示域外分子，据此判断能否为目标性质选择信息足够且成本合适的表示。

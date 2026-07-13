"""第7章代码练习：神经网络、Transformer、GNN与基础模型

任务：用NumPy实现两层网络和缩放点积注意力，并比较MLP、1D-CNN思路。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

Q=rng.normal(size=(16,32))
K=rng.normal(size=(16,32))
V=rng.normal(size=(16,24))
scores=Q@K.T/np.sqrt(Q.shape[-1])
A=np.exp(scores-scores.max(1,keepdims=True))
A/=A.sum(1,keepdims=True)
context=A@V

# TODO 1: 用课程或开放数据替换合成输入，明确对象为同一批一维光谱及其标签或连续参照值。
# TODO 2: 实现固定外部批次并在训练内选择网络结构，并与随机划分或默认流程对照。
# TODO 3: 输出比较局部峰、长程相关、参数量与种子波动，据此判断能否判断CNN、Transformer或GNN的结构偏置是否匹配数据。

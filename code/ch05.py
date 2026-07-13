"""第5章代码练习：实验设计、贝叶斯推理与主动学习

任务：实现高斯过程与EI/UCB，记录每轮候选、实验结果和后验变化。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

mean=rng.normal(size=30)
std=rng.uniform(0.05,0.5,size=30)
safe_mask=rng.random(30)>0.15
kappa=1.96
ucb=mean+kappa*std
next_id=int(np.argmax(np.where(safe_mask,ucb,-np.inf)))
print({'next':next_id,'mean':mean[next_id],'std':std[next_id]})

# TODO 1: 用课程或开放数据替换合成输入，明确对象为受温度、配比和危险边界约束的反应空间。
# TODO 2: 实现用未参与优化的确认实验检验推荐条件，并与随机划分或默认流程对照。
# TODO 3: 输出区分模型不确定性、实验噪声和边界外推，据此判断能否在预算内选择下一轮安全且有信息量的实验。

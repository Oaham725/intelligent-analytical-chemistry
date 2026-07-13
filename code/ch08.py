"""第8章代码练习：生成式模型与扩散模型：从信号恢复到化学反演

任务：构造一维光谱扩散过程，比较噪声调度并检查峰位、峰宽和强度守恒。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

x0=rng.normal(size=(32,256))
t=rng.uniform(0,1,size=(len(x0),1))
noise=rng.normal(size=x0.shape)
xt=np.sqrt(1-t)*x0+np.sqrt(t)*noise
# train a denoiser epsilon_theta(xt,t)

# TODO 1: 用课程或开放数据替换合成输入，明确对象为目标性质条件下生成的分子或光谱候选。
# TODO 2: 实现用价态、去重、正向预测和保留测试逐层过滤，并与随机划分或默认流程对照。
# TODO 3: 输出识别模式坍塌、训练集记忆、奖励投机与不可合成结构，据此判断能否只把通过多级筛选的候选送入昂贵计算或实验。

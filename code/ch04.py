"""第4章代码练习：机器学习基础：任务、模型、泛化与解释

任务：构造含重复样品和批次的数据，对比随机划分、GroupKFold与时间外推。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

groups=np.repeat(np.arange(8),5)
X=rng.normal(size=(40,12))
y=rng.normal(size=40)
for held_out in np.unique(groups):
    test=groups==held_out
    train=~test
    assert set(groups[train]).isdisjoint(groups[test])
    # fit preprocessing and model on train only

# TODO 1: 用课程或开放数据替换合成输入，明确对象为含重复谱图、化合物身份和采集时间的数据集。
# TODO 2: 实现比较随机、按化合物分组和时间外推三种划分，并与随机划分或默认流程对照。
# TODO 3: 输出检查概率校准、少数类召回和最高置信错误，据此判断能否确定模型是否真正学到可迁移的化学结构。

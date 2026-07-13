"""第11章代码练习：化学成像、空间分辨率与多维数据

任务：生成光谱立方体，完成PCA组分映射、分割和按个体评价。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

cube=rng.normal(size=(64,64,40))
target_band=18
reference_band=5
threshold=cube.mean(axis=(0,1))+cube.std(axis=(0,1))
score=cube[...,target_band]-cube[...,reference_band]
mask=score>np.percentile(score,80)

# TODO 1: 用课程或开放数据替换合成输入，明确对象为具有空间坐标和波长轴的化学成像立方体。
# TODO 2: 实现按患者或样品留出而不是随机切分图块，并与随机划分或默认流程对照。
# TODO 3: 输出比较Dice/IoU、边界误差、空间自相关和伪高分辨细节，据此判断能否把组分图与原始像素谱及光学分辨率对应。

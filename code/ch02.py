"""第2章代码练习：化学数据的采集、预处理、可视化与计算基础

任务：建立带fit/transform边界的光谱预处理流水线并比较处理前后峰形。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

x=np.linspace(400,1800,600)
y=np.exp(-0.5*((x-1000)/30)**2)+0.0003*x+rng.normal(0,0.02,x.size)
baseline=np.polyval(np.polyfit(x,y,2),x)
yc=y-baseline
yc/=np.linalg.norm(yc)+1e-12

# TODO 1: 用课程或开放数据替换合成输入，明确对象为带波数轴、批次标签和空白记录的原始拉曼光谱。
# TODO 2: 实现按采集批次冻结处理参数并外推，并与随机划分或默认流程对照。
# TODO 3: 输出逐项量化尖峰、基线、平滑和归一化对峰位峰面积的影响，据此判断能否输出能够从原始文件重建的预处理数据集。

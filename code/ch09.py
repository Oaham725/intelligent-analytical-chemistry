"""第9章代码练习：光谱分析与智能谱学

任务：建立跨批次光谱预处理—PLS—一维特征模型流水线。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

raw=rng.normal(size=(30,500))+np.linspace(0,1,500)
baseline=np.percentile(raw,10,axis=1,keepdims=True)
X=raw-baseline
X/=np.linalg.norm(X,axis=1,keepdims=True)+1e-12
# fit PLS only inside each training fold

# TODO 1: 用课程或开放数据替换合成输入，明确对象为跨仪器、跨批次采集的连续拉曼或近红外光谱。
# TODO 2: 实现整台仪器或整批样品留作测试域，并与随机划分或默认流程对照。
# TODO 3: 输出对照峰位、峰宽、散射校正和增强前后的物理合理性，据此判断能否确定预处理与模型组合能否跨设备使用。

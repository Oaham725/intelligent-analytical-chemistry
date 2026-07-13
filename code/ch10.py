"""第10章代码练习：质谱、色谱、核磁与结构解析

任务：实现质谱余弦检索、保留时间对齐和多证据候选融合。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

query=rng.random(200)
library=rng.random((100,200))
def cosine(a,b):
    return float(a@b/(np.linalg.norm(a)*np.linalg.norm(b)+1e-12))
scores=np.array([cosine(query,ref) for ref in library])
topk=np.argsort(scores)[-10:][::-1]

# TODO 1: 用课程或开放数据替换合成输入，明确对象为GC-MS峰、碎片谱、保留指数及互补NMR/IR证据。
# TODO 2: 实现用库外化合物和真实共洗脱峰检验开放集性能，并与随机划分或默认流程对照。
# TODO 3: 输出分析Top-k遗漏、保留指数冲突与多谱证据矛盾，据此判断能否输出候选排序、证据矩阵和无法确认的原因。

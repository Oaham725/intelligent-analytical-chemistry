"""第14章代码练习：仪器标准化、校准迁移与FAIR数据

任务：实现DS/PDS校准迁移和样品—仪器—处理—模型元数据检查器。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

X_master=rng.normal(size=(30,100))
X_slave=X_master@np.eye(100)+rng.normal(scale=0.03,size=(30,100))
metadata={'sample_id':'S001','instrument':'NIR-02','unit':'a.u.','preprocess':'SNV','checksum':'demo'}
F=np.linalg.lstsq(X_slave,X_master,rcond=None)[0]
X_transfer=X_slave@F
required={'sample_id','instrument','unit','preprocess','checksum'}
assert not required-set(metadata)

# TODO 1: 用课程或开放数据替换合成输入，明确对象为主仪器与从仪器对同一批传递样品的响应。
# TODO 2: 实现在独立日期与未参与传递的目标域样品上检验，并与随机划分或默认流程对照。
# TODO 3: 输出定位波长区间、浓度范围和仪器状态造成的迁移失效，据此判断能否交付可追溯的校准迁移模型与FAIR数据包。

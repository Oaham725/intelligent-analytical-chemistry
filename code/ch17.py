"""第17章代码练习：实验决策、强化学习与具身自主实验室

任务：用有限状态机和模拟仪器实现闭环实验，注入故障并验证恢复路径。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

state='LOAD'
next_state='DISPENSE'
allowed={'IDLE':['LOAD'],'LOAD':['DISPENSE','SAFE'],'DISPENSE':['MEASURE','SAFE'],'MEASURE':['UPDATE','SAFE'],'UPDATE':['LOAD','DONE']}
assert next_state in allowed[state]

# TODO 1: 用课程或开放数据替换合成输入，明确对象为自动移液、显色、光谱测量平台的传感器与执行器。
# TODO 2: 实现通过故障注入和长时间运行检验恢复能力，并与随机划分或默认流程对照。
# TODO 3: 输出记录移液失败、通信中断、漂移、急停和人工接管，据此判断能否形成可恢复的感知—规划—行动—学习闭环。

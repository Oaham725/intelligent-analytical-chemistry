"""第1章代码练习：AI时代的分析化学：从化学测量到智能测量

任务：将一个模糊的‘AI识别谱图’需求改写为机器可读的问题卡和测量链。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

problem = {'object':'sample','measurement':'spectrum','target':'class','split':'external_batch','metric':'macro_f1','reject_rule':'distance'}
required=set(problem)
assert required == {'object','measurement','target','split','metric','reject_rule'}

# TODO 1: 用课程或开放数据替换合成输入，明确对象为拉曼样品、测量协议与待识别物质。
# TODO 2: 实现把不同日期、操作者和仪器作为外部条件，并与随机划分或默认流程对照。
# TODO 3: 输出比较测量不确定度、误报代价与拒识样品，据此判断能否形成带适用范围和停止条件的任务书。

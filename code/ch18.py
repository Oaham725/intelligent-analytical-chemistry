"""第18章代码练习：世界模型、化学数字孪生与机器科学家

任务：建立连续流反应器简化世界模型，完成状态估计和滚动时域规划。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

def dynamics(state,action):
    concentration,temp=state
    return np.array([max(0,concentration-0.05*action), temp+0.2*action-0.1*(temp-25)])

# TODO 1: 用课程或开放数据替换合成输入，明确对象为温控连续流反应器的隐藏状态、传感观测和控制动作。
# TODO 2: 实现用未参与辨识的扰动轨迹检验多步预测，并与随机划分或默认流程对照。
# TODO 3: 输出分解状态估计误差、动力学失配和长时滚动漂移，据此判断能否在守恒和设备边界内执行滚动时域控制。

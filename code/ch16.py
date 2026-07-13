"""第16章代码练习：科学大模型与分析化学智能体

任务：实现带白名单工具、结构化返回、日志和复算检查的分析智能体骨架。
运行方式：python chapter_exercise.py
所有合成数据仅用于验证接口；换用真实数据时必须保留样品/批次分组。
"""

import numpy as np

rng = np.random.default_rng(42)

audit_log=[]
def fit_model(**kwargs): return {'status':'fit','kwargs':kwargs}
def check_units(**kwargs): return {'status':'checked','kwargs':kwargs}
def plot_residuals(**kwargs): return {'status':'plotted','kwargs':kwargs}
TOOLS={'fit':fit_model,'check_units':check_units,'plot_residuals':plot_residuals}
def call_tool(name,kwargs):
    if name not in TOOLS: raise PermissionError(name)
    result=TOOLS[name](**kwargs)
    audit_log.append({'tool':name,'kwargs':kwargs})
    return result

# TODO 1: 用课程或开放数据替换合成输入，明确对象为吸附数据、候选等温模型、计算工具和来源材料。
# TODO 2: 实现让独立测试用例和复算结果约束智能体输出，并与随机划分或默认流程对照。
# TODO 3: 输出区分来源事实、模型推断、工具错误和待验假设，据此判断能否生成可证伪的下一步实验而非无出处结论。

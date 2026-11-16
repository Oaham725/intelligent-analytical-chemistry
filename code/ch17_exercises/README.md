# 第17章运行与复核说明

本章使用简化的移液—显色—光谱仿真，帮助区分一次性优化与连续决策，检查奖励投机、安全屏蔽和执行故障。全部数值是教学模拟，不能作为真实仪器性能、化学安全认证或外部验证结果。

## 最短运行路径

在本仓库根目录运行。参考环境为 Python 3.12.14、NumPy 2.5.4、Windows；无需GPU或真实仪器。

```powershell
py -3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -r code/ch17_exercises/requirements.txt
.venv/Scripts/python.exe -X utf8 code/ch17.py
```

已安装NumPy时可直接使用 `python code/ch17.py`。只运行练习1和3用 `python code/ch17.py 1 3`。完整运行耗时以电脑为准，不把作者机器时间当作性能保证。

| 入口 | 做什么 | 核对现象 |
|---|---|---|
| `01_colorimetric_mdp.py` | 显色MDP与值迭代 | 高浓度、试剂足、显色完全但未稀释时，稀释Q值8.50，直接报告−10 |
| `02_reward_and_shield.py` | 三种奖励/屏蔽设置 | 固定默认种子下，A/B/C的中位相对误差约30.0%/2.3%/2.5%；训练期溢出1258/6326/0 |
| `03_fsm_fault_injection.py` | 七类故障注入 | 固定默认种子下，naive/robust静默错误336/10；总样品各1000 |

这些数值来自本次默认运行，其他种子、仿真参数和环境需重新检验。信号奖励、误差奖励和屏蔽规则的差异在正文解释；安全屏蔽不消除所有不可观测故障。

## 不训练也能检查已交记录

```powershell
python code/ch17_exercises/verify_archive.py
```

只需Python标准库：检查默认三练习输出完整性、关键Q值、归档和源代码SHA-256。不重新执行训练，不构成独立外组复现。已交的[默认输出与环境](../../resources/annual/2026-2027/results/ch17/README.md)可直接查看。

需要在自己的电脑重新运行并保存新记录：

```powershell
python code/ch17_exercises/run_and_archive.py --out runs/ch17-local-check
python code/ch17_exercises/verify_archive.py --archive runs/ch17-local-check
```

使用新的空输出目录。运行器记录真实退出码、输出、版本与源代码校验和，不手填实验结果。

## 网页交互

```powershell
python -m http.server 8000
```

打开 `http://localhost:8000/#/docs/ch17`。Docsify与公式渲染依赖原站公开CDN，需能联网；GitHub文件预览不执行JavaScript。

| 模块 | 最短核查 |
|---|---|
| 夜间值班 | 依次选择状态B、奖励C、故障B、迁移A，确认后显示4/4；重置清空 |
| 问题类型 | 依次选择批量、选点、控制、控制、控制、控制，检查得到6/6 |
| 状态设计 | 先检查空选择的反馈，再加入时间、读数趋势、体积等相关变量，检查解释 |
| 奖励调节 | 改变滑块后得分和选中策略改变；打开硬约束后不允许被约束排除的策略 |
| 屏蔽器 | 选择容量、空白、饱和、温度规则；检查漏拦和误拦，避免把禁止稀释当安全规则 |
| 故障注入 | 无保护时气泡产生静默错误；体积核验与幂等补液后可恢复；显色剂失效仍明确为不可观测 |
| 时间尺度 | 依次分配硬件、状态机、策略、状态机、策略、硬件、人、人，检查得到8/8 |

另检查Tab可达、Enter激活、375px窄屏及离开/返回章节不重复挂载。缓存只保存在浏览器本地；正式设备的联锁、安全态与独立验证不由教学网页代替。

## 交付和评审边界

- PR：[第17章 #27](https://github.com/Oaham725/intelligent-analytical-chemistry/pull/27)，关联Issue #26，已收到G07外组评审，修订待推送及复核，教师/助教验收待完成。
- G17对G07的实质性交叉评审：[已提交记录](https://github.com/Oaham725/intelligent-analytical-chemistry/pull/15#pullrequestreview-5888302365)。本组已收到[G07评审](https://github.com/Oaham725/intelligent-analytical-chemistry/pull/27#issuecomment-6888572322)，相应修订待推送复核。
- 基础图、三张前沿卡、两道传承题和引文入口见[第17章](../../docs/ch17.md)。Word版同步修正四处表述并保留原有版式。
- Pt/C研究方向汇报与本章仿真实验分别归档，见[学生汇报材料](../../resources/annual/2026-2027/student-reports/ch17-ptc/README.md)；没有放进教师正式课件目录。

## G07评审的定向回归检查

```powershell
python -X utf8 code/ch17_exercises/test_review_regressions.py
```

8项检查覆盖参比持续超时有限退出、短暂超时恢复、通信与重校准预算独立、质控持续失败、样品超时、屏蔽后继价值备份、终止目标和B/C相同容量上限。测试均为模拟硬件。修订说明与完整验收边界见[逐项回应](../../resources/annual/2026-2027/results/ch17/review-response.md)。

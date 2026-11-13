# G17 第17章默认模拟结果与核验记录

本目录保存2026年11月13日实际运行的三项教学仿真输出。它们不是实物工作站实验，也不代表跨种子、跨平台泛化或外组独立复现。完整运行退出码为0，参考环境为Python 3.12.14、NumPy 2.5.4、Windows。

| 文件 | 用途 |
|---|---|
| [stdout.txt](stdout.txt) | 实际执行三个练习的完整标准输出，换行统一为LF，未手工填充结果 |
| [manifest.json](manifest.json) | 实际版本、退出码、耗时及源代码/输出SHA-256；源代码校验先统一CRLF为LF |
| [browser-check.json](browser-check.json) | 本次浏览器检查范围、结果与已知全站兼容告警 |

## 关键结果

练习1中，高浓度且试剂充足、显色完全但未稀释时，稀释的Q值为8.50，直接报告为−10。默认比较中，开环与闭环报告正确率分别约95.6%与100.0%，仅属于本仿真。

练习2的A信号奖励、B误差奖励、C误差奖励加屏蔽器，中位相对误差分别约30.0%、2.3%、2.6%；训练期溢出分别为1258、6326、0。不能把这种对照写成真实仪器安全认证；最高浓度样品仍受动作集合和容量限制。

练习3中，各处理1000个模拟样品，naive/robust的有效结果为663/987，静默错误为336/10，已标记弃样为1/3。更长自治时长不等于错误更少，未被当前传感器覆盖的故障仍可能静默发生。

## 最短复核

在仓库根目录执行，标准库即可核验归档：

```powershell
python code/ch17_exercises/verify_archive.py
```

重新运行全部模拟并生成自己的记录，需要NumPy：

```powershell
python -m pip install -r code/ch17_exercises/requirements.txt
python code/ch17_exercises/run_and_archive.py --out runs/ch17-local-check
python code/ch17_exercises/verify_archive.py --archive runs/ch17-local-check
```

详见[运行说明](../../../../../code/ch17_exercises/README.md)。快速核验只检查已归档输出完整性、关键打印数值与校验和，不重新训练，也不替代外组评审。

## 网页核查范围

在本次本地Docsify页面实测7个模块挂载、章首4项决定、问题分类6项、状态反馈、奖励滑块与硬约束、故障注入、时间尺度8项、重置、Tab/Enter、章节返回不重复挂载和375px页面宽度。详细结果见JSON。

检查同时发现原站CDN/渲染组件的兼容告警，原始提交页面也可出现；本次记录告警，不将其写成已修复，不扩大范围改动其他章节的共享依赖。模块行为通过不等于网站所有功能、所有浏览器均已验收。

## 评审与验收状态

- 已提交对G07的实质性评审：[PR #15中的G17评语](https://github.com/Oaham725/intelligent-analytical-chemistry/pull/15#pullrequestreview-5888302365)。
- 本章交付：[PR #27](https://github.com/Oaham725/intelligent-analytical-chemistry/pull/27)，关联Issue #26。外组评审结论与教师/助教合并以GitHub实际记录为准。
- 本记录由Codex辅助执行和整理，不冒称非本组人员独立复现。

# 数据字典

所有行均由虚拟传感器或模型计算产生，随机种子固定。吸光度以 A 标记，量纲为一。

| 文件 | 主要字段与用途 |
|---|---|
| `optical-standards.csv` | CV⁺ 标准浓度（µM）、重复编号、样品与空白吸光度，6 个浓度各 3 次 |
| `kinetics-calibration.csv` | 批次、初始 OH⁻（mM）、时间（s）、吸光度，5 批各 25 点 |
| `decision-plans.csv` | 候选加液量与体积（mL）、加液后 OH⁻（mM）、名义与较慢到阈值时间（s）、是否可行 |
| `default-timeseries.csv` | 0–480 s 每 5 s 的配对轨迹。CV 比例无量纲，`estimated` 由估计器计算，`simulated` 为模拟器内部值 |
| `endpoint-comparison.csv` | 三种终点判据、首次连续达标的第一个采样时刻和确认时刻（s）。对照使用同一组默认自动加液读数 |
| `events.csv` | 情景、时间、事件类型、事件数值和命令编号。command、receipt、sync 的数值为 mL |
| `summary.json` | 标定值、默认指令和回执、终点确认时间与故障状态 |

时序中 90 s 样本在加液指令前读取，事件文件保存之后的回执与体积更新。下一次采样反映执行后的状态。在故障情景，浏览器导出的空字段表示未确认或缺失的量。

# 第十五章实验记录

本记录对应Issue #6及本组课程论文。维护组：刘翔、尹伟旭、王怡可、王磊、周裕东、曾凡琦。记录中的技术核验是本组自查，不能替代外组复现、交叉评审或教师验收。

## 数据与预设方案

- <a href="protocol.md" data-ch15-site-href="#/resources/annual/2026-2027/results/ch15/protocol">方案与角色边界</a>
- <a href="audit-log.md" data-ch15-site-href="#/resources/annual/2026-2027/results/ch15/audit-log">先导标签冲突、种子更正和确认实验审计</a>
- <a href="../../../../../data/ch15/README.md" data-ch15-site-href="#/data/ch15/README">选谱、规则标签与许可</a>
- <a href="../../../../../code/ch15_exercises/README.md" data-ch15-site-href="#/code/ch15_exercises/README">根目录运行说明</a>
- <a href="verification.md" data-ch15-site-href="#/resources/annual/2026-2027/results/ch15/verification">网站接入与重算验证记录</a>

280个RRUFF编号与340个先导编号完全分离。确认实验包含3个理想式规则类各60个、留出未知100个；已知类按90训练、30概率校准、24阈值验证、36最终测试分配。标签不是全面矿物学鉴定，编号隔离也不是矿物种、仪器或实验室的外部验证。

## 全量输出

- <a href="metrics.json" data-ch15-site-href="./resources/annual/2026-2027/results/ch15/metrics.json" download>metrics.json：主实验与全部5种子</a>
- <a href="predictions.csv" data-ch15-site-href="./resources/annual/2026-2027/results/ch15/predictions.csv" download>predictions.csv：280个编号的角色、概率与评分</a>
- <a href="inner_cv_results.csv" data-ch15-site-href="./resources/annual/2026-2027/results/ch15/inner_cv_results.csv" download>训练内4折的9组候选参数</a>
- <a href="evaluation_arrays.npz" data-ch15-site-href="./resources/annual/2026-2027/results/ch15/evaluation_arrays.npz" download>评价数组（不含可执行对象）</a>
- <a href="verification.json" data-ch15-site-href="./resources/annual/2026-2027/results/ch15/verification.json" download>独立指标重算核验</a>
- <a href="../../../../../assets/ch15/threshold-lab.html" data-ch15-site-href="./assets/ch15/threshold-lab.html" target="_blank" rel="noopener">阈值、风险、概率及失败记录交互</a>

主实验准确率22/36；正温度变换保持argmax。已知测试NLL从1.566260降至1.294644；T²/Q预设操作点接受34/36个已知，其中13错，接受81/100个未知。最大概率参照接受95/100个未知。5次同池划分中2次NLL变差；这些不是5次重新采集的独立实验。

主阈值来自专用已知验证集。页面中的测试阈值探索是描述性分析，不能据此再选择阈值并宣称新的独立测试成绩。混合样本的未知占比人为构造，不代表部署风险。

重新训练生成的fitted_model.joblib为本地缓存，未作为网站下载发布；验证脚本只读取数值数据与CSV，无需加载模型对象。完整源库约285 MB，不在此重复发布。

# 第十五章汇报讲稿

建议总时长约10—12分钟，实际以课程安排为准。

## 第1页

建议45秒。我们的重点是建立可复核的分析证据。先导实验发现标签问题；确认实验中概率有所改善，但未知拒识仍不可靠。后续不以单一高分概括可信性。

来源：本组PROTOCOL.md及results/metrics.json。

## 第2页

建议55秒。校准关注概率与频率的关系，共形通常在相应数据条件下提供边际覆盖。适用域是输入支持问题，拒识进一步决定何时转交复测。解释模型需要额外的化学和对照证据。

来源：Guo et al. 2017 https://proceedings.mlr.press/v70/guo17a.html；Angelopoulos & Bates v6 https://arxiv.org/abs/2107.07511v6；Jackson & Mudholkar 1979；论文表2。

## 第3页

建议65秒。来源字段不是天然无误的真值。冲突发现于所下载的RamanLab整理库，不据此指责整个原RRUFF项目。没有在看过的测试集上改标后宣称性能提升。新任务只按理想式字符串定义有限规则类，不能替代完整矿物鉴定。

来源：RamanLab v1 https://doi.org/10.5281/zenodo.15717961；CSIRO https://spectroscopy.csiro.au/material/Gasp%C3%A9ite；AUDIT_LOG.md。

## 第4页

建议60秒。固定532 nm、已处理且非定向的谱，窗口200到1200 cm⁻¹，插值间隔2 cm⁻¹共501点。未知含Si和O且不含CO3、SO4、PO4、AsO4，可能有SiO2，不统称硅酸盐。化学式仅生成标签，不进入模型。编号隔离不等于矿物种、产地和仪器批次隔离。

来源：data/data_audit.json；data/sample_manifest.csv；PROTOCOL.md。

## 第5页

建议55秒。均值可帮助观察峰区，但掩盖类内变化。训练集PCA图与全部501点分析见论文图3。我们没有根据测试谱的视觉分离程度选样。

来源：results/evaluation_arrays.npz，roles=train；图3。

## 第6页

建议60秒。每折重新拟合PCA，候选维数5、10、20，C为0.1、1、10，按验证NLL选择。温度优化在30个校准样品上完成。T²和Q分别除以训练95%分位数再取较大值；阈值按专用验证集90%经验分位数higher约定。这个90%不是未知检出保证。

来源：PROTOCOL.md；results/inner_cv_results.csv；results/metrics.json。

## 第7页

建议65秒。正温度不改变类别排序，准确率与宏F1保持不变。NLL、Brier是概率质量指标，不都是纯校准误差。配对区间来自2000次重采样，仅描述这36个编号，不包括划分、标签与仪器变化。可靠性图每箱数量与Wilson区间见论文图4。

来源：results/metrics.json known_before/known_after及paired_nll_delta_after_minus_before。

## 第8页

建议60秒。未知接受率分母为100个未知，而条件错误率分母为34个已接受已知。主规则接受81个未知，区间72.2%到87.5%。AUROC并不说明预设阈值可用。附加概率基线接受95个未知。没有用最终测试重新挑阈值后替换结果。

来源：论文表5；results/metrics.json tq_rejection/msp_reference。

## 第9页

建议55秒。曲线是固定测试输出上的描述性排序，不提供严格风险控制保证。混合已接受115个中94个错误，错误率81.7%，受人为未知比例影响。部署未知比例改变时不能照搬。可以现场打开交互页面演示全接受和全拒识。

来源：results/evaluation_arrays.npz；论文图5；interactive/index.html。

## 第10页

建议55秒。两个样品的原始来源理想式和全窗口SNV谱见论文图6和sample_manifest.csv。模型归因或峰形观察只能产生待检验解释。确认实验没有把来源分类当作化学真值，也未对所有理想式作全面鉴定。

来源：results/metrics.json failure_analysis；data/sample_manifest.csv；论文图6。

## 第11页

建议55秒。准确率61.1%到77.8%，未知接受率52%到85%。同一数据池的随机划分主要检查开发边界敏感性，不能据此声称跨仪器稳定。下一步需要按矿物种和仪器等真实推广对象留出。

来源：results/metrics.json sensitivity_runs，明确5个种子。

## 第12页

建议55秒。现场演示准备：打开interactive/index.html，预设阈值可见34个已知和81个未知被接受，全拒识时错误率记不适用。所有资源已有离线包。课程GitHub提交与PR合并需要在实际仓库核对，不能把本地文件准备等同于完成仓库提交。收尾可讨论为什么标签核查也属于可信智能分析。

来源：README.md、PROTOCOL.md、verification.json；完整参考文献见论文。

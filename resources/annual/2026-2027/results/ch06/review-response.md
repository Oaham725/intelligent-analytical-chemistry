# 第6章交叉评审整改记录

本次整改对应 [Issue #4](https://github.com/Oaham725/intelligent-analytical-chemistry/issues/4) 和 [PR #5](https://github.com/Oaham725/intelligent-analytical-chemistry/pull/5)。2026-11-09 重跑 ESOL 实验并同步更新章节、图表、探查器、传承题答案及年度归档。待评审人复核和教师验收。

| 评审意见 | 复核发现 | 整改及证据 |
|---|---|---|
| G13 补充骨架测试集构成 | 种子42和44均测试同一批316条无环分子，种子43测试224条有环分子 | 正文新增每个种子的有环与无环计数及三个模型的MAE。图6-5标明所示骨架测试集仅含无环分子。[测试集构成](esol/split_composition.csv) · [逐种子指标](esol/metrics.csv) |
| G13 统一相似度阈值 | 旧版按钮保留T等于0.40的分子，但图例和散点配色将其划入高相似组 | 按钮、散点与分层统计统一为T ≤ 0.40（橙色）和T > 0.40（绿色）。使用随机留出、种子42和Ridge下的边界分子ESOL-1045复测。 |
| G14 区分种子数与实际划分数 | 6组配置中，骨架42与44的规范异构SMILES训练集合及测试集合分别相同 | 归档保留所有运行配置，汇总按不同划分等权计算。随机3个、骨架2个，共5个不同划分。汇总增加 `n_seeds` 与 `n_distinct_splits`。[汇总表](esol/summary.csv) · [划分名单](esol/split_assignments.csv) |
| G14 固定5-NN的并列次序 | 旧代码按训练行序打破相似度并列。骨架42与44对同一批样本的316条5-NN预测中有44条差异超过10⁻¹² | 按Tanimoto降序、规范异构SMILES升序选邻居。整改后316条配对预测逐条完全一致。[逐分子预测](esol/predictions.csv) |

原评审见 [G13](https://github.com/Oaham725/intelligent-analytical-chemistry/pull/5#pullrequestreview-5809502394) 和 [G14](https://github.com/Oaham725/intelligent-analytical-chemistry/pull/5#pullrequestreview-5811334147)。

按不同划分等权汇总后，Morgan 5-NN随机与骨架MAE分别为1.018和1.721，Ridge分别为0.786和0.841，单位为log10(mol/L)。骨架留出下Morgan 5-NN的样本SD由旧版0.527更新为0.647，其中包含并列规则修正与汇总权重变更。样本SD描述同一份数据上这些划分之间的变化。图6-5所用骨架种子42中，Morgan 5-NN的低相似子集为308/316条，MAE约2.193，RMSE约2.492。

从仓库根目录可重算实验和核对归档。[运行说明](../../../../../code/ch06_exercises/README.md)

```text
python code/ch06_exercises/verify_outputs.py
python code/ch06_exercises/build_explorer_data.py --check
node code/ch06_exercises/check_site.cjs
```

探查器可手动复查。选择随机留出、种子42与7描述符＋Ridge，点击“低相似邻域”，再搜索ESOL-1045。预期保留该分子，散点为橙色，点选后详情显示最近邻Tanimoto为0.400。

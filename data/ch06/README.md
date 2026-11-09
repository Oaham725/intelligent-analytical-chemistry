# 第6章数据说明

- `delaney-processed.csv`：[DeepChem公开处理表快照](https://github.com/deepchem/deepchem/blob/970b0d32771f1d67175d4f4a630e13f446ba97a8/datasets/delaney-processed.csv)。源blob为`970b0d32771f1d67175d4f4a630e13f446ba97a8`；实际文件SHA256与处理版本在年度结果的`run_manifest.json`中记录。
- 原始研究：Delaney J S. ESOL: Estimating Aqueous Solubility Directly from Molecular Structure. *Journal of Chemical Information and Computer Sciences* 2004, 44(3), 1000–1005. DOI: [10.1021/ci034243x](https://doi.org/10.1021/ci034243x)。
- 终点仅使用`measured log solubility in mols per litre`，单位log10(mol/L)。其他预计算描述符与`ESOL predicted`列不作为输入。
- 规范isomeric SMILES去重，保留首条并审计11条重复及标签差异；该确定性策略不表示首条实验测量更准确。未擅自把冲突测量平均。
- `molecules.csv`给出六个明确指定结构；`problem_card.md`、`data_dictionary.csv`与`representation_failures.csv`记录任务、字段与信息损失边界。

数据快照不是统一实验条件的保证；处理表缺少逐条pH、温度、盐型与晶型。独立预测能力须在匹配使用情境的测试上验证。

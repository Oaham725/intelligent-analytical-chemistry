# 第6章：表示信息与结构外推实践

关联任务：[Issue #4](https://github.com/Oaham725/intelligent-analytical-chemistry/issues/4)。本目录提供六分子表示辨识、真实ESOL基线及保存结果的独立校验；不训练GNN，也不复现各前沿论文的全部基准。

## 从仓库根目录运行

```text
python -m pip install -r code/ch06_exercises/requirements.txt
python code/ch06_exercises/case_study.py --output resources/annual/2026-2027/results/ch06
python code/ch06_exercises/esol_baseline.py --data data/ch06/delaney-processed.csv --output resources/annual/2026-2027/results/ch06/esol
python code/ch06_exercises/verify_outputs.py
python code/ch06_exercises/build_explorer_data.py --check
node code/ch06_exercises/check_site.cjs
```

验证脚本和探查器数据生成脚本分别使用Python标准库或Node内置模块。要保留已提交输出，可将两项计算的输出目录改为同一个临时目录（ESOL在该目录的`esol/`子目录），再用`verify_outputs.py --results 临时目录`检查。计算脚本会写入所指定的输出目录。重新发布探查器数据时，去掉 `build_explorer_data.py` 的 `--check`，可用 `--results` 指定结果根目录，用 `--output` 指定JS文件。

## 应观察到什么

- 六分子：乙醇/二甲醚质量相同但HBD为1/0；E/Z与乳酸镜像对在关闭立体选项时指纹相似度为1，启用后分别约0.4286和0.6923。六个样本只检验分辨能力，不用于声称结构外推性能。
- ESOL：原表1128条，规范isomeric SMILES身份去重后1117条，11条重复单独保存，不擅自平均冲突标签。描述符重新计算，未使用表内ESOL预测列。
- 固定参数：Ridge alpha=1；Morgan radius=2、2048位、includeChirality=True；Tanimoto kNN k=5；种子42/43/44。标准化只拟合训练集。所有无环分子同组，完整骨架分配可能使比例偏离80/20。
- 6组运行配置对应5个不同划分。骨架种子42与44的测试分子完全相同，均为316条无环分子。种子43测试224条有环分子。汇总按各类不同划分等权计算，Ridge随机与骨架平均MAE约为0.786与0.841，Morgan 5-NN约为1.018与1.721，单位log10(mol/L)。并列近邻按规范异构SMILES升序排列。
- `rejected_records.csv`为空表示本快照没有解析或标签拒绝记录，不是数据文件丢失。

`verify_outputs.py`检查原始快照SHA256、去重身份、六组运行配置及五个不同划分、骨架隔离、Ridge训练内均值和尺度、保存预测与18组指标、测试集构成、相同划分的5-NN预测、相似度边界及不同划分的等权汇总；`check_site.cjs`检查章节顺序、本地下载资源、原生脚本入口及浏览器汇总与保存指标一致。两者不替代其他同学的独立复现、浏览器无障碍检查或教师评审。

## 浏览器人工复核

从仓库根目录启动静态服务器，例如`python -m http.server 4173`，打开`http://127.0.0.1:4173/#/docs/ch06`。

1. 检查图谱、课件和资源入口；6.1—6.7原生组件应显示具体控件。
2. 在反事实表示工作台保留分子量，加入HBD后比较冲突；切换乳酸镜像任务，保留立体信息再模拟预先删除，记录前后方案。
3. 在真实结果探查中选择不同模型、划分、种子和相似度区间；检查空子集不显示零误差，点击样本查看残差；导出的是对应的真实记录。
4. 检查Space/Enter、Tab、重置、刷新后本地记录、窄屏滚动；错误选项应有具体理由。
5. 从第6章切换到第2章，检查原有组件与正文样式不受影响；预测数据只在进入第6章时按需加载。

## 数据、版本与限制

原始方法：Delaney, *J. Chem. Inf. Comput. Sci.* 2004, DOI [10.1021/ci034243x](https://doi.org/10.1021/ci034243x)。处理表来自[DeepChem](https://github.com/deepchem/deepchem/blob/970b0d32771f1d67175d4f4a630e13f446ba97a8/datasets/delaney-processed.csv)，快照哈希、工具版本、参数和清洗策略见`run_manifest.json`。

该表缺少逐条pH、温度、盐型和晶型条件；残差不能直接证明机制。比较同时改变表示与算法，固定超参数也会影响相对表现。前沿卡是文献证据整理；真实电子特征、学习近似与实验真值分别表述。

准备合并时需据实完成成员独立复核、交叉评审和正式贡献记录；Word出版稿尚未同步；学生汇报PPTX已归档，另见年度presentations/ch06/README.md。对外评审记录与本章收到的评审分别维护，最新状态见年度results/ch06/delivery-status.md。

# G07 第7章默认实验数值归档

这里保存可直接核验的默认教学实验输出，全部来自**模拟数据**。读者不必先安装 PyTorch 或重新训练，就能从预测与逐视频指标复算正文中的汇总结果。原始图像、模型权重和真实实验数据不在本归档中。

## 文件与来源

| 文件 | 内容与评价单位 | 记录数 |
| --- | --- | ---: |
| [spectra/metrics.json](spectra/metrics.json) | 四模型 × 三种子的所选轮次、参数量、分层测试指标与分区统计 | 12 次运行 |
| [spectra/predictions.csv](spectra/predictions.csv) | 重复扫描概率平均后的样品级预测；每次运行 96 个样品 | 1152 |
| [spectra/history.csv](spectra/history.csv) | 训练扫描损失、验证样品损失；每次运行 30 轮 | 360 |
| [lptem/metrics.csv](lptem/metrics.csv) | 两条件 × 两方法 × 每条件 8 段视频的分割指标 | 32 |
| [lptem/training.csv](lptem/training.csv) | CNN 每轮训练加权 BCE | 20 |
| [summary.json](summary.json) | 校验器从上述数值重新计算的均值、记录数与起止损失 | — |
| [manifest.json](manifest.json) | 六个数值文件的 SHA-256、实际运行环境、种子、命令及来源说明 | — |

光谱文件来自 2026-11-05 增加数据一致性检查后的默认重跑。`history.csv` 和 `predictions.csv` 与此前 2026-11-03 已验证输出逐字节相同，`metrics.json` 中原有 `runs`、`data_seed`、`batches` 不变，增加了 `dataset_summary`。LPTEM 文件来自 2026-11-03 已实际运行并重复核验的默认实验；本次归档没有重新训练 LPTEM，也没有手工补造输出。

`dataset_summary` 记录训练/验证/测试分别有 144/48/96 个独立样品、288/96/192 条扫描，每样品两条扫描。测试批次为 8–11，每批 24 个样品。校验器在该字段存在时逐项核对样品数、扫描数、批次和每样品扫描数。跨集合独立性由 `ch07.py` 运行时检查与分组负例测试覆盖；测试集预测文件本身不能重新证明训练、验证数据没有交叉。

## 不训练即可验证

在仓库根目录运行，只需 Python 标准库，无需 NumPy、PyTorch 或 Matplotlib。以下命令已在 Python 3.12.14、Windows 11 上执行，退出码均为 0。

```bash
python code/ch07_exercises/verify_results.py
python -m unittest discover -s code/ch07_exercises -p test_verify_results.py -v
```

默认检查本目录；指定其他副本可用 `--archive 路径`。检查通过后，可另存复算结果：

```bash
python code/ch07_exercises/verify_results.py --write-summary checked-summary.json
```

校验器先检查记录结构与统计一致性，再比对归档校验和。它从光谱预测重新计算每模型/种子的准确率、宏 F1 和混淆矩阵，并分别核对全部测试、常规/偏移条件及每个批次与 `metrics.json` 一致；同时核查概率范围、概率和、argmax、样品标签与批次跨运行一致、组合完整性和验证损失最低轮次。各类数量及默认协议写在脚本中，不依赖可随意改写的清单来决定“应该有多少条”。

LPTEM 部分按独立视频等权重算四组 IoU、Dice 与面积 MAE 均值，并检查逐视频 Dice–IoU 关系、固定验证阈值及 20 轮训练记录。这里复算的是**逐视频指标的汇总**，没有从原始掩膜重新计算交并集或逐帧面积。最后核对 `summary.json` 和正文表格的舍入值。

12 项回归测试在临时副本中制造缺失记录、同条数重复记录、概率/类别冲突、跨运行标签冲突、混淆矩阵或所选轮次错误、LPTEM 记录缺失、汇总值错误及单纯字节变化。其中内容错误测试主动绕开校验和，确认程序仍会因统计或结构不一致失败；仅字节变化则由 SHA-256 拒绝。测试不会修改正式归档。

## 对应训练命令及环境

这些命令说明如何重新生成实验，不是快速核验所必需。

| 实验 | 实测环境 | 随机设置 |
| --- | --- | --- |
| 光谱，2026-11-05 | Python 3.12.14、NumPy 2.3.5、PyTorch 2.15.0+cpu；Windows 11 | 数据种子 2026，模型种子 7/19/42，30 轮 |
| LPTEM，2026-11-03 | Python 3.12.14、NumPy 2.5.4、Matplotlib 3.11.2；Windows 11 | 种子 2026，20 轮；运行时设置 `OPENBLAS_NUM_THREADS=1` |

```bash
python code/ch07.py --out runs/ch07-spectra
python code/ch07_exercises/lptem.py --seed 2026 --out runs/ch07-lptem --plot
```

以上两套依赖环境不同，具体案例的安装与数据生成说明见 `code/ch07_exercises/spectra.md`、`code/ch07_exercises/lptem.md`。归档命令中的输出目录可以更换。清单中的源脚本哈希描述实际运行时的文件字节，换行转换可能使不同平台的工作树哈希不同；校验器核对的是归档结果文件的字节与统计内容。跨软件版本或跨设备不保证逐字节相同，更新默认协议或结果时应同时审查数据、脚本、正文表格、汇总及清单，不能仅重写校验和来使失败消失。

## 复算均值

| 光谱模型 | 全测试宏 F1 | 常规宏 F1 | 偏移宏 F1 |
| --- | ---: | ---: | ---: |
| 逻辑回归 | 0.954852 | 0.979146 | 0.929781 |
| MLP | 0.948314 | 0.979146 | 0.917728 |
| 1D-CNN | 0.955243 | 0.993049 | 0.917728 |
| Transformer | 0.961775 | 0.993049 | 0.930316 |

| LPTEM 条件 | 方法 | 平均 IoU | 平均 Dice | 面积 MAE（像素平方） |
| --- | --- | ---: | ---: | ---: |
| 同分布 | 局部均值 | 0.635631 | 0.772432 | 26.625 |
| 同分布 | CNN | 0.672637 | 0.800812 | 25.656 |
| 偏移 | 局部均值 | 0.265227 | 0.399665 | 69.219 |
| 偏移 | CNN | 0.255147 | 0.388721 | 68.594 |

本目录的 `.gitattributes` 对 CSV 和 JSON 禁用 Git 的换行转换，以保留实际输出的字节及其 SHA-256。在其他平台克隆后也应先运行校验器，再使用这些结果。

完整精度见 `summary.json`。这些结果只支持相应模拟条件下的教学对照，不构成真实 LPTEM 分割性能或机制判断的证据。

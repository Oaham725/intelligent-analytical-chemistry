# 第11章成员 B：UHRED 思路教学案例

关联任务：[课程 Issue #9](https://github.com/Oaham725/intelligent-analytical-chemistry/issues/9)。

本贡献提供真实矿物高光谱处理、传统方法与简化卷积自编码器对照、组分类别图、模拟噪声实验及数据划分审计。**不是原论文精确复现，也不是定量浓度成像。**

## 查看交付成果

- [中文实验报告](docs/B_results.md)
- [真实矿物组分类别图](results/real/real/spatial/component_maps.png)
- [模拟噪声评价图](results/synthetic/quality_summary.png)
- [全部指标：真实数据](results/real/metrics.csv)、[模拟数据](results/synthetic/metrics.csv)
- [技术解释](docs/ch11_B_insert.md)、[B部分汇报讲稿](docs/B_presentation_notes.md)
- [实验题与答案](resources/annual/2026-2027/questions/ch11_case_question_B.md)
- [论文、代码和数据来源](resources/annual/2026-2027/references/ch11_UHRED.md)
- [本机验证记录](docs/verification.json)

## 安装与运行

建议 Python 3.12，在仓库根目录执行；CPU 可运行。

```sh
python -m pip install -r code/ch11_exercises/requirements-lock.txt
python code/ch11_exercises/download_data.py
python code/ch11_exercises/prepare_real.py --train data/raw/fov1.tif --test data/raw/fov2.tif --output data/mineral_small.npz
python code/ch11_exercises/run.py --data data/mineral_small.npz --output results/real --epochs 80
python code/ch11_exercises/run.py --output results/synthetic --epochs 80
python code/ch11_exercises/build_report.py
python code/ch11_exercises/verify.py
```

原始 TIFF 约119 MB/文件。仓库提供下载脚本，不重新分发原始 TIFF、抽样真实数据或包含真实光谱的预测数组。运行后会在本地产生这些文件。若原始数据下载不可用，仍可独立执行模拟实验命令；完整报告生成和验证需先跑完两类实验。

依赖锁定文件记录已验证的核心版本；常规版本范围见 requirements.txt。首次训练耗时依硬件而异，本次在CPU执行每类实验约1分钟，不含下载和依赖安装。

模型重新加载：

```sh
python code/ch11_exercises/predict.py --model-dir results/real/real/spatial --data data/mineral_small.npz --output results/real/reloaded_prediction.npz
```

输出包括 PNG/SVG 图表、CSV 指标、训练记录、模型权重、聚类中心、显示映射、预测数组和本地 viewer.html。GitHub中的HTML可下载后本地打开，或在运行后使用本地产生的查看器。

## 数据、方法及复现边界

- [原论文](https://doi.org/10.1364/OE.439662)：Abdolghader 等，Optics Express 29(21), 34205–34219 (2021)。
- [作者代码](https://github.com/CLEANit/SRS2021) 为GPL-3.0；本组独立编写教学实现，未把作者原始代码作为本组成果提交。
- [作者数据](https://clean.energyscience.ca/datasets/)公开链接见下载脚本。数据页未明确单列这套SRS数据再分发许可，故采用来源链接和下载方式，不重新授予数据许可。
- 原网络使用四层卷积等结构；本组为两层1D卷积、6维瓶颈和插值解码器。保留带噪自重建及潜在特征k-means思路，固定K=3，不声称自动发现三种矿物。
- 真实FOV1/FOV2原始为909×256×256，空间每4像素、光谱每3通道抽样成64×64×303。抽样会丢信息，不是超分辨提升。未标定通道到拉曼位移，未复现论文手工饱和像素替换。
- 归一化、模型选择与聚类中心仅用允许的训练/验证数据；FOV2不参与拟合。随机划分与带两列缓冲的空间划分均保存索引，并核查直接邻接。
- 不同视野不保证不同样品、批次或仪器。真实矿物无干净参考和像素类别真值，不报告真实识别准确率，不把处理改变量当真实误差，也不把Cluster命名为已确认矿物或浓度。
- 模拟解析光谱不是真实矿物谱；两视野共享几何布局而光谱和噪声不同。每个噪声水平单独训练，非固定模型抗噪测试；只报告固定种子725的教学结果。
- 模拟组分标签仅用于最终评价及训练区簇编号匹配，不进入自编码器训练或模型选择。训练区必须覆盖全部类别。
- 2021论文是案例来源，不自动满足年度近三年文献要求；A负责补充前沿文献，C负责基础图整合与最终汇报PDF。独立同学复核及交叉评审仍待完成。

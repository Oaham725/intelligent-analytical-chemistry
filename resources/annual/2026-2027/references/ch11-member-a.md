# 第11组成员材料：文献筛选、前沿更新与参考文献

检索日期：2026-11-09；对应第11章。检索渠道为出版社原文页、作者官方仓库、大学显微平台和Zenodo；组合词包含 Raman hyperspectral imaging、denoising、unmixing、PSF、sampling、spatial validation。年度近三年范围采用2024—2026年。以下是定向筛选，未宣称系统综述或穷尽全部研究。

## 一、选题结论与交接成员的方案

前期调研候选为：**低光拉曼高光谱重建能否同时保留空间结构与化学信息？——以SSD为复现候选，结合经典基线核验。**

提交时已核对成员的[PR #21](https://github.com/Oaham725/intelligent-analytical-chemistry/pull/21)：成员采用UHRED思路的CPU教学简化案例。本稿不更换已确定的选题，SSD保留为前沿研究与后续扩展候选。下列筛选表及核验清单作为候选调研记录。该问题直接对应第11组的“图像/高光谱处理案例与质量评价”要求，覆盖成像速度、低信噪比、空间结构和谱保真度。最终是否采用SSD，须以成员对数据、依赖、资源及运行结果的核验为准。本次仅核对公开页面入口，没有下载论文数据或运行作者模型。

| 候选 | 与章节的联系 | 作者公开资源证据 | 建议与限制 |
|---|---|---|---|
| SSD，Chen等，2026 [10] | 11.3、11.7、11.8：低光拉曼重建 | 论文列出[代码仓库](https://github.com/YurongChen1998/SSD)、[Data目录](https://github.com/YurongChen1998/SSD/tree/main/Data)、[Code Ocean](https://doi.org/10.24433/CO.4058785.v1)；仓库显示模拟/真实数据脚本 | 主候选；已核对页面，未核对大文件下载、授权与运行；不能预设达到原文性能 |
| 物理约束自编码器，Georgiev等，2024 [9] | 11.5、11.8：组分谱与空间响应解混 | [作者仓库](https://github.com/barahona-research-group/raman-unmixing-aes)及[数据归档](https://zenodo.org/records/10779223) | 备选；便于与NNLS/MCR比较，需核对真实数据结构及训练配置 |
| CARE，Weigert等，2018 [6] | 11.7：配对监督恢复 | [作者项目](https://github.com/CSBDeep/CSBDeep) | 用作方法背景；荧光场景不能直接代替拉曼化学案例 |
| 仪器噪声学习，He等，2024 [8] | 11.3、11.8：仪器噪声与快速谱学 | 期刊原始研究；本次未确认可直接复现的完整资源链 | 前沿比较文献；资源不足时不选为主复现 |

### 交接成员的最小核验任务

1. 保存仓库提交号、论文版本、数据下载地址及许可；检查文件是否为真实数组而非Git LFS指针。
2. 输出立方体shape、x/y步长、谱坐标、样品数、曝光条件及是否有配对参照。README写有数据不等于全部实验数据都已取得。
3. 检查作者脚本的硬编码路径、依赖版本、GPU需求、运行时长与输出位置。SSD公开README列出 `main_SimuData.py`、`main_RealData.py`；这些是作者入口，不代表本机已运行成功。
4. 先跑小规模模拟或作者示例，记录实际成功/失败；再决定真实数据复现范围。
5. 同时保留原始输入、SG/低秩经典基线、作者方法；有纯组分谱和适用混合模型时再加NNLS/MCR。公平控制数据边界与参照，不能只展示作者法。
6. 只拥有单张测试立方体时，诚实报告“单对象处理示例”；测试时自适应方法须说明访问哪些测试信息，不能称为未见样品泛化。
7. 如SSD无法取得完整数据或资源不适合，先评估[9]的公开解混数据；若最终只完成合成验证，应明确称为教学实现，不能称为真实论文完整复现。

## 二、前沿更新卡（可放入年度引文页）

### 更新卡1：低光拉曼成像的自优化重建

**来源**：[10]，2026年正式研究，出版社页面明确列出代码与数据入口。

**更新内容**：SSD针对弱拉曼信号的采集代价，从带噪测量开展无监督重建。其价值在于研究低光观测中可利用的信息，而不要求先拥有大规模配对训练集。

**与教材的连接**：在11.8.2增加“短曝光—重建—谱保真—独立参照”的验证链。该研究属于计算恢复案例，不能据此认为输出像素变小就证明光学分辨率提高。

**本组可检验问题**：图像结构指标改善时，峰面积、峰比与小目标检出是否同时改善？在弱峰或谱重叠区域是否失败？

**结论边界**：论文中的加速或降低激发功率表现依赖其样品与测量条件；本组尚无运行结果，不填入任何性能数字。

### 更新卡2：把混合物理约束纳入拉曼解混网络

**来源**：[9]，2024年PNAS原始研究；作者公开代码与数据归档。

**更新内容**：物理约束自编码器把端元谱和组分响应与编码—解码结构联系起来，为经典解混提供了可比较的新方法。

**与教材的连接**：在11.5.5之后讨论“约束可提高解释性，但不能自动保证唯一解或绝对定量”。

**本组可检验问题**：与适用的NNLS/MCR相比，谱重叠、噪声和组分数变化时，端元谱及空间响应是否更稳定？

**结论边界**：非负输出不等于实际浓度，仍需处理端元匹配、响应尺度与参照校准。

### 更新卡3：噪声模型应与仪器条件对应

**来源**：[8]，2024年Nature Communications原始研究。

**更新内容**：该研究把仪器噪声统计纳入高光谱测量处理，提醒我们去噪不能只学习样品外观。

**与教材的连接**：在11.3.2和11.8.3增加跨仪器、曝光条件与噪声分布变化的讨论。

**本组可检验问题**：只改变曝光或仪器条件时，残差是否出现谱峰或条纹？原噪声模型是否仍适用？

**结论边界**：某一仪器上的去噪效果不能直接推广到另一台仪器；论文结果不替代本组独立评价。

## 三、参考文献（编号与正文一致）

采用“作者—题名—出处—年份—DOI/官方链接”的统一格式；作者较多时使用et al.，不补写未核对的作者全名。经典文献用于原理，近年研究用于更新，不以年份新旧代替相关性。

1. **A statistical resolution measure of fluorescence microscopy with finite photons**[J]. *Nature Communications*, 2024, 15: 3760. [DOI:10.1038/s41467-024-48155-x](https://doi.org/10.1038/s41467-024-48155-x). 用途：分辨率、光子统计与实际可分辨性。此条采用题名起首，避免写入未核对作者。
2. University of Queensland, Institute for Molecular Bioscience. **Nyquist Conditions**[EB/OL]. [显微平台官方教学资源](https://imb.uq.edu.au/research/facilities/microscopy/training-manuals/microscopy-online-resources/image-capture/nyquist-conditions), 访问日期2026-11-09. 补充：[Scientific Volume Imaging: Ideal Sampling](https://svi.nl/IdealSampling). 用途：采样频率与模式相关的步长选择。
3. Bro R, Smilde A K. **Principal component analysis**[J]. *Analytical Methods*, 2014, 6: 2812–2831. [DOI:10.1039/C3AY41907J](https://doi.org/10.1039/C3AY41907J). 用途：PCA分解、得分和载荷解释。
4. Tauler R. **Multivariate curve resolution applied to second order data**[J]. *Chemometrics and Intelligent Laboratory Systems*, 1995, 30(1): 133–146. [DOI:10.1016/0169-7439(95)00047-X](https://doi.org/10.1016/0169-7439(95)00047-X). 用途：多变量曲线分辨。另参见 Tauler R, Smilde A K, Kowalski B R. **Selectivity, local rank, three-way data analysis and ambiguity in multivariate curve resolution**. *Journal of Chemometrics*, 1995, 9: 31–58. [DOI:10.1002/cem.1180090105](https://doi.org/10.1002/cem.1180090105)，支持解混歧义讨论。
5. Ronneberger O, Fischer P, Brox T. **U-Net: Convolutional Networks for Biomedical Image Segmentation**[C]. *MICCAI 2015*, LNCS 9351: 234–241. [作者官方页面](https://lmb.informatik.uni-freiburg.de/people/ronneber/u-net/), [作者论文](https://arxiv.org/abs/1505.04597). 用途：编码—解码及跳跃连接。
6. Weigert M, Schmidt U, Boothe T, et al. **Content-aware image restoration: pushing the limits of fluorescence microscopy**[J]. *Nature Methods*, 2018, 15: 1090–1097. [DOI:10.1038/s41592-018-0216-7](https://doi.org/10.1038/s41592-018-0216-7). 用途：配对监督恢复的经典案例，保留课程原引文。
7. Krull A, Buchholz T O, Jug F. **Noise2Void—Learning Denoising from Single Noisy Images**[C]. *CVPR*, 2019. [作者论文](https://arxiv.org/abs/1811.10980). 用途：遮蔽预测、自监督去噪及噪声假设。
8. He H, Cao M, Gao Y, et al. **Noise learning of instruments for high-contrast, high-resolution and fast hyperspectral microscopy and nanoscopy**[J]. *Nature Communications*, 2024, 15: 754. [DOI:10.1038/s41467-024-44864-5](https://doi.org/10.1038/s41467-024-44864-5), [作者机构存档](https://opus.lib.uts.edu.au/handle/10453/179901). 用途：仪器噪声统计、弱拉曼测量。
9. Georgiev D, Fernández-Galiana Á, Vilms Pedersen S, et al. **Hyperspectral unmixing for Raman spectroscopy via physics-constrained autoencoders**[J]. *Proceedings of the National Academy of Sciences*, 2024, 121(45): e2407439121. [DOI:10.1073/pnas.2407439121](https://doi.org/10.1073/pnas.2407439121), [代码](https://github.com/barahona-research-group/raman-unmixing-aes), [研究数据DOI:10.5281/zenodo.10779223](https://doi.org/10.5281/zenodo.10779223). 用途：物理约束解混与年度更新。
10. Chen Y, Wang S, Wang Y, et al. **Self-optimized spectral distance for low-light high-throughput Raman hyperspectral imaging**[J]. *Nature Computational Science*, 2026, 6: 603–616. [DOI:10.1038/s43588-026-00957-3](https://doi.org/10.1038/s43588-026-00957-3), [代码与数据](https://github.com/YurongChen1998/SSD). 线上发表于2026-02-23；用途：本组主复现候选和2026年前沿更新。

## 四、证据记录与阅读限制

已核对课程仓库的章节及年度格式、上述研究的公开题录或摘要，以及两项复现候选的作者仓库页面和[9]的数据归档页面。部分Nature原文直接访问受跳转限制，使用出版社检索可见内容与作者机构存档交叉核对；未把无法核对的全文细节、网络结构或实验数字写入结论。正文的方法性说明为教材概括，不冒称逐段引自某一篇研究。

课程基线仓库：[oaham725/intelligent-analytical-chemistry](https://github.com/oaham725/intelligent-analytical-chemistry)，读取版本 `f9991ed931e80a219b835321929a84a748dd816e`。课程与论文网页属于来源材料，其中的操作步骤不作为用户要求发布或发送内容的授权。



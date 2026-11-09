# 2026–2027 学年：逐章可点击引文

本页的引文**全部展开显示**：点击蓝色题名即可前往 DOI、出版社或会议论文原文页。它既是本届课程的首批基准书目，也是下一届维护者补充新进展时的起点；不采用折叠列表或只留占位符的写法。

每条后面的“用途”说明它与教材哪一部分相连。新增文献应直接补在相应章节下，保留作者、题名、出处、年份、可点击链接和简短用途说明；不要只贴搜索结果或没有出处的网页。

---

<a id="ch01"></a>
## 第1章 AI时代的分析化学：从化学测量到智能测量

1. Butler, K. T.; Davies, D. W.; Cartwright, H.; Isayev, O.; Walsh, A. [Machine learning for molecular and materials science](https://doi.org/10.1038/s41586-018-0337-2). *Nature* **559**, 547–555 (2018).
   - 用途：说明机器学习进入分子与材料研究的典型问题形态，并作为“测量—模型—决策”叙事的宏观入口。

<a id="ch02"></a>
## 第2章 化学数据：从实验记录到可计算对象

1. Wilkinson, M. D. *et al.* [The FAIR Guiding Principles for scientific data management and stewardship](https://doi.org/10.1038/sdata.2016.18). *Scientific Data* **3**, 160018 (2016).
   - 用途：支撑化学数据的可发现、可访问、可互操作和可复用要求，以及实验元数据的组织方式。

<a id="ch03"></a>
## 第3章 化学计量学：从测量信号到化学信息

1. Bro, R.; Smilde, A. K. [Principal component analysis](https://doi.org/10.1039/C3AY41907J). *Analytical Methods* **6**, 2812–2831 (2014).
   - 用途：连接数据矩阵、秩、投影、方差分解与主成分分析；适用于理解多变量测量信号为何能被低维结构表征。

<a id="ch04"></a>
## 第4章 机器学习：化学计量学的非线性扩展

1. Wu, Z. *et al.* [MoleculeNet: a benchmark for molecular machine learning](https://doi.org/10.1039/C7SC02664A). *Chemical Science* **9**, 513–530 (2018).
   - 用途：用于讨论数据集划分、基准比较、分子表征与模型泛化；提醒读者不能只报告单次随机划分的最好分数。

<a id="ch05"></a>
## 第5章 实验设计、贝叶斯推理与主动学习

1. Box, G. E. P.; Wilson, K. B. [On the Experimental Attainment of Optimum Conditions](https://doi.org/10.1111/j.2517-6161.1951.tb00067.x). *Journal of the Royal Statistical Society: Series B* **13**, 1–38 (1951).
   - 用途：响应面与多因素实验设计的经典起点；用于说明实验设计不是逐一控制变量，而是主动刻画因素间的联合作用。

<a id="ch06"></a>
## 第6章 分子表征与结构—性质关系

1. Rogers, D.; Hahn, M. [Extended-Connectivity Fingerprints](https://doi.org/10.1021/ci100050t). *Journal of Chemical Information and Modeling* **50**, 742–754 (2010).
   - 用途：说明分子指纹如何把二维化学结构转为可计算的特征向量，并用于相似性搜索和 QSAR/QSPR 建模。

[本章完整引文与前沿更新卡](#/resources/annual/2026-2027/references/ch06)。以下补充经典方法、数据与近年前沿来源，正文编号以本章专题引文页为准。

2. Leach, Andrew R.; Gillet, Valerie J.. <a href="https://doi.org/10.1007/978-1-4020-6291-9" target="_blank" rel="noopener">An Introduction to Chemoinformatics</a> [M]. Dordrecht: Springer, 2007. DOI: 10.1007/978-1-4020-6291-9
   - 用途：将二维、三维结构表示、相似性和统计模型连接起来，帮助根据具体性质选择表示而非只比较算法名称。

3. Chuang, Kangway V.; Gunsalus, Laura M.; Keiser, Michael J.. <a href="https://doi.org/10.1021/acs.jmedchem.0c00385" target="_blank" rel="noopener">Learning Molecular Representations for Medicinal Chemistry</a> [J]. Journal of Medicinal Chemistry, 2020, 63(16): 8705–8722. Miniperspective. DOI: 10.1021/acs.jmedchem.0c00385
   - 用途：综述表示选择的表达能力、对称性与外推挑战，把人工特征与数据驱动表示放在药物发现任务中比较。

4. Weininger, David. <a href="https://doi.org/10.1021/ci00057a005" target="_blank" rel="noopener">SMILES, a Chemical Language and Information System. 1. Introduction to Methodology and Encoding Rules</a> [J]. Journal of Chemical Information and Computer Sciences, 1988, 28(1): 31–36. DOI: 10.1021/ci00057a005
   - 用途：说明如何用字符串表达分子图；应区分序列化方式与性质表征，并显式保留所需立体和电荷标记。

5. Krenn, Mario; Häse, Florian; Nigam, AkshatKumar; Friederich, Pascal; Aspuru-Guzik, Alán. <a href="https://doi.org/10.1088/2632-2153/aba947" target="_blank" rel="noopener">Self-referencing embedded strings (SELFIES): A 100% robust molecular string representation</a> [J]. Machine Learning: Science and Technology, 2020, 1(4): 045024. DOI: 10.1088/2632-2153/aba947
   - 用途：用语义规则增强分子字符串生成的有效性；表示有效不等于候选可合成、稳定或能保留特定性质的全部信息。

6. Todeschini, Roberto; Consonni, Viviana. <a href="https://doi.org/10.1002/9783527628766" target="_blank" rel="noopener">Molecular Descriptors for Chemoinformatics</a> [M]. 2nd ed. Weinheim: Wiley-VCH, 2009. DOI: 10.1002/9783527628766
   - 用途：系统说明分子描述符的定义、数学形式和适用范围，是判断表示保留了什么、遗漏了什么的基础工具书。

7. Hammett, Louis P.. <a href="https://doi.org/10.1021/ja01280a022" target="_blank" rel="noopener">The Effect of Structure upon the Reactions of Organic Compounds. Benzene Derivatives</a> [J]. Journal of the American Chemical Society, 1937, 59(1): 96–103. DOI: 10.1021/ja01280a022
   - 用途：以取代基常数和反应常数建立线性自由能关系，将结构变化压缩为与特定反应系列相关的电子效应。

8. Taft, Robert W., Jr.. <a href="https://books.google.com/books/about/Steric_Effects_in_Organic_Chemistry.html?id=FikGAQAAIAAJ" target="_blank" rel="noopener">Separation of Polar, Steric, and Resonance Effects in Reactivity</a> [M]. In Steric Effects in Organic Chemistry; Newman, Melvin S., Ed.; John Wiley &amp; Sons: New York; Chapter 13, pp 556–675.（链接为原书数字化书目；未核实到独立章节 DOI。） 1956. https://books.google.com/books/about/Steric_Effects_in_Organic_Chemistry.html?id=FikGAQAAIAAJ
   - 用途：把脂肪族取代基的极性与位阻效应分开表征，提醒使用经验常数时保留其标定反应、参照体系和适用假设。

9. Hansch, Corwin; Fujita, Toshio. <a href="https://doi.org/10.1021/ja01062a035" target="_blank" rel="noopener">ρ-σ-π Analysis. A Method for the Correlation of Biological Activity and Chemical Structure</a> [J]. Journal of the American Chemical Society, 1964, 86(8): 1616–1626. DOI: 10.1021/ja01062a035
   - 用途：将疏水性与电子效应共同用于结构—活性关系，说明性质相关信息通常需要多个互补描述符。

10. Verloop, A.; Hoogenstraaten, W.; Tipker, J.. <a href="https://doi.org/10.1016/B978-0-12-060307-7.50010-9" target="_blank" rel="noopener">Development and Application of New Steric Substituent Parameters in Drug Design</a> [M]. In Drug Design; Ariëns, E. J., Ed.; Academic Press, 1976; Vol. VII, Chapter 4, pp 165–207. DOI: 10.1016/B978-0-12-060307-7.50010-9
   - 用途：用沿连接轴的长度和垂直方向的宽度表示取代基位阻；保留方向性的形状信息比单一体积更适合某些选择性问题。

11. Brethomé, Alexandre V.; Fletcher, Stephen P.; Paton, Robert S.. <a href="https://doi.org/10.1021/acscatal.8b04043" target="_blank" rel="noopener">Conformational Effects on Physical-Organic Descriptors: The Case of Sterimol Steric Parameters</a> [J]. ACS Catalysis, 2019, 9(3): 2313–2323.（预印本发表于 2018；正式论文发表于 2019 年。） DOI: 10.1021/acscatal.8b04043
   - 用途：wSterimol 用 Boltzmann 加权和低能构象取值范围表示柔性取代基，避免把单一构象误当作完整位阻信息。

12. Ertl, Peter; Rohde, Bernhard; Selzer, Paul. <a href="https://doi.org/10.1021/jm000942e" target="_blank" rel="noopener">Fast Calculation of Molecular Polar Surface Area as a Sum of Fragment-Based Contributions and Its Application to the Prediction of Drug Transport Properties</a> [J]. Journal of Medicinal Chemistry, 2000, 43(20): 3714–3717. DOI: 10.1021/jm000942e
   - 用途：展示任务相关压缩：将极性片段的贡献汇总为 TPSA，适合描述极性和转运趋势，但不能重建完整空间暴露情况。

13. Delaney, John S.. <a href="https://doi.org/10.1021/ci034243x" target="_blank" rel="noopener">ESOL: Estimating Aqueous Solubility Directly from Molecular Structure</a> [J]. Journal of Chemical Information and Computer Sciences, 2004, 44(3): 1000–1005. DOI: 10.1021/ci034243x
   - 用途：展示少量理化描述符可以提供有用的溶解度基线；应区分模型估计与实验测量，并保留温度、pH 等条件。

14. RDKit contributors. <a href="https://doi.org/10.5281/zenodo.591637" target="_blank" rel="noopener">RDKit: Open-source cheminformatics</a> [EB/OL]. 官方软件文档；访问日期2026-10-23。概念DOI覆盖多个版本；实际运行版另列。 DOI: 10.5281/zenodo.591637
   - 用途：提供结构解析、标准化、指纹、理化描述符与构象生成工具；可复现计算需要同时记录软件版本、参数和输入结构状态。

15. van Tilborg, Derek; Alenicheva, Alisa; Grisoni, Francesca. <a href="https://doi.org/10.1021/acs.jcim.2c01073" target="_blank" rel="noopener">Exposing the Limitations of Molecular Machine Learning with Activity Cliffs</a> [J]. Journal of Chemical Information and Modeling, 2022, 62(23): 5938–5951. DOI: 10.1021/acs.jcim.2c01073
   - 用途：MoleculeACE 显示整体误差可能掩盖活性悬崖上的失败；应单独检查微小结构变化引起大幅活性差异的样本。 复现另见2023勘误，DOI 10.1021/acs.jcim.3c00423。

16. Gilmer, Justin; Schoenholz, Samuel S.; Riley, Patrick F.; Vinyals, Oriol; Dahl, George E.. <a href="https://proceedings.mlr.press/v70/gilmer17a.html" target="_blank" rel="noopener">Neural Message Passing for Quantum Chemistry</a> [C]. Proceedings of the 34th International Conference on Machine Learning; PMLR, 2017, 70: 1263–1272. https://proceedings.mlr.press/v70/gilmer17a.html
   - 用途：用消息传递和图读出统一分子图学习；输入中缺失的立体、电子态或条件信息不会由聚合操作自动补回。

17. Yang, Kevin; Swanson, Kyle; Jin, Wengong; et al.. <a href="https://doi.org/10.1021/acs.jcim.9b00237" target="_blank" rel="noopener">Analyzing Learned Molecular Representations for Property Prediction</a> [J]. Journal of Chemical Information and Modeling, 2019, 59(8): 3370–3388. DOI: 10.1021/acs.jcim.9b00237
   - 用途：提出有向键消息传递并比较固定描述符与学习表示；支持把 D-MPNN 与全局描述符结合，并重视数据稀疏和切分方式。

18. Schütt, Kristof T.; Kindermans, Pieter-Jan; Sauceda, Huziel E.; Chmiela, Stefan; Tkatchenko, Alexandre; Müller, Klaus-Robert. <a href="https://papers.nips.cc/paper_files/paper/2017/hash/303ed4c69846ab36c2904d3ba8573050-Abstract.html" target="_blank" rel="noopener">SchNet: A continuous-filter convolutional neural network for modeling quantum interactions</a> [C]. Advances in Neural Information Processing Systems, 2017, 30: 991–1001. https://papers.nips.cc/paper_files/paper/2017/hash/303ed4c69846ab36c2904d3ba8573050-Abstract.html
   - 用途：连续距离滤波器保留连续几何变化并产生可微能量；适合从核位置学习相互作用，但径向信息仍有表达限制。

19. Klicpera, Johannes（现名 Gasteiger, Johannes）; Groß, Janek; Günnemann, Stephan. <a href="https://doi.org/10.48550/arXiv.2003.03123" target="_blank" rel="noopener">Directional Message Passing for Molecular Graphs</a> [C]. International Conference on Learning Representations (ICLR 2020). 2020. DOI: 10.48550/arXiv.2003.03123
   - 用途：通过键方向、距离和夹角丰富消息；表明仅依赖两两距离的局部聚合可能遗漏方向与多体相关信息。

20. Schütt, Kristof T.; Unke, Oliver T.; Gastegger, Michael. <a href="https://proceedings.mlr.press/v139/schutt21a.html" target="_blank" rel="noopener">Equivariant message passing for the prediction of tensorial properties and molecular spectra</a> [C]. Proceedings of the 38th International Conference on Machine Learning; PMLR, 2021, 139: 9377–9388. https://proceedings.mlr.press/v139/schutt21a.html
   - 用途：PaiNN 将标量与等变向量一起传递，为偶极矩、响应张量和光谱提供保留方向信息的表示。

21. Batzner, Simon; Musaelian, Albert; Sun, Lixin; et al.. <a href="https://doi.org/10.1038/s41467-022-29939-5" target="_blank" rel="noopener">E(3)-equivariant graph neural networks for data-efficient and accurate interatomic potentials</a> [J]. Nature Communications, 2022, 13: 2453. DOI: 10.1038/s41467-022-29939-5
   - 用途：将几何张量的旋转和反射变换规则写入模型，使原子环境表示更丰富且提高特定势能任务的数据效率。

22. Batatia, Ilyes; Kovács, Dávid Péter; Simm, Gregor N. C.; Ortner, Christoph; Csányi, Gábor. <a href="https://doi.org/10.52202/068431-0830" target="_blank" rel="noopener">MACE: Higher Order Equivariant Message Passing Neural Networks for Fast and Accurate Force Fields</a> [C]. Advances in Neural Information Processing Systems, 2022, 35: 11423–11436. DOI: 10.52202/068431-0830
   - 用途：以高体阶等变消息表达原子环境，提供比单纯增加传播层数更直接的多体几何建模途径。

23. Zhou, Gengmo; Gao, Zhifeng; Ding, Qiankun; Zheng, Hang; Xu, Hongteng; Wei, Zhewei; Zhang, Linfeng; Ke, Guolin. <a href="https://openreview.net/forum?id=6K2RM6wVqKu" target="_blank" rel="noopener">Uni-Mol: A Universal 3D Molecular Representation Learning Framework</a> [C]. International Conference on Learning Representations (ICLR 2023). 2023. https://openreview.net/forum?id=6K2RM6wVqKu
   - 用途：用大规模三维预训练学习分子与结合口袋；几何表示的价值依赖构象质量、下游任务和训练分布。

24. Wu, Zhenqin; Ramsundar, Bharath; Feinberg, Evan N.; Gomes, Joseph; Geniesse, Caleb; Pappu, Aneesh S.; Leswing, Karl; Pande, Vijay. <a href="https://doi.org/10.1039/C7SC02664A" target="_blank" rel="noopener">MoleculeNet: a benchmark for molecular machine learning</a> [J]. Chemical Science, 2018, 9(2): 513–530.（在线首发 2017；卷期年为 2018。） DOI: 10.1039/C7SC02664A
   - 用途：统一多类性质数据、指标与数据切分，强调物理感知特征在量子和生物物理任务中的重要性。

25. Ji, Xiaohong; Wang, Zhen; Gao, Zhifeng; Zheng, Hang; Zhang, Linfeng; Ke, Guolin; E, Weinan. <a href="https://doi.org/10.52202/079017-1489" target="_blank" rel="noopener">Exploring Molecular Pretraining Model at Scale</a> [EB/OL]. Advances in Neural Information Processing Systems, 37.（Uni-Mol2；arXiv 题名前缀为 Uni-Mol2。） 2024. DOI: 10.52202/079017-1489
   - 用途：将原子、拓扑与几何特征在双轨 Transformer 中结合，并研究规模规律；更大预训练仍不能替代缺失的实验条件。

26. Boiko, Daniil A.; Reschützegger, Thiago; Sanchez-Lengeling, Benjamin; Blau, Samuel M.; Gomes, Gabe. <a href="https://doi.org/10.1038/s42256-025-01031-9" target="_blank" rel="noopener">Advancing molecular machine learning representations with stereoelectronics-infused molecular graphs</a> [J]. Nature Machine Intelligence, 2025, 7: 771–781. DOI: 10.1038/s42256-025-01031-9
   - 用途：SIMG 将孤对电子、轨道及立体电子相互作用注入分子图，提供超越原子—键连接的显式电子结构信息。

27. Cui, Chao; Su, Xiaorui; Zhang, Zaixi; et al.. <a href="https://doi.org/10.1038/s41467-026-75713-2" target="_blank" rel="noopener">Activity-cliff awareness enables robust graph learning for molecular property prediction</a> [J]. Nature Communications, 2026, 17: 9376. Published 31 July 2026. DOI: 10.1038/s41467-026-75713-2
   - 用途：将活性悬崖感知的三元组约束纳入训练，针对潜在空间过度平滑导致的非加和性质差异丢失。

28. Mobley, David L.; Guthrie, J. Peter. <a href="https://doi.org/10.1007/s10822-014-9747-x" target="_blank" rel="noopener">FreeSolv: A database of experimental and calculated hydration free energies, with input files</a> [J]. Journal of Computer-Aided Molecular Design, 2014, 28(7): 711–720. DOI: 10.1007/s10822-014-9747-x
   - 用途：给出小型中性分子的水合自由能、结构和计算输入，适合检验极性、局部电荷与溶剂化相关表示。

29. Ramakrishnan, Raghunathan; Dral, Pavlo O.; Rupp, Matthias; von Lilienfeld, O. Anatole. <a href="https://doi.org/10.1038/sdata.2014.22" target="_blank" rel="noopener">Quantum chemistry structures and properties of 134 kilo molecules</a> [J]. Scientific Data, 2014, 1: 140022. DOI: 10.1038/sdata.2014.22
   - 用途：QM9 将几何和一组量子化学标签关联起来；其小型中性有机分子覆盖范围限制了外推结论。

30. Bemis, Guy W.; Murcko, Mark A.. <a href="https://doi.org/10.1021/jm9602928" target="_blank" rel="noopener">The Properties of Known Drugs. 1. Molecular Frameworks</a> [J]. Journal of Medicinal Chemistry, 1996, 39(15): 2887–2893. DOI: 10.1021/jm9602928
   - 用途：定义用于比较药物骨架的框架概念；现代骨架切分利用这一思想评估新骨架泛化，但并不能保证完全消除相似性泄漏。

31. Rupp, Matthias; Tkatchenko, Alexandre; Müller, Klaus-Robert; von Lilienfeld, O. Anatole. <a href="https://doi.org/10.1103/PhysRevLett.108.058301" target="_blank" rel="noopener">Fast and Accurate Modeling of Molecular Atomization Energies with Machine Learning</a> [J]. Physical Review Letters, 2012, 108(5): 058301. DOI: 10.1103/PhysRevLett.108.058301
   - 用途：将核电荷和原子间距离编码为库仑矩阵，说明量子性质建模需要保留元素身份与几何，并处理原子排序。

32. Bartók, Albert P.; Kondor, Risi; Csányi, Gábor. <a href="https://doi.org/10.1103/PhysRevB.87.184115" target="_blank" rel="noopener">On representing chemical environments</a> [J]. Physical Review B, 2013, 87(18): 184115. DOI: 10.1103/PhysRevB.87.184115
   - 用途：提出 SOAP 并讨论原子环境描述符的忠实性、平滑性和对称性；不变性设计必须结合目标物理量。

33. Behler, Jörg; Parrinello, Michele. <a href="https://doi.org/10.1103/PhysRevLett.98.146401" target="_blank" rel="noopener">Generalized Neural-Network Representation of High-Dimensional Potential-Energy Surfaces</a> [J]. Physical Review Letters, 2007, 98(14): 146401. DOI: 10.1103/PhysRevLett.98.146401
   - 用途：把体系能量分解为局部原子贡献，并用对称函数表达环境，为可微、可扩展的原子势表示奠定基础。

34. Wang, Yuyang; Wang, Jianren; Cao, Zhonglin; Farimani, Amir Barati. <a href="https://doi.org/10.1038/s42256-022-00447-x" target="_blank" rel="noopener">Molecular contrastive learning of representations via graph neural networks</a> [J]. Nature Machine Intelligence, 2022, 4: 279–287. DOI: 10.1038/s42256-022-00447-x
   - 用途：利用图增强与对比学习获取预训练表示；增强方式必须检查是否删除了与目标性质有关的官能团或立体信息。

35. Liu, Shengchao; Wang, Hanchen; Liu, Weiyang; Lasenby, Joan; Guo, Hongyu; Tang, Jian. <a href="https://openreview.net/forum?id=xQUe1pOKPam" target="_blank" rel="noopener">Pre-training Molecular Graph Representation with 3D Geometry</a> [C]. International Conference on Learning Representations (ICLR 2022). 2022. https://openreview.net/forum?id=xQUe1pOKPam
   - 用途：GraphMVP 在预训练时对齐二维拓扑和三维视图，使只输入二维图的下游编码器也可利用学到的几何先验。

36. Fang, Xiaomin; Liu, Lihang; Lei, Jieqiong; et al.. <a href="https://doi.org/10.1038/s42256-021-00438-4" target="_blank" rel="noopener">Geometry-enhanced molecular representation learning for property prediction</a> [J]. Nature Machine Intelligence, 2022, 4: 127–134. DOI: 10.1038/s42256-021-00438-4
   - 用途：GEM 用原子—键图与键—角图联合学习，通过几何自监督任务保留键长和键角层面的空间知识。

37. Kovács, Dávid Péter; Moore, J. Harry; Browning, Nicholas J.; et al.. <a href="https://doi.org/10.1021/jacs.4c07099" target="_blank" rel="noopener">MACE-OFF: Short-Range Transferable Machine Learning Force Fields for Organic Molecules</a> [J]. Journal of the American Chemical Society, 2025, 147(21): 17598–17611. DOI: 10.1021/jacs.4c07099
   - 用途：把等变多体表示迁移到有机分子与凝聚相，展示构象、分子间作用和采样范围对可转移性的影响。

38. Hamada, Lisa; Kishimoto, Akihiro; Miyaguchi, Kohei; et al.. <a href="https://doi.org/10.1038/s43588-026-01036-3" target="_blank" rel="noopener">Revisiting molecular descriptors with TDiMS for interpretable intramolecular interactions based on substructure pairs</a> [J]. Nature Computational Science, 2026, 6(9): 945–953. Published 17 September 2026. DOI: 10.1038/s43588-026-01036-3
   - 用途：用子结构对之间的拓扑距离构造可解释描述符，说明经典描述符仍可通过保留片段间关系发展。

39. Levine, Daniel S.; Shuaibi, Muhammed; Spotte-Smith, Evan Walter Clark; et al.. <a href="https://doi.org/10.48550/arXiv.2505.08762" target="_blank" rel="noopener">The Open Molecules 2025 (OMol25) Dataset, Evaluations, and Models</a> [EB/OL]. arXiv:2505.08762 [physics.chem-ph]. Preprint; v2 revised 4 March 2026. 2025. DOI: 10.48550/arXiv.2505.08762
   - 用途：把电荷、自旋、构象、显式溶剂与多元素覆盖纳入大型计算数据集；强调只给元素与几何时仍须明确电子态。

40. Kretschmer, Fleming; Seipp, Jan; Ludwig, Marcus; Klau, Gunnar W.; Böcker, Sebastian. <a href="https://doi.org/10.1038/s41467-024-55462-w" target="_blank" rel="noopener">Coverage bias in small molecule machine learning</a> [J]. Nature Communications, 2025, 16: 554. DOI: 10.1038/s41467-024-55462-w
   - 用途：用分子结构距离揭示训练集覆盖偏差；即使骨架切分得分良好，也应检查测试分子与训练分布的真实关系。

41. van Tilborg, Derek; Alenicheva, Alisa; Grisoni, Francesca. <a href="https://doi.org/10.1021/acs.jcim.3c00423" target="_blank" rel="noopener">Correction to “Exposing the Limitations of Molecular Machine Learning with Activity Cliffs”</a> [J]. Journal of Chemical Information and Modeling, 2023, 63(7): 2266. DOI: 10.1021/acs.jcim.3c00423
   - 用途：修正early-stopping方法文字；复现时应连同原文读取。作者称文字修正不改变原结论。

42. RDKit contributors. <a href="https://doi.org/10.5281/zenodo.23116821" target="_blank" rel="noopener">RDKit 2026.09.1</a> [EB/OL]. Zenodo software release; version 2026.09.1, released 3 October 2026. 2026. DOI: 10.5281/zenodo.23116821
   - 用途：本地脚本日志实际记录rdBase.rdkitVersion=2026.09.1；版本引用与概念引用分开，不以访问年冒充软件首次发布年。

43. DeepChem contributors. <a href="https://github.com/deepchem/deepchem/blob/master/datasets/delaney-processed.csv" target="_blank" rel="noopener">Delaney (ESOL) processed dataset and official loader</a> [EB/OL]. Official repository dataset and loader; accessed 23 October 2026. Original experimental source: Delaney (2004). 2026. https://github.com/deepchem/deepchem/blob/master/datasets/delaney-processed.csv
   - 用途：本作业1128条公开处理表的数据入口。目标为measured log solubility；原始快照、blob标识与SHA256另附日志。

<a id="ch07"></a>
## 第7章 神经网络、Transformer、GNN与基础模型

1. Vaswani, A. *et al.* [Attention Is All You Need](https://proceedings.neurips.cc/paper_files/paper/2017/hash/3f5ee243547dee91fbd053c1c4a845aa-Abstract.html). *Advances in Neural Information Processing Systems* **30** (2017).
   - 用途：自注意力与 Transformer 的原始论文；用于建立后续分子语言模型、谱图 Transformer 和多模态基础模型的共同技术语言。

<a id="ch08"></a>
## 第8章 生成式模型与扩散模型：从信号恢复到化学反演

1. Abramson, J. *et al.* [Accurate structure prediction of biomolecular interactions with AlphaFold 3](https://doi.org/10.1038/s41586-024-07487-w). *Nature* **630**, 493–500 (2024).
   - 用途：展示扩散式生成如何用于蛋白质、核酸、小分子和离子组成的复合体系建模；作为“生成不是凭空作图，而是受化学约束的反演”案例。

<a id="ch09"></a>
## 第9章 光谱分析与智能谱学

1. McNaughton, A. D. *et al.* [Machine Learning Models for Predicting Molecular UV–Vis Spectra with Quantum Mechanical Properties](https://doi.org/10.1021/acs.jcim.2c01662). *Journal of Chemical Information and Modeling* **63**, 1462–1471 (2023).
   - 用途：以 UV–Vis 谱预测为例，连接量子化学、分子表示和机器学习，讨论模型对异构体谱学差异的预测边界。

<a id="ch10"></a>
## 第10章 质谱、色谱、核磁与结构解析

1. Wei, J. N.; Duvenaud, D.; Aspuru-Guzik, A. [Rapid Prediction of Electron–Ionization Mass Spectrometry Using Neural Networks](https://doi.org/10.1021/acscentsci.9b00085). *ACS Central Science* **5**, 700–708 (2019).
   - 用途：说明基于分子结构快速预测 EI 质谱的思路，并引出碎片化规律、谱库检索与结构约束的关系。

<a id="ch11"></a>
## 第11章 化学成像、空间分辨率与多维数据

1. Weigert, M. *et al.* [Content-aware image restoration: pushing the limits of fluorescence microscopy](https://doi.org/10.1038/s41592-018-0216-7). *Nature Methods* **15**, 1090–1097 (2018).
   - 用途：讨论低信噪比图像恢复、空间分辨率提升与深度学习；配合本章强调恢复结果仍须受成像物理和验证样本约束。

<a id="ch12"></a>
## 第12章 生物分析、单细胞与多组学测量

1. Jumper, J. *et al.* [Highly accurate protein structure prediction with AlphaFold](https://doi.org/10.1038/s41586-021-03819-2). *Nature* **596**, 583–589 (2021).
   - 用途：说明生物序列、结构信息和深度学习如何结合，并为后续的蛋白质组学、结构生物学和多组学数据解释提供背景。

<a id="ch13"></a>
## 第13章 多模态基础模型与知识增强分析

1. Radford, A. *et al.* [Learning Transferable Visual Models From Natural Language Supervision](https://proceedings.mlr.press/v139/radford21a.html). *Proceedings of the 38th International Conference on Machine Learning*, 8748–8763 (2021).
   - 用途：以图像—文本对比学习为共同表示的范例，帮助理解谱图—结构—图像—文本之间建立对齐空间的基本思想。

<a id="ch14"></a>
## 第14章 仪器标准化、校准迁移与FAIR数据

1. Wilkinson, M. D. *et al.* [The FAIR Guiding Principles for scientific data management and stewardship](https://doi.org/10.1038/sdata.2016.18). *Scientific Data* **3**, 160018 (2016).
   - 用途：将标准样品、仪器元数据、校准迁移和跨实验室复用放入 FAIR 数据治理框架；与第2章的数据对象观相互呼应。

<a id="ch15"></a>
## 第15章 可信智能分析：不确定度、适用域与因果机制

1. Ovadia, Y. *et al.* [Can you trust your model’s uncertainty? Evaluating predictive uncertainty under dataset shift](https://proceedings.neurips.cc/paper/2019/hash/8558cb408c1d76621371888657d2eb1d-Abstract.html). *Advances in Neural Information Processing Systems* **32** (2019).
   - 用途：讨论部署数据偏离训练分布时，不确定度为何会失效；可直接对应仪器漂移、批次变化与未知基质。
2. Guo, C.; Pleiss, G.; Sun, Y.; Weinberger, K. Q. [On Calibration of Modern Neural Networks](https://proceedings.mlr.press/v70/guo17a.html). *Proceedings of the 34th International Conference on Machine Learning*, 1321–1330 (2017).
   - 用途：用于解释“置信度”与“正确率”不是一回事，并介绍温度缩放等置信度校准思想。

<a id="ch16"></a>
## 第16章 科学大模型与分析化学智能体

1. Bran, A. M. *et al.* [Augmenting large language models with chemistry tools](https://doi.org/10.1038/s42256-024-00832-8). *Nature Machine Intelligence* **6**, 525–535 (2024).
   - 用途：说明化学智能体通过检索、化学软件和执行工具扩展能力的架构，也提示工具调用并不等于结果自动可信。
2. Boiko, D. A.; MacKnight, R.; Kline, B.; Gomes, G. [Autonomous chemical research with large language models](https://doi.org/10.1038/s41586-023-06792-0). *Nature* **624**, 570–578 (2023).
   - 用途：作为大模型规划、查阅仪器文档、编写控制代码和实验优化的综合案例。

<a id="ch17"></a>
## 第17章 实验决策、强化学习与具身自主实验室

1. Shields, B. J. *et al.* [Bayesian reaction optimization as a tool for chemical synthesis](https://doi.org/10.1038/s41586-021-03213-y). *Nature* **590**, 89–96 (2021).
   - 用途：用于区分“选择下一个最有价值实验”的贝叶斯优化与固定网格筛选，并为主动学习和强化学习的实验决策作铺垫。
2. Burger, B. *et al.* [A mobile robotic chemist](https://doi.org/10.1038/s41586-020-2442-2). *Nature* **583**, 237–241 (2020).
   - 用途：说明移动机器人、表征设备与实验规划的实体耦合，是理解具身自主实验室的现实起点。

<a id="ch18"></a>
## 第18章 世界模型、化学数字孪生与机器科学家

1. Hafner, D.; Pasukonis, J.; Ba, J.; Lillicrap, T. [Mastering diverse control tasks through world models](https://doi.org/10.1038/s41586-025-08744-2). *Nature* (2025).
   - 用途：给出世界模型“预测未来状态和奖励、在模型内规划行动”的清晰技术范式；教材据此将样品、仪器、环境和操作共同抽象为化学测量系统。
2. Burger, B. *et al.* [A mobile robotic chemist](https://doi.org/10.1038/s41586-020-2442-2). *Nature* **583**, 237–241 (2020).
   - 用途：为从数字孪生走向可执行的机器科学家提供实验室实体系统的参照。

---

## 新增引文的公开写法

请把新条目直接写在对应章节下，而不是收进注释、折叠框或“待补充”清单。推荐格式如下：

```markdown
2. 作者. [题名](https://doi.org/...). *期刊* **卷**, 页码 (年份).
   - 用途：明确说明它更新或支撑教材中的哪一项结论、方法或案例；更新 PR：#编号。
```

每年各章至少补入一篇近三年的原始研究、权威综述、标准或官方技术资料；若没有足以改变教材判断的新材料，应明确写“本年检索后未发现需要改写基础结论的证据”，并保留检索范围和日期。

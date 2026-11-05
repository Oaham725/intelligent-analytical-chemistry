# 2026–2027 学年传承题库

这里的题目由本届学生为下一届学生设计。题目不追求偏、怪或重复计算，而应检验一个能够迁移到真实分析问题的判断。每道题应在本页相应章节下添加：题目标题、题型、考查目标、题干、答案要点、所需数据/代码链接和贡献 PR。

## 题目质量要求

- **有对象**：给出足以作答的样品、测量条件、矩阵/谱图/图像或数据背景。
- **有判断**：不能只要求复述定义；应要求比较方法、识别假设、解释失败或完成推导。
- **有答案边界**：写出关键得分点与常见误区，而不是只放最终数值。
- **可传承**：不依赖已失效的临时网页、私人数据或本届课堂口头信息。

## 按章节归档

### ch01

待本届维护组补充。

### ch02

待本届维护组补充。

### ch03

待本届维护组补充。

### ch04

待本届维护组补充。

### ch05

待本届维护组补充。

### ch06

<a href="https://github.com/yoimiya-610/intelligent-analytical-chemistry/blob/ch06/information-preservation-issue-4/resources/annual/2026-2027/questions/ch06.md" data-ch06-site-href="#/resources/annual/2026-2027/questions/ch06">单章题库与数据入口</a>；关联[Issue #4](https://github.com/Oaham725/intelligent-analytical-chemistry/issues/4)。

#### 数据与代码入口

- Q06-01：<a href="https://github.com/yoimiya-610/intelligent-analytical-chemistry/blob/ch06/information-preservation-issue-4/data/ch06/molecules.csv" data-ch06-site-href="./data/ch06/molecules.csv" download>六分子表</a>；<a href="https://github.com/yoimiya-610/intelligent-analytical-chemistry/blob/ch06/information-preservation-issue-4/resources/annual/2026-2027/results/ch06/descriptors.csv" data-ch06-site-href="./resources/annual/2026-2027/results/ch06/descriptors.csv" download>描述符结果</a>；<a href="https://github.com/yoimiya-610/intelligent-analytical-chemistry/blob/ch06/information-preservation-issue-4/resources/annual/2026-2027/results/ch06/fingerprint_comparisons.csv" data-ch06-site-href="./resources/annual/2026-2027/results/ch06/fingerprint_comparisons.csv" download>指纹比较</a>；<a href="https://github.com/yoimiya-610/intelligent-analytical-chemistry/blob/ch06/information-preservation-issue-4/code/ch06_exercises/case_study.py" data-ch06-site-href="./code/ch06_exercises/case_study.py" download>RDKit脚本</a>。
- Q06-02、Q06-05：题干已给出坐标、参数和假设；<a href="https://github.com/yoimiya-610/intelligent-analytical-chemistry/blob/ch06/information-preservation-issue-4/docs/ch06.md#ch06-geometry" data-ch06-site-href="#/docs/ch06?id=ch06-geometry">本章几何与状态说明</a>。
- Q06-03：<a href="https://github.com/yoimiya-610/intelligent-analytical-chemistry/blob/ch06/information-preservation-issue-4/data/ch06/delaney-processed.csv" data-ch06-site-href="./data/ch06/delaney-processed.csv" download>数据快照</a>；<a href="https://github.com/yoimiya-610/intelligent-analytical-chemistry/blob/ch06/information-preservation-issue-4/resources/annual/2026-2027/results/ch06/esol/summary.csv" data-ch06-site-href="./resources/annual/2026-2027/results/ch06/esol/summary.csv" download>汇总</a>；<a href="https://github.com/yoimiya-610/intelligent-analytical-chemistry/blob/ch06/information-preservation-issue-4/resources/annual/2026-2027/results/ch06/esol/metrics.csv" data-ch06-site-href="./resources/annual/2026-2027/results/ch06/esol/metrics.csv" download>逐次指标</a>；<a href="https://github.com/yoimiya-610/intelligent-analytical-chemistry/blob/ch06/information-preservation-issue-4/resources/annual/2026-2027/results/ch06/esol/duplicate_audit.csv" data-ch06-site-href="./resources/annual/2026-2027/results/ch06/esol/duplicate_audit.csv" download>重复审计</a>；<a href="https://github.com/yoimiya-610/intelligent-analytical-chemistry/blob/ch06/information-preservation-issue-4/resources/annual/2026-2027/results/ch06/esol/failure_samples.csv" data-ch06-site-href="./resources/annual/2026-2027/results/ch06/esol/failure_samples.csv" download>失败样本</a>；<a href="https://github.com/yoimiya-610/intelligent-analytical-chemistry/blob/ch06/information-preservation-issue-4/code/ch06_exercises/esol_baseline.py" data-ch06-site-href="./code/ch06_exercises/esol_baseline.py" download>基线脚本</a>。
- Q06-04：[SIMG正式论文](https://doi.org/10.1038/s42256-025-01031-9)；[作者全文](https://arxiv.org/pdf/2408.04520)。

<section class="insight" id="Q06-01" style="margin:22px 0"><span class="badge">Q06-01 · 计算与表示辨识（10分）</span>

#### 相同分子式，为什么一个向量仍然不够？

<strong>考查目标：</strong>区分组成、局部化学和立体信息；说明可区分性与预测充分性的不同。

<strong>数据/条件：</strong>molecules.csv；results/descriptors.csv；results/fingerprint_comparisons.csv

<strong>题干：</strong>比较乙醇/二甲醚及乳酸镜像对。①仅用分子量能否区分？②加入HBD、HBA、TPSA后哪一对可以区分？③给出乳酸对在关闭与启用手性Morgan下的Tanimoto。④能否据此宣称可准确预测手性受体活性？

<h4>答案要点与评分边界</h4><ol><li>乙醇/二甲醚均为46.069 g·mol⁻¹；乳酸镜像对也各自具有相同质量。仅质量均不能区分（2分）。</li><li>乙醇/二甲醚HBD分别1/0，TPSA分别20.23/9.23 Å²；HBA均1，因此该向量能区分连接异构对。乳酸对这些标量仍相同（3分）。</li><li>固定radius=2、fpSize=2048：乳酸对includeChirality=False为1.0000；True约0.6923（2分）。</li><li>不能。可区分仅说明没有以此方式合并这对输入；活性还需受体/状态、真实标签和独立验证（3分）。</li></ol>

<strong>常见误区：</strong>把@/@@脱离邻居顺序直接当作R/S；把相似度当成活性预测概率。

<a href="https://doi.org/10.1021/ci100050t" target="_blank" rel="noopener">来源与方法依据 ↗</a>

</section><section class="insight" id="Q06-02" style="margin:22px 0"><span class="badge">Q06-02 · 推导与迁移判断（10分）</span>

#### 镜像距离不变，为什么手性会被丢失？

<strong>考查目标：</strong>区分正旋转不变性、反射不变性和任务相关的手性。

<strong>数据/条件：</strong>理想四面体坐标：(1,1,1)、(−1,−1,1)、(−1,1,−1)、(1,−1,−1)，邻居顺序固定。

<strong>题干：</strong>①计算任意两个配体间的距离。②计算固定顺序χ，并将x坐标反号后重新计算。③交换两个邻居顺序会怎样？④分别讨论手性受体识别与非手性环境下镜像构象标量能量的表示要求。

<h4>答案要点与评分边界</h4><ol><li>任意两个配体的距离为√8≈2.828，无量纲。刚体旋转和镜像都保持该距离（2分）。</li><li>χ=(r₁−r₄)·[(r₂−r₄)×(r₃−r₄)]=−16；x反号后为+16（3分）。</li><li>交换两个邻居也会翻转符号，因此χ必须结合固定、化学一致的排序；不是无需排序的R/S标签（2分）。</li><li>手性识别可能需要镜像差异与手性环境；相同电子态、固定镜像构象、非手性环境下的通常标量能量应相同（3分）。</li></ol>

<strong>常见误区：</strong>声称所有对映体性质都不同，或声称只要三维距离就总能区分手性。

<a href="https://doi.org/10.1038/s42256-021-00418-8" target="_blank" rel="noopener">来源与方法依据 ↗</a>

</section><section class="insight" id="Q06-03" style="margin:22px 0"><span class="badge">Q06-03 · 真实数据审计与实验（10分）</span>

#### 随机划分的优势，能否变成新骨架结论？

<strong>考查目标：</strong>理解身份去重、骨架组留出、训练内处理和局部失败分析。

<strong>数据/条件：</strong>data/delaney-processed.csv；results/esol/metrics.csv、summary.csv、duplicate_audit.csv、failure_samples.csv。

<strong>题干：</strong>使用已附ESOL输出。①说明1128条为何保留1117条。②比较两种划分下Ridge与Morgan 5-NN的平均MAE。③指出一个不能作出的因果结论。④给出一个下一步验证方案与一个拒绝过度解释的条件。

<h4>答案要点与评分边界</h4><ol><li>本次解析成功；规范isomeric SMILES身份去重移除11条重复，保留首条、另存冲突，不在两侧保留同一分子。不是假定后来的测量必错（2分）。</li><li>3个预设种子下，Ridge随机/骨架MAE约0.786/0.830；Morgan 5-NN约1.051/1.852，单位log10(mol/L)。须同时读种子波动与实际测试规模（3分）。</li><li>不能说“所有指纹都差于描述符”或把差异全部归因于表示：算法、归纳偏置、固定超参数和划分均参与（2分）。</li><li>例如保持划分和调参预算比较多种模型，核查低相似邻域与极性/电荷子集；缺少pH/盐型/晶型条件时不能把每个残差归于结构机理（3分）。</li></ol>

<strong>常见误区：</strong>把ESOL预测列作实验真值或输入特征；用测试集挑超参数；把标准差当作单样本置信区间。

<a href="https://doi.org/10.1039/C7SC02664A" target="_blank" rel="noopener">来源与方法依据 ↗</a>

</section><section class="insight" id="Q06-04" style="margin:22px 0"><span class="badge">Q06-04 · 前沿证据判断（10分）</span>

#### 看到SIMG提升后，能否直接迁移到带电自由基？

<strong>考查目标：</strong>能从原始来源提取适用对象、估计量和具体失效边界。

<strong>数据/条件：</strong>SIMG原始论文与作者全文；本专题前沿更新卡。

<strong>题干：</strong>某团队拟将SIMG*直接用于新元素的带电开壳层分子，并宣称它必然优于三维等变模型。请给出三条需要修正的判断，并设计最小对照。

<h4>答案要点与评分边界</h4><ol><li>该工作的主要范围为训练所含元素的中性闭壳层分子，新元素需补充数据与验证；带电/开壳层不属于已解决范围（3分）。</li><li>SIMG*是轨道信息的学习近似，不是独立量化真值；须检查特征预测误差和几何质量（2分）。</li><li>原文未证明全面优于三维等变模型，所测二维模型仍存在差距（2分）。</li><li>固定数据边界，比较普通图、真实电子特征、估计电子特征及适当几何基线；记录新增成本与域外失败（3分）。</li></ol>

<strong>常见误区：</strong>把单一任务提升写成普遍最优，把预测先验当作实验或量化真值。

<a href="https://doi.org/10.1038/s42256-025-01031-9" target="_blank" rel="noopener">来源与方法依据 ↗</a>

</section><section class="insight" id="Q06-05" style="margin:22px 0"><span class="badge">Q06-05 · 计算与边界条件（10分）</span>

#### 状态平均：pH与自由能差改变了什么？

<strong>考查目标：</strong>正确计算物种比例，区分规则计算、理想模型与真实测量。

<strong>数据/条件：</strong>单酸理想模型pKa=4.8；pH=4.8或5.8。二态等简并度T=298 K，ΔG=5 kJ·mol⁻¹。

<strong>题干：</strong>①计算两种pH下A⁻占比。②计算高自由能构象B占比。③列出各模型至少一个假设。④这些比例是否直接等于logD或溶解度？

<h4>答案要点与评分边界</h4><ol><li>α(A⁻)=1/(1+10^(pKa−pH))，分别为50%与约90.91%（3分）。</li><li>p(B)=1/(1+exp(ΔG/RT))，R=0.0083144626 kJ·mol⁻¹·K⁻¹，约11.73%（3分）。</li><li>单酸模型忽略活度与多质子耦合；二态模型等简并度、采样状态明确且使用相关自由能；温度依赖ΔG未建模（2分）。</li><li>不是。logD、溶解度还需要各物种分配/溶剂化、固态与相应实验条件（2分）。</li></ol>

<strong>常见误区：</strong>将kJ与J混用；把气相电子能直接当溶液自由能；把物种比例当作性质本身。

<a href="https://link.springer.com/book/10.1007/978-1-4020-6291-9" target="_blank" rel="noopener">来源与方法依据 ↗</a>

</section>

### ch07

待本届维护组补充。

### ch08

待本届维护组补充。

### ch09

待本届维护组补充。

### ch10

待本届维护组补充。

### ch11

待本届维护组补充。

### ch12

待本届维护组补充。

### ch13

待本届维护组补充。

### ch14

待本届维护组补充。

### ch15

待本届维护组补充。

### ch16

待本届维护组补充。

### ch17

待本届维护组补充。

### ch18

待本届维护组补充。

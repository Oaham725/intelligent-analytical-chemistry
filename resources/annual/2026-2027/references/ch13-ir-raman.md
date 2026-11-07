# G13 年度前沿更新卡　按真实缺失模式评价融合系统

## 研究与来源

Wu R, Wang H, Chen HT, Carneiro G. Deep Multimodal Learning with Missing Modality: A Survey. *Transactions on Machine Learning Research*, 2026。来源类型为同行评议综述。 [期刊记录](https://openreview.net/forum?id=tc7RFcx4hT) · [可读作者稿](https://arxiv.org/abs/2409.07825)

早期原始研究中，Neverova 等在手势识别里尝试对整个输入通道进行随机遮挡。Ma 等在图文基准上比较了不同融合位置对缺失的鲁棒性，观察到策略选择随数据集变化。两项均为其他领域的实证。 [ModDrop](https://arxiv.org/abs/1501.00102) · [CVPR 原始论文](https://openaccess.thecvf.com/content/CVPR2022/papers/Ma_Are_Multimodal_Transformers_Robust_to_Missing_Modality_CVPR_2022_paper.pdf)

## 改变哪一个方法选择

教材的决策级融合使回退易于实现。近年的缺失模态框架进一步把**训练可见的组合**和**部署可用的组合**分开。对 G13，具体改动是把一项完整样本误差拆成四类路径评估：IR 与 Raman 兼有、仅 IR、仅 Raman、无可靠测量。可在有代表性的训练数据上比较缺失掩码、模态 dropout 与单模态回退，并报告各路径的样本数、误差和覆盖率。

## 对象与边界

可用于多仪器测量中因成本、仪器停机或质控失败而缺失整种测量的情况。随机遮挡可检验模型对指定输入缺失的敏感性。若荧光失效与配方相关，完整病例和随机遮挡病例可能均无法代表真实缺失子群。需要记录质控原因、保留现实缺失对象，并按批次与配方验证。本卡所引方法研究未测量本章案例的光谱。

## 连接本章的化学实证

Lösel 等在榛子储藏研究中发现，近红外与空间偏移拉曼的整谱拼接增益随冻干处理和储藏条件变化。该研究对照了不同制样条件下的完整模态表现。下一届可据此设计另一项检验：在现场制样受限且拉曼质控失败时，按真实可用模式报告回退的误判率与覆盖率。该问题属于本卡提出的后续验证。 [榛子储藏原始研究](https://doi.org/10.1007/s12161-024-02578-w)

# 案例来源及复现边界

Abdolghader P, Ridsdale A, Grammatikopoulos T, Resch G, Légaré F, Stolow A, Pegoraro A F, Tamblyn I. Unsupervised hyperspectral stimulated Raman microscopy image enhancement: denoising and segmentation via one-shot deep learning. Optics Express, 2021, 29(21): 34205–34219. DOI: https://doi.org/10.1364/OE.439662

- 原代码：https://github.com/CLEANit/SRS2021 ，GPL-3.0，许可见作者仓库 LICENSE。
- 作者数据入口：https://clean.energyscience.ca/datasets/
- 公开数据文件夹：https://drive.google.com/drive/folders/1Wnd8kgCrDWru8J4eJ5LBkvHkYA_veaMz
- FOV1文件ID：1i1N-SlQdlzZjKS6Et971_xX5NVK3VSa-
- FOV2文件ID：1tS6sPnNA0yym3Os2awbVsXbVBF10dXeW
- 访问日期：2026-11-08。

方法变化：无需独立干净训练目标，利用一个视野中的多条带噪光谱训练自编码器，再用潜在空间聚类展示化学差异区域。

适用对象：高光谱SRS显微图像，论文包含十六烷/水与矿物样品。

证据：论文比较带噪、干净高SNR与模型输出，并将矿物分区代表光谱和参考谱对照。不能把论文证据直接当成本组已复现结果。

局限：非严格定量；混合像素受硬聚类限制；需处理饱和响应；跨样品与仪器适用范围需更多验证。本组采用简化网络及抽样数据，未重新确认具体矿物。

该研究发表于2021年。由成员A判断是否满足年度“近年”前沿更新标准，必要时另加近期论文；此条作为案例来源与技术卡素材。

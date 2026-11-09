# 第15章数据字典与来源

来源Celestian 2025 RamanLab数据库v1，DOI 10.5281/zenodo.15717961，整理库API声明CC BY 4.0；同时署名RRUFF Project。完整285 MB库不再发布，校验和及署名见LICENSE_AND_SOURCES.md。

| 文件或字段 | 含义 |
|---|---|
| selected_spectra.npz / X | 280×501，线性插值后的来源强度，尚未SNV |
| wavenumber | 200–1200，间隔2，单位cm⁻¹ |
| ids | R加六位数字的RRUFF编号 |
| y / class_label | 理想化学式字符串规则标签，不沿用来源分类字段 |
| mineral_name / ideal_formula | 来源材料名及解码后的理想式，不进入模型输入 |
| source_catalog_class | 来源HEY CLASSIFICATION字段，保留供审计 |
| source_record / source_url | 唯一整理记录及原来源链接 |
| laser_nm | 激发波长532 nm |
| status | 来源鉴定状态原文，未由本组重新鉴定 |
| spectrum_sha256 | 插值谱的little-endian float64字节散列 |
| pilot_excluded_ids.csv | 全部340个先导编号，确认实验排除 |
| label_audit_examples.csv | 整理分类与理想式冲突的示例，非全面审计 |
| data_audit.json | 筛选规则、去重数量和样本统计 |
| source_metadata.json | 固定Zenodo记录及许可元数据 |

CO3、SO4、PO4、AsO4按大小写敏感字符串匹配，仅命中一个且属于前三者时标作对应已知类。未知含Si和O且无上述基团，可含SiO2，不统称硅酸盐。标签仍依赖来源理想式；不保证所有来源式或纯度都正确。编号无重叠不证明按矿物种、产地或仪器批次完全隔离。

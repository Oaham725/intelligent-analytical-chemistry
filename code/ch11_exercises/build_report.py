"""Build Chinese handoff report and case question from actual experiment outputs."""
import csv,json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

root=Path(__file__).resolve().parents[2]
docs=root/'docs';docs.mkdir(exist_ok=True)
for kind in ['real','synthetic']:
    auditfile=root/f'results/{kind}/leakage_audit.json'
    records=json.loads(auditfile.read_text())
    for record in records:record['same_sample_external_independence']='Different fields do not establish independent sample/batch/instrument generalization'
    auditfile.write_text(json.dumps(records,indent=2),encoding='utf8')
with (root/'results/synthetic/metrics.csv').open(encoding='utf-8-sig') as f: rows=list(csv.DictReader(f))
with (root/'results/real/metrics.csv').open(encoding='utf-8-sig') as f: real=list(csv.DictReader(f))
audit=json.loads((root/'results/synthetic/leakage_audit.json').read_text())
ra=json.loads((root/'results/real/leakage_audit.json').read_text())
manifest=json.loads((root/'results/real/run_manifest.json').read_text())
prep=json.loads((root/'data/mineral_small.json').read_text())

# Consistent legends and a continuous grayscale for real raw mean intensity.
colors=['#2764ac','#dd8540','#37a386'];cmap=ListedColormap(colors)
for kind in ['real','synthetic']:
    for npz in (root/f'results/{kind}').glob('*/*/predictions.npz'):
        pr=np.load(npz);fig,axs=plt.subplots(1,4,figsize=(13,3.6))
        if kind=='real':
            original=np.load(root/'data/mineral_small.npz')['test_cube']
            axs[0].imshow(original.mean(-1),cmap='gray');axs[0].set_title('Raw mean intensity\n(not reference)',fontsize=10)
        else:
            truth=np.load(root/'results/synthetic/synthetic_clean.npz')['test_labels']
            axs[0].imshow(truth,cmap=cmap,vmin=0,vmax=2);axs[0].set_title('Synthetic true classes',fontsize=10)
        for ax,method in zip(axs[1:],['Raw','MovingAverage5','ConvAE']):
            ax.imshow(pr[f'{method}_labels'],cmap=cmap,vmin=0,vmax=2);ax.set_title(method+' + k-means',fontsize=10)
        for ax in axs:ax.set_xticks([]);ax.set_yticks([])
        fig.suptitle(('REAL AUTHOR MINERAL DATA | No pixel ground truth' if kind=='real' else 'SYNTHETIC TEACHING DATA | Not measured mineral spectra')+'\nExternal field | '+str(npz.parent.relative_to(root/f'results/{kind}')),fontsize=11)
        fig.legend(handles=[Patch(color=c,label=f'Cluster / class {i}') for i,c in enumerate(colors)],loc='lower center',ncol=3,fontsize=9)
        fig.tight_layout(rect=[0,.08,1,1]);fig.savefig(npz.parent/'component_maps.png',dpi=180,bbox_inches='tight');fig.savefig(npz.parent/'component_maps.svg',bbox_inches='tight');plt.close(fig)

def table(rr):
    head='| 噪声σ | 方法 | RMSE↓ | PSNR/dB↑ | SAM/度↓ | 宏F1↑ |\n|---|---|---|---|---|---|\n'
    return head+'\n'.join(f"| {r['noise_sigma']} | {r['method']} | {float(r['RMSE']):.4f} | {float(r['PSNR_dB']):.2f} | {float(r['SAM_deg']):.2f} | {float(r['macro_F1']):.4f} |" for r in rr)

selected=[r for r in rows if r['split']=='spatial' and r['scope']=='external_field']
text='''# 成员 B 实验结果与交接报告

## 完成范围

已实际下载作者 FOV1/FOV2 原始矿物 TIFF，完成简化卷积自编码器、传统移动平均、潜在特征/光谱 k-means、真实组分类别图、模拟真值评价、划分审计及交互图查看器。

**这是 UHRED 思路的教学简化与扩展，不是论文精确复现。真实图中 Cluster 不代表已确认矿物，更不代表浓度。模拟数据不属于作者实验数据。**

## 真实数据与方法

'''
text+='\n'.join(f"- {f['path']}：原始形状 `{f['raw_shape']}`，抽样后 `{f['prepared_shape']}`；SHA256 `{f['sha256']}`。" for f in prep['files'])
text+='''

空间步长4、光谱步长3；通道索引保持来源。使用训练像素的全局均值和极差归一化，三种方法统一使用相同划分。自编码器2层1D卷积、6维潜在空间，MSE带噪自重建，Adam学习率0.002，weight decay 1e-5，80轮，batch上限128，按验证带噪MSE保存模型。没有用干净真值早停。

原始数据/5通道移动平均接光谱k-means；ConvAE接潜在特征k-means，K=3。K是教学指定值，不是自动推断出矿物种类。图中颜色用训练像素重叠对齐，外部测试标签不用于显示对齐。

真实数据没有逐像素类别和干净参考，所以不能报告识别准确率、真实去噪RMSE或PSNR。`error_maps` 在真实数据下仅表示相对原始输入的变化；变化少不等于效果好。极端信号未做论文的人工饱和像素替换，可能主导某些聚类。

![真实数据类别图](../results/real/real/spatial/component_maps.png)

![各簇原始平均光谱](../results/real/real/spatial/cluster_mean_raw_spectra.png)

## 有真值模拟实验：外部视野，空间划分训练

模拟数据由解析峰和几何空间区域生成，每个视野48×48×96；三类纯组分，存在光强变化与轻微视野级谱峰变化，不代表真实矿物，也未模拟混合丰度。噪声是人工独立高斯噪声，不等同于完整SRS噪声机制。

'''+table(selected)
text+='\n\n逐噪声判断（基于本次固定种子，非统计显著性结论）：\n\n'
for sig in ['0.08','0.2','0.4']:
    rr=[r for r in selected if r['noise_sigma']==sig]
    rm=min(rr,key=lambda r:float(r['RMSE']));f1=max(rr,key=lambda r:float(r['macro_F1']))
    winners='、'.join(r['method'] for r in rr if np.isclose(float(r['macro_F1']),float(f1['macro_F1']),atol=1e-8))
    text+=f"- σ={sig}：RMSE最低为 {rm['method']}（{float(rm['RMSE']):.4f}）；宏F1最高为 {winners}（{float(f1['macro_F1']):.4f}，多个方法时为并列）。不能预设深度学习在所有指标上获胜。\n"
text+='''

![模拟质量评价](../results/synthetic/quality_summary.png)

## 划分与相邻像素审计

| 数据 | 划分 | 训练/验证/测试数量 | 测试像素直接邻接训练比例 |
|---|---|---|---|
'''
for name,rr in [('真实',ra),('模拟σ=0.20',[r for r in audit if r['noise']==.2])]:
    for r in rr:text+=f"| {name} | {r['scheme']} | {r['train_n']}/{r['val_n']}/{r['test_n']} | {r['test_adjacent_to_train_fraction']:.3%} |\n"
text+='''

训练与测试索引无交集；空间划分在训练/验证及验证/测试之间留两列缓冲。邻接比例只检查上下左右直接相邻，不代表消除了所有空间相关。FOV2完全不参与拟合，但仍不能证明跨样品/批次/仪器泛化。

随机和空间划分的训练量及组成不同，指标差异不能全部归因为泄露。若本次随机划分没有更高分，也不能据此认定它没有风险。这里展示风险与审计，而非预先保证某种分数趋势。

## 错误分析与化学信息边界

- 对照 `error_maps` 与 `spectra` 判断误差是否集中在某类光谱和较高信号区域。模拟图为真实误差，真实矿物图仅为改变量。
- 移动平均可能削弱窄峰；瓶颈网络可能改变峰高、抑制弱峰。请结合SAM与峰高误差，不只看图像平滑度。
- 分类图每个像素只有一个类别，没有丰度估计；混合组分不能通过单标签图正确表达。
- 当前合成样品较简单，结果不能作为真实矿物准确性的替代证据。
- 当前固定种子725单次运行，未进行多次统计或调参选择最优测试结果。

## 复现、交接与未完成的外部环节

完整命令见 README_B.md；依赖版本和耗时见各 run_manifest.json。PNG用于汇报，SVG用于编辑，NPZ/CSV用于复核；查看器可本地切换结果。

本机已执行训练与输出验证；尚未由其他同学在独立环境完成交叉验证。当前不是课程Git仓库，不声称已推送或建立PR。年度目录按Issue暂定2026-2027，合并前由C核对仓库命名。汇报最终PDF由C整合，本文提供B部分讲稿。2021论文是否满足“近年”需由A确认并补充。

## 来源

Abdolghader et al. Optics Express 29(21),34205–34219 (2021). DOI: https://doi.org/10.1364/OE.439662 。
作者代码：https://github.com/CLEANit/SRS2021 。作者数据：https://clean.energyscience.ca/datasets/ 。课程任务：https://github.com/Oaham725/intelligent-analytical-chemistry/issues/9 。
'''
text+='\n### 高噪声逐类别错误（模拟外部视野）\n\n'
for method in ['Raw','MovingAverage5','ConvAE']:
    cm=np.loadtxt(root/f'results/synthetic/0.4/spatial/{method}_external_field_confusion.csv',delimiter=',')
    rates=1-np.diag(cm)/np.maximum(cm.sum(1),1)
    text+=f"- {method}：类别0/1/2错误率分别为 "+'、'.join(f'{r:.2%}' for r in rates)+'。\n'
sl=np.load(root/'results/synthetic/0.2/spatial/split.npz')
truth=np.load(root/'results/synthetic/synthetic_clean.npz')['train_labels']
text+='\n空间训练区类别0/1/2像素数：'+str(np.bincount(truth.ravel()[sl['train']],minlength=3).tolist())+'。三类均进入训练，但仍存在类别比例差异。两个模拟视野共享几何布局，光谱与噪声实现不同；不代表跨结构样品的泛化。每个噪声水平分别重新训练模型，因此曲线也不是同一固定模型的抗噪测试。\n'
(docs/'B_results.md').write_text(text,encoding='utf8')

qdir=root/'resources/annual/2026-2027/questions';qdir.mkdir(parents=True,exist_ok=True)
q='''# 传承题：噪声、组分图与数据划分（成员B实验依据，供A定稿）

## 题目

一组同学使用单幅高光谱图中的像素光谱训练自编码器，再用潜在特征k-means生成类别图。以下表格来自本组模拟实验的独立生成视野，干净真值没有参与模型训练。

'''+table(selected)+'''

1. 从表中分别找出σ=0.40下光谱RMSE最低和宏F1最高的方法。两者是否必然相同？
2. 为什么“处理图更平滑”不能证明化学信息保存更好？应增加哪些证据？
3. 随机像素划分与带缓冲空间划分有什么区别？为什么训练/测试没有相同像素仍可能有泄露风险？
4. 用同一样品的另一个视野测试，能否证明跨仪器或跨样品泛化？
5. 若真实矿物图没有像素真值，能否报告真实分类准确率？Cluster 0能否直接称作锂辉石浓度？

## 可核查答案

'''
rr=[r for r in selected if r['noise_sigma']=='0.4'];rm=min(rr,key=lambda r:float(r['RMSE']));ff=max(rr,key=lambda r:float(r['macro_F1']))
winners='、'.join(r['method'] for r in rr if np.isclose(float(r['macro_F1']),float(ff['macro_F1']),atol=1e-8))
q+=f"1. 本次σ=0.40，RMSE最低为{rm['method']}（{float(rm['RMSE']):.4f}），宏F1最高为{winners}（{float(ff['macro_F1']):.4f}，多个方法时为并列）；按表读取，二者衡量不同目标，不必相同。\n"
q+='''2. 平滑可能抹掉窄峰或弱峰，应检查代表光谱、峰高、谱形/SAM、错误区域及有真值时的组分指标。
3. 随机划分可能把相邻、强相关像素分入两侧；空间划分和缓冲降低直接邻接，但不保证独立样品泛化。无索引重复不等于无相关性风险；全数据归一化也可能泄露测试统计。
4. 不能。不同视野是较好的外部评估，但样品、批次和仪器仍可能相同。
5. 不能凭空报告准确率；簇编号不等于化学身份，单类别图更不是定量浓度。需要独立参考光谱、标定和真实标签等支持。

核查文件：results/synthetic/metrics.csv、leakage_audit.json，以及 run.py。评分建议每问2分，共10分；允许结论与预期不同，但必须依据实际数据。
'''
(qdir/'ch11_case_question_B.md').write_text(q,encoding='utf8')

# Directly visible original image slice, and original spatial coordinates in sampled grid.
d=np.load(root/'data/mineral_small.npz')
fig,axs=plt.subplots(1,2,figsize=(10,4))
for ax,key in zip(axs,['train_cube','test_cube']):
    v=d[key];im=ax.imshow(v[:,:,v.shape[-1]//2],cmap='viridis');ax.set_title(key+' | original channel 453');ax.set_xlabel('Sampled x (stride 4)');ax.set_ylabel('Sampled y (stride 4)');fig.colorbar(im,ax=ax,shrink=.7)
fig.suptitle('REAL AUTHOR DATA | Raw intensity slice, not a concentration map');fig.tight_layout()
fig.savefig(root/'results/real/raw_overview.png',dpi=180,bbox_inches='tight');fig.savefig(root/'results/real/raw_overview.svg',bbox_inches='tight');plt.close(fig)
print('Report and question generated from actual CSV files')
fig,axs=plt.subplots(1,2,figsize=(9,3))
for method in ['Raw','MovingAverage5','ConvAE']:
    rr=[r for r in selected if r['method']==method]
    axs[0].plot([float(r['noise_sigma']) for r in rr],[float(r['RMSE']) for r in rr],'-o',label=method)
    axs[1].plot([float(r['noise_sigma']) for r in rr],[float(r['macro_F1']) for r in rr],'-o',label=method)
axs[0].set_ylabel('Spectral RMSE');axs[1].set_ylabel('Macro F1 (curves may overlap)');axs[1].set_ylim(0,1.05)
for ax in axs:ax.set_xlabel('Synthetic Gaussian noise sigma');ax.legend(fontsize=8)
fig.suptitle('SYNTHETIC ONLY | External field | Spatial training split');fig.tight_layout()
fig.savefig(root/'results/synthetic/quality_summary.png',dpi=180,bbox_inches='tight');fig.savefig(root/'results/synthetic/quality_summary.svg',bbox_inches='tight');plt.close(fig)
from html import escape
cells=''.join('<tr>'+''.join('<td>'+escape(str(v))+'</td>' for v in [r['noise_sigma'],r['method'],f"{float(r['RMSE']):.4f}",f"{float(r['SAM_deg']):.2f}",f"{float(r['macro_F1']):.4f}"])+'</tr>' for r in selected)
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>G11 成员B交付</title><style>body{font:17px/1.7 system-ui,'Microsoft YaHei';max-width:1100px;margin:35px auto;padding:0 20px;color:#183149;background:#f4f7fb}h1,h2{line-height:1.3}section{background:white;padding:22px;margin:20px 0;border-radius:14px}a{color:#175ca4}img{width:100%}table{border-collapse:collapse;width:100%}td,th{padding:8px;border-bottom:1px solid #dde4ec;text-align:left}.note{border-left:5px solid #dc9a38;padding:15px;background:#fff7e7}</style>
<h1>化学成像：成员 B 实验交付</h1><p>数据 → 预处理 → 传统方法与深度学习 → 组分类别图 → 质量评价</p>
<p class="note">真实作者数据已运行；网络为本组教学简化实现。真实图没有逐像素真值，Cluster不是已确认矿物或浓度。模拟图单独用于有真值评价。</p>
<section><h2>先看这些</h2><p><a href="README_B.md">运行与交接说明</a> · <a href="docs/B_results.md">完整中文结果报告</a> · <a href="docs/B_presentation_notes.md">汇报讲稿</a> · <a href="docs/verification.json">验证记录</a></p><p><a href="results/real/viewer.html">真实数据交互图</a> · <a href="results/synthetic/viewer.html">模拟数据交互图</a> · <a href="code/ch11_exercises/run.py">主代码</a></p></section>
<section><h2>真实矿物：不同方法的空间类别图</h2><img src="results/real/real/spatial/component_maps.png"><p>FOV1训练，FOV2评估；训练区拟合归一化和聚类。颜色按训练区簇重叠对齐，仅用于比较显示。</p></section>
<section><h2>模拟实验：已知真值下的质量评价</h2><img src="results/synthetic/quality_summary.png"><table><tr><th>噪声σ</th><th>方法</th><th>RMSE↓</th><th>SAM/度↓</th><th>宏F1↑</th></tr>TABLE_ROWS</table><p>每个噪声水平分别训练，固定种子单次运行；误差与分类指标不必一致，不代表真实矿物准确率。</p></section>
<section><h2>交给组员</h2><p>A：技术正文片段、实验结果、引文、传承题实验依据。C：PNG/SVG图件、数值数据、讲稿和演示。最终汇报PDF、他人独立验证和GitHub PR仍需在小组流程中完成。</p><p><a href="resources/annual/2026-2027/questions/ch11_case_question_B.md">实验题与答案</a> · <a href="resources/annual/2026-2027/references/ch11_UHRED.md">来源与引文</a> · <a href="docs/PR_B.md">PR说明草稿</a></p></section></html>'''
(root/'开始阅读.html').write_text(page.replace('TABLE_ROWS',cells),encoding='utf8')

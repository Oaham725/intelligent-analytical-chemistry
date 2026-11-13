# G18 结晶紫自动化 UV–Vis 实验

<a href="../../docs/ch18-uvvis.md" data-g18-site-href="#/docs/ch18-uvvis">实验原理</a> · <a href="../../assets/labs/g18/index.html" data-g18-site-href="./assets/labs/g18/index.html" target="_blank" rel="noopener">离线实验 HTML</a> · <a href="data/README.md" data-g18-site-href="#/code/ch18_uvvis/data/README">数据字典</a>

在课程网站打开实验，或从 GitHub 下载 `assets/labs/g18/index.html` 后用浏览器打开。默认时限为 290 s，最大加液量为 0.60 mL。点击「运行自动实验」，可看曲线逐点绘制、切换观测量和导出 CSV。

## 复现实验数据

使用 Node.js 18 或更新版本。脚本使用 Node.js 内置模块。在课程仓库根目录运行：

```text
node code/ch18_uvvis/reproduce.cjs ./g18-reproduced
```

脚本先检查物料衡算、泵回执和异常处理，再将校准数据、候选剂量、时间序列、终点对照和事件日志写入 `g18-reproduced/`。该目录用于存放本次复现结果。省略输出目录时，脚本写入 `code/ch18_uvvis/data/`。

| 核查对象 | 默认结果 |
|---|---|
| `summary.json` | 指令 0.30 mL，模拟泵回执 0.294 mL。自动加液 275 s 确认达标，无加液参照 415 s 确认达标。 |
| `endpoint-comparison.csv` | 同一批读数中，净吸光度判据在 260 s 确认，体积校正判据在 275 s 确认。 |
| `events.csv` | 剂量上限 0.20 mL 时无可行方案。决策时空白缺失时跳过加液。泵回执丢失后暂停达标判断。 |

## 在网页中复核

1. 正常运行，核对加液量、回执体积和 275 s 确认时刻。
2. 切换「空白扣除后的吸光度」和「结晶紫剩余量」，结合回执说明加液后曲线为什么不同。
3. 选择「加液后泵回执丢失」，检查状态提示和事件记录，并核对终点确认栏留空。

默认数据使用固定随机种子生成。数值用于复现教学仿真，实际仪器的体积、混合和测量误差需要用独立实验校准与验证。

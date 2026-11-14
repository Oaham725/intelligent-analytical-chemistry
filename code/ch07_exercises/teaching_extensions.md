# 第7章互动与逐视频配对图：运行与核验

## 先按任务选择依赖

以下命令均从仓库根目录运行。按所需任务安装依赖即可，不必为查看归档结果安装整套训练与绘图库；表中列的是源码实际使用的依赖。

| 任务 | 最小运行依赖 | 入口命令 | 是否训练模型 |
| --- | --- | --- | --- |
| 复算已归档指标与校验和 | Python标准库，无额外包 | `python code/ch07_exercises/verify_results.py` | 否 |
| CNN、GNN、注意力前向与梯度图例 | Python＋NumPy | `python code/ch07_exercises/model_steps.py`；`python code/ch07_exercises/gradient_check.py` | 否 |
| 四模型模拟光谱实验 | Python＋NumPy＋PyTorch | `python code/ch07.py --out runs/ch07-spectra` | 是 |
| 重新生成逐视频配对图 | Python＋Matplotlib及其依赖项（含NumPy） | `python code/ch07_exercises/plot_lptem_pairs.py --out runs/ch07-pairs/paired.svg` | 否，读取已有指标 |
| 注意力计算与迁移反馈测试 | Node.js及其内置测试运行器，无额外npm包 | `node --test code/ch07_exercises/test_attention_lab.cjs` | 否 |
| 教材网页互动 | 浏览器；Python标准库用于启动网页服务 | `python -m http.server 8000`，再打开 `http://localhost:8000/#/docs/ch07` | 否 |

完整Python测试命令 `python -m unittest discover -s code/ch07_exercises -p "test_*.py" -v` 同时包含归档测试和光谱分组测试，后者需要NumPy与PyTorch。若只检查归档故障处理，可运行 `python -m unittest discover -s code/ch07_exercises -p "test_verify_results.py" -v`，仅需标准库。NumPy模拟LPTEM分割的运行方法另见[原案例说明](lptem.md)；该脚本使用 `--plot` 时也需要Matplotlib。

## 注意力互动

在仓库根目录启动一个静态网页服务：

```bash
python -m http.server 8000
```

打开 `http://localhost:8000/#/docs/ch07`，找到“动手改变匹配、掩码与汇入内容”。教材原有 Docsify、KaTeX 等依赖通过 CDN 加载，需要能访问相应资源。GitHub Markdown 文件预览不会执行网页脚本，保留图解和数值说明作为阅读入口。

互动模块自身无额外网页库依赖，输入只用于当前页面计算，不保存或上传。它固定使用一维 q、两个 k、两个 v，d_k=1；默认第二个键为自然对数 ln3，计算保留完整精度，显示保留6位小数。它没有训练模型，也不输出经过化学标定的测量值。

| 操作 | 应观察到的结果 | 解释 |
| --- | --- | --- |
| 默认状态 | 权重0.25、0.75；Z=5 | 对得分0、ln3做softmax，再汇聚2、6 |
| 将q改为0 | 权重0.5、0.5；Z=4 | 两个可读键的匹配得分相同 |
| 恢复默认，将v₂改为0 | 权重不变；Z=0.5 | V改变汇聚内容，不决定匹配权重 |
| 屏蔽第二键 | 权重1、0；Z=2 | softmax前屏蔽并重新归一化 |
| 保持屏蔽，再改v₂ | Z保持2 | 被屏蔽的内容没有贡献 |
| 清空一个数值 | 显示输入错误并停止展示旧结果 | 避免把无效输入默认为零 |

迁移判断区对完整光谱分类与实时下一时刻预测分别解释读取边界。屏蔽第二个键只是一行的掩码操作，不代表自动构成多查询的完整因果掩码。每个查询都必须至少保留一个可读取的键。

使用 Node.js 内置测试运行器检查计算、数值稳定性、异常与迁移反馈：

```bash
node --test code/ch07_exercises/test_attention_lab.cjs
```

另在教材网页检查：Tab、空格及Enter能操作控件；重置后默认数值和判断恢复；375px窄屏无组件横向溢出；切到其他章节再返回只挂载一次。这些行为检查与纯数值测试分别记录，不能仅凭Node测试认定网页已可用。

## 从归档生成逐视频配对图

[脚本](plot_lptem_pairs.py)默认读取[32条逐视频指标](../../resources/annual/2026-2027/results/ch07/lptem/metrics.csv)，在同一条件、同一视频内配对局部均值法与CNN。依赖 Matplotlib 及其依赖项；本次实测 Python 3.12.14、NumPy 2.5.4、Matplotlib 3.11.2。

```bash
python code/ch07_exercises/plot_lptem_pairs.py
```

默认生成 `assets/figures/ch07_lptem_pairs.svg`。保留全部32条记录、16对方法比较；同分布条件CNN较高8/8，偏移条件2/8。两个条件使用不同视频，编号不能跨条件配对。图中只展示每段视频的观测值，不添加显著性或真实实验性能推断。

可另指定输出与预览目录：

```bash
python code/ch07_exercises/plot_lptem_pairs.py --out runs/ch07-pairs/paired.svg --qa-dir runs/ch07-pairs
```

预览目录保存PDF、PNG与逐条件数值汇总。默认读写位置基于脚本所在仓库解析；输出目录可替换。缺失、重复、未知组合和非有限IoU会被拒绝，脚本不静默合并或丢弃视频。它没有重新训练，也没有修改输入CSV。相同软件环境下的重复导出已核对SVG字节一致，跨版本不保证相同文件哈希。

### 受限权限环境：指定绘图缓存

Matplotlib需要可写的配置与字体缓存目录。如果默认用户目录不可写，可在启动Python、导入Matplotlib之前，把 `MPLCONFIGDIR` 指向当前工作目录内的可写文件夹。以下示例同时把图片和预览写入 `runs/`，避免覆盖教材默认SVG。

PowerShell：

```powershell
$env:MPLCONFIGDIR = Join-Path (Get-Location).Path "runs/ch07-mpl-cache"
New-Item -ItemType Directory -Force -Path $env:MPLCONFIGDIR | Out-Null
python code/ch07_exercises/plot_lptem_pairs.py --out runs/ch07-pairs/paired.svg --qa-dir runs/ch07-pairs
```

bash：

```bash
export MPLCONFIGDIR="$PWD/runs/ch07-mpl-cache"
mkdir -p "$MPLCONFIGDIR"
python code/ch07_exercises/plot_lptem_pairs.py --out runs/ch07-pairs/paired.svg --qa-dir runs/ch07-pairs
```

该设置只作用于当前终端会话及之后启动的子进程，不会永久修改系统环境变量。应确认所选目录可写；在Python中途设置变量，不能可靠地更改已经初始化的缓存位置。可在同一终端启动一个新Python进程检查实际位置：

```bash
python -c "import matplotlib; print(matplotlib.get_configdir()); print(matplotlib.get_cachedir())"
```

两处路径应指向所选目录，绘图应成功生成SVG及可选预览，且不再出现默认用户缓存目录不可写的回退警告。这里调整的是运行环境，不改变数据、模型或指标；也不代表完成了全新环境的依赖安装验证。

归档本身的完整性与指标复算仍使用：

```bash
python code/ch07_exercises/verify_results.py
```

## 前沿表的证据边界

[正文](#/docs/ch07)比较的是小CNN、U-Net、SAM 2与SAM-EM的信息、监督、提示和时间记忆。U-Net和SAM 2的原始来源已补入[文献证据库](#/resources/annual/2026-2027/references/ch07-g07)。本项目未训练或独立复跑后三者，不能把外部研究结果与本章模拟指标直接排名。

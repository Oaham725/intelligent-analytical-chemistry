#!/usr/bin/env bash
set -euo pipefail

repo="${1:-Oaham725/intelligent-analytical-chemistry}"
gh repo view "$repo" >/dev/null

create_label() {
  gh label create "$1" --repo "$repo" --color "$2" --description "$3" --force >/dev/null
}

create_label "课程任务" "0B6095" "课程共建的可认领任务"
create_label "待认领" "6C757D" "尚未由学生小组认领"
create_label "需评审" "FBCA04" "等待其他小组审阅"
create_label "教材勘误" "D73A49" "文字、公式、图表或链接错误"
create_label "代码练习" "7B2CBF" "需要补充或维护代码、数据、运行说明"

create_task() {
  local chapter="$1"
  local title="$2"
  local question="$3"
  local deliverable="$4"

  if gh issue list --repo "$repo" --state all --search "\"$title\" in:title" --json title --jq '.[].title' | grep -Fxq "$title"; then
    return
  fi

  gh issue create --repo "$repo" \
    --title "$title" \
    --label "课程任务" \
    --label "待认领" \
    --body "## 章节\n\n$chapter\n\n## 核心问题\n\n$question\n\n## 最低交付成果\n\n$deliverable\n\n## 提交要求\n\n- 先在评论中写明小组名称与任务分工；\n- 在独立分支完成修改并提交 Pull Request；\n- PR 中给出验证方式，并请求其他小组评审；\n- 合并前在章节末尾补充贡献者记录。"
}

create_task "第1章" "[课程任务] G01：智能测量导论" "如何把 AI 放回样品—测量—信号—模型—决策闭环？" "一个真实分析任务拆解案例，以及导论知识图谱修订。"
create_task "第2章" "[课程任务] G02：化学数据" "原始仪器数据如何成为可建模的数据对象？" "一个数据审计与预处理练习，以及数据字典或元数据示例。"
create_task "第3章" "[课程任务] G03：化学计量学" "矩阵、秩、逆、SVD、PCA 与 PLS 如何服务于信号分解与定量？" "线性代数推导核查，以及 PCA/SVD 或 PLS 可运行练习。"
create_task "第4章" "[课程任务] G04：机器学习" "模型为何会泛化失败，如何避免数据泄露？" "基线模型对比，以及分组划分或校准曲线练习。"
create_task "第5章" "[课程任务] G05：实验设计" "如何以多变量实验替代单因素试错？" "析因、正交或响应面案例，以及实验设计代码。"
create_task "第6章" "[课程任务] G06：分子表征" "如何让结构表示保留与性质相关的化学信息？" "描述符或分子图案例，以及表示选择说明。"
create_task "第7章" "[课程任务] G07：深度学习" "CNN、Transformer、GNN 的归纳偏置分别适合何种化学数据？" "一个可解释的模型比较或小型实现。"
create_task "第8章" "[课程任务] G08：生成与扩散" "生成模型怎样用于反演、去噪和不确定性表达？" "条件生成或去噪案例，以及失效边界说明。"
create_task "第9章" "[课程任务] G09：智能谱学" "预处理、校正与模型如何共同提高谱学结论质量？" "一套谱图处理流程，以及波段或误差分析。"
create_task "第10章" "[课程任务] G10：MS、色谱、NMR" "如何将分离、谱库检索和结构约束组织为结构解析证据链？" "谱库匹配或峰表处理案例，以及结构判断流程图。"
create_task "第11章" "[课程任务] G11：化学成像" "空间分辨、光谱维度和图像质量如何共同决定结论？" "图像或高光谱处理案例，以及质量评价示意图。"
create_task "第12章" "[课程任务] G12：生物分析" "生物样品的动态性、批次效应和多尺度性如何进入模型？" "一个生物分析数据案例，以及批次效应讨论。"
create_task "第13章" "[课程任务] G13：多模态分析" "不同测量模态何时互补、何时引入新偏差？" "融合策略比较，以及缺失模态处理方案。"
create_task "第14章" "[课程任务] G14：标准化与 FAIR" "为什么模型跨仪器、跨批次或跨实验室会失效？" "校准迁移或元数据案例，以及标准化检查表。"
create_task "第15章" "[课程任务] G15：可信智能分析" "如何报告不确定度、适用域和潜在混杂因素？" "失败样本分析，以及适用域或置信度练习。"
create_task "第16章" "[课程任务] G16：科学大模型与智能体" "大模型怎样在工具与约束下参与分析任务？" "一个受限工具调用流程，以及核验清单。"
create_task "第17章" "[课程任务] G17：强化学习与自主实验室" "什么情况下实验问题是连续决策而非一次性优化？" "状态—动作—奖励建模，以及安全约束案例。"
create_task "第18章" "[课程任务] G18：世界模型与数字孪生" "如何预测操作—样品状态—仪器信号的动态关系？" "简化测量系统模型，以及虚拟实验或反事实案例。"

echo "课程任务已准备完毕：https://github.com/$repo/issues"

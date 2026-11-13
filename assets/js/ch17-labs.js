/*
 * 第 17 章互动实验室：实验决策、强化学习与具身自主实验室
 *
 * 一个章首综合案例 + 六个分节模块，每个模块操纵本节的一个核心对象：
 *   ch17-autonomy-shift   章首：夜间值班（状态、奖励、故障三项决定 + 迁移题）
 *   ch17-problem-sorter   17.1 判断批量设计 / 序贯选点 / 序贯控制
 *   ch17-state-designer   17.2 为显色孔设计满足马尔可夫性的状态
 *   ch17-reward-tuner     17.3 调节奖励权重，观察被选中的策略与奖励投机
 *   ch17-shield-lab       17.4 为策略配置屏蔽规则：漏拦与误拦
 *   ch17-fault-injection  17.5 选择控制器能力并注入故障，观察静默错误
 *   ch17-loop-assigner    17.6 把决策分配到正确的时间尺度
 *
 * 状态只保存在浏览器本地（localStorage，失败时静默降级），不上传任何答案或个人信息。
 * 样式复用 theme.css 中的 .section-lab 系列类，第 17 章特有样式以 .ch17- 前缀补充。
 */
(function () {
  'use strict';

  var prefix = 'iac-ch17-lab-v1:';

  function read(key, initial) {
    try {
      var stored = window.localStorage.getItem(prefix + key);
      return stored ? Object.assign({}, initial, JSON.parse(stored)) : JSON.parse(JSON.stringify(initial));
    } catch (error) {
      return JSON.parse(JSON.stringify(initial));
    }
  }

  function save(key, value) {
    try { window.localStorage.setItem(prefix + key, JSON.stringify(value)); } catch (error) { /* 无本地存储时仍可完成当前操作。 */ }
  }

  function clear(key) {
    try { window.localStorage.removeItem(prefix + key); } catch (error) { /* 无需处理。 */ }
  }

  function esc(text) {
    return String(text).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
  }

  function feedback(type, title, text) {
    return '<div class="section-lab-feedback section-lab-feedback--' + type + '" role="status" aria-live="polite"><strong>' + title + '</strong><p>' + text + '</p></div>';
  }

  function shell(kicker, title, objective, body) {
    return '<section class="section-lab" aria-label="' + esc(title) + '"><header class="section-lab__header"><p>' + kicker + '</p><h4>' + title + '</h4><span>' + objective + '</span></header><div class="section-lab__body">' + body + '</div></section>';
  }

  function actions(primaryAction, primaryLabel, resetAction) {
    return '<div class="section-lab-actions">' + (primaryAction ? '<button type="button" class="section-lab-primary" data-action="' + primaryAction + '">' + primaryLabel + '</button>' : '') + '<button type="button" class="section-lab-secondary" data-action="' + resetAction + '">重置</button></div>';
  }

  function bind(root, handler) {
    root.onclick = function (event) {
      var target = event.target.closest('[data-action]');
      if (!target || !root.contains(target)) return;
      handler(target.getAttribute('data-action'), target, event);
    };
  }

  /* ------------------------------------------------------------ 章首：夜间值班 */
  function autonomyShift(root) {
    var key = 'shift';
    var initial = { answers: {}, revealed: {} };
    var state = read(key, initial);
    var stages = [
      {
        id: 'state', kicker: '决定 1 · 对应 17.2', title: '系统的“状态”记录哪些量？',
        context: '策略只能依据状态做决定。夜间没有人看着，状态缺了什么，策略就看不到什么。',
        options: [
          { id: 'a', text: '只记录当前吸光度 A', ok: false, why: '同样 A = 0.35 的两个孔，一个刚加完试剂、一个已显色 20 分钟，后续变化完全不同。缺少“自加试剂以来的时间”，过程不是马尔可夫的，策略会在两者之间摇摆。' },
          { id: 'b', text: 'A 的最近两次读数 + 自加试剂以来时间 + 已加试剂量 + 稀释倍数 + 孔内体积', ok: true, why: '这是对未来决策有影响的最小充分集合：时间与读数趋势判断显色是否完成，试剂量判断络合是否充足，稀释倍数用于换算浓度，孔内体积供屏蔽器检查溢出。' },
          { id: 'c', text: '把仪器的全部原始日志（每秒一条）都作为状态', ok: false, why: '信息没有丢，但状态维度巨大，学习所需数据成倍增加，且大部分变量（如风扇转速）与决策无关。状态应当是“最小充分”的，而不是“越全越好”。' }
        ]
      },
      {
        id: 'reward', kicker: '决定 2 · 对应 17.3', title: '用什么作为奖励？',
        context: '系统会尽一切办法提高你写下的奖励——包括你没想到的办法。',
        options: [
          { id: 'a', text: '报告时吸光度越大，奖励越高（信号越强越好）', ok: false, why: '典型的奖励投机：系统会少加显色剂、不稀释、让读数落入杂散光非线性区。练习 2 中这类奖励使浓度误差约 30%。' },
          { id: 'b', text: '每小时完成的样品数', ok: false, why: '系统会跳过空白、缩短等待、不做质控——吞吐很高，数据不可用。吞吐应当是在质量约束满足之后才优化的资源项。' },
          { id: 'c', text: '以质控样标定的浓度相对误差为主，扣除时间与试剂成本；读数 > 1.5 不得报告（约束）', ok: true, why: '奖励对准了分析结果，资源项作为次要权衡，读数饱和写成硬约束而不是靠权重“劝阻”。注意真值来自质控样，其不确定度决定策略能学到的精度上限。' }
        ]
      },
      {
        id: 'fault', kicker: '决定 3 · 对应 17.5', title: '凌晨 2:13，分液命令超时没有收到确认。系统应当……',
        context: '泵可能执行了，也可能没执行。控制器看不到真实状态，只能看到“没有回应”。',
        options: [
          { id: 'a', text: '立即重发同一分液命令', ok: false, why: '若泵其实已执行、只是确认帧丢失，重发会导致重复分液（100 µL 而非 50 µL），而且没有任何报警——这是静默错误。' },
          { id: 'b', text: '查询泵计数器 / 体积传感器，只补足差额；连续失败则进入安全态并通知值班人员', ok: true, why: '幂等重试：动作语义是“使孔内体积达到 50 µL”而不是“再打 50 µL”。有限次数后升级处理，避免在故障上无限循环。' },
          { id: 'c', text: '跳过这个样品，继续下一个', ok: false, why: '跳过并不安全：孔内状态未知，若后续仍向同一孔板操作可能溢出；同时该样品没有被标记为弃样，数据库中会留下一条不完整的记录。' }
        ]
      },
      {
        id: 'transfer', kicker: '迁移题', title: '换成“自动电位滴定判断终点”，状态中最容易被遗漏、从而破坏马尔可夫性的是？',
        context: '把刚才的推理迁移到另一类连续决策问题。',
        options: [
          { id: 'a', text: '电极响应滞后：需要记录最近几次读数与每次加液后的时间间隔', ok: true, why: '电极电位需要时间达到平衡；只看“当前电位”，无法区分“已平衡”与“仍在漂移”。这与显色时间完全同构：缺少时间/趋势变量，过程就不是马尔可夫的。' },
          { id: 'b', text: '滴定剂试剂瓶的标签颜色', ok: false, why: '与决策无关的变量只会增加状态维度。' },
          { id: 'c', text: '当前电位值本身', ok: false, why: '当前电位当然要记录，但它恰恰是“最不容易被遗漏”的变量。问题在于只记录它是不够的。' }
        ]
      }
    ];

    function draw() {
      var done = stages.filter(function (s) { return state.revealed[s.id]; }).length;
      var correct = stages.filter(function (s) {
        var pick = state.answers[s.id];
        return state.revealed[s.id] && s.options.some(function (o) { return o.id === pick && o.ok; });
      }).length;
      var html = '<p class="section-lab-lead">你的角色：首次夜间无人值守运行的负责人。依次作出决定，每一步都会看到系统在这个决定下会怎样表现。</p>';
      html += '<div class="ch17-progress" aria-label="进度">已完成 ' + done + ' / ' + stages.length + '　·　与推荐方案一致 ' + correct + '</div>';
      stages.forEach(function (stage) {
        var pick = state.answers[stage.id];
        var revealed = state.revealed[stage.id];
        html += '<fieldset class="ch17-stage"><legend><span>' + stage.kicker + '</span>' + stage.title + '</legend><p class="section-lab-caption">' + stage.context + '</p>';
        stage.options.forEach(function (o) {
          var cls = 'section-lab-choice section-lab-choice--compact';
          if (pick === o.id) cls += ' is-selected';
          if (revealed && pick === o.id) cls += o.ok ? ' is-correct' : ' is-incorrect';
          html += '<button type="button" class="' + cls + '" data-action="pick" data-stage="' + stage.id + '" data-id="' + o.id + '" aria-pressed="' + (pick === o.id) + '"><b>' + o.id.toUpperCase() + '</b><span>' + o.text + '</span></button>';
        });
        if (pick && !revealed) html += '<div class="section-lab-actions"><button type="button" class="section-lab-primary" data-action="reveal" data-stage="' + stage.id + '">确认这个决定</button></div>';
        if (revealed) {
          var chosen = stage.options.filter(function (o) { return o.id === pick; })[0];
          var best = stage.options.filter(function (o) { return o.ok; })[0];
          html += feedback(chosen.ok ? 'success' : 'warning', chosen.ok ? '系统表现可辩护' : '运行后会出问题', chosen.why + (chosen.ok ? '' : '<br>推荐：' + best.text + '。'));
        }
        html += '</fieldset>';
      });
      if (done === stages.length) {
        html += '<div class="section-lab-callout">值班复盘：状态决定系统“看得见什么”，奖励决定系统“想要什么”，执行层决定“做了的是否就是想做的”。三者任何一个出错，算法再好也会在夜里安静地产生错误数据。</div>';
      }
      html += actions(null, '', 'reset');
      root.innerHTML = shell('第17章 · 章首综合互动', '自主显色工作站的第一次夜间值班', '目标：把状态、奖励与故障恢复联系为同一条可辩护的运行方案。', html);
    }

    bind(root, function (action, target) {
      var sid = target.getAttribute('data-stage');
      if (action === 'pick' && !state.revealed[sid]) { state.answers[sid] = target.getAttribute('data-id'); }
      if (action === 'reveal') { state.revealed[sid] = true; }
      if (action === 'reset') { clear(key); state = read(key, initial); }
      save(key, state); draw();
    });
    draw();
  }

  /* ------------------------------------------------------------ 17.1 问题分拣 */
  function problemSorter(root) {
    var key = 'sorter';
    var initial = { picks: {}, checked: false };
    var state = read(key, initial);
    var types = [{ id: 'batch', label: '批量设计' }, { id: 'seq', label: '序贯选点' }, { id: 'ctrl', label: '序贯控制' }];
    var cases = [
      { id: 'c1', text: '一次性安排 3 因素 2 水平的 8 组色谱实验，全部做完再分析', ans: 'batch', why: '所有条件事先确定，实验之间不存在信息或状态的传递。' },
      { id: 'c2', text: '逐轮选择 pH 与温度以最大化荧光强度，每轮使用新配制的样品', ans: 'seq', why: '每轮样品状态被重置，只有“模型知识”在积累——贝叶斯优化的典型场景。' },
      { id: 'c3', text: '同一显色孔中，决定何时加第二份显色剂、何时稀释、何时读数', ans: 'ctrl', why: '状态延续（已加试剂、显色时间）、不可逆（加液、稀释）、延迟后果（是否显色完全）——四条判据中满足三条以上。' },
      { id: 'c4', text: '电化学传感器连续测量中，决定何时清洗电极', ans: 'ctrl', why: '电极表面污染随测量累积（状态延续），清洗会中断测量并改变后续响应，后果延迟显现。' },
      { id: 'c5', text: '在线监测合成反应，决定何时取样、何时淬灭', ans: 'ctrl', why: '取样消耗反应液、淬灭不可逆；取样时机决定了能观测到什么——“动作改变可观测信息”。' },
      { id: 'c6', text: '核—壳纳米颗粒多步包覆：每一步选择注入哪种前驱体（AlphaFlow 类问题）', ans: 'ctrl', why: '每一步都改变颗粒表面状态，后续步骤效果取决于前面的序列，光学性质要多步之后才评估。' }
    ];

    function draw() {
      var score = cases.filter(function (c) { return state.picks[c.id] === c.ans; }).length;
      var rows = cases.map(function (c, i) {
        var pick = state.picks[c.id];
        var btns = types.map(function (t) {
          var cls = 'section-lab-chip';
          if (pick === t.id) cls += ' is-selected';
          return '<button type="button" class="' + cls + '" data-action="pick" data-case="' + c.id + '" data-id="' + t.id + '" aria-pressed="' + (pick === t.id) + '">' + t.label + '</button>';
        }).join('');
        var note = '';
        if (state.checked) {
          var ok = pick === c.ans;
          var ansLabel = types.filter(function (t) { return t.id === c.ans; })[0].label;
          note = '<p class="ch17-note ' + (ok ? 'is-ok' : 'is-bad') + '">' + (ok ? '✓ ' : '✗ 应为“' + ansLabel + '”：') + c.why + '</p>';
        }
        return '<div class="ch17-row"><p><span class="section-lab-card__index">' + (i + 1) + '</span>' + c.text + '</p><div class="ch17-chips" role="group" aria-label="问题类型">' + btns + '</div>' + note + '</div>';
      }).join('');
      var fb = state.checked ? feedback(score === cases.length ? 'success' : 'warning', '判对 ' + score + ' / ' + cases.length, score === cases.length ? '你在用判据而不是关键词分类。注意第 2 题：同样是“一步一步做”，样品状态每轮重置，所以不需要强化学习。' : '回到 17.1.2 的四条判据：状态是否在步骤之间延续？动作能否撤销？后果是否延迟？动作是否改变能观测到的信息？') : '';
      var body = '<p class="section-lab-lead">为每个实验问题选择最合适的问题形式。判据比方法名更重要。</p>' + rows + actions('check', '检查分类', 'reset') + fb;
      root.innerHTML = shell('17.1 问题类型', '一次性优化还是连续决策？', '目标：用四条判据区分批量设计、序贯选点与序贯控制。', body);
    }

    bind(root, function (action, target) {
      if (action === 'pick') { state.picks[target.getAttribute('data-case')] = target.getAttribute('data-id'); state.checked = false; }
      if (action === 'check') state.checked = true;
      if (action === 'reset') { clear(key); state = read(key, initial); }
      save(key, state); draw();
    });
    draw();
  }

  /* ------------------------------------------------------------ 17.2 状态设计 */
  function stateDesigner(root) {
    var key = 'state';
    var initial = { on: {}, checked: false };
    var state = read(key, initial);
    var vars = [
      { id: 'A', label: '当前吸光度 A', role: 'need' },
      { id: 'trend', label: '最近两次读数之差', role: 'alt' },
      { id: 'time', label: '自加试剂以来的时间', role: 'alt' },
      { id: 'reagent', label: '已加显色剂量', role: 'need' },
      { id: 'dil', label: '稀释倍数', role: 'need' },
      { id: 'vol', label: '孔内体积', role: 'need' },
      { id: 'temp', label: '孔板温度', role: 'bonus' },
      { id: 'qc', label: '最近一次参比质控偏差', role: 'bonus' },
      { id: 'op', label: '当班操作员姓名', role: 'noise' },
      { id: 'barcode', label: '孔板条码', role: 'noise' }
    ];
    var tests = [
      { need: ['time', 'trend'], any: true, fail: '两个孔读数都是 0.35：一个刚加试剂，一个已显色 20 分钟。状态相同，后续却完全不同——缺少“时间”或“读数趋势”，马尔可夫性被破坏。' },
      { need: ['A'], fail: '没有读数，策略无法判断是否显色、是否超出线性区。' },
      { need: ['reagent'], fail: '不知道已加多少显色剂，就无法区分“显色慢”与“试剂不足、永远显色不完全”。' },
      { need: ['dil'], fail: '没有稀释倍数，读数无法换算回样品浓度，报告奖励无从计算。' },
      { need: ['vol'], fail: '没有孔内体积，屏蔽器无法检查“再加 50 µL 是否溢出”——状态不仅服务于策略，也服务于安全检查。' }
    ];

    function draw() {
      var picked = vars.filter(function (v) { return state.on[v.id]; });
      var chips = vars.map(function (v) {
        var on = Boolean(state.on[v.id]);
        return '<button type="button" class="section-lab-toggle' + (on ? ' is-selected' : '') + '" data-action="toggle" data-id="' + v.id + '" aria-pressed="' + on + '">' + (on ? '✓ ' : '+ ') + v.label + '</button>';
      }).join('');
      var dims = picked.length;
      var fb = '';
      if (state.checked) {
        var fails = tests.filter(function (t) {
          return t.any ? !t.need.some(function (id) { return state.on[id]; }) : !t.need.every(function (id) { return state.on[id]; });
        });
        var noise = picked.filter(function (v) { return v.role === 'noise'; });
        var bonus = picked.filter(function (v) { return v.role === 'bonus'; });
        if (fails.length) {
          fb = feedback('warning', '双轨迹检验未通过（' + fails.length + ' 项）', fails.map(function (f) { return '· ' + f.fail; }).join('<br>'));
        } else {
          var extra = noise.length ? '<br>但你加入了与决策无关的变量（' + noise.map(function (v) { return v.label; }).join('、') + '）：它们不破坏马尔可夫性，却让状态空间成倍增大，表格方法需要的数据随之增加。' : '';
          var plus = bonus.length ? '<br>加入' + bonus.map(function (v) { return v.label; }).join('、') + '是合理的：温度影响显色速率，质控偏差提示读数是否可信——在仿真到真实迁移时尤其重要。' : '';
          fb = feedback(noise.length ? 'warning' : 'success', '双轨迹检验通过', '任意两条状态相同的历史，在你的状态定义下后续统计一致。' + extra + plus);
        }
      }
      var body = '<p class="section-lab-lead">勾选要写入状态 s 的变量，再用“双轨迹检验”检查：两条历史不同、状态相同的轨迹，未来是否会不同？</p><div class="ch17-chips ch17-chips--wrap">' + chips + '</div><p class="section-lab-caption">当前状态维度：' + dims + '。若每个变量离散为 5 档，表格方法需要估计的状态数约为 5<sup>' + dims + '</sup> = ' + Math.pow(5, dims).toLocaleString('zh-CN') + '。</p>' + actions('check', '运行双轨迹检验', 'reset') + fb;
      root.innerHTML = shell('17.2 状态设计', '为显色孔设计“最小充分”的状态', '目标：理解马尔可夫性是对状态定义的要求，以及状态维度的代价。', body);
    }

    bind(root, function (action, target) {
      if (action === 'toggle') { var id = target.getAttribute('data-id'); state.on[id] = !state.on[id]; state.checked = false; }
      if (action === 'check') state.checked = true;
      if (action === 'reset') { clear(key); state = read(key, initial); }
      save(key, state); draw();
    });
    draw();
  }

  /* ------------------------------------------------------------ 17.3 奖励调节 */
  function rewardTuner(root) {
    var key = 'reward';
    var initial = { wSig: 2, wErr: 0, wTime: 3, wReag: 2, constraint: false };
    var state = read(key, initial);
    // 四个候选策略的仿真表现（与练习 2 的现象一致，数值为教学示意）
    var policies = [
      { id: 'P1', name: '少试剂、快报告', sig: 1.00, err: 30, time: 6, reag: 1, sat: false, desc: '只加 1 份显色剂；高浓度样品络合不完全' },
      { id: 'P2', name: '加足试剂、等稳、不稀释', sig: 1.60, err: 9, time: 11, reag: 2, sat: true, desc: '高浓度样品读数进入杂散光非线性区' },
      { id: 'P3', name: '加足试剂、等稳、过高才稀释', sig: 0.85, err: 2.5, time: 13, reag: 2, sat: false, desc: '先预读，A > 1 时稀释后再读' },
      { id: 'P4', name: '一律 10 倍稀释、长时间等待', sig: 0.15, err: 6, time: 18, reag: 3, sat: false, desc: '低浓度样品信号过弱，噪声主导误差' }
    ];
    var sliders = [
      { id: 'wSig', label: '信号强度权重 w<sub>sig</sub>', hint: '奖励 + w × 报告时吸光度' },
      { id: 'wErr', label: '浓度误差权重 w<sub>err</sub>', hint: '奖励 − w × 相对误差(%) / 10' },
      { id: 'wTime', label: '时间成本权重 w<sub>t</sub>', hint: '奖励 − w × 步数 / 10' },
      { id: 'wReag', label: '试剂成本权重 w<sub>v</sub>', hint: '奖励 − w × 试剂份数 / 10' }
    ];

    function score(p) {
      return state.wSig * p.sig - state.wErr * p.err / 10 - state.wTime * p.time / 10 - state.wReag * p.reag / 10;
    }

    function draw() {
      var feasible = policies.filter(function (p) { return !(state.constraint && p.sat); });
      var best = feasible.reduce(function (a, b) { return score(b) > score(a) ? b : a; });
      var rows = policies.map(function (p) {
        var off = state.constraint && p.sat;
        return '<tr class="' + (p === best ? 'is-best' : '') + (off ? ' is-off' : '') + '"><th scope="row">' + p.id + ' ' + p.name + '<small>' + p.desc + '</small></th><td>' + p.sig.toFixed(2) + '</td><td>' + p.err + '%</td><td>' + p.time + '</td><td>' + p.reag + '</td><td>' + (off ? '被约束排除' : (Math.abs(score(p)) < 0.005 ? 0 : score(p)).toFixed(2)) + '</td></tr>';
      }).join('');
      var ctrl = sliders.map(function (s) {
        return '<label class="process-slider ch17-slider"><span>' + s.label + '：<output>' + state[s.id] + '</output></span><input type="range" min="0" max="10" step="1" value="' + state[s.id] + '" data-slider="' + s.id + '"><small>' + s.hint + '</small></label>';
      }).join('');
      var verdict;
      if (best.err > 5) {
        verdict = feedback('warning', '被选中的是 ' + best.id + '：奖励投机', '这组权重下，“' + best.name + '”得分最高，但它的浓度误差为 ' + best.err + '%，超过 5% 的分析要求。奖励被优化了，分析目标被牺牲了。试着提高误差权重，或打开“读数 > 1.5 不得报告”约束。');
      } else {
        verdict = feedback('success', '被选中的是 ' + best.id + '：' + best.name, '误差 ' + best.err + '% 满足要求。再试试：只把信号权重调高，看看需要多大的误差权重才能“压住”它——这说明用加权和表达硬性质量要求是多么脆弱。');
      }
      var body = '<p class="section-lab-lead">调节奖励中的各项权重。系统总会选出得分最高的策略——不管它是否符合你的本意。</p><div class="ch17-split"><div>' + ctrl + '<button type="button" class="section-lab-toggle' + (state.constraint ? ' is-selected' : '') + '" data-action="constraint" aria-pressed="' + state.constraint + '">' + (state.constraint ? '✓ ' : '+ ') + '约束：读数 &gt; 1.5 不得报告</button></div><div class="ch17-table-wrap"><table class="ch17-table"><thead><tr><th>候选策略</th><th>报告时 A</th><th>误差</th><th>步数</th><th>试剂</th><th>奖励</th></tr></thead><tbody>' + rows + '</tbody></table></div></div>' + verdict + actions(null, '', 'reset');
      root.innerHTML = shell('17.3 奖励设计', '奖励调节台：系统想要的就是你写下的', '目标：观察加权和奖励如何诱导奖励投机，以及约束为何比权重更可靠。', body);
    }

    root.oninput = function (event) {
      var id = event.target.getAttribute('data-slider');
      if (!id) return;
      state[id] = Number(event.target.value);
      save(key, state);
      var focusId = id;
      draw();
      var el = root.querySelector('[data-slider="' + focusId + '"]');
      if (el) el.focus();
    };
    bind(root, function (action) {
      if (action === 'constraint') state.constraint = !state.constraint;
      if (action === 'reset') { clear(key); state = read(key, initial); }
      save(key, state); draw();
    });
    draw();
  }

  /* ------------------------------------------------------------ 17.4 屏蔽器 */
  function shieldLab(root) {
    var key = 'shield';
    var initial = { rules: {}, ran: false };
    var state = read(key, initial);
    var rules = [
      { id: 'vol', label: '孔内体积加上本次加液不得超过 400 µL', good: true },
      { id: 'blank', label: '当日未测空白，不得测量', good: true },
      { id: 'sat', label: '读数 > 1.5 不得报告', good: true },
      { id: 'temp', label: '加热设定不得超过 40 °C', good: true },
      { id: 'low', label: '读数 < 0.3 不得报告', good: false },
      { id: 'nodil', label: '禁止稀释（稀释消耗样品）', good: false }
    ];
    var proposals = [
      { text: '加显色剂 50 µL（孔内已有 380 µL）', unsafe: true, by: 'vol', note: '溢出：试剂外泄、污染相邻孔。' },
      { text: '测量 B3（今天尚未测空白）', unsafe: true, by: 'blank', note: '没有空白的读数不可换算。' },
      { text: '报告 C5，读数 1.72', unsafe: true, by: 'sat', note: '读数位于杂散光非线性区，报告值系统偏低。' },
      { text: '把加热块设为 45 °C 以加速显色', unsafe: true, by: 'temp', note: '超出方法规定温度，可能使试剂分解。' },
      { text: '报告 A2，读数 0.21，最近三次读数稳定', unsafe: false, by: 'low', note: '低浓度样品的正常结果——这是一个科学判断，不该由屏蔽器否决。' },
      { text: '稀释 D1（孔内 200 µL，读数 1.30）', unsafe: false, by: 'nodil', note: '这正是把高读数拉回线性区的正确动作。' }
    ];

    function draw() {
      var chips = rules.map(function (r) {
        var on = Boolean(state.rules[r.id]);
        return '<button type="button" class="section-lab-toggle' + (on ? ' is-selected' : '') + '" data-action="rule" data-id="' + r.id + '" aria-pressed="' + on + '">' + (on ? '✓ ' : '+ ') + r.label + '</button>';
      }).join('');
      var result = '';
      if (state.ran) {
        var leak = 0, falseBlock = 0;
        var items = proposals.map(function (p) {
          var blocked = Boolean(state.rules[p.by]);
          var cls, tag;
          if (p.unsafe && blocked) { cls = 'is-ok'; tag = '已拦截'; }
          else if (p.unsafe) { cls = 'is-bad'; tag = '漏拦！'; leak++; }
          else if (blocked) { cls = 'is-warn'; tag = '误拦'; falseBlock++; }
          else { cls = 'is-ok'; tag = '放行'; }
          return '<li class="' + cls + '"><strong>' + tag + '</strong>' + p.text + '<small>' + p.note + '</small></li>';
        }).join('');
        var msg = leak ? '有 ' + leak + ' 个违反硬约束的动作被执行了。在真实平台上，每一个都是一次事故或一条错误数据。' : '所有违反硬约束的动作都被拦住了。';
        msg += falseBlock ? '<br>另有 ' + falseBlock + ' 个合理动作被误拦：你把“科学判断”写进了屏蔽器。屏蔽器只该表达“能不能做”，“值不值得做”交给奖励。' : '';
        result = '<ul class="ch17-log">' + items + '</ul>' + feedback(leak || falseBlock ? 'warning' : 'success', leak || falseBlock ? '屏蔽器需要修订' : '屏蔽器只表达了硬约束', msg);
      }
      var body = '<p class="section-lab-lead">策略在夜间提出了 6 个动作。选择要写进屏蔽器的规则，然后运行。好的屏蔽器：不漏拦危险动作，也不替策略做科学决定。</p><div class="ch17-chips ch17-chips--wrap">' + chips + '</div>' + actions('run', '运行这 6 个动作', 'reset') + result;
      root.innerHTML = shell('17.4 安全探索', '给策略装上屏蔽器', '目标：区分硬约束与科学目标，理解漏拦与误拦的代价。', body);
    }

    bind(root, function (action, target) {
      if (action === 'rule') { var id = target.getAttribute('data-id'); state.rules[id] = !state.rules[id]; state.ran = false; }
      if (action === 'run') state.ran = true;
      if (action === 'reset') { clear(key); state = read(key, initial); }
      save(key, state); draw();
    });
    draw();
  }

  /* ------------------------------------------------------------ 17.5 故障注入 */
  function faultInjection(root) {
    var key = 'fault';
    var initial = { caps: {}, log: [] };
    var state = read(key, initial);
    var caps = [
      { id: 'verify', label: '后置条件：体积核验' },
      { id: 'idem', label: '幂等补液（命令编号 + 查询）' },
      { id: 'timeout', label: '超时与有限次重试' },
      { id: 'qc', label: '参比质控样' },
      { id: 'interlock', label: '液位联锁 → 安全态' }
    ];
    var faults = [
      { id: 'bubble', label: '吸入气泡（实际只分出 70%）' },
      { id: 'ack', label: '泵已执行但确认帧丢失' },
      { id: 'comm', label: '光谱仪 USB 断开' },
      { id: 'lamp', label: '灯源漂移 +7%' },
      { id: 'leak', label: '孔板漏液' },
      { id: 'reagent', label: '显色剂分装失效' }
    ];
    var outcomeLabel = { ok: '已恢复', safe: '安全态 + 人工', flag: '已标记弃样', silent: '静默错误', hang: '卡死', danger: '危险继续' };

    function outcome(f) {
      var c = state.caps;
      switch (f) {
        case 'bubble':
          if (!c.verify) return ['silent', '没有体积核验，样品以 70% 体积继续显色和读数，结果偏低约 30% 且无报警。'];
          if (c.idem) return ['ok', '核验发现体积不足，按“使体积达到 50 µL”补足差额，流程继续。'];
          return ['flag', '核验发现不足，但补液命令是“再打 50 µL”，体积变为 85 µL；再次核验超差，样品被弃。'];
        case 'ack':
          if (c.idem) return ['ok', '超时后查询泵计数器，确认已执行，不重复分液。'];
          if (c.timeout) return c.verify ? ['flag', '超时后盲目重发，实际分液 100 µL；体积核验发现超差，弃样。'] : ['silent', '超时后盲目重发，实际分液 100 µL，无人发现——结果偏差 2 倍以上。'];
          return ['hang', '没有超时机制，控制器永远等待一个不会到来的确认。'];
        case 'comm':
          if (c.timeout) return ['ok', '读数超时后重连光谱仪并重测，有限次失败才进入安全态。'];
          return ['hang', '测量命令没有超时，流程卡在“等待读数”，后续样品全部停滞。'];
        case 'lamp':
          if (c.qc) return ['ok', '参比读数偏差 7% > 3%，触发空白 + 标准重新校准，并重测本样品。'];
          return ['silent', '没有参比质控，此后所有读数偏高 7%，直到下一次人工校准。'];
        case 'leak':
          if (c.interlock) return ['safe', '液位传感器触发联锁：关泵、关阀、保存数据、报警，等待人工处理。'];
          return ['danger', '系统继续向漏液的孔板加液，污染扩散至相邻孔和仪器。'];
        case 'reagent':
          return ['silent', '体积、通信、参比都正常——现有传感器看不见这种故障，显色只完成约 70%。要发现它，需要新增“带显色步骤的质控样”或读数平台期检查。'];
      }
      return ['ok', ''];
    }

    function draw() {
      var capChips = caps.map(function (c) {
        var on = Boolean(state.caps[c.id]);
        return '<button type="button" class="section-lab-toggle' + (on ? ' is-selected' : '') + '" data-action="cap" data-id="' + c.id + '" aria-pressed="' + on + '">' + (on ? '✓ ' : '+ ') + c.label + '</button>';
      }).join('');
      var faultBtns = faults.map(function (f) {
        return '<button type="button" class="section-lab-chip ch17-fault" data-action="inject" data-id="' + f.id + '">⚡ ' + f.label + '</button>';
      }).join('');
      var tally = {};
      state.log.forEach(function (e) { tally[e.o] = (tally[e.o] || 0) + 1; });
      var tallyHtml = Object.keys(outcomeLabel).filter(function (k) { return tally[k]; }).map(function (k) {
        return '<span class="ch17-pill ch17-pill--' + k + '">' + outcomeLabel[k] + ' × ' + tally[k] + '</span>';
      }).join('');
      var log = state.log.slice(-8).reverse().map(function (e) {
        var f = faults.filter(function (x) { return x.id === e.f; })[0];
        return '<li class="' + (e.o === 'ok' || e.o === 'safe' || e.o === 'flag' ? 'is-ok' : 'is-bad') + '"><strong>' + outcomeLabel[e.o] + '</strong>' + f.label + '<small>' + e.msg + '</small></li>';
      }).join('');
      var summary = '';
      if (state.log.length >= 3) {
        var silent = (tally.silent || 0) + (tally.danger || 0) + (tally.hang || 0);
        summary = feedback(silent ? 'warning' : 'success', silent ? '仍有故障被“吞掉”或使系统失控' : '注入的故障都被转成了可见事件', '记住：没有停机不等于没有错误。静默错误与卡死要和吞吐、自治时长一起报告。“显色剂分装失效”无论如何配置都会是静默错误——它提醒你，能检测什么取决于放置了哪些传感器和质控样。');
      }
      var body = '<p class="section-lab-lead">先为控制器选择能力，再逐个注入故障。观察每个故障最终变成了什么：恢复、安全停机、弃样，还是没有报警的错误数据。</p><h5 class="ch17-h5">控制器能力</h5><div class="ch17-chips ch17-chips--wrap">' + capChips + '</div><h5 class="ch17-h5">注入故障</h5><div class="ch17-chips ch17-chips--wrap">' + faultBtns + '</div><div class="ch17-tally">' + (tallyHtml || '<span class="section-lab-caption">尚未注入故障。</span>') + '</div><ul class="ch17-log">' + log + '</ul>' + summary + actions(null, '', 'reset');
      root.innerHTML = shell('17.5 具身执行层', '故障注入演练', '目标：理解后置条件、幂等重试、超时和联锁各自拦住哪类故障，以及什么仍然看不见。', body);
    }

    bind(root, function (action, target) {
      var id = target.getAttribute('data-id');
      if (action === 'cap') state.caps[id] = !state.caps[id];
      if (action === 'inject') { var r = outcome(id); state.log.push({ f: id, o: r[0], msg: r[1] }); if (state.log.length > 40) state.log.shift(); }
      if (action === 'reset') { clear(key); state = read(key, initial); }
      save(key, state); draw();
    });
    draw();
  }

  /* ------------------------------------------------------------ 17.6 环路分配 */
  function loopAssigner(root) {
    var key = 'loops';
    var initial = { picks: {}, checked: false };
    var state = read(key, initial);
    var loops = [
      { id: 'hw', label: '硬件联锁（毫秒）' },
      { id: 'fsm', label: '技能状态机（秒—分钟）' },
      { id: 'pol', label: '科学策略（分钟—小时）' },
      { id: 'human', label: '人（天—周）' }
    ];
    var items = [
      { id: 'i1', text: '液位传感器触发后关闭泵', ans: 'hw', why: '必须在毫秒级完成，且不能依赖任何软件或学习模型。' },
      { id: 'i2', text: '分液确认超时后，查询泵计数器再决定是否补液', ans: 'fsm', why: '这是技能内部的恢复逻辑，有明确的前置/后置条件。' },
      { id: 'i3', text: '根据预读结果决定这个样品是否稀释', ans: 'pol', why: '依赖对样品状态的估计与奖励权衡，是科学决策。' },
      { id: 'i4', text: '参比读数偏差 > 3% 时重新校准', ans: 'fsm', why: '规则明确的质控门，应作为技能的一部分可靠执行，而不是交给策略“权衡”。' },
      { id: 'i5', text: '选择下一轮实验使用的显色剂浓度', ans: 'pol', why: '外环的序贯选点 / 策略决策。' },
      { id: 'i6', text: '加热块超温时切断加热', ans: 'hw', why: '安全联锁，与液位联锁同理。' },
      { id: 'i7', text: '是否把误差容限从 5% 放宽到 8%', ans: 'human', why: '这改变了分析目标本身，必须由人批准并记录。' },
      { id: 'i8', text: '批准系统从“只建议”升级到“无人值守”', ans: 'human', why: '扩大自主权限需要依据前一阶段的指标作出判断，并承担责任。' }
    ];

    function draw() {
      var score = items.filter(function (it) { return state.picks[it.id] === it.ans; }).length;
      var rows = items.map(function (it) {
        var opts = '<option value="">— 选择 —</option>' + loops.map(function (l) { return '<option value="' + l.id + '"' + (state.picks[it.id] === l.id ? ' selected' : '') + '>' + l.label + '</option>'; }).join('');
        var note = '';
        if (state.checked) {
          var ok = state.picks[it.id] === it.ans;
          var right = loops.filter(function (l) { return l.id === it.ans; })[0].label;
          note = '<p class="ch17-note ' + (ok ? 'is-ok' : 'is-bad') + '">' + (ok ? '✓ ' : '✗ 应为“' + right + '”：') + it.why + '</p>';
        }
        return '<div class="ch17-row ch17-row--select"><label for="ch17-' + it.id + '">' + it.text + '</label><select id="ch17-' + it.id + '" data-item="' + it.id + '">' + opts + '</select>' + note + '</div>';
      }).join('');
      var fb = state.checked ? feedback(score === items.length ? 'success' : 'warning', '分配正确 ' + score + ' / ' + items.length, '原则：越快、越危险的决定越靠近硬件，越与目标和责任相关的决定越靠近人；学习模型只放在中间的科学策略层。') : '';
      var body = '<p class="section-lab-lead">把每个决定分配到它应当所在的环。放错层的决定，要么太慢，要么不可审查。</p>' + rows + actions('check', '检查分配', 'reset') + fb;
      root.innerHTML = shell('17.6 双时间尺度', '把决策分配到正确的环', '目标：理解快控制环、慢科学环与人的职责边界。', body);
    }

    root.onchange = function (event) {
      var id = event.target.getAttribute('data-item');
      if (!id) return;
      state.picks[id] = event.target.value;
      state.checked = false;
      save(key, state);
      draw();
      var el = root.querySelector('[data-item="' + id + '"]');
      if (el) el.focus();
    };
    bind(root, function (action) {
      if (action === 'check') state.checked = true;
      if (action === 'reset') { clear(key); state = read(key, initial); }
      save(key, state); draw();
    });
    draw();
  }

  /* ------------------------------------------------------------ 挂载 */
  var renderers = {
    'ch17-autonomy-shift': autonomyShift,
    'ch17-problem-sorter': problemSorter,
    'ch17-state-designer': stateDesigner,
    'ch17-reward-tuner': rewardTuner,
    'ch17-shield-lab': shieldLab,
    'ch17-fault-injection': faultInjection,
    'ch17-loop-assigner': loopAssigner
  };

  function mount() {
    document.querySelectorAll('.interactive-lab[data-lab]').forEach(function (root) {
      var renderer = renderers[root.getAttribute('data-lab')];
      if (!renderer || root.getAttribute('data-ch17-mounted') === 'true') return;
      root.setAttribute('data-ch17-mounted', 'true');
      renderer(root);
    });
  }

  window.$docsify = window.$docsify || {};
  window.$docsify.plugins = (window.$docsify.plugins || []).concat(function (hook) {
    hook.doneEach(function () { window.requestAnimationFrame(mount); });
    hook.mounted(function () { window.requestAnimationFrame(mount); });
  });
  document.addEventListener('DOMContentLoaded', mount);
}());

/*
 * 《智能分析化学》互动教材组件
 *
 * 约定：Markdown 中放置 <section class="interactive-lab" data-lab="..."></section>。
 * 组件只在浏览器本地保存学习进度，不上传任何学生数据。
 */
(function () {
  'use strict';

  var storagePrefix = 'iac-interactive-v1:';

  function readState(key, fallback) {
    try {
      var value = window.localStorage.getItem(storagePrefix + key);
      return value ? Object.assign({}, fallback, JSON.parse(value)) : Object.assign({}, fallback);
    } catch (error) {
      return Object.assign({}, fallback);
    }
  }

  function saveState(key, value) {
    try {
      window.localStorage.setItem(storagePrefix + key, JSON.stringify(value));
    } catch (error) {
      // 无痕浏览或禁用本地存储时，互动仍可在当前页面完成。
    }
  }

  function clearState(key) {
    try {
      window.localStorage.removeItem(storagePrefix + key);
    } catch (error) {
      // 忽略本地存储不可用的情形。
    }
  }

  function countSelected(values) {
    return Object.keys(values || {}).filter(function (key) { return values[key]; }).length;
  }

  function progressDots(current, total) {
    var dots = [];
    for (var index = 0; index < total; index += 1) {
      dots.push('<span class="lab-progress-dot ' + (index < current ? 'is-done' : '') + '" aria-hidden="true"></span>');
    }
    return dots.join('');
  }

  function feedbackBox(type, title, body) {
    return '<div class="lab-feedback lab-feedback--' + type + '" role="status" aria-live="polite">'
      + '<strong>' + title + '</strong><p>' + body + '</p></div>';
  }

  function renderChapterOne(root) {
    var initial = { choices: {}, submitted: false, matches: {}, matchChecked: false };
    var state = readState('ch01-measurement-loop', initial);
    var stages = [
      {
        id: 'sample',
        short: '样品',
        title: '先界定样品代表性',
        question: '河流异味只出现在雨后。你准备怎样取样？',
        options: [
          { id: 'one', label: '在岸边取一瓶水，尽快送检', detail: '速度快，但无法判断空间、时间与采样操作造成的差异。', correct: false },
          { id: 'design', label: '设置上、下游与投诉点；记录时间；加入平行样、现场空白和保存条件', detail: '把“河水”变成有边界、可比较的样品集合。', correct: true }
        ],
        explanation: '模型只能处理进入仪器的样品，不能补回未被采到的空间异质性。代表性是整条证据链的起点。'
      },
      {
        id: 'measure',
        short: '测量',
        title: '把测量写成可复核的接口',
        question: '你希望报告“疑似污染物的浓度”。测量方案应优先补上什么？',
        options: [
          { id: 'single', label: '直接测未知样品，用单次读数与阈值比较', detail: '没有量程、空白、校准和质量控制，读数还不是可比较的浓度。', correct: false },
          { id: 'calibrated', label: '明确目标物和量程，使用空白、标准/加标、质量控制与仪器状态记录', detail: '让仪器响应能够追溯到一个有适用范围的量值。', correct: true }
        ],
        explanation: '“测到了一个信号”与“得到了一个浓度”之间，隔着校准、基质效应和仪器稳定性。'
      },
      {
        id: 'signal',
        short: '信号',
        title: '分清化学信息与测量伪影',
        question: '光谱出现宽背景和峰位轻微移动。你的第一步是？',
        options: [
          { id: 'model', label: '立刻投入复杂神经网络，让模型自动忽略异常', detail: '模型可能把背景、批次或漂移当成目标物的证据。', correct: false },
          { id: 'diagnose', label: '核对空白、标准物、重复测量与坐标轴，再决定是否校正、对齐或重测', detail: '先解释信号的来源，才知道怎样处理不会损伤化学信息。', correct: true }
        ],
        explanation: '预处理不是修图。每一步都在声明“哪些变化是无关干扰，哪些变化可能就是目标信息”。'
      },
      {
        id: 'decision',
        short: '决策',
        title: '让结论能指导行动，也能承认未知',
        question: '投诉点预测值接近行动阈值，且样品基质与校准集不同。报告应该怎样写？',
        options: [
          { id: 'number', label: '只给一个预测浓度，并直接宣布“达标”或“不达标”', detail: '一个数字掩盖了适用域之外的风险，也没有说明下一步要做什么。', correct: false },
          { id: 'conditional', label: '报告预测值、证据和不确定性；标记域外风险；建议补充确证测量或加密采样', detail: '把模型结论变成可审查、可行动的判断。', correct: true }
        ],
        explanation: '分析系统不仅要会接受或拒绝，还必须在证据不足时会说“需要补充测量”。'
      }
    ];

    function choice(stage) {
      return stages.filter(function (item) { return item.id === stage; })[0].options.filter(function (item) {
        return item.id === state.choices[stage];
      })[0];
    }

    function stageMarkup(stage, index) {
      var selected = choice(stage.id);
      var options = stage.options.map(function (option) {
        var active = state.choices[stage.id] === option.id;
        var status = state.submitted && active ? (option.correct ? ' is-correct' : ' is-incorrect') : '';
        return '<button type="button" class="lab-option' + (active ? ' is-selected' : '') + status + '" '
          + 'data-action="ch01-choice" data-stage="' + stage.id + '" data-value="' + option.id + '" '
          + 'aria-pressed="' + (active ? 'true' : 'false') + '">'
          + '<span class="lab-option-letter">' + String.fromCharCode(65 + stage.options.indexOf(option)) + '</span>'
          + '<span><strong>' + option.label + '</strong><small>' + option.detail + '</small></span></button>';
      }).join('');
      var result = '';
      if (state.submitted && selected) {
        result = feedbackBox(selected.correct ? 'success' : 'warning', selected.correct ? '这一步站得住脚' : '这一步会让结论失去支撑', stage.explanation);
      }
      return '<article class="lab-stage"><div class="lab-stage-number">' + (index + 1) + '</div><div class="lab-stage-content">'
        + '<p class="lab-stage-kicker">' + stage.short + '</p><h4>' + stage.title + '</h4><p>' + stage.question + '</p>'
        + '<div class="lab-option-grid">' + options + '</div>' + result + '</div></article>';
    }

    function matchMarkup() {
      var prompts = [
        { id: 'turbidity', label: '雨后浑浊度升高，不同采样点差别很大', answer: 'sample' },
        { id: 'drift', label: '质量控制样峰位整批向高波数移动', answer: 'measure' },
        { id: 'background', label: '未知样出现强荧光背景，目标峰几乎被覆盖', answer: 'signal' },
        { id: 'outside', label: '样品颜色与训练集完全不同，模型仍给出高置信度', answer: 'decision' }
      ];
      return prompts.map(function (item) {
        var selected = state.matches[item.id] || '';
        var checked = state.matchChecked;
        var correct = selected === item.answer;
        return '<div class="lab-match-row"><p>' + item.label + '</p><div class="lab-select-wrap"><label class="sr-only" for="ch01-' + item.id + '">选择问题先出现在哪一环</label>'
          + '<select id="ch01-' + item.id + '" data-action="ch01-match" data-id="' + item.id + '" class="' + (checked ? (correct ? ' is-correct' : ' is-incorrect') : '') + '">'
          + '<option value="">请选择</option><option value="sample"' + (selected === 'sample' ? ' selected' : '') + '>样品</option>'
          + '<option value="measure"' + (selected === 'measure' ? ' selected' : '') + '>测量</option>'
          + '<option value="signal"' + (selected === 'signal' ? ' selected' : '') + '>信号</option>'
          + '<option value="decision"' + (selected === 'decision' ? ' selected' : '') + '>模型 / 决策</option></select></div></div>';
      }).join('');
    }

    function draw() {
      var selectedCount = countSelected(state.choices);
      var correctCount = stages.filter(function (stage) {
        var selected = choice(stage.id);
        return selected && selected.correct;
      }).length;
      var closure = state.submitted
        ? feedbackBox(correctCount === 4 ? 'success' : 'warning', correctCount === 4 ? '你已形成可辩护的测量闭环' : '闭环仍有断点', correctCount === 4
          ? '你没有把 AI 当作捷径，而是把它放在代表性样品、稳定测量、可解释信号和条件化决策之间。下一步才值得讨论用什么模型。'
          : '请回看标红步骤：后续算法无法可靠弥补采样、校准或信号归因中留下的缺口。')
        : '';
      var matchResult = '';
      if (state.matchChecked) {
        var matchTotal = 4;
        var matchScore = ['turbidity', 'drift', 'background', 'outside'].filter(function (id) {
          var answers = { turbidity: 'sample', drift: 'measure', background: 'signal', outside: 'decision' };
          return state.matches[id] === answers[id];
        }).length;
        matchResult = feedbackBox(matchScore === matchTotal ? 'success' : 'warning', '归因检查：' + matchScore + ' / ' + matchTotal,
          matchScore === matchTotal ? '很好。复杂问题常跨越多个环节，但首先把失效位置说清，才能避免用“换一个算法”掩盖测量问题。' : '提示：空间异质性优先追溯到样品；峰位整体漂移优先检查测量坐标；背景属于信号问题；训练集之外的样品属于模型与决策边界。');
      }
      root.innerHTML = '<section class="lab-shell lab-shell--ch01" aria-labelledby="ch01-lab-title">'
        + '<header class="lab-header"><div><p class="lab-eyebrow">互动案例 · 约 12 分钟 · 浏览器本地保存进度</p><h3 id="ch01-lab-title">任务一：雨后河流异味，今晚能否发布风险提示？</h3>'
        + '<p>你是应急检测小组的分析负责人。请在发布建议前，为每个环节选择一条能被复核的证据路线。</p></div>'
        + '<div class="lab-progress" aria-label="已完成 ' + selectedCount + ' / 4 个测量决策">' + progressDots(selectedCount, 4) + '<span>' + selectedCount + ' / 4</span></div></header>'
        + '<div class="lab-brief"><strong>现场简报</strong><ul><li>雨后 6 小时，两个取水点出现藻腥味投诉。</li><li>目标并未完全确定；初筛光谱有弱峰，也有明显基质背景。</li><li>监管方今晚需要的不是“一个漂亮分数”，而是一份可追溯的行动建议。</li></ul></div>'
        + '<div class="lab-stage-list">' + stages.map(stageMarkup).join('') + '</div>'
        + '<div class="lab-actions"><button type="button" class="lab-primary" data-action="ch01-submit" ' + (selectedCount === 4 ? '' : 'disabled') + '>形成并审查测量闭环</button>'
        + '<button type="button" class="lab-secondary" data-action="ch01-reset">重置本题</button></div>' + closure
        + '<section class="lab-transfer"><div><p class="lab-eyebrow">迁移检查</p><h4>把失效信号放回它最先出现的位置</h4><p>同一问题可能影响后续多个环节；这里请先指出最早应被处理的位置。</p></div>'
        + '<div class="lab-match-list">' + matchMarkup() + '</div><div class="lab-actions"><button type="button" class="lab-secondary" data-action="ch01-check-match">检查归因</button></div>' + matchResult + '</section>'
        + '<aside class="lab-note"><strong>带走的原则：</strong>可信化学信息不是模型分数的同义词，而是代表性样品、稳定测量、高质量信号、适当模型和可行动解释共同构成的证据链。</aside>'
        + '</section>';
    }

    root.onclick = function (event) {
      var button = event.target.closest('[data-action]');
      if (!button || !root.contains(button)) return;
      var action = button.getAttribute('data-action');
      if (action === 'ch01-choice') {
        state.choices[button.getAttribute('data-stage')] = button.getAttribute('data-value');
        state.submitted = false;
        saveState('ch01-measurement-loop', state);
        draw();
      } else if (action === 'ch01-submit') {
        state.submitted = true;
        saveState('ch01-measurement-loop', state);
        draw();
      } else if (action === 'ch01-reset') {
        clearState('ch01-measurement-loop');
        state = Object.assign({}, initial);
        draw();
      } else if (action === 'ch01-check-match') {
        state.matchChecked = true;
        saveState('ch01-measurement-loop', state);
        draw();
      }
    };
    root.onchange = function (event) {
      var target = event.target;
      if (target && target.getAttribute('data-action') === 'ch01-match') {
        state.matches[target.getAttribute('data-id')] = target.value;
        state.matchChecked = false;
        saveState('ch01-measurement-loop', state);
        draw();
      }
    };
    draw();
  }

  function gaussian(x, center, width, height) {
    return height * Math.exp(-Math.pow((x - center) / width, 2));
  }

  function movingAverage(values, radius) {
    return values.map(function (_, index) {
      var start = Math.max(0, index - radius);
      var end = Math.min(values.length - 1, index + radius);
      var sum = 0;
      for (var point = start; point <= end; point += 1) sum += values[point];
      return sum / (end - start + 1);
    });
  }

  function spectrum(mode) {
    var points = [];
    for (var index = 0; index <= 72; index += 1) {
      var x = 400 + index * 5;
      var baseline = 0.22 + 0.00115 * (x - 400) + 0.0000011 * Math.pow(x - 590, 2);
      var peak = gaussian(x, 515, 22, 0.72) + gaussian(x, 645, 34, 1.05);
      var noise = 0.045 * Math.sin(index * 2.25) + 0.025 * Math.sin(index * 5.8);
      points.push({ x: x, y: baseline + peak + noise });
    }
    if (mode === 'baseline' || mode === 'smooth' || mode === 'normalised') {
      points = points.map(function (point) {
        var correction = 0.22 + 0.00115 * (point.x - 400) + 0.0000011 * Math.pow(point.x - 590, 2);
        return { x: point.x, y: point.y - correction };
      });
    }
    if (mode === 'smooth' || mode === 'normalised') {
      var smoothed = movingAverage(points.map(function (point) { return point.y; }), 2);
      points = points.map(function (point, index) { return { x: point.x, y: smoothed[index] }; });
    }
    if (mode === 'normalised') {
      var maximum = Math.max.apply(null, points.map(function (point) { return point.y; }));
      points = points.map(function (point) { return { x: point.x, y: point.y / maximum }; });
    }
    return points;
  }

  function plotSpectrum(mode) {
    var data = spectrum(mode);
    var width = 650;
    var height = 230;
    var pad = { left: 46, right: 18, top: 18, bottom: 34 };
    var values = data.map(function (point) { return point.y; });
    var min = Math.min.apply(null, values);
    var max = Math.max.apply(null, values);
    var range = max - min || 1;
    var path = data.map(function (point, index) {
      var x = pad.left + index * (width - pad.left - pad.right) / (data.length - 1);
      var y = height - pad.bottom - (point.y - min) / range * (height - pad.top - pad.bottom);
      return (index === 0 ? 'M' : 'L') + x.toFixed(1) + ' ' + y.toFixed(1);
    }).join(' ');
    var grid = [0.2, 0.5, 0.8].map(function (ratio) {
      var y = pad.top + ratio * (height - pad.top - pad.bottom);
      return '<line x1="' + pad.left + '" x2="' + (width - pad.right) + '" y1="' + y.toFixed(1) + '" y2="' + y.toFixed(1) + '" class="lab-gridline" />';
    }).join('');
    return '<svg class="lab-spectrum" viewBox="0 0 ' + width + ' ' + height + '" role="img" aria-label="' + ({ raw: '原始光谱，带有基线和噪声', baseline: '基线校正后的光谱', smooth: '基线校正并平滑后的光谱', normalised: '归一化后的光谱' }[mode]) + '">'
      + '<rect width="' + width + '" height="' + height + '" rx="10" class="lab-plot-bg" />' + grid
      + '<path d="' + path + '" class="lab-spectrum-line lab-spectrum-line--' + mode + '" />'
      + '<text x="' + pad.left + '" y="' + (height - 10) + '" class="lab-axis-text">400</text><text x="' + (width / 2 - 15) + '" y="' + (height - 10) + '" class="lab-axis-text">波长 / nm</text><text x="' + (width - 40) + '" y="' + (height - 10) + '" class="lab-axis-text">760</text>'
      + '<text x="14" y="24" class="lab-axis-text">强度</text></svg>';
  }

  function renderChapterTwo(root) {
    var initial = { held: {}, metadata: {}, mode: 'raw', split: '', normalise: '', checked: false };
    var state = readState('ch02-data-clinic', initial);
    var holdRecords = [
      { id: 'axis', name: 'Q-021', issue: '只有强度数组，缺失波长坐标与单位', correct: true },
      { id: 'saturation', name: 'Q-034', issue: '检测器饱和标记为 true，峰顶被削平', correct: true },
      { id: 'repeat', name: 'Q-043', issue: '完整元数据的技术重复，两个峰高度略有差异', correct: false },
      { id: 'normal', name: 'Q-052', issue: '样品、坐标、方法、批次和质控记录完整', correct: false }
    ];
    var metadata = [
      { id: 'identity', label: '样品 ID 与独立取样单位', correct: true },
      { id: 'axis', label: '坐标轴、单位与网格信息', correct: true },
      { id: 'instrument', label: '仪器、方法参数与校准状态', correct: true },
      { id: 'batch', label: '采集时间、批次与质量控制记录', correct: true },
      { id: 'reference', label: '前处理、参照方法与标签不确定度', correct: true },
      { id: 'folder', label: '文件夹颜色和电脑用户名', correct: false }
    ];
    var modes = [
      { id: 'raw', label: '原始信号', metric: '基线漂移明显；峰 / 噪声估计约 5.1', explanation: '此图告诉你“仪器看到了什么”；它不是直接送入模型的理由。' },
      { id: 'baseline', label: '校正基线', metric: '宽背景被移除；需检查宽峰是否被一并扣除', explanation: '校正假设缓慢变化主要来自背景。这个假设必须与空白、标准或机制相符。' },
      { id: 'smooth', label: '再做平滑', metric: '随机起伏变小；峰高和峰宽必须重新核验', explanation: '平滑交换的是方差与偏差。视觉更顺眼，不等于定量更准确。' },
      { id: 'normalised', label: '向量归一化', metric: '尺度信息被统一；浓度信息可能同时被删除', explanation: '归一化适用于重视相对谱形的任务；本案目标是浓度，不能把它当默认步骤。' }
    ];

    function hasCorrectSet(items, values) {
      return items.every(function (item) { return Boolean(values[item.id]) === item.correct; });
    }

    function heldMarkup(record) {
      var active = Boolean(state.held[record.id]);
      var status = state.checked ? (active === record.correct ? ' is-correct' : ' is-incorrect') : '';
      return '<button type="button" class="lab-record' + (active ? ' is-selected' : '') + status + '" data-action="ch02-hold" data-id="' + record.id + '" aria-pressed="' + active + '">'
        + '<span class="lab-checkbox" aria-hidden="true">' + (active ? '✓' : '') + '</span><span><strong>' + record.name + '</strong><small>' + record.issue + '</small></span></button>';
    }

    function metadataMarkup(item) {
      var active = Boolean(state.metadata[item.id]);
      var status = state.checked ? (active === item.correct ? ' is-correct' : ' is-incorrect') : '';
      return '<button type="button" class="lab-chip' + (active ? ' is-selected' : '') + status + '" data-action="ch02-meta" data-id="' + item.id + '" aria-pressed="' + active + '">'
        + '<span aria-hidden="true">' + (active ? '✓' : '+') + '</span> ' + item.label + '</button>';
    }

    function draw() {
      var metaScore = metadata.filter(function (item) { return Boolean(state.metadata[item.id]) === item.correct; }).length;
      var holdScore = holdRecords.filter(function (item) { return Boolean(state.held[item.id]) === item.correct; }).length;
      var splitCorrect = state.split === 'grouped';
      var normCorrect = state.normalise === 'verify';
      var readyCount = (hasCorrectSet(holdRecords, state.held) ? 1 : 0) + (hasCorrectSet(metadata, state.metadata) ? 1 : 0) + (splitCorrect ? 1 : 0) + (normCorrect ? 1 : 0);
      var mode = modes.filter(function (item) { return item.id === state.mode; })[0];
      var assessment = '';
      if (state.checked) {
        assessment = feedbackBox(readyCount === 4 ? 'success' : 'warning', readyCount === 4 ? '这批数据可以进入“受控的”建模流程' : '先修复数据对象，再训练模型', readyCount === 4
          ? '你保留了数据谱系：坏记录被隔离，元数据定义了边界，数据划分模拟未来使用场景，预处理没有被当成默认美化。接下来才能在训练集内拟合处理参数。'
          : '当前得分 ' + readyCount + ' / 4。模型训练之前，先处理未闭合的数据边界；否则再高的交叉验证分数也可能只是批次或处理流程的记忆。');
      }
      root.innerHTML = '<section class="lab-shell lab-shell--ch02" aria-labelledby="ch02-lab-title">'
        + '<header class="lab-header"><div><p class="lab-eyebrow">互动案例 · 约 15 分钟 · 浏览器本地保存进度</p><h3 id="ch02-lab-title">任务二：数据急诊室——这批光谱能进入模型吗？</h3>'
        + '<p>你接手了一批用于水样浓度建模的光谱文件。目标不是“清洗得好看”，而是判断哪些数据对象仍然可信。</p></div>'
        + '<div class="lab-progress" aria-label="已完成 ' + readyCount + ' / 4 项质量关卡">' + progressDots(readyCount, 4) + '<span>' + readyCount + ' / 4</span></div></header>'
        + '<div class="lab-brief"><strong>批次背景</strong><ul><li>数据来自两台仪器、三个采样日；目标是预测水样中某指标的浓度。</li><li>后续模型会部署到下一周的新样品，而不是只解释今天这批文件。</li><li>每一个“处理”选择，都在改变可被模型看见的化学信息。</li></ul></div>'
        + '<article class="lab-stage"><div class="lab-stage-number">1</div><div class="lab-stage-content"><p class="lab-stage-kicker">质量门 1</p><h4>先隔离无法被正确解释的记录</h4><p>请选择必须在建模前<strong>暂缓</strong>的文件。暂缓不等于删除：它意味着先回查、补测或补齐元数据。</p><div class="lab-record-grid">' + holdRecords.map(heldMarkup).join('') + '</div>'
        + (state.checked ? feedbackBox(holdScore === 4 ? 'success' : 'warning', '记录判定：' + holdScore + ' / 4', '缺少坐标轴时，强度没有物理位置；饱和时，峰顶已丢失。技术重复则是估计误差的重要证据，不应因“不完全相同”而直接删除。') : '') + '</div></article>'
        + '<article class="lab-stage"><div class="lab-stage-number">2</div><div class="lab-stage-content"><p class="lab-stage-kicker">质量门 2</p><h4>把数值放回测量语境</h4><p>哪些字段必须伴随光谱进入可建模数据对象？</p><div class="lab-chip-grid">' + metadata.map(metadataMarkup).join('') + '</div>'
        + (state.checked ? feedbackBox(metaScore === metadata.length ? 'success' : 'warning', '元数据选择：' + metaScore + ' / ' + metadata.length, '化学数据至少由数值、坐标、样品与方法元数据、误差和处理历史共同构成。电脑用户名不能界定化学含义。') : '') + '</div></article>'
        + '<article class="lab-stage"><div class="lab-stage-number">3</div><div class="lab-stage-content"><p class="lab-stage-kicker">质量门 3</p><h4>观察预处理怎样改变信号</h4><p>切换处理步骤，观察图形与解释同时发生的变化。</p><div class="lab-mode-tabs" role="tablist" aria-label="光谱处理步骤">' + modes.map(function (item) {
          return '<button type="button" role="tab" aria-selected="' + (state.mode === item.id) + '" class="lab-tab' + (state.mode === item.id ? ' is-selected' : '') + '" data-action="ch02-mode" data-id="' + item.id + '">' + item.label + '</button>';
        }).join('') + '</div><div class="lab-plot-wrap">' + plotSpectrum(state.mode) + '<div class="lab-plot-note"><strong>' + mode.metric + '</strong><p>' + mode.explanation + '</p></div></div>'
        + '<section class="lab-inline-question" aria-label="归一化判断"><h5>本案要预测<strong>绝对浓度</strong>。向量归一化能否直接作为默认步骤？</h5><div class="lab-option-grid"><button type="button" class="lab-option' + (state.normalise === 'always' ? ' is-selected' : '') + '" data-action="ch02-normalise" data-id="always" aria-pressed="' + (state.normalise === 'always') + '"><span class="lab-option-letter">A</span><span><strong>可以，曲线越统一越适合建模</strong><small>把视觉整齐误当成了量值可靠。</small></span></button><button type="button" class="lab-option' + (state.normalise === 'verify' ? ' is-selected' : '') + '" data-action="ch02-normalise" data-id="verify" aria-pressed="' + (state.normalise === 'verify') + '"><span class="lab-option-letter">B</span><span><strong>不能默认使用；先判断整体强度是否携带浓度信息，并在独立样品上验证</strong><small>预处理必须服从任务目标与验证证据。</small></span></button></div></section>'
        + (state.checked && state.normalise ? feedbackBox(normCorrect ? 'success' : 'warning', normCorrect ? '预处理边界判断正确' : '这里混淆了“整齐”与“有用”', '归一化会主动移除尺度差异。对于相对组成可能有益；对于绝对浓度，尺度恰可能是主要信息。') : '') + '</div></article>'
        + '<article class="lab-stage"><div class="lab-stage-number">4</div><div class="lab-stage-content"><p class="lab-stage-kicker">质量门 4</p><h4>让验证模拟未来，而不是记住今天</h4><p>数据来自三天、两台仪器。哪一种划分最能检验下周新样品的表现？</p><div class="lab-option-grid"><button type="button" class="lab-option' + (state.split === 'random' ? ' is-selected' : '') + (state.checked && state.split === 'random' ? ' is-incorrect' : '') + '" data-action="ch02-split" data-id="random" aria-pressed="' + (state.split === 'random') + '"><span class="lab-option-letter">A</span><span><strong>把所有扫描随机打散</strong><small>同一样品、同一批次的相似记录可能同时进入训练与测试。</small></span></button><button type="button" class="lab-option' + (state.split === 'grouped' ? ' is-selected' : '') + (state.checked && state.split === 'grouped' ? ' is-correct' : '') + '" data-action="ch02-split" data-id="grouped" aria-pressed="' + (state.split === 'grouped') + '"><span class="lab-option-letter">B</span><span><strong>按独立样品、采样日或仪器批次分组保留测试集</strong><small>让测试样品更接近真正部署时尚未见过的条件。</small></span></button></div>'
        + (state.checked && state.split ? feedbackBox(splitCorrect ? 'success' : 'warning', splitCorrect ? '划分方式符合任务边界' : '随机划分可能制造数据泄露', '测试集不应只是训练样本的近邻副本。独立单位必须由未来实际要预测的对象决定。') : '') + '</div></article>'
        + '<div class="lab-actions"><button type="button" class="lab-primary" data-action="ch02-check">执行数据入库审计</button><button type="button" class="lab-secondary" data-action="ch02-reset">重置本题</button></div>' + assessment
        + '<aside class="lab-note"><strong>带走的原则：</strong>数据清洗不是把表格变整齐，而是让每一次变换都能回答“它基于什么测量假设、可能损失什么信息、是否只在训练数据内学得”。</aside></section>';
    }

    root.onclick = function (event) {
      var button = event.target.closest('[data-action]');
      if (!button || !root.contains(button)) return;
      var action = button.getAttribute('data-action');
      var id = button.getAttribute('data-id');
      if (action === 'ch02-hold') state.held[id] = !state.held[id];
      if (action === 'ch02-meta') state.metadata[id] = !state.metadata[id];
      if (action === 'ch02-mode') state.mode = id;
      if (action === 'ch02-normalise') state.normalise = id;
      if (action === 'ch02-split') state.split = id;
      if (action === 'ch02-check') state.checked = true;
      if (action === 'ch02-reset') {
        clearState('ch02-data-clinic');
        state = Object.assign({}, initial);
      }
      saveState('ch02-data-clinic', state);
      draw();
    };
    draw();
  }

  function renderChapterFourteen(root) {
    var storageKey = 'ch14-calibration-transfer';
    var initial = { hardware: false, difference: '', method: '', validation: '', checked: false };
    var state = readState(storageKey, initial);

    var differences = [
      { id: 'additive', label: '全局加性 / 乘性差异', detail: '峰位基本重合，主要是强度与截距整体偏移。' },
      { id: 'smooth', label: '全局平滑谱响应差异', detail: '峰位重合、峰宽相近，增益随波长缓慢变化。' },
      { id: 'local', label: '局部峰形 / 波长依赖差异', detail: '某一波段的峰宽或峰高发生明显改变。' }
    ];
    var methods = [
      { id: 'direct', label: '直接套用主仪器模型', detail: '不做任何校正，把 B 的光谱直接送进 A 的模型。' },
      { id: 'slope', label: '斜率—偏差校正（slope/bias）', detail: '只用传递样品修正预测值的尺度与截距。' },
      { id: 'ds', label: '全局 DS（直接标准化）', detail: '在全部波长上学习一条主从映射。' },
      { id: 'pds', label: 'PDS（分段直接标准化）', detail: '在每个局部波长窗口分别学习映射。' }
    ];
    var validations = [
      { id: 'transfer', label: '参与迁移拟合的传递样品', detail: '这些样品已经用于估计 DS / PDS 的映射参数。' },
      { id: 'independent', label: '未参与训练与迁移的独立目标域样品', detail: '更接近下周部署到 B 上的真实条件。' }
    ];

    var answer = { difference: 'smooth', method: 'ds', validation: 'independent' };
    var acceptableMethod = { direct: false, slope: false, ds: true, pds: true };

    function pick(items, id) {
      return items.filter(function (item) { return item.id === id; })[0] || items[0];
    }

    function labelOf(items, id) {
      return id ? pick(items, id).label : '未选择';
    }

    function spectra(kind) {
      var master = [];
      var slave = [];
      for (var index = 0; index <= 200; index += 1) {
        var x = 1100 + index * 6.5;
        var m = gaussian(x, 1450, 65, 0.95) + gaussian(x, 1900, 95, 0.68) + gaussian(x, 2180, 120, 0.42);
        var s;
        if (kind === 'additive') {
          s = m * 1.10 + 0.06;
        } else if (kind === 'local') {
          s = m * 1.02 + gaussian(x, 1450, 105, 0.24) - gaussian(x, 1850, 52, 0.20);
        } else {
          s = m * (0.90 + 0.14 * Math.exp(-0.5 * Math.pow((x - 1950) / 420, 2)));
        }
        master.push({ x: x, y: m });
        slave.push({ x: x, y: s });
      }
      return { master: master, slave: slave };
    }

    function plot(selected) {
      var measured = spectra('smooth');
      var hypothesis = selected && selected !== 'smooth' ? spectra(selected).slave : null;
      var width = 650;
      var height = 230;
      var pad = { left: 46, right: 18, top: 34, bottom: 34 };
      var values = measured.master.concat(measured.slave).concat(hypothesis || []).map(function (point) { return point.y; });
      var min = Math.min.apply(null, values);
      var max = Math.max.apply(null, values);
      var range = max - min || 1;
      var innerHeight = height - pad.top - pad.bottom;

      function pathOf(points, color, dashed) {
        var path = points.map(function (point, index) {
          var px = pad.left + index * (width - pad.left - pad.right) / (points.length - 1);
          var py = height - pad.bottom - (point.y - min) / range * innerHeight;
          return (index === 0 ? 'M' : 'L') + px.toFixed(1) + ' ' + py.toFixed(1);
        }).join(' ');
        return '<path d="' + path + '" class="lab-spectrum-line" stroke="' + color + '" stroke-width="2.6"'
          + (dashed ? ' stroke-dasharray="5 4" stroke-opacity="0.8"' : '') + ' />';
      }

      var grid = [0.2, 0.5, 0.8].map(function (ratio) {
        var y = pad.top + ratio * innerHeight;
        return '<line x1="' + pad.left + '" x2="' + (width - pad.right) + '" y1="' + y.toFixed(1) + '" y2="' + y.toFixed(1) + '" class="lab-gridline" />';
      }).join('');

      var legend = '<line x1="196" x2="218" y1="16" y2="16" stroke="#0a76aa" stroke-width="2.6" /><text x="224" y="20" class="lab-axis-text">主仪器 A</text>'
        + '<line x1="316" x2="338" y1="16" y2="16" stroke="#d56643" stroke-width="2.6" /><text x="344" y="20" class="lab-axis-text">实测 B</text>';
      if (hypothesis) {
        legend += '<line x1="416" x2="438" y1="16" y2="16" stroke="#7b8794" stroke-width="2.6" stroke-dasharray="5 4" /><text x="444" y="20" class="lab-axis-text">假设谱形</text>';
      }

      var caption = '主仪器 A 与 42 个传递样品实测 B 的近红外光谱对比'
        + (hypothesis ? '，虚线为假设' + pick(differences, selected).label + '时 B 应有的形状' : '')
        + '；峰位重合、峰宽相近，B 在 1900 nm 附近增益偏高。';

      return '<svg class="lab-spectrum" viewBox="0 0 ' + width + ' ' + height + '" role="img" aria-label="' + caption + '">'
        + '<rect width="' + width + '" height="' + height + '" rx="10" class="lab-plot-bg" />' + grid + legend
        + pathOf(measured.master, '#0a76aa', false)
        + pathOf(measured.slave, '#d56643', false)
        + (hypothesis ? pathOf(hypothesis, '#7b8794', true) : '')
        + '<text x="' + pad.left + '" y="' + (height - 10) + '" class="lab-axis-text">1100</text>'
        + '<text x="' + (width / 2 - 26) + '" y="' + (height - 10) + '" class="lab-axis-text">波长 / nm</text>'
        + '<text x="' + (width - 58) + '" y="' + (height - 10) + '" class="lab-axis-text">2400</text>'
        + '<text x="12" y="' + (pad.top + 8) + '" class="lab-axis-text">响应</text></svg>';
    }

    function optionMarkup(items, selectedId, action, statusOf) {
      return items.map(function (item, index) {
        var active = item.id === selectedId;
        var status = statusOf ? statusOf(item) : '';
        return '<button type="button" class="lab-option' + (active ? ' is-selected' : '') + status + '" '
          + 'data-action="' + action + '" data-value="' + item.id + '" aria-pressed="' + (active ? 'true' : 'false') + '">'
          + '<span class="lab-option-letter">' + String.fromCharCode(65 + index) + '</span>'
          + '<span><strong>' + item.label + '</strong><small>' + item.detail + '</small></span></button>';
      }).join('');
    }

    function differenceStatus(item) {
      if (!state.checked) return '';
      if (item.id === answer.difference) return ' is-correct';
      return state.difference === item.id ? ' is-incorrect' : '';
    }

    function methodStatus(item) {
      if (!state.checked) return '';
      if (item.id === answer.method) return ' is-correct';
      if (state.method === item.id) return acceptableMethod[item.id] ? '' : ' is-incorrect';
      return '';
    }

    function validationStatus(item) {
      if (!state.checked) return '';
      if (item.id === answer.validation) return ' is-correct';
      return state.validation === item.id ? ' is-incorrect' : '';
    }

    function draw() {
      var gates = [
        Boolean(state.hardware),
        state.difference === answer.difference,
        state.method === answer.method,
        state.validation === answer.validation
      ];
      var readyCount = gates.filter(function (pass) { return pass; }).length;
      var allPass = readyCount === 4;

      var differenceFeedback = state.checked
        ? feedbackBox(gates[1] ? 'success' : 'warning', gates[1] ? '差异结构判断正确' : '先把差异结构看清，再谈迁移方法', gates[1]
          ? '峰位重合、峰宽相近、增益随波长缓慢变化——这是典型的全局平滑谱响应差异，对应“整条谱的乘法型漂移”，而不是个别峰的形变。'
          : '本案例中 B 的峰位与峰宽基本不变，只有增益沿波长缓慢变化。判成加性差异会漏掉波长依赖；判成局部差异，会把 PDS 用在没有局部形变的数据上。')
        : '';

      var methodFeedback = state.checked
        ? feedbackBox(gates[2] ? 'success' : 'warning', gates[2] ? '迁移方法与差异结构一致' : '这个方法解决不了当前的差异', gates[2]
          ? 'DS 用少量传递样品在全部波长上学习一条映射，正好对应平滑的全局增益差异；若差异确属局部、且传递样品足够多，才轮到 PDS。'
          : acceptableMethod[state.method]
            ? 'PDS 适用于局部峰形 / 波长依赖差异；本案例是全局平滑差异，因此不应得到完整通过。'
            : state.method
              ? '斜率—偏差只修正预测值的尺度与截距，改变不了“不同波长被不同增益放大”这一事实；直接套用则把仪器差异整体算进浓度。'
              : '还没有选择迁移方法。本案例的差异落在整条光谱的增益上，需要一条在全部波长上学习的映射。')
        : '';

      var assessment = state.checked
        ? feedbackBox(allPass ? 'success' : 'warning', allPass ? '这条迁移链可以被审查' : '迁移链仍有断点（' + readyCount + ' / 4）', allPass
          ? '硬件量值链先闭合，差异结构被正确识别，方法与结构匹配，最终误差报告在未参与拟合的独立目标域样品上。这四步顺序不能互换：任何一步跳过，后面的误差数字都不再代表 B 上的真实性能。'
          : '请回看标红环节。最常见的错误是先用 DS/PDS 把曲线“对齐”，再拿传递样品上的误差当最终结果——那是拟合残差，不是迁移性能。')
        : '';

      root.innerHTML = '<section class="lab-shell lab-shell--ch14" aria-labelledby="ch14-lab-title">'
        + '<header class="lab-header"><div><p class="lab-eyebrow">互动案例 · 约 15 分钟 · 浏览器本地保存进度</p>'
        + '<h3 id="ch14-lab-title">任务十四：主仪器模型能直接部署到从仪器吗？</h3>'
        + '<p>你是负责方法转移的分析人员。模型建在 A 上，下周要在 B 上报告 70 个新样品的浓度。请依次决定：量值链、差异结构、迁移方法、验证集合。</p></div>'
        + '<div class="lab-progress" aria-label="已完成 ' + readyCount + ' / 4 个迁移决策">' + progressDots(readyCount, 4) + '<span>' + readyCount + ' / 4</span></div></header>'
        + '<div class="lab-brief"><strong>现场简报</strong><ul>'
        + '<li>A、B 为同型号近红外光谱仪，不同批次；A 上已有 PLS 浓度模型与完整验证记录。</li>'
        + '<li>在 B 上重测了 42 个传递样品：峰位基本重合，峰宽变化不明显，B 的响应在 1900 nm 附近整体偏高，且随波长缓慢变化。</li>'
        + '<li>现场只允许再测少量样品；监管方要的是 B 上“未来样品”的误差，而不是这 42 个样品拟合得多好。</li>'
        + '</ul></div>'

        + '<article class="lab-stage"><div class="lab-stage-number">1</div><div class="lab-stage-content">'
        + '<p class="lab-stage-kicker">前提</p><h4>先闭合硬件与量值链</h4>'
        + '<p>在讨论任何数学迁移之前，B 的波长、强度、分辨率与检测器响应是否已经可溯源？</p>'
        + '<div class="lab-chip-grid"><button type="button" class="lab-chip' + (state.hardware ? ' is-selected' : '') + (state.checked ? (state.hardware ? ' is-correct' : ' is-incorrect') : '') + '" '
        + 'data-action="ch14-hardware" aria-pressed="' + (state.hardware ? 'true' : 'false') + '"><span aria-hidden="true">' + (state.hardware ? '✓' : '+') + '</span> 已完成波长、强度、分辨率与检测器响应校准</button></div>'
        + (state.checked && !state.hardware ? feedbackBox('warning', '这一步不能用算法替代', 'DS / PDS 只能对齐“已经正确测量的光谱”。波长轴偏了或检测器饱和了，迁移函数会把仪器故障学成一个漂亮的映射。') : '')
        + '</div></article>'

        + '<article class="lab-stage"><div class="lab-stage-number">2</div><div class="lab-stage-content">'
        + '<p class="lab-stage-kicker">诊断</p><h4>主从差异更像哪一种？</h4>'
        + '<p>下图是 42 个传递样品的实测对比。选定一种描述后，灰色虚线会叠加该结构下 B 应有的形状，用来和实测曲线比对。</p>'
        + '<div class="lab-option-grid">' + optionMarkup(differences, state.difference, 'ch14-difference', differenceStatus) + '</div>'
        + '<div class="lab-plot-wrap">' + plot(state.difference) + '<div class="lab-plot-note"><strong>' + labelOf(differences, state.difference) + '</strong><p>'
        + (state.difference ? pick(differences, state.difference).detail + (state.difference === answer.difference ? '' : ' —— 请把它和实测橙线比对：峰位、峰宽是否真的变了？')
          : '还没有选择差异结构。先看橙线与蓝线的差别出现在哪里：整体高度、随波长的增益，还是某个峰的宽度。')
        + '</p></div></div>'
        + differenceFeedback
        + '</div></article>'

        + '<article class="lab-stage"><div class="lab-stage-number">3</div><div class="lab-stage-content">'
        + '<p class="lab-stage-kicker">方法</p><h4>选择迁移方式</h4>'
        + '<p>只有 42 个传递样品。你打算怎样把 A 的模型用到 B 上？</p>'
        + '<div class="lab-option-grid">' + optionMarkup(methods, state.method, 'ch14-method', methodStatus) + '</div>'
        + methodFeedback
        + '</div></article>'

        + '<article class="lab-stage"><div class="lab-stage-number">4</div><div class="lab-stage-content">'
        + '<p class="lab-stage-kicker">验证</p><h4>用哪个集合报告最终误差？</h4>'
        + '<p>RMSEP 写进报告之前，先决定它来自哪个集合。</p>'
        + '<div class="lab-option-grid">' + optionMarkup(validations, state.validation, 'ch14-validation', validationStatus) + '</div>'
        + (state.checked && state.validation === 'transfer' ? feedbackBox('warning', '传递样品不能充当独立测试集', '它们参与了映射参数（甚至斜率—偏差系数）的估计，残差里已经不含“没见过 B”的成分。必须另留未参与拟合的目标域样品。') : '')
        + '</div></article>'

        + '<div class="lab-actions"><button type="button" class="lab-primary" data-action="ch14-check">检查迁移方案</button>'
        + '<button type="button" class="lab-secondary" data-action="ch14-reset">重置本题</button></div>' + assessment
        + '<aside class="lab-note"><strong>带走的原则：</strong>迁移不是“把曲线对齐”。顺序是硬件量值链 → 差异结构 → 迁移方法 → 独立目标域验证；报告的误差只能来自最后一步，而且必须排除参与拟合的样品。</aside>'
        + '</section>';

      root.setAttribute('data-ch14-record', '硬件=' + (state.hardware ? '已校准' : '未校准')
        + '；差异=' + labelOf(differences, state.difference)
        + '；方法=' + labelOf(methods, state.method)
        + '；验证=' + labelOf(validations, state.validation));
    }

    root.onclick = function (event) {
      var button = event.target.closest('[data-action]');
      if (!button || !root.contains(button)) return;
      var action = button.getAttribute('data-action');
      var value = button.getAttribute('data-value');
      if (action === 'ch14-hardware') {
        state.hardware = !state.hardware;
        state.checked = false;
      } else if (action === 'ch14-difference') {
        state.difference = value;
        state.checked = false;
      } else if (action === 'ch14-method') {
        state.method = value;
        state.checked = false;
      } else if (action === 'ch14-validation') {
        state.validation = value;
        state.checked = false;
      } else if (action === 'ch14-check') {
        state.checked = true;
      } else if (action === 'ch14-reset') {
        clearState(storageKey);
        state = Object.assign({}, initial);
        saveState(storageKey, state);
        draw();
        return;
      } else {
        return;
      }
      saveState(storageKey, state);
      draw();
    };
    draw();
  }

  function mountLabs() {
    var labs = document.querySelectorAll('.interactive-lab[data-lab]');
    labs.forEach(function (root) {
      if (root.getAttribute('data-mounted') === 'true') return;
      root.setAttribute('data-mounted', 'true');
      if (root.getAttribute('data-lab') === 'ch01-measurement-loop') renderChapterOne(root);
      if (root.getAttribute('data-lab') === 'ch02-data-clinic') renderChapterTwo(root);
      if (root.getAttribute('data-lab') === 'ch14-calibration-transfer') renderChapterFourteen(root);
    });
  }

  window.$docsify = window.$docsify || {};
  window.$docsify.plugins = (window.$docsify.plugins || []).concat(function (hook) {
    hook.doneEach(function () {
      window.requestAnimationFrame(mountLabs);
    });
    hook.mounted(function () {
      window.requestAnimationFrame(mountLabs);
    });
  });
  document.addEventListener('DOMContentLoaded', mountLabs);
}());

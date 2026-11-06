/*
 * 第7章：一个查询、两个键的注意力实验。
 * 固定手算教学值；不加载模型、不上传输入、不保存个人答案。
 * 独立 Docsify 插件，避免改变其他章节的互动逻辑。
 */
(function (global, factory) {
  'use strict';
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (global && global.document) {
    global.Ch07AttentionLab = api;
    api.install(global);
  }
}(typeof window !== 'undefined' ? window : globalThis, function () {
  'use strict';

  var nextId = 0;
  var defaults = { q: 1, k1: 0, k2: Math.log(3), v1: 2, v2: 6 };

  function computeAttentionRow(parameters) {
    var q = parameters.q;
    var keys = parameters.keys;
    var values = parameters.values;
    var mask = parameters.mask || [false, false];
    if (!Number.isFinite(q) || !Array.isArray(keys) || keys.length !== 2 ||
        !Array.isArray(values) || values.length !== 2 ||
        !Array.isArray(mask) || mask.length !== 2 ||
        !keys.every(Number.isFinite) || !values.every(Number.isFinite) ||
        !mask.every(function (v) { return typeof v === 'boolean'; })) {
      throw new TypeError('本例需要有限的标量q、两个键、两个值，以及两个布尔掩码。');
    }
    if (mask.every(Boolean)) throw new RangeError('每个查询至少应有一个可读取的键。');
    // d_k = 1，因此缩放因子 sqrt(d_k) = 1。
    var scores = keys.map(function (key) { return q * key; });
    if (!scores.every(Number.isFinite)) throw new RangeError('点积超出有限数值范围。');
    var maskedScores = scores.map(function (score, i) { return mask[i] ? -Infinity : score; });
    var maximum = Math.max.apply(null, maskedScores);
    var exponentials = maskedScores.map(function (score) { return Math.exp(score - maximum); });
    var denominator = exponentials[0] + exponentials[1];
    var weights = exponentials.map(function (value) { return value / denominator; });
    var contributions = values.map(function (value, i) { return value * weights[i]; });
    return {
      scores: scores,
      maskedScores: maskedScores,
      weights: weights,
      contributions: contributions,
      output: contributions[0] + contributions[1]
    };
  }

  function taskFeedback(task, access) {
    if (!task || !access) return {
      kind: 'incomplete', title: '先选定任务与读取范围',
      text: '信息可用范围由实际预测任务决定。请为所选任务选择一种读取方式。'
    };
    if (task === 'spectrum' && access === 'all') return {
      kind: 'correct', title: '完整输入在预测时已经可用',
      text: '整条光谱采集完成后分类，可以同时读取各谱段；谱段索引不等于未来时间。通常不需要因果掩码，补齐长度的空位置仍应屏蔽。'
    };
    if (task === 'forecast' && access === 'observed') return {
      kind: 'correct', title: '读取边界符合实时预测',
      text: '预测下一时刻的电镜状态时，只能读取当前及以前已取得的观测。训练时也须防止后续真实帧通过注意力进入该预测，否则评价可能高估部署表现。'
    };
    if (task === 'spectrum' && access === 'observed') return {
      kind: 'consider', title: '这是额外施加的读取限制',
      text: '完整光谱分类并不要求只读前缀。屏蔽后面的谱段可能丢掉已采集的伴峰信息；若要研究“只用部分谱段能否分类”，应把它明确为另一项任务并独立验证。'
    };
    if (task === 'forecast' && access === 'all') return {
      kind: 'risk', title: '后续真实帧在部署时尚不可用',
      text: '如果完整输入含当前预测时刻之后的真实观测，就使用了未来信息。应按可用时间设置因果读取边界。离线回看完整视频是另一个任务，不能把其结果当成实时预测性能。'
    };
    throw new RangeError('未知的任务或读取方式。');
  }

  function format(value) {
    if (value === -Infinity) return '−∞';
    return Math.abs(value) < 0.0000005 ? '0' : String(Number(value.toFixed(6)));
  }

  function addStyles(document) {
    if (document.getElementById('ch07-attention-lab-style')) return;
    var style = document.createElement('style');
    style.id = 'ch07-attention-lab-style';
    style.textContent = [
      '[data-lab="ch07-attention"] .ch07-attention{border:1px solid #cbd7df;border-radius:12px;padding:clamp(14px,3vw,24px);margin:24px 0;background:#f7fafb;color:#173042;overflow-wrap:anywhere;line-height:1.65}',
      '[data-lab="ch07-attention"] .ch07-attention *{box-sizing:border-box}',
      '[data-lab="ch07-attention"] .ch07-attention h3,[data-lab="ch07-attention"] .ch07-attention h4{margin:0 0 10px;color:#173042}',
      '[data-lab="ch07-attention"] .ch07-attention p{margin:8px 0 14px}',
      '[data-lab="ch07-attention"] .ch07-attention fieldset{min-width:0;margin:16px 0;padding:14px;border:1px solid #cbd7df;border-radius:8px}',
      '[data-lab="ch07-attention"] .ch07-attention legend{padding:0 6px;font-weight:700;max-width:100%;white-space:normal}',
      '[data-lab="ch07-attention"] .ch07-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}',
      '[data-lab="ch07-attention"] .ch07-control{display:flex;flex-direction:column;gap:5px;font-weight:600;min-width:0}',
      '[data-lab="ch07-attention"] .ch07-control small{font-weight:400;color:#435d6b}',
      '[data-lab="ch07-attention"] .ch07-control input{width:100%;min-width:0;min-height:42px;padding:8px;border:1px solid #7b929e;border-radius:5px;background:#fff;color:#173042;font:inherit}',
      '[data-lab="ch07-attention"] .ch07-control input[aria-invalid="true"]{border:2px solid #a43f29}',
      '[data-lab="ch07-attention"] .ch07-options{display:flex;flex-wrap:wrap;gap:10px 20px;margin:10px 0}',
      '[data-lab="ch07-attention"] .ch07-option{display:flex;align-items:flex-start;gap:8px;min-height:36px;cursor:pointer}',
      '[data-lab="ch07-attention"] .ch07-option input{margin-top:6px;flex:none;accent-color:#176879}',
      '[data-lab="ch07-attention"] .ch07-key-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;margin:14px 0}',
      '[data-lab="ch07-attention"] .ch07-key-card{background:#fff;border:1px solid #cbd7df;border-radius:8px;padding:14px;min-width:0}',
      '[data-lab="ch07-attention"] .ch07-key-card dl{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px 10px;margin:0}',
      '[data-lab="ch07-attention"] .ch07-key-card dt,[data-lab="ch07-attention"] .ch07-key-card dd{margin:0}',
      '[data-lab="ch07-attention"] .ch07-key-card dd{font-variant-numeric:tabular-nums;text-align:right}',
      '[data-lab="ch07-attention"] .ch07-weight-track{height:10px;background:#e5edf0;border-radius:5px;margin:10px 0 0;overflow:hidden}',
      '[data-lab="ch07-attention"] .ch07-weight-fill{height:100%;width:0;background:#197c8b}',
      '[data-lab="ch07-attention"] .ch07-key-card:nth-child(2) .ch07-weight-fill{background:#805ba5}',
      '[data-lab="ch07-attention"] .ch07-result{display:block;padding:12px 16px;border-left:4px solid #176879;background:#e4f1f3;font-weight:700;font-size:1.15em}',
      '[data-lab="ch07-attention"] .ch07-note{font-size:.93em;color:#435d6b}',
      '[data-lab="ch07-attention"] .ch07-feedback{margin:12px 0;padding:12px;border:1px solid #9eb9c1;border-radius:6px;background:#edf4f6}',
      '[data-lab="ch07-attention"] .ch07-feedback[data-kind="risk"],[data-lab="ch07-attention"] .ch07-error{border-color:#b0644d;background:#fff3ed}',
      '[data-lab="ch07-attention"] .ch07-feedback p{margin:5px 0 0}',
      '[data-lab="ch07-attention"] .ch07-actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:12px}',
      '[data-lab="ch07-attention"] .ch07-attention button{font:inherit;min-height:42px;padding:8px 14px;border:1px solid #176879;border-radius:6px;background:#176879;color:#fff;cursor:pointer;white-space:normal}',
      '[data-lab="ch07-attention"] .ch07-attention button.ch07-reset{background:#fff;color:#173042}',
      '[data-lab="ch07-attention"] .ch07-attention :focus-visible{outline:3px solid #a85c00;outline-offset:3px}',
      '[data-lab="ch07-attention"] .ch07-attention [hidden]{display:none!important}',
      '@media(max-width:640px){[data-lab="ch07-attention"] .ch07-grid,[data-lab="ch07-attention"] .ch07-key-grid{grid-template-columns:minmax(0,1fr)}[data-lab="ch07-attention"] .ch07-options{display:grid;grid-template-columns:minmax(0,1fr)}}'
    ].join('\n');
    document.head.appendChild(style);
  }

  function numberControl(prefix, field, label, note, minimum, maximum) {
    return '<label class="ch07-control" for="' + prefix + field + '">' + label +
      '<input type="number" id="' + prefix + field + '" data-ch07-field="' + field +
      '" value="' + defaults[field] + '" min="' + minimum + '" max="' + maximum +
      '" step="any" inputmode="decimal" aria-describedby="' + prefix + field + '-note">' +
      '<small id="' + prefix + field + '-note">' + note + '</small></label>';
  }

  function keyCard(index) {
    return '<article class="ch07-key-card"><h4>键 ' + index + '</h4><dl>' +
      '<dt>原始得分 q × k</dt><dd data-ch07-result="score' + index + '"></dd>' +
      '<dt>加掩码后</dt><dd data-ch07-result="masked' + index + '"></dd>' +
      '<dt>权重 a' + index + '</dt><dd data-ch07-result="weight' + index + '"></dd>' +
      '<dt>值 v' + index + '</dt><dd data-ch07-result="value' + index + '"></dd>' +
      '<dt>贡献 a' + index + ' × v' + index + '</dt><dd data-ch07-result="term' + index + '"></dd>' +
      '</dl><div class="ch07-weight-track" aria-hidden="true"><div class="ch07-weight-fill" data-ch07-bar="' + index + '"></div></div></article>';
  }

  function mount(root) {
    if (root.getAttribute('data-ch07-attention-mounted') === 'true') return;
    root.setAttribute('data-ch07-attention-mounted', 'true');
    var document = root.ownerDocument;
    addStyles(document);
    var prefix = 'ch07-attention-' + (++nextId) + '-';
    root.innerHTML = '<div class="ch07-attention" role="region" aria-label="注意力计算实验">' +
      '<h3>动手算：匹配权重与汇聚内容</h3>' +
      '<p>情境：你想判断一个谱段应读取哪处伴峰信息。先用一个查询、两个键练习计算，再决定不同分析任务允许读取哪些位置。本例用手工数值说明运算，不能据此判断真实化学组分。</p>' +
      '<fieldset><legend>1　改 Q/K：观察匹配怎样改变权重</legend>' +
      '<p class="ch07-note">这里 q、k、v 都是一维，d_k = 1，缩放因子为1。默认 k₂ = ln 3；显示值保留6位小数，计算使用完整精度。</p><div class="ch07-grid">' +
      numberControl(prefix, 'q', '查询 q', '范围 −4 至 4；试试改为0。', -4, 4) +
      numberControl(prefix, 'k1', '第一个键 k₁', '范围 −4 至 4。', -4, 4) +
      numberControl(prefix, 'k2', '第二个键 k₂', '默认值为 ln 3（自然对数）。', -4, 4) +
      '</div></fieldset>' +
      '<fieldset><legend>2　设读取边界：观察掩码后的重新归一化</legend>' +
      '<label class="ch07-option"><input type="checkbox" data-ch07-mask><span>屏蔽第二个键：本查询不能读取它</span></label>' +
      '<p class="ch07-note">只展示一行的允许/屏蔽操作；它本身不是完整因果掩码。实际自注意力有多个查询，每行都要分别计算，并至少保留一个可读的键。</p></fieldset>' +
      '<fieldset><legend>3　改 V：区分权重与汇入的内容</legend><div class="ch07-grid">' +
      numberControl(prefix, 'v1', '第一个值 v₁', '范围 −10 至 10；默认2。', -10, 10) +
      numberControl(prefix, 'v2', '第二个值 v₂', '范围 −10 至 10；先解除屏蔽，再把6改为0。', -10, 10) +
      '</div></fieldset>' +
      '<div class="ch07-error ch07-feedback" data-ch07-error role="status" hidden></div>' +
      '<div class="ch07-key-grid">' + keyCard(1) + keyCard(2) + '</div>' +
      '<output class="ch07-result" data-ch07-output aria-live="polite" aria-atomic="true"></output>' +
      '<p data-ch07-explanation></p>' +
      '<p class="ch07-note">Z是这一行的一维汇聚值，不是类别概率。真实网络的Q/K/V通常由可学习投影产生，本例没有训练过程。固定Q/K和掩码时，单独改变V不会改变注意力权重。</p>' +
      '<fieldset><legend>迁移判断：换一种任务，还应读取全部位置吗？</legend>' +
      '<p>先选择任务，再选择预测时可读取的范围。这里“位置”在光谱中指谱段顺序，在视频中指时间顺序。</p><div class="ch07-options">' +
      '<label class="ch07-option"><input type="radio" name="' + prefix + 'task" value="spectrum" checked><span>完整光谱采集结束后，判断样品类别</span></label>' +
      '<label class="ch07-option"><input type="radio" name="' + prefix + 'task" value="forecast"><span>依据电镜历史帧，实时预测下一时刻状态</span></label></div>' +
      '<div class="ch07-options"><label class="ch07-option"><input type="radio" name="' + prefix + 'access" value="all"><span>读取完整输入，包括后续位置的真实观测</span></label>' +
      '<label class="ch07-option"><input type="radio" name="' + prefix + 'access" value="observed"><span>只读当前查询及以前的位置，屏蔽后续位置</span></label></div>' +
      '<button type="button" data-ch07-check>检查我的迁移判断</button>' +
      '<div class="ch07-feedback" data-ch07-task-feedback role="status" aria-live="polite" hidden><strong></strong><p></p></div></fieldset>' +
      '<div class="ch07-actions"><button type="button" class="ch07-reset" data-ch07-reset>重置数值与判断</button></div>' +
      '<p class="ch07-note">可用Tab键依次访问控件。输入仅用于当前页面计算，不保存、不上传。</p></div>';

    var inputs = {};
    Object.keys(defaults).forEach(function (key) { inputs[key] = root.querySelector('[data-ch07-field="' + key + '"]'); });
    var maskInput = root.querySelector('[data-ch07-mask]');
    var output = root.querySelector('[data-ch07-output]');
    var error = root.querySelector('[data-ch07-error]');
    var explanation = root.querySelector('[data-ch07-explanation]');

    function setResult(name, value) {
      root.querySelector('[data-ch07-result="' + name + '"]').textContent = value;
    }
    function update() {
      var current = {};
      var invalid = [];
      Object.keys(inputs).forEach(function (key) {
        var input = inputs[key];
        var value = Number(input.value);
        var valid = input.value.trim() !== '' && Number.isFinite(value) && value >= Number(input.min) && value <= Number(input.max);
        input.setAttribute('aria-invalid', valid ? 'false' : 'true');
        input.setCustomValidity(valid ? '' : '请输入范围内的有限数字。');
        if (!valid) invalid.push(key);
        current[key] = value;
      });
      error.hidden = invalid.length === 0;
      if (invalid.length) {
        error.textContent = '请检查 ' + invalid.join('、') + '：需要输入所示范围内的有限数字。当前结果暂不计算。';
        root.querySelectorAll('[data-ch07-result]').forEach(function (node) { node.textContent = '—'; });
        root.querySelectorAll('[data-ch07-bar]').forEach(function (node) { node.style.width = '0%'; });
        output.textContent = 'Z暂不计算：请先修正输入';
        explanation.textContent = '';
        return;
      }
      var result = computeAttentionRow({q: current.q, keys: [current.k1, current.k2], values: [current.v1, current.v2], mask: [false, maskInput.checked]});
      for (var i = 0; i < 2; i += 1) {
        var n = i + 1;
        setResult('score' + n, format(result.scores[i]));
        setResult('masked' + n, format(result.maskedScores[i]));
        setResult('weight' + n, format(result.weights[i]));
        setResult('value' + n, format(i === 0 ? current.v1 : current.v2));
        setResult('term' + n, format(result.contributions[i]));
        root.querySelector('[data-ch07-bar="' + n + '"]').style.width = (100 * result.weights[i]) + '%';
      }
      output.textContent = 'Z = ' + format(result.contributions[0]) + ' + ' + format(result.contributions[1]) + ' = ' + format(result.output);
      if (maskInput.checked) {
        explanation.textContent = '第二个得分在softmax前变成−∞，权重重新归一化为(1, 0)。所以输出等于v₁；此时改变v₂也不会改变输出。解除屏蔽后，可比较相同Q/K下改变V的影响。';
      } else if (result.scores[0] === result.scores[1]) {
        explanation.textContent = '两个可读键的得分相同，softmax给出相同权重(0.5, 0.5)。因此输出是两个值的平均。保持Q/K不变、单独改V，权重仍不变。';
      } else {
        var larger = result.scores[0] > result.scores[1] ? '第一个' : '第二个';
        explanation.textContent = '当前' + larger + '键的匹配得分更大，softmax为它分配更高权重。两个权重之和为1，输出是两项“权重×值”的和。保持Q/K和掩码不变、单独改V，权重不会改变。';
      }
    }

    root.addEventListener('input', function (event) {
      if (event.target.matches('[data-ch07-field],[data-ch07-mask]')) update();
    });
    root.addEventListener('change', function (event) {
      if (event.target === maskInput) update();
      if (event.target.name === prefix + 'task' || event.target.name === prefix + 'access') {
        root.querySelector('[data-ch07-task-feedback]').hidden = true;
      }
    });
    root.querySelector('[data-ch07-check]').addEventListener('click', function () {
      var task = root.querySelector('input[name="' + prefix + 'task"]:checked');
      var access = root.querySelector('input[name="' + prefix + 'access"]:checked');
      var feedback = taskFeedback(task && task.value, access && access.value);
      var box = root.querySelector('[data-ch07-task-feedback]');
      box.setAttribute('data-kind', feedback.kind);
      box.querySelector('strong').textContent = feedback.title;
      box.querySelector('p').textContent = feedback.text;
      box.hidden = false;
    });
    root.querySelector('[data-ch07-reset]').addEventListener('click', function () {
      Object.keys(inputs).forEach(function (key) { inputs[key].value = String(defaults[key]); });
      maskInput.checked = false;
      root.querySelector('input[name="' + prefix + 'task"][value="spectrum"]').checked = true;
      root.querySelectorAll('input[name="' + prefix + 'access"]').forEach(function (node) { node.checked = false; });
      root.querySelector('[data-ch07-task-feedback]').hidden = true;
      update();
    });
    update();
  }

  function install(window) {
    if (window.__ch07AttentionLabInstalled) return;
    window.__ch07AttentionLabInstalled = true;
    function mountAll() {
      window.document.querySelectorAll('[data-lab="ch07-attention"]').forEach(mount);
    }
    function schedule() { window.requestAnimationFrame(mountAll); }
    window.$docsify = window.$docsify || {};
    window.$docsify.plugins = (window.$docsify.plugins || []).concat(function (hook) {
      hook.doneEach(schedule);
      hook.mounted(schedule);
    });
    window.document.addEventListener('DOMContentLoaded', mountAll);
    if (window.document.readyState !== 'loading') schedule();
  }

  return { computeAttentionRow: computeAttentionRow, taskFeedback: taskFeedback, mount: mount, install: install };
}));

/* Chapter 15: deterministic teaching simulations; no model training or answer collection. */
(function (root) {
  'use strict';
  const uncertainty = (a,b,r) => Math.sqrt(Math.max(0,a*a+b*b+2*r*a*b));
  function temperature(logits,t) {
    if (!(t>0)) throw new RangeError('Temperature must be positive');
    const m=Math.max(...logits),a=logits.map(v=>Math.exp((v-m)/t)),s=a.reduce((x,y)=>x+y,0);
    return a.map(v=>v/s);
  }
  const attribution = w => ({first:w,second:1-w,prediction:1});
  function snv(a) {
    const mean=a.reduce((s,v)=>s+v,0)/a.length;
    const sd=Math.sqrt(a.reduce((s,v)=>s+(v-mean)**2,0)/(a.length-1));
    return a.map(v=>(v-mean)/sd);
  }
  const api={uncertainty,temperature,attribution,snv};
  if (typeof module!=='undefined'&&module.exports) module.exports=api;
  if (!root||!root.document) return;
  const doc=root.document;
  function installStyle() {
    if(doc.getElementById('ch15-labs-style'))return;
    const s=doc.createElement('style');s.id='ch15-labs-style';
    s.textContent='.ch15-lab{border:1px solid #b9cbd2;border-left:4px solid #28677a;padding:20px;margin:24px 0;background:#f6f9fa;color:#173744}.ch15-lab h4{margin:0 0 10px;font-size:1.15rem}.ch15-lab label{display:block;margin:12px 0}.ch15-lab input[type=range]{display:block;width:100%;max-width:550px;accent-color:#28677a}.ch15-lab select{max-width:100%;padding:7px;white-space:normal}.ch15-lab button{font:inherit;padding:7px 13px;background:#28677a;color:#fff;border:0;border-radius:3px;cursor:pointer;margin:8px 0}.ch15-lab :is(input,select,button,a):focus-visible{outline:3px solid #d39135;outline-offset:3px}.ch15-lab .ch15-feedback{padding:10px 12px;background:#e8f0f3;border-left:3px solid #648b9a;min-height:55px}.ch15-lab .ch15-transfer{font-size:.94rem}.ch15-lab svg{display:block;width:100%;max-width:540px;height:auto}.ch15-lab iframe{width:100%;height:1150px;border:1px solid #ccd8de;background:white}@media(max-width:600px){.ch15-lab{padding:14px}.ch15-lab iframe{height:1200px}}';
    doc.head.appendChild(s);
  }
  const range=(k,t,min,max,step,v)=>`<label>${t}<input data-control="${k}" type="range" min="${min}" max="${max}" step="${step}" value="${v}"></label>`;
  const select=(k,t,opts)=>`<label>${t}<select data-control="${k}">${opts.map(([v,s])=>`<option value="${v}">${s}</option>`).join('')}</select></label>`;
  function shell(el,title,context,controls,transfer,update) {
    el.innerHTML=`<h4>${title}</h4><p>${context}</p><form>${controls}<button type="reset">重置本节演示</button></form><div class="ch15-feedback" aria-live="polite"></div><p class="ch15-transfer">迁移判断：${transfer}</p>`;
    const form=el.querySelector('form'),get=k=>el.querySelector(`[data-control="${k}"]`).value;
    const render=()=>update(get,el.querySelector('.ch15-feedback'));
    form.addEventListener('submit',e=>e.preventDefault());form.addEventListener('input',render);form.addEventListener('change',render);
    form.addEventListener('reset',()=>root.setTimeout(render,0));render();
  }
  const views={
    1(el) {
      shell(el,'15.1 操作不确定度的相关性','教学情境：报告y=x₁+x₂。只考虑两个标准不确定度和相关系数，暂不纳入模型与代表性问题。',
        range('u1','u₁（相同单位）',0,5,.1,1)+range('u2','u₂（相同单位）',0,5,.1,1)+range('rho','相关系数ρ',-1,1,.1,0),
        '若两个结果来自同一校准曲线，独立性还成立吗？先找共同影响因素，再决定协方差。',
        (g,f)=>{const a=+g('u1'),b=+g('u2'),r=+g('rho');f.textContent=`u₁=${a.toFixed(1)}，u₂=${b.toFixed(1)}，ρ=${r.toFixed(1)}：u(y)=√(u₁²+u₂²+2ρu₁u₂)=${uncertainty(a,b,r).toFixed(3)}。${r===0?'当前假定不相关。':r>0?'共同变化使这个和的不确定度增加。':'负相关使这个和的部分变化相抵。'} 这是合成教学例子，不能替代实际不确定度评定。`;});
    },
    2(el) {
      shell(el,'15.2 调节概率表达','合成例子：固定logit=[2,1,0]，本条真类为A。改变正温度，观察概率与类别判断。',range('t','温度T',.2,4,.05,1),
        '若真类是B，升温对这条NLL一定有相同影响吗？真实温度应在专用校准集拟合。',
        (g,f)=>{const t=+g('t'),p=temperature([2,1,0],t);f.innerHTML=`<p>T=${t.toFixed(2)}，预测仍为A；此条真类为A的NLL=${(-Math.log(p[0])).toFixed(3)}。</p><svg viewBox="0 0 520 150" role="img" aria-label="三个类别的温度变换概率">${p.map((v,i)=>`<text x="0" y="${30+45*i}">${['A','B','C'][i]}</text><rect x="30" y="${12+45*i}" width="${370*v}" height="26" fill="#28677a"/><text x="${40+370*v}" y="${30+45*i}">${v.toFixed(3)}</text>`).join('')}</svg><p>共同正温度保持argmax；单条NLL变化不等于整体校准改善或准确率提高。这不是本章真实模型的重新拟合。</p>`;});
    },
    3(el) {
      el.innerHTML='<h4>15.3 用真实输出比较拒识规则</h4><p>依次尝试预设、全拒识和全接受，再切换评分与评价范围，回查失败编号。真实数据与公式见下文综合案例。</p><p><a href="./assets/ch15/threshold-lab.html" target="_blank" rel="noopener" data-no-router>在独立页面打开完整交互</a></p><iframe src="assets/ch15/threshold-lab.html" loading="lazy" title="真实拉曼测试的阈值、概率与失败记录"></iframe><p class="ch15-transfer">迁移判断：部署时未知比例改变后，人工混合的错误率还可直接沿用吗？重置按钮位于演示设置；切换评分恢复各自预设阈值。</p>';
    },
    4(el) {
      const choices={random:'按扫描拆分会让同一样品的重复谱跨角色，不能回答新样品任务。应将重复谱按试样一起分配。',specimen:'按试样分组可隔离重复扫描；仍需核查物种、日期和仪器是否重叠，不能据此宣称跨仪器有效。',instrument:'整台仪器留出可检验相应迁移，但需有该仪器的独立数据和可比参比。若类别与仪器完全绑定，无法分开两者作用。'};
      shell(el,'15.4 选择数据角色的边界','设计例子：每个试样有3次扫描，来自两台仪器。目标为预测新试样或新仪器。这里没有模拟性能数字。',
        select('unit','如何留出？',[['random','按扫描随机拆分'],['specimen','按试样整体留出'],['instrument','整台仪器留出']])+select('balance','类别与仪器的关系',[['crossed','每台仪器测各类别'],['confounded','仪器甲只测A，乙只测B']]),
        '若预测新矿物种，编号分组还缺少哪一级元数据？',
        (g,f)=>{f.innerHTML=`<p>${choices[g('unit')]}</p><p>${g('balance')==='crossed'?'交叉采集使类别与仪器有机会分开检查，仍需样本量和重复设计。':'完全混杂：当前没有同类跨仪器对照。补采交叉条件，提高模型复杂度不能补回观测。'}</p>`;});
    },
    5(el) {
      const choices={observe:'只增加现成谱：Y←S→B→X仍可能解释预测关联，不能据此识别化学干预效应。',cross:'同样品跨批复测、同批包含各类，可检验部分批次依赖；需记录重制样等伴随变化。它不自动识别任意因果效应。',random:'对可操作处理随机分配、阻断批次，并定义参比和终点，可在对应假设下支持该处理的因果比较。不可对材料身份凭空随机化。'};
      shell(el,'15.5 在因果图上选择对照','设计例子：采样安排S影响类别Y与批次B，化学状态M与B都影响光谱X。模型可能利用批次。',
        select('design','下一步获取什么证据？',[['observe','增加同条件现成谱'],['cross','同样品跨批复测并补齐交叉类别'],['random','定义可操作处理并随机分配']]),
        '若是否入选S同时受类别与批次影响，应画成Y→S←B；按S筛选可能怎样改变关联？',
        (g,f)=>{f.innerHTML=`<p>图示路径：Y ← S → B → X；M → X。</p><p>${choices[g('design')]}</p><p>箭头是假设；本章实际计算未开展这些化学干预。</p>`;});
    },
    6(el) {
      shell(el,'15.6 检查相关特征的归因分配','合成例子：x₁=x₂=1，预测为wx₁+(1−w)x₂。调节w比较权重解释与总预测。这不是SHAP输出。',range('w','特征1的权重w',0,1,.05,.5),
        '相邻波数高度相关时，如何通过背景选择、重采样和独立测量核查解释的稳定性与机制？',
        (g,f)=>{const a=attribution(+g('w'));f.textContent=`特征1贡献=${a.first.toFixed(2)}，特征2贡献=${a.second.toFixed(2)}，总预测=${a.prediction.toFixed(2)}。预测相同可有不同权重配置。模型依赖不足以唯一识别化学机制，需分别检验解释忠实性和化学依据。`;});
    },
    7(el) {
      shell(el,'15.7 判断约束对应哪一种信号','合成原始强度=[2,4,8]。SNV中心化后有负数，表示相对于本谱均值的位置。',
        select('constraint','在SNV后执行什么操作？',[['keep','保留正负信号'],['clip','以原始强度非负为由将负值截为0']]),
        '若拟合对象是非负组分浓度，非负约束的对象和依据如何改变？',
        (g,f)=>{const a=snv([2,4,8]),b=g('constraint')==='clip'?a.map(v=>Math.max(0,v)):a;f.innerHTML=`<p>SNV=[${a.map(v=>v.toFixed(3)).join(', ')}]；当前结果=[${b.map(v=>v.toFixed(3)).join(', ')}]。</p><p>${g('constraint')==='clip'?'截断改变中心化信号和相对结构；原始强度的约束不能直接搬到SNV坐标。':'保留SNV中心化结构；不代表适合所有分析目标。'} 此代数演示不代表真实样品的约束性能。</p>`;});
    },
    8(el) {
      const choices={accuracy:'可报告22/36的有限任务分类正确比例，注明规则标签、区间与同库边界。这不替代分析方法的完整准确度验证。',instrument:'当前没有新仪器数据，5次同池划分不能证明跨仪器有效。需预定外部条件、参比与判据，再获取对应复测。',causal:'当前没有化学干预或独立结构鉴定，不能把高权重峰写成机制确证。需明确目标效应并设计对应对照。'};
      shell(el,'15.8 让主张对应验证证据','决策情境：准备向使用者报告拉曼计算。选择一项主张，检查已有证据。',
        select('claim','计划报告的结论',[['accuracy','三个已知规则类的测试正确比例'],['instrument','适用于另一台仪器'],['causal','模型已确认化学机制']]),
        '用途改为现场鉴定后，哪些参比、样品、外部条件与错误代价必须重新规定？',
        (g,f)=>{f.textContent=choices[g('claim')];});
    }
  };
  function mount() {
    // Repository-relative hrefs work in GitHub; Docsify uses its own routes/base URL.
    doc.querySelectorAll('a[data-ch15-site-href]').forEach(a=>{
      a.setAttribute('href',a.getAttribute('data-ch15-site-href'));
    });
    doc.querySelectorAll('[data-ch15-lab]').forEach(el=>{
      if(el.dataset.ch15Mounted)return;
      const render=views[el.dataset.ch15Lab];if(!render)return;
      installStyle();render(el);el.dataset.ch15Mounted='true';
    });
  }
  root.ch15Labs=Object.assign(api,{mount});
  root.$docsify=root.$docsify||{};
  root.$docsify.plugins=(root.$docsify.plugins||[]).concat(function(hook){hook.doneEach(mount);});
})(typeof window==='undefined'?null:window);

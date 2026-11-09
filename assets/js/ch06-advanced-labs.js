/* 原生课程组件：实际结果探查与反事实表示设计。无网络训练、无答案上传。 */
(function(){'use strict';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const table=(heads,rows)=>`<div class="lr-scroll"><table><thead><tr>${heads.map(x=>`<th>${x}</th>`).join('')}</tr></thead><tbody>${rows.map(row=>`<tr>${row.map(x=>`<td>${x}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
const download=(name,text,type='text/plain')=>{const u=URL.createObjectURL(new Blob(['\uFEFF'+text],{type:type+';charset=utf-8'})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);};
const csv=rows=>rows.map(row=>row.map(s=>'"'+String(s).replaceAll('"','""')+'"').join(',')).join('\n');
let serial=0;
const cn=['乙醇','二甲醚','E-2-丁烯','Z-2-丁烯','乳酸构型A','乳酸构型B'];
const featureInfo=[['MW_g_mol','分子量 M / g·mol⁻¹'],['HBD','氢键供体 HBD'],['HBA','氢键受体 HBA'],['TPSA_A2','极性表面积 TPSA / Å²'],['canonical_no_stereo','元素与连接（无立体）'],['canonical_isomeric_SMILES','指定立体结构']];
function design(root){
 let history=[];try{history=JSON.parse(localStorage.getItem('ch06-design-history-v3')||'[]');if(!Array.isArray(history))history=[];}catch{}
 const data=window.CH06_DESCRIPTOR_DATA||[],uid='adv-'+(++serial);
 root.innerHTML=`<h3>反事实表示设计：保留什么，才能解决当前问题？</h3><p>问题：同一表示可能合并性质不同的分子，也可能为当前任务保存了不必要的细节。先写假设，再选择特征，记录至少两组方案，最后比较证据。所有数值取自本章实际RDKit输出。</p><fieldset><legend>1 · 定义终点与观察对象</legend><div class="lr-controls"><label>待解决问题<select data-task><option value="hbd">识别规则HBD：氢键供体数能否保留？</option><option value="identity">结构辨识：立体异构体会不会被合并？</option><option value="activity">手性受体活性：当前证据是否充分？</option></select></label><label>重点分子对<select data-pair><option value="0">乙醇 / 二甲醚</option><option value="1">E / Z-2-丁烯</option><option value="2">乳酸镜像构型</option></select></label></div><label for="${uid}-hyp">我的假设（本地记录，不上传）</label><textarea id="${uid}-hyp" data-hyp rows="2" style="width:100%;font:inherit" maxlength="500" placeholder="例如：只增加分子量无法区分HBD不同的乙醇与二甲醚。"></textarea></fieldset><fieldset><legend>2 · 设计表示并做受控干预</legend><p class="lr-small">字符串这里只作为确切结构身份键，不是学习嵌入；“关闭立体”只去掉立体标签，其他数据保持不变。</p>${featureInfo.map(([key,label],i)=>`<label class="adv-feature"><input type="checkbox" data-feature="${key}" ${i===0?'checked':''}>${label}</label>`).join('')}<div class="lr-controls"><label><input type="checkbox" data-strip>在编码前去掉立体标签</label><button class="lr-button" data-minimal>应用当前问题的最小修复</button></div></fieldset><div data-diagnosis aria-live="polite"></div><div data-encoding></div><fieldset><legend>3 · 记录、比较、解释</legend><button class="lr-button" data-save>记录当前方案</button><button class="lr-button" data-export>导出对照CSV</button><button class="lr-button" data-reset>重置控件与实验记录</button><div data-history class="adv-history"></div></fieldset><p class="lr-small">验证边界：HBD是规则计算终点；立体身份是结构辨识任务；本表没有真实受体活性，任何方案都不能在这里宣称已准确预测活性。增加特征后的维数变化不等于训练成本或泛化性能变化。</p>`;
 const q=s=>root.querySelector(s);let current;
 function renderHistory(){q('[data-history]').innerHTML=history.length?table(['方案','假设','表示 / 干预','重点对照与结果'],history.map((r,i)=>[i+1,esc(r.hypothesis||'未填写'),esc(r.features.join(' + ')||'空表示')+(r.strip?'；去立体':''),esc(r.pair+'：'+r.result)])):'<p>尚未记录。建议依次比较“仅M”“M＋HBD”“指定立体但预先去立体”等方案。</p>';}
 function update(){const keys=[...root.querySelectorAll('[data-feature]:checked')].map(x=>x.dataset.feature),strip=q('[data-strip]').checked,task=q('[data-task]').value,pair=Number(q('[data-pair]').value),a=pair*2,b=a+1;
 const vectors=data.map(r=>keys.map(k=>k==='canonical_isomeric_SMILES'&&strip?r.canonical_no_stereo:r[k]));
 const same=(i,j)=>JSON.stringify(vectors[i])===JSON.stringify(vectors[j]);
 const collisions=[];for(let i=0;i<data.length;i++)for(let j=i+1;j<data.length;j++)if(same(i,j))collisions.push([i,j]);
 const conflicts=collisions.filter(([i,j])=>task==='hbd'?data[i].HBD!==data[j].HBD:task==='identity'?data[i].canonical_isomeric_SMILES!==data[j].canonical_isomeric_SMILES:false);
 const result=task==='activity'?(same(a,b)?'重点分子对已被合并，可能遗漏任务相关差异；受体活性标签仍缺失。':'重点分子对可以区分，但缺少受体与活性标签，预测问题尚未解决。'):task==='hbd'?(conflicts.length?'发现HBD冲突，表示尚不适合这一规则终点。':'六个案例中没有HBD冲突；这不是对全部化学空间的保证。'):(same(a,b)?'重点分子对仍被合并；需要补充连接或立体信息。':'重点分子对可区分；结构辨识问题在本对照中得到修复。');
 q('[data-diagnosis]').innerHTML=`<div class="adv-metrics"><div class="adv-metric">所选通道<b>${keys.length}</b></div><div class="adv-metric">全体相同编码对<b>${collisions.length}</b></div><div class="adv-metric">${task==='activity'?'活性真值':'已知终点冲突对'}<b>${task==='activity'?'缺失':conflicts.length}</b></div></div><div class="lr-output ${task==='activity'||conflicts.length?'lr-warning':''}"><strong>${cn[a]} / ${cn[b]}：${same(a,b)?'相同编码':'不同编码'}</strong><p>${result}</p><p>${keys.length===0?'空表示把全部分子合并。':strip&&keys.includes('canonical_isomeric_SMILES')?'你在编码前删掉了立体信息；即使选择“指定立体结构”也无法恢复。':'先保持其他设置固定，再观察某一个特征带来的变化。'}</p></div>`;
 q('[data-encoding]').innerHTML=table(['分子','当前编码向量','已知规则HBD'],data.map((r,i)=>[cn[i],esc(JSON.stringify(vectors[i])),r.HBD]));
 current={task,pair:cn[a]+' / '+cn[b],features:keys.map(k=>featureInfo.find(f=>f[0]===k)[1]),strip,result,hypothesis:q('[data-hyp]').value};
 }
 root.querySelectorAll('select,input').forEach(x=>x.onchange=update);
 q('[data-minimal]').onclick=()=>{const task=q('[data-task]').value,pair=Number(q('[data-pair]').value);root.querySelectorAll('[data-feature]').forEach(x=>x.checked=x.dataset.feature===(task==='hbd'?'HBD':pair===0?'canonical_no_stereo':'canonical_isomeric_SMILES'));q('[data-strip]').checked=false;update();};
 q('[data-save]').onclick=()=>{update();history.push({...current});history=history.slice(-12);try{localStorage.setItem('ch06-design-history-v3',JSON.stringify(history));}catch{}renderHistory();};
 q('[data-export]').onclick=()=>download('representation-design-records.csv',csv([['task','pair','hypothesis','features','strip_stereo','result'],...history.map(r=>[r.task,r.pair,r.hypothesis,r.features.join(' + '),r.strip,r.result])]),'text/csv');
 q('[data-reset]').onclick=()=>{try{localStorage.removeItem('ch06-design-history-v3');}catch{}design(root);};
 update();renderHistory();
}
// 每条记录：[split,seed,model,id,name,SMILES,y_true,y_pred,nearestT,heavyAtoms,formalCharge]
const LOW_SIMILARITY_MAX = 0.40;
const modelNames={training_mean:'训练均值',descriptors_ridge:'7描述符＋Ridge',morgan_5nn:'Morgan＋Tanimoto 5-NN'};
function stats(rows){const n=rows.length;if(!n)return{n:0,mae:null,rmse:null};return{n,mae:rows.reduce((s,r)=>s+Math.abs(r[7]-r[6]),0)/n,rmse:Math.sqrt(rows.reduce((s,r)=>s+(r[7]-r[6])**2,0)/n)};}
function subset(data,s){return data.filter(r=>r[0]===s.split&&r[1]===s.seed&&r[2]===s.model&&r[8]>=s.minT&&r[8]<=s.maxT&&r[9]>=s.minHeavy&&r[9]<=s.maxHeavy&&(s.charge==='all'||(s.charge==='neutral'?r[10]===0:r[10]!==0))&&(!s.term||(r[3]+' '+r[4]+' '+r[5]).toLowerCase().includes(s.term)));}
function explorer(root){
 const data=window.CH06_EXPLORER_DATA||[];let filtered=[],base=[],selected='',snapshots=[];
 root.innerHTML=`<h3>真实结果探查：低误差是否经得住测试边界改变？</h3><p>问题：总体平均误差可能掩盖新骨架与低相似邻域的失败。按下列条件筛选本章<strong>已经实际运行</strong>的逐样本结果，比较总体与子集，点击样本查看误差。这里不在浏览器重新训练，也不提供域外分子的实时预测。</p><div class="lr-controls"><label>测试边界<select data-split><option value="random">随机留出</option><option value="scaffold">完整骨架组留出</option></select></label><label>模型<select data-model>${Object.entries(modelNames).map(([key,name])=>`<option value="${key}" ${key==='descriptors_ridge'?'selected':''}>${name}</option>`).join('')}</select></label><label>预设种子<select data-seed><option>42</option><option>43</option><option>44</option></select></label></div><fieldset><legend>控制误差探查的条件</legend><div class="lr-grid"><label>最近训练邻居Tanimoto下限 <output data-tlabel>0.00</output><input data-mint type="range" min="0" max="1" step="0.05" value="0"></label><label>最近训练邻居Tanimoto上限 <output data-ulabel>1.00</output><input data-maxt type="range" min="0" max="1" step="0.05" value="1"></label></div><div class="lr-controls"><label>重原子数下限<input data-minh type="number" min="1" max="100" value="1"></label><label>重原子数上限<input data-maxh type="number" min="1" max="100" value="100"></label><label>形式电荷<select data-charge><option value="all">全部</option><option value="neutral">中性</option><option value="charged">非零形式电荷</option></select></label><label>查找分子<input data-term type="search" placeholder="名称、ID或SMILES"></label></div><button class="lr-button" data-low>低相似邻域：T ≤ ${LOW_SIMILARITY_MAX.toFixed(2)}</button><button class="lr-button" data-full>恢复当前划分的全体样本</button></fieldset><div data-summary aria-live="polite"></div><div data-chart></div><div class="lr-output" data-selected aria-live="polite">点击散点或下表的样本查看详情。</div><div class="adv-results" data-table></div><div class="lr-controls"><button class="lr-button" data-snapshot>记录这一比较条件</button><button class="lr-button" data-export>导出筛选后的逐样本CSV</button><button class="lr-button" data-reset>重置整个探查器</button></div><div data-snapshots></div><p class="lr-small">筛选只改变评价对象，不改变训练数据或原模型。按测试误差反复选择条件只能用于诊断，不能作为新的独立测试结论。不同划分的测试样本不相同。T=0.40是教学观察阈值，不是通用适用域标准；原表缺少逐条pH、温度、晶型信息。</p>`;
 const q=s=>root.querySelector(s);
 function settings(){return{split:q('[data-split]').value,seed:Number(q('[data-seed]').value),model:q('[data-model]').value,minT:Number(q('[data-mint]').value),maxT:Number(q('[data-maxt]').value),minHeavy:Number(q('[data-minh]').value),maxHeavy:Number(q('[data-maxh]').value),charge:q('[data-charge]').value,term:q('[data-term]').value.trim().toLowerCase()};}
 function detail(id){const r=filtered.find(r=>r[3]===id);if(!r)return;selected=id;q('[data-selected]').innerHTML=`<strong>${esc(r[4])} · ${esc(r[3])}</strong><p>实测 ${r[6].toFixed(3)}；预测 ${r[7].toFixed(3)}；残差（预测−实测）${(r[7]-r[6]).toFixed(3)}；最近邻T ${r[8].toFixed(3)}；重原子数 ${r[9]}；形式电荷 ${r[10]}。</p><p>规范SMILES：<code>${esc(r[5])}</code></p><p class="lr-small">这条残差用于定位失败，不能单凭它断言具体溶剂化或晶态机制。</p>`;}
 function update(){const s=settings();q('[data-tlabel]').textContent=s.minT.toFixed(2);q('[data-ulabel]').textContent=s.maxT.toFixed(2);base=data.filter(r=>r[0]===s.split&&r[1]===s.seed&&r[2]===s.model);filtered=subset(data,s);const total=stats(base),sub=stats(filtered),valid=s.minT<=s.maxT&&s.minHeavy<=s.maxHeavy;
 q('[data-summary]').innerHTML=`<div class="adv-metrics"><div class="adv-metric">当前子集 / 原测试集<b>${sub.n} / ${total.n}</b></div><div class="adv-metric">子集MAE / log10(mol/L)<b>${sub.mae===null?'—':sub.mae.toFixed(3)}</b></div><div class="adv-metric">子集RMSE / log10(mol/L)<b>${sub.rmse===null?'—':sub.rmse.toFixed(3)}</b></div></div><div class="lr-output ${sub.n<20?'lr-warning':''}">${valid?'':'上下限顺序不合法，请调整。 '}${!sub.n?'没有匹配样本；空子集的误差未定义，不记为零。':`原测试集MAE ${total.mae.toFixed(3)}。${sub.n<20?'当前子集少于20条，结果易波动。':'请比较样本量、划分与最近邻条件，再解释误差。'}`}<p>误差来自真实测量标签与已保存预测；不由所选阈值生成新预测。</p></div>`;
 const W=640,H=400,L=67,R=22,T=28,B=57,lo=-12,hi=3,x=v=>L+(v-lo)/(hi-lo)*(W-L-R),y=v=>H-B-(v-lo)/(hi-lo)*(H-T-B);
 q('[data-chart]').innerHTML=`<svg class="adv-chart" viewBox="0 0 ${W} ${H}" role="img" aria-label="当前筛选子集的实测与预测散点图；每个点也可从下方表格按键选择"><defs><clipPath id="plotclip-${serial}"><rect x="${L}" y="${T}" width="${W-L-R}" height="${H-T-B}"/></clipPath></defs>${[-12,-9,-6,-3,0,3].map(t=>`<path d="M${x(t)} ${T}V${H-B}M${L} ${y(t)}H${W-R}" stroke="#e1e8d8"/><text x="${x(t)}" y="${H-B+25}" text-anchor="middle">${t}</text><text x="${L-12}" y="${y(t)+5}" text-anchor="end">${t}</text>`).join('')}<path d="M${L} ${T}V${H-B}H${W-R}" fill="none" stroke="#4b6851"/><line x1="${x(lo)}" y1="${y(lo)}" x2="${x(hi)}" y2="${y(hi)}" stroke="#b47e4f" stroke-dasharray="6 4"/><g clip-path="url(#plotclip-${serial})">${filtered.map(r=>`<circle class="adv-point" data-point="${esc(r[3])}" cx="${x(r[6])}" cy="${y(r[7])}" r="4.4" opacity=".75" fill="${r[8]<=LOW_SIMILARITY_MAX?'#bf794c':'#46734e'}"><title>${esc(r[4])}：实测${r[6].toFixed(2)}，预测${r[7].toFixed(2)}</title></circle>`).join('')}</g><text x="${(W+L-R)/2}" y="${H-9}" text-anchor="middle">实测 logS / log10(mol/L)</text><text transform="translate(20 ${H/2}) rotate(-90)" text-anchor="middle">预测 logS / log10(mol/L)</text></svg><p class="lr-small">橙点 T ≤ ${LOW_SIMILARITY_MAX.toFixed(2)}，绿点 T > ${LOW_SIMILARITY_MAX.toFixed(2)}。虚线为预测＝实测。固定坐标−12至3，超出图界的记录仍保留在指标与导出中。</p>`;
 const sorted=[...filtered].sort((a,b)=>Math.abs(b[7]-b[6])-Math.abs(a[7]-a[6]));q('[data-table]').innerHTML='<p>按绝对误差排序的前12条；完整子集可导出。</p>'+table(['样本','实测 / 预测','绝对误差','最近邻T'],sorted.slice(0,12).map(r=>[`<button data-sample="${esc(r[3])}">${esc(r[4])}</button>`,r[6].toFixed(3)+' / '+r[7].toFixed(3),Math.abs(r[7]-r[6]).toFixed(3),r[8].toFixed(3)]));
 root.querySelectorAll('[data-point]').forEach(x=>x.onclick=()=>detail(x.dataset.point));root.querySelectorAll('[data-sample]').forEach(x=>x.onclick=()=>detail(x.dataset.sample));if(filtered.some(r=>r[3]===selected))detail(selected);else q('[data-selected]').textContent='点击散点或下表的样本查看详情。';
 }
 root.querySelectorAll('input,select').forEach(x=>{x.oninput=update;x.onchange=update;});
 function full(){q('[data-mint]').value=0;q('[data-maxt]').value=1;q('[data-minh]').value=1;q('[data-maxh]').value=100;q('[data-charge]').value='all';q('[data-term]').value='';}
 q('[data-low]').onclick=()=>{q('[data-mint]').value=0;q('[data-maxt]').value=LOW_SIMILARITY_MAX;update();};q('[data-full]').onclick=()=>{full();update();};
 q('[data-snapshot]').onclick=()=>{const s=settings(),a=stats(filtered);snapshots.push([s.split,s.seed,modelNames[s.model],`${s.minT}≤T≤${s.maxT}；${s.minHeavy}≤重原子≤${s.maxHeavy}；${s.charge}；${s.term||'无检索词'}`,a.n,a.mae===null?'—':a.mae.toFixed(3)]);q('[data-snapshots]').innerHTML=table(['划分','种子','模型','筛选条件','n','MAE'],snapshots.slice(-8));};
 q('[data-export]').onclick=()=>download('esol-filtered-predictions.csv',csv([['split','seed','model','id','name','canonical_smiles','measured_logS','predicted_logS','nearest_train_tanimoto','n_heavy_atoms','formal_charge'],...filtered]),'text/csv');q('[data-reset]').onclick=()=>explorer(root);update();
}
function mount(root,name){root.classList.add('ch06-learning','ch06-advanced');root.dataset.ch06Advanced=name;root.dataset.advancedMounted='true';serial++;if(name==='design')design(root);else explorer(root);}
const dataURL=new URL('ch06-explorer-data.js',document.currentScript.src).href;
let dataPromise=null;
function ensureData(){
 if(window.CH06_EXPLORER_DATA&&window.CH06_DESCRIPTOR_DATA)return Promise.resolve();
 if(dataPromise)return dataPromise;
 dataPromise=new Promise((resolve,reject)=>{const script=document.createElement('script');script.src=dataURL;script.onload=()=>{if(window.CH06_EXPLORER_DATA&&window.CH06_DESCRIPTOR_DATA)resolve();else reject(new Error('数据快照不完整'));};script.onerror=()=>reject(new Error('数据快照未能加载'));document.head.appendChild(script);}).catch(error=>{dataPromise=null;throw error;});
 return dataPromise;
}
function autoMount(scope=document){
 const roots=[...scope.querySelectorAll('[data-ch06-advanced]')].filter(root=>root.dataset.advancedMounted!=='true');
 if(!roots.length)return;
 const start=()=>roots.forEach(root=>{if(root.isConnected&&root.dataset.advancedMounted!=='true')mount(root,root.dataset.ch06Advanced);});
 if(window.CH06_EXPLORER_DATA&&window.CH06_DESCRIPTOR_DATA){start();return;}
 roots.forEach(root=>{root.innerHTML='<p role="status">正在加载本章实验数据…</p>';});
 ensureData().then(start).catch(()=>roots.forEach(root=>{if(!root.isConnected)return;root.innerHTML='<p role="status">本章实验数据未能加载，请检查网络后重试。</p><button type="button">重新加载实验数据</button>';root.querySelector('button').onclick=()=>autoMount(scope);}));
}

window.Ch06Advanced={mount,autoMount,stats,subset};
if(window.$docsify)window.$docsify.plugins=(window.$docsify.plugins||[]).concat(hook=>hook.doneEach(()=>requestAnimationFrame(()=>autoMount())));
document.addEventListener('DOMContentLoaded',()=>autoMount());
})();

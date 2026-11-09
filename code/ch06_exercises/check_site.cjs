/* 从仓库根目录运行；检查静态接入与浏览器汇总数据，不代替实际浏览器验收。 */
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const root=path.resolve(__dirname,'../..'),read=p=>fs.readFileSync(path.join(root,p),'utf8');
const markdown=read('docs/ch06.md'),headings=[...markdown.matchAll(/^## (.+)$/gm)].map(m=>m[1]);
assert.deepEqual(headings.slice(0,3),['章首导引','学习目标','本章知识图谱']);
assert.deepEqual(headings.slice(-6),['代码实践','本章小结','思考题与计算题','下载本章资源','年度课程资源、传承题与更新引文','本章共建记录与致谢']);
let checked=0;
for(const file of ['docs/ch06.md','resources/annual/2026-2027/questions/ch06.md','resources/annual/2026-2027/references/ch06.md','resources/annual/2026-2027/presentations/README.md','resources/annual/2026-2027/presentations/ch06/README.md']){
 for(const [,target]of read(file).matchAll(/(?:href|src)="\.\/([^"]+)"/g)){assert.ok(fs.existsSync(path.join(root,decodeURIComponent(target))),target);checked++;}
}
const index=read('index.html');for(const file of ['assets/ch06/learning.css','assets/js/ch06-section-labs.js','assets/js/ch06-advanced-labs.js'])assert.equal(index.split(file).length-1,1);
assert.ok(!index.includes('<script src="assets/js/ch06-explorer-data.js"'),'prediction data must load only when ch06 mounts');
const context={URL,document:{currentScript:{src:'https://example.invalid/assets/js/ch06-advanced-labs.js'},addEventListener(){}}};context.window=context;vm.createContext(context);
for(const file of ['assets/js/ch06-explorer-data.js','assets/js/ch06-advanced-labs.js','assets/js/ch06-section-labs.js'])vm.runInContext(read(file),context,{filename:file});
const siteMarkdown=context.Ch06Learning.siteResourceMarkup(markdown);
assert.ok(!/\bhref="#\/resources\/annual\/2026-2027\/ppt\/ch06-index"/.test(siteMarkdown));
assert.ok(siteMarkdown.includes('href="./code/ch06_exercises/case_study.py"'));
assert.ok(markdown.includes('href="https://github.com/yoimiya-610/intelligent-analytical-chemistry/blob/ch06/information-preservation-issue-4/code/ch06_exercises/case_study.py"'));
assert.ok(siteMarkdown.includes('src="./assets/graphs/ch06.svg"'));
assert.ok(markdown.includes('src="https://raw.githubusercontent.com/yoimiya-610/'));
assert.equal(new URL('./code/ch06_exercises/case_study.py','https://example.invalid/book/').pathname,'/book/code/ch06_exercises/case_study.py');
assert.equal(context.Ch06Learning.siteResourceMarkup('<a href="./unrelated">Other chapter</a>'),'<a href="./unrelated">Other chapter</a>');
const data=JSON.parse(read('resources/annual/2026-2027/results/ch06/esol/summary.json'));
for(const metric of data.metrics){const rows=context.Ch06Advanced.subset(context.CH06_EXPLORER_DATA,{split:metric.split,seed:metric.seed,model:metric.model,minT:0,maxT:1,minHeavy:1,maxHeavy:100,charge:'all',term:''});const m=context.Ch06Advanced.stats(rows);assert.equal(m.n,metric.n_test);assert.ok(Math.abs(m.mae-metric.MAE_logS)<1e-10);assert.ok(Math.abs(m.rmse-metric.RMSE_logS)<1e-10);}
assert.equal(context.Ch06Advanced.stats([]).mae,null);

// Run the explorer's real mount, button and input callbacks against a minimal DOM.
const controls = new Map(Object.entries({
    split: 'random', seed: '42', model: 'descriptors_ridge', mint: '0', maxt: '1',
    minh: '1', maxh: '100', charge: 'all', term: '',
}).map(([name, value]) => [`[data-${name}]`, {value}]));
const explorerRoot = {
    classList: {add() {}},
    dataset: {},
    querySelector(selector) {
        if (!controls.has(selector)) controls.set(selector, {});
        return controls.get(selector);
    },
    querySelectorAll(selector) {
        return selector === 'input,select' ? [...controls.values()].filter(control => 'value' in control) : [];
    },
};
const control = name => explorerRoot.querySelector(`[data-${name}]`);
context.Ch06Advanced.mount(explorerRoot, 'explorer');
const boundary = context.CH06_EXPLORER_DATA.find(r =>
    r[0] === 'random' && r[1] === 42 && r[2] === 'descriptors_ridge' && r[3] === 'ESOL-1045');
assert.equal(boundary[8], 0.4);
control('low').onclick();
assert.equal(Number(control('maxt').value), 0.4);
assert.match(control('chart').innerHTML, /data-point="ESOL-1045"[^>]*fill="#bf794c"/);
control('term').value = 'ESOL-1045';
control('term').oninput();
assert.equal([...control('chart').innerHTML.matchAll(/data-point="([^"]+)"/g)].map(m => m[1]).join(), 'ESOL-1045');
assert.match(control('chart').innerHTML, /data-point="ESOL-1045"[^>]*fill="#bf794c"/);
assert.match(control('chart').innerHTML, /橙点 T ≤ 0\.40，绿点 T > 0\.40/);

console.log(JSON.stringify({headings:headings.length,localResources:checked,browserPredictionRows:context.CH06_EXPLORER_DATA.length,metricGroups:data.metrics.length,boundaryFixture:'ESOL-1045 retained and orange',staticAndDataChecks:'passed'},null,2));

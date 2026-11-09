/* Dependency-free logic/asset checks. This does not claim a real browser UI test. */
'use strict';
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),assert=require('node:assert/strict');
const base=path.resolve(__dirname,'../..'),read=p=>fs.readFileSync(path.join(base,p),'utf8');
const year='resources/annual/2026-2027',js=read('assets/js/ch15-section-labs.js');
const chapter=read('docs/ch15.md'),refs=read(year+'/references/ch15.md');
const labs=[...chapter.matchAll(/data-ch15-lab="(\d+)"/g)].map(m=>+m[1]);
assert.deepEqual(labs,[1,2,3,4,5,6,7,8]);
const headings=[...chapter.matchAll(/^### (15\.\d+\.\d+) /gm)].map(m=>m[1]);
assert.equal(headings.length,38);assert.equal(new Set(headings).size,38);
assert.equal([...refs.matchAll(/<a id="ref-\d+">/g)].length,34);
for(const m of chapter.matchAll(/\?id=(ref-\d+)/g))assert(refs.includes('id="'+m[1]+'"'),m[1]);
assert.equal([...read(year+'/questions/ch15.md').matchAll(/^## 题\d /gm)].length,3);
assert(read('index.html').includes('assets/js/ch15-section-labs.js'));
// Keep GitHub's native MathML on ordinary rows: mlabeledtr from \\tag stacks in Chromium.
for(const name of ['docs/ch15.md',year+'/presentations/ch15/course-paper.md']){
  const source=read(name),blocks=[...source.matchAll(/^\$\$\r?\n([\s\S]*?)\r?\n\$\$/gm)];
  assert.equal(blocks.length,7,`${name}: seven numbered display equations`);
  blocks.forEach((m,i)=>assert(m[1].includes('\\text{('+(i+1)+')}'),`${name}: equation number ${i+1}`));
  assert(!/\\tag\{|\\[{}]/.test(source),`${name}: portable numbering and set braces`);
  const prose=source.replace(/^\$\$\r?\n[\s\S]*?\r?\n\$\$/gm,'');
  const inline=[...prose.matchAll(/\$([^$\n]+)\$/g)];
  assert.equal(inline.length,4,`${name}: complete inline expressions`);
  for(const m of inline)assert(prose[m.index-1]===' '&&prose[m.index+m[0].length]===' ',`${name}: inline math boundaries`);
}
// Resolve the local links introduced by this chapter, not unrelated baseline pages.
const docs=['docs/ch15.md',year+'/README.md',year+'/questions/README.md',year+'/questions/ch15.md',year+'/references/README.md',year+'/references/ch15.md',year+'/presentations/ch15/README.md',year+'/presentations/ch15/course-paper.md',year+'/results/ch15/README.md'];
let checkedLinks=0,dualLinks=0;
for(const name of docs){
  const s=read(name),links=[...s.matchAll(/!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+'[^']*')?\)/g)].map(m=>({url:m[1],site:false}));
  assert(!/\]\(#\//.test(s),`${name}: use a root Markdown path or raw HTML for a Docsify page link`);
  links.push(...[...s.matchAll(/(?<![\w-])(?:href|src)="([^"]+)"/g)].map(m=>({url:m[1],site:false})));
  const siteLinks=[...s.matchAll(/data-ch15-site-href="([^"]+)"/g)];dualLinks+=siteLinks.length;
  links.push(...siteLinks.map(m=>({url:m[1],site:true})));
  for(const item of links){
    const link=item.url;
    if(/^(?:https?:|mailto:|data:|#(?!\/))/.test(link))continue;
    let target;
    if(link.startsWith('/'))target=link.slice(1).split('?')[0];
    else if(link.startsWith('#/')){assert(item.site,`${name}: GitHub fallback must target a file, not a Docsify route`);target=link.slice(2).split('?')[0];if(!path.extname(target))target+='.md';}
    else if(item.site)target=link.replace(/^\.\//,'').split(/[?#]/)[0];
    else target=path.posix.normalize(path.posix.join(path.posix.dirname(name),link.split(/[?#]/)[0]));
    assert(fs.existsSync(path.join(base,decodeURIComponent(target))),`${name} -> ${link} (${target})`);checkedLinks++;
  }
}
const pure=require(path.join(base,'assets/js/ch15-section-labs.js'));
assert.equal(pure.uncertainty(1,1,1),2);assert.equal(pure.uncertainty(1,1,-1),0);
assert(Math.abs(pure.uncertainty(1,1,0)-Math.SQRT2)<1e-12);
for(const t of [.2,1,4]){const p=pure.temperature([2,1,0],t);assert(Math.abs(p.reduce((a,b)=>a+b,0)-1)<1e-12);assert(p[0]>p[1]&&p[1]>p[2]);}
assert.throws(()=>pure.temperature([2,1,0],0));
for(const w of [0,.5,1]){const a=pure.attribution(w);assert.equal(a.first+a.second,1);assert.equal(a.prediction,1);}
const signal=pure.snv([2,4,8]);assert(Math.abs(signal.reduce((a,b)=>a+b))<1e-12);assert(signal[0]<0);
assert(signal.map(v=>Math.max(0,v)).reduce((a,b)=>a+b)>0);
// Minimal DOM test double for render/event wiring; layout and browser policy are not simulated.
class Element {
  constructor(n){this.dataset={ch15Lab:String(n)};this.controls={};this.feedback={textContent:'',innerHTML:''};this.form={events:{},addEventListener(k,v){this.events[k]=v;}};this.renders=0;}
  set innerHTML(s){this.html=s;this.renders++;this.controls={};
    for(const m of s.matchAll(/<input data-control="([^"]+)"[^>]*value="([^"]+)"/g))this.controls[m[1]]={value:m[2],initial:m[2],options:[m[2]]};
    for(const m of s.matchAll(/<select data-control="([^"]+)">([\s\S]*?)<\/select>/g)){const opts=[...m[2].matchAll(/value="([^"]+)"/g)].map(x=>x[1]);this.controls[m[1]]={value:opts[0],initial:opts[0],options:opts};}
  }
  get innerHTML(){return this.html;}
  querySelector(q){if(q==='form')return this.form;if(q==='.ch15-feedback')return this.feedback;const m=q.match(/data-control="([^"]+)"/);return m?this.controls[m[1]]:null;}
}
function environment(numbers,siteLinks=[]){
  const els=numbers.map(n=>new Element(n)),styles=[];
  const anchors=siteLinks.map(site=>({href:'../repository-file.md',getAttribute:k=>k==='data-ch15-site-href'?site:null,setAttribute(k,v){assert.equal(k,'href');this.href=v;}}));
  const document={head:{appendChild:s=>styles.push(s)},getElementById:id=>styles.find(s=>s.id===id),createElement:()=>({}),querySelectorAll:s=>s==='a[data-ch15-site-href]'?anchors:els};
  const window={document,setTimeout:cb=>cb(),$docsify:{plugins:[]}};vm.runInNewContext(js,{window});
  let registered;window.$docsify.plugins[0]({doneEach:fn=>{registered=fn;}});assert.equal(typeof registered,'function');registered();return {els,styles,anchors,registered};
}
const empty=environment([]);assert.equal(empty.styles.length,0);
const linkOnly=environment([],['#/code/ch15_exercises/README','./downloads/word/ch15-course-paper.docx']);
assert.deepEqual(linkOnly.anchors.map(a=>a.href),['#/code/ch15_exercises/README','./downloads/word/ch15-course-paper.docx']);
linkOnly.registered();assert.equal(linkOnly.styles.length,0);
const env=environment(labs);assert.equal(env.styles.length,1);assert.equal(env.els.filter(e=>e.html.includes('<iframe')).length,1);
for(const el of env.els){
  assert.equal(el.dataset.ch15Mounted,'true');const renders=el.renders;env.registered();assert.equal(el.renders,renders);
  if(el.dataset.ch15Lab==='3'){assert(el.html.includes('loading="lazy"'));assert(el.html.includes('title='));continue;}
  assert(el.html.includes('type="reset"'));assert(el.html.includes('aria-live="polite"'));assert(el.html.includes('迁移判断'));
  const output=()=>el.feedback.textContent+el.feedback.innerHTML,initial=output();
  assert(initial.length>30);
  for(const [key,c] of Object.entries(el.controls)){
    c.value=c.options.length>1?c.options[c.options.length-1]:String(+c.value+.1);
    el.form.events.input();assert(output().length>30);assert.notEqual(output(),initial,`lab ${el.dataset.ch15Lab}/${key}`);
    c.value=c.initial;el.form.events.reset();assert.equal(output(),initial);
  }
}
console.log(JSON.stringify({status:'passed',numbered_subsections:38,section_labs:8,bibliography:34,questions:3,checked_local_links:checkedLinks,dual_context_links:dualLinks,checks:['GitHub file fallbacks and Docsify destinations','assets and citation targets','numerical simulation invariants','Docsify mount and idempotence','input/change/reset event wiring','no module assets on other chapters'],real_browser_ui:'not covered by this check'},null,2));

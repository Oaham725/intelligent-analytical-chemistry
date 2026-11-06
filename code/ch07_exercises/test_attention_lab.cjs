/* Run from the repository root: node --test code/ch07_exercises/test_attention_lab.cjs */
const test = require('node:test');
const assert = require('node:assert/strict');
const {computeAttentionRow, taskFeedback} = require('../../assets/js/ch07-attention-lab.js');

function parameters(changes={}) {
  return {...{q:1,keys:[0,Math.log(3)],values:[2,6],mask:[false,false]},...changes};
}
function near(actual, expected, tolerance=1e-12) {
  assert.ok(Math.abs(actual-expected)<=tolerance, `${actual} differs from ${expected}`);
}

test('published hand calculation agrees with chapter and NumPy example', () => {
  const result=computeAttentionRow(parameters());
  near(result.weights[0],1/4); near(result.weights[1],3/4); near(result.output,5);
});
test('masking happens before renormalization, not by subtracting the value', () => {
  const result=computeAttentionRow(parameters({mask:[false,true]}));
  assert.deepEqual(result.weights,[1,0]); assert.equal(result.maskedScores[1],-Infinity);
  assert.equal(result.output,2);
});
test('changing V alone leaves weights unchanged and changes the weighted content', () => {
  const before=computeAttentionRow(parameters());
  const after=computeAttentionRow(parameters({values:[2,0]}));
  assert.deepEqual(after.weights,before.weights); near(after.output,0.5);
});
test('the masked value cannot influence the output', () => {
  const a=computeAttentionRow(parameters({mask:[false,true],values:[2,6]}));
  const b=computeAttentionRow(parameters({mask:[false,true],values:[2,-9]}));
  assert.equal(a.output,b.output);
});
test('zero query gives uniform weights for readable keys', () => {
  const result=computeAttentionRow(parameters({q:0}));
  assert.deepEqual(result.weights,[0.5,0.5]); assert.equal(result.output,4);
});
test('query sign changes which key receives more weight', () => {
  const result=computeAttentionRow(parameters({q:-1}));
  near(result.weights[0],0.75); near(result.weights[1],0.25); near(result.output,3);
});
test('a common score shift does not change softmax weights', () => {
  const shifted=computeAttentionRow(parameters({keys:[2,2+Math.log(3)]}));
  const original=computeAttentionRow(parameters());
  shifted.weights.forEach((value,i)=>near(value,original.weights[i])); near(shifted.output,5);
});
test('large finite scores remain finite after stable softmax', () => {
  const result=computeAttentionRow(parameters({q:1000,keys:[1000,-1000]}));
  assert.deepEqual(result.weights,[1,0]); assert.equal(result.output,2);
});
test('weighted output stays in the readable values interval', () => {
  for(const q of [-4,-1,0,1,4]) {
    const result=computeAttentionRow(parameters({q,values:[-3,7]}));
    near(result.weights[0]+result.weights[1],1);
    assert.ok(result.output>=-3 && result.output<=7);
  }
});
test('invalid metadata, nonfinite arithmetic and all-masked rows fail explicitly', () => {
  for(const changes of [{q:NaN},{keys:[1]},{values:[2,Infinity]},{mask:[false,0]}]) {
    assert.throws(()=>computeAttentionRow(parameters(changes)),TypeError);
  }
  assert.throws(()=>computeAttentionRow(parameters({q:1e308,keys:[1e308,1]})),RangeError);
  assert.throws(()=>computeAttentionRow(parameters({mask:[true,true]})),RangeError);
});
test('migration feedback distinguishes full-input classification from real-time forecasting', () => {
  assert.equal(taskFeedback('spectrum','all').kind,'correct');
  assert.equal(taskFeedback('forecast','observed').kind,'correct');
  assert.equal(taskFeedback('forecast','all').kind,'risk');
  assert.equal(taskFeedback('spectrum','observed').kind,'consider');
  assert.equal(taskFeedback('spectrum',null).kind,'incomplete');
});

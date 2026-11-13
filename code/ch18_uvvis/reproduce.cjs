'use strict';

const fs = require('node:fs');
const path = require('node:path');
const assert = require('node:assert/strict');
const lab = require('./model.cjs');

const directory = path.resolve(process.argv[2] || path.join(__dirname, 'data'));
fs.mkdirSync(directory, { recursive: true });

const input = lab.calibrationData();
const fit = lab.calibrate(input);
const normal = lab.experiment(lab.defaults, fit);
const blankFault = lab.experiment({ ...lab.defaults, fault: 'blank' }, fit);
const receiptFault = lab.experiment({ ...lab.defaults, fault: 'receipt' }, fit);
const smallBudget = lab.experiment({ ...lab.defaults, maxDose: 0.2 }, fit);

const { auto, reference } = normal;
assert.equal(input.standards.length, 18);
assert.equal(input.kinetics.length, 125);
assert.equal(auto.selected.doseMl, 0.3);
assert.equal(auto.receipt.actualMl, 0.294);
assert.equal(auto.receipt.volumeMl, 3.294);
assert.equal(auto.events.find(event => event.type === 'receipt').commandId,
  auto.events.find(event => event.type === 'command').commandId);
assert.equal(auto.receipt.beforeCvNmoles, auto.receipt.afterCvNmoles);
assert.ok(Math.abs(auto.receipt.afterA / auto.receipt.beforeA - 3 / 3.294) < 1e-12);
assert.equal(auto.confirmationTime, 275);
assert.equal(reference.confirmationTime, 415);
assert.equal(blankFault.auto.action, 'bad-reading');
assert.ok(!blankFault.auto.events.some(event => event.type === 'command'));
assert.equal(receiptFault.auto.action, 'receipt-lost');
assert.equal(receiptFault.auto.confirmationTime, null);
assert.ok(receiptFault.auto.samples.filter(row => row.time > 90).every(row => row.estimatedFraction === null));
assert.equal(smallBudget.auto.action, 'no-feasible');
const state = lab.makeState();
const advanced = lab.advance(state, 90, fit.rate);
assert.ok(Math.abs((state.oh - advanced.oh) - (state.cv - advanced.cv)) < 1e-17);
const exact = lab.advance(advanced, lab.targetDelay(advanced, state.cv * 0.2, fit.rate), fit.rate);
assert.ok(Math.abs(exact.cv - state.cv * 0.2) < 1e-17);

function thresholdPair(samples, fractionAt) {
  let consecutive = 0;
  for (const [index, sample] of samples.entries()) {
    const fraction = fractionAt(sample);
    consecutive = Number.isFinite(fraction) && fraction <= lab.config.target ? consecutive + 1 : 0;
    if (consecutive === lab.config.confirmSamples) {
      return [samples[index - consecutive + 1].time, sample.time];
    }
  }
  return [null, null];
}

// Compare the endpoint rules on the same default measurements and dose history.
const [initialSample] = auto.samples;
assert.ok(initialSample.net > 0 && initialSample.knownVolumeMl > 0);
assert.ok(auto.samples.every(sample =>
  Number.isFinite(sample.net) && Number.isFinite(sample.knownVolumeMl)));
const absorbanceRatio = sample => sample.net / initialSample.net;
const correctedRatio = sample => absorbanceRatio(sample) * sample.knownVolumeMl / initialSample.knownVolumeMl;
const endpoints = [
  ['net_absorbance_ratio', ...thresholdPair(auto.samples, absorbanceRatio)],
  ['volume_corrected_absorbance_ratio', ...thresholdPair(auto.samples, correctedRatio)],
  ['controller_cv_fraction', ...thresholdPair(auto.samples, sample => sample.estimatedFraction)]
];
assert.deepEqual(endpoints.map(row => row.slice(1)), [[255, 260], [270, 275], [270, auto.confirmationTime]]);

function writeCSV(name, headers, rows) {
  const cells = rows.map(row => row.map(value => value ?? '').join(','));
  fs.writeFileSync(path.join(directory, name), [headers.join(','), ...cells].join('\n') + '\n');
}
const fixed = value => value === null ? null : value.toFixed(8);

writeCSV('optical-standards.csv', ['cv_uM','repeat','a_raw','a_blank','a_net'],
  input.standards.map(row => [row.cvMicromolar,row.repeat,fixed(row.raw),fixed(row.blank),fixed(row.net)]));
writeCSV('kinetics-calibration.csv', ['batch','oh_mM','time_s','a_raw','a_blank','a_net'],
  input.kinetics.map(row => [row.batch,row.ohMm,row.time,fixed(row.raw),fixed(row.blank),fixed(row.net)]));
writeCSV('decision-plans.csv', ['dose_mL','planned_volume_mL','post_oh_mM','nominal_hit_s','slow_hit_s','feasible'],
  auto.candidates.map(row => [row.doseMl,fixed(row.volumeMl),fixed(row.ohMm),fixed(row.nominalTime),
    fixed(row.conservativeTime),row.allowed ? 1 : 0]));
writeCSV('default-timeseries.csv',
  ['time_s','a_raw_auto','a_blank_auto','a_net_auto','a_net_reference',
    'cv_fraction_estimated_auto','cv_fraction_estimated_reference','cv_fraction_simulated_auto',
    'cv_fraction_simulated_reference','known_volume_mL','estimated_oh_mM'],
  auto.samples.map((row, index) => [row.time,fixed(row.raw),fixed(row.blank),fixed(row.net),fixed(reference.samples[index].net),
    fixed(row.estimatedFraction),fixed(reference.samples[index].estimatedFraction),fixed(row.actualFraction),
    fixed(reference.samples[index].actualFraction),fixed(row.knownVolumeMl),fixed(row.estimatedOhMm)]));
writeCSV('endpoint-comparison.csv', ['method','first_sample_in_confirmed_pair_s','confirmation_s'], endpoints);
writeCSV('events.csv', ['case','time_s','event','value','command_id'],
  [['default',auto],['blank_lost',blankFault.auto],['receipt_lost',receiptFault.auto],['small_budget',smallBudget.auto]]
    .flatMap(([label, run]) => run.events.map(event => [label,event.time,event.type,event.value,event.commandId])));
const summary = {
  simulatedOnly: true,
  settings: normal.settings,
  calibration: fit,
  candidateCount: auto.candidates.length,
  selected: auto.selected,
  receipt: auto.receipt,
  confirmationTime: auto.confirmationTime,
  referenceTime: reference.confirmationTime,
  faultOutcomes: {
    blank: blankFault.auto.action,
    receipt: receiptFault.auto.action,
    smallBudget: smallBudget.auto.action
  }
};
fs.writeFileSync(path.join(directory, 'summary.json'), JSON.stringify(summary, null, 2) + '\n');
console.log(JSON.stringify(summary, null, 2));

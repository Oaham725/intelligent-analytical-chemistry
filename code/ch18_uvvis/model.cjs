'use strict';

const config = Object.freeze({
  dt: 5,
  duration: 480,
  decisionTime: 90,
  initialVolume: 0.003,
  volumeLimit: 0.0036,
  initialCV: 10e-6,
  initialOH: 0.010,
  stockOH: 0.100,
  target: 0.20,
  deliverFraction: 0.98,
  rateFraction: 0.94,
  confirmSamples: 2
});
const doseChoices = Object.freeze([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]);
const simulated = Object.freeze({ gain: 80000, rate: 0.4, wavelength: 590, temperature: 294 });
const defaults = Object.freeze({ deadline: 290, maxDose: 0.6, fault: 'none' });

function randomFor(seed) {
  let value = seed >>> 0;
  return () => {
    value = (Math.imul(value, 1664525) + 1013904223) >>> 0;
    return (value + 0.5) / 4294967296;
  };
}

function normal(random) {
  return Math.sqrt(-2 * Math.log(random())) * Math.cos(2 * Math.PI * random());
}

function makeState(oh = config.initialOH) {
  return { volume: config.initialVolume, cv: config.initialCV * config.initialVolume,
    oh: oh * config.initialVolume };
}

function addDose(state, doseMl) {
  const dv = doseMl / 1000;
  return { volume: state.volume + dv, cv: state.cv, oh: state.oh + config.stockOH * dv };
}

function advance(state, seconds, rate) {
  const smaller = Math.min(state.cv, state.oh) / state.volume;
  const larger = Math.max(state.cv, state.oh) / state.volume;
  if (seconds <= 0 || smaller <= 0) return { ...state };
  const difference = larger - smaller;
  const ratio = (smaller / larger) * Math.exp(-rate * difference * seconds);
  const remaining = difference < 1e-13
    ? smaller / (1 + rate * smaller * seconds)
    : difference * ratio / (1 - ratio);
  const extent = Math.max(0, smaller - remaining) * state.volume;
  return { volume: state.volume, cv: Math.max(0, state.cv - extent), oh: Math.max(0, state.oh - extent) };
}

function ideal(state, gain) {
  return gain * state.cv / state.volume;
}

function targetDelay(state, targetMoles, rate) {
  if (state.cv <= targetMoles) return 0;
  const a = state.cv / state.volume;
  const b = state.oh / state.volume;
  const g = targetMoles / state.volume;
  const d = b - a;
  if (g + d <= 0) return Infinity;
  return Math.abs(d) < 1e-13
    ? (1/g - 1/a) / rate
    : (Math.log(a/b) - Math.log(g/(g+d))) / (rate*d);
}

function measure(signal, time, random) {
  const baseline = 0.018 + 0.000075 * time;
  const raw = signal + baseline + 0.0026 * normal(random);
  const blank = baseline + 0.0016 * normal(random);
  return { raw, blank, net: raw - blank };
}

function calibrationData() {
  const random = randomFor(180314);
  const standards = [];
  for (const c of [0, 2, 4, 6, 8, 10]) {
    for (let repeat = 1; repeat <= 3; repeat++) {
      standards.push({ cvMicromolar: c, repeat, ...measure(simulated.gain * c * 1e-6, 0, random) });
    }
  }
  const kinetics = [];
  for (const [i, oh] of [0.008, 0.012, 0.016, 0.020, 0.025].entries()) {
    const initial = makeState(oh);
    const rng = randomFor(180500 + i * 13);
    for (let time = 0; time <= 240; time += 10) {
      const state = advance(initial, time, simulated.rate);
      kinetics.push({ batch: i + 1, ohMm: 1000 * oh, time, ...measure(ideal(state, simulated.gain), time, rng) });
    }
  }
  return { standards, kinetics };
}

function calibrate(data = calibrationData()) {
  let cc = 0, ca = 0;
  for (const row of data.standards) {
    const concentration = row.cvMicromolar * 1e-6;
    cc += concentration * concentration;
    ca += concentration * row.net;
  }
  const gain = ca / cc;
  function error(rate) {
    let sum = 0;
    for (const row of data.kinetics) {
      const initial = makeState(row.ohMm / 1000);
      const predicted = ideal(advance(initial, row.time, rate), gain);
      sum += (row.net - predicted) ** 2;
    }
    return sum;
  }
  let left = 0.15, right = 0.75;
  for (let i = 0; i < 56; i++) {
    const a = (2 * left + right) / 3;
    const b = (left + 2 * right) / 3;
    if (error(a) < error(b)) right = b;
    else left = a;
  }
  const rate = (left + right) / 2;
  return { gain, rate, rmse: Math.sqrt(error(rate) / data.kinetics.length) };
}

function hasReading(measurement) {
  return Number.isFinite(measurement.blank) && measurement.raw >= 0 &&
    measurement.raw <= 1.10 && measurement.net >= -0.012;
}

function assimilate(prediction, previousCv, initial, totalMl, reading, calibration) {
  if (!hasReading(reading)) return prediction;
  const observedMoles = reading.net * prediction.volume / calibration.gain;
  const estimate = 0.35 * prediction.cv + 0.65 * observedMoles;
  const cv = Math.min(previousCv, Math.max(0, estimate));
  const dosedOh = config.stockOH * totalMl / 1000;
  return { volume: prediction.volume, cv, oh: initial.oh + dosedOh - (initial.cv - cv) };
}

function plan(state, initialCv, calibration, settings) {
  return doseChoices.filter(doseMl => doseMl <= settings.maxDose + 1e-12)
    .map(doseMl => {
      const nominalState = addDose(state, doseMl);
      const lowerDeliveryState = addDose(state, doseMl * config.deliverFraction);
      const goal = initialCv * config.target;
      const nominalTime = config.decisionTime + targetDelay(nominalState, goal, calibration.rate);
      const conservativeTime = config.decisionTime +
        targetDelay(lowerDeliveryState, goal, config.rateFraction * calibration.rate);
      const confirmationMargin = config.confirmSamples * config.dt;
      return {
        doseMl, volumeMl: nominalState.volume * 1000,
        ohMm: 1000 * nominalState.oh / nominalState.volume,
        nominalTime, conservativeTime,
        allowed: nominalState.volume <= config.volumeLimit + 1e-12 &&
          conservativeTime + confirmationMargin <= settings.deadline
      };
    });
}

function run(calibration, settings = defaults, execute = true) {
  const initial = makeState();
  const target = initial.cv * config.target;
  const random = randomFor(180611);
  const samples = [];
  const events = [];
  let plant = { ...initial }, estimate = { ...initial };
  let twinValid = true;
  let totalDelivered = 0;
  let confirmationTime = null;
  let confirmations = 0;
  let action = 'monitor';
  let candidates = [];
  let selected = null;
  let receipt = null;
  const log = (time, type, value = null, commandId = null) => events.push({ time, type, value, commandId });

  log(0, 'start');
  for (let time = 0; time <= config.duration; time += config.dt) {
    if (time > 0) {
      plant = advance(plant, config.dt, simulated.rate);
      const previousCv = estimate.cv;
      estimate = advance(estimate, config.dt, calibration.rate);
      const measurement = measure(ideal(plant, simulated.gain), time, random);
      if (settings.fault === 'blank' && time === config.decisionTime) {
        measurement.blank = null;
        measurement.net = null;
      }
      if (twinValid) estimate = assimilate(estimate, previousCv, initial, totalDelivered, measurement, calibration);
      addSample(time, measurement);
      if (time === config.decisionTime && execute) handleDecision(time, measurement);
    } else {
      addSample(time, measure(ideal(plant, simulated.gain), time, random));
    }
  }

  function addSample(time, measurement) {
    const valid = twinValid && hasReading(measurement);
    const fraction = twinValid ? estimate.cv / initial.cv : null;
    if (valid && estimate.cv <= target) confirmations++;
    else confirmations = 0;
    if (confirmationTime === null && confirmations >= config.confirmSamples) {
      confirmationTime = time;
      log(time, 'confirmed');
    }
    samples.push({ time, ...measurement,
      actualFraction: plant.cv / initial.cv,
      estimatedFraction: fraction,
      knownVolumeMl: twinValid ? 1000 * estimate.volume : null,
      estimatedOhMm: twinValid ? 1000 * estimate.oh / estimate.volume : null
    });
  }

  function handleDecision(time, measurement) {
    log(time, 'read');
    if (!hasReading(measurement)) {
      action = 'bad-reading';
      log(time, 'bad-reading');
      return;
    }
    candidates = plan(estimate, initial.cv, calibration, settings);
    log(time, 'plan');
    selected = candidates.find(candidate => candidate.allowed) ?? null;
    if (!selected) {
      action = 'no-feasible';
      log(time, 'no-feasible');
      return;
    }
    if (selected.doseMl === 0) {
      action = 'no-dose';
      log(time, 'no-dose');
      return;
    }
    const requestedMl = selected.doseMl;
    const actualMl = requestedMl * config.deliverFraction;
    const commandId = 'dose-090';
    log(time, 'command', requestedMl, commandId);
    plant = addDose(plant, actualMl);
    if (settings.fault === 'receipt') {
      twinValid = false;
      action = 'receipt-lost';
      log(time, 'receipt-lost', null, commandId);
      return;
    }
    const before = estimate;
    totalDelivered += actualMl;
    estimate = addDose(estimate, actualMl);
    receipt = { time, commandId, requestedMl, actualMl, volumeMl: estimate.volume * 1000,
      beforeOhMm: before.oh / before.volume * 1000, afterOhMm: estimate.oh / estimate.volume * 1000,
      beforeA: ideal(before, calibration.gain), afterA: ideal(estimate, calibration.gain),
      beforeCvNmoles: before.cv * 1e9, afterCvNmoles: estimate.cv * 1e9 };
    action = 'dosed';
    log(time, 'receipt', actualMl, commandId);
    log(time, 'sync', receipt.volumeMl, commandId);
  }

  return { candidates, selected, receipt, action, confirmationTime, events, samples };
}

function experiment(settings = defaults, calibration = calibrate()) {
  const reference = run(calibration, { ...settings, fault: 'none' }, false);
  return { settings, calibration, auto: run(calibration, settings), reference };
}

const lab = Object.freeze({ config, simulated, defaults, doseChoices, makeState, addDose,
  advance, ideal, targetDelay, calibrationData, calibrate, plan, experiment });
if (typeof module !== 'undefined' && module.exports) module.exports = lab;

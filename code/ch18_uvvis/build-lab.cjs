'use strict';

const fs = require('node:fs');
const path = require('node:path');

const destination = path.resolve(process.argv[2] || path.join(__dirname, '../../assets/labs/g18/index.html'));
const original = fs.readFileSync(destination, 'utf8');
const model = fs.readFileSync(path.join(__dirname, 'model.cjs'), 'utf8').trim();
const block = /\/\/ BEGIN SHARED G18 PHYSICAL MODEL[\s\S]*?\/\/ END SHARED G18 PHYSICAL MODEL/;
if (!block.test(original)) throw new Error('The HTML file has no G18 model block.');
fs.writeFileSync(destination, original.replace(block, () =>
  '// BEGIN SHARED G18 PHYSICAL MODEL\n' + model + '\n// END SHARED G18 PHYSICAL MODEL'));

// Runs the lab engine (lab/minibatch.js) on examples/data and compares every shared number with the Python run
// (examples/out/python-result.json). Also checks that lab/index.html embeds the same default corpus and config.
// usage: node films/minibatch-gradient-20261023/lab/check.cjs     exit 0 = match, 1 = mismatch
const fs = require('fs'), path = require('path');
const MB = require('./minibatch.js');
const here = __dirname, ex = path.join(here, '..', 'examples');
const corpus = fs.readFileSync(path.join(ex, 'data', 'corpus.txt'), 'utf8');
const config = fs.readFileSync(path.join(ex, 'data', 'config.txt'), 'utf8');
const py = JSON.parse(fs.readFileSync(path.join(ex, 'out', 'python-result.json'), 'utf8'));
const js = MB.run(corpus, MB.parseConfig(config));

let n = 0, worst = 0;
const bad = [];
function cmp(a, b, p) {  // b = lab value; every key it has must match Python
  if (Array.isArray(b)) { if (!Array.isArray(a) || a.length !== b.length) return bad.push(p + ' length'); b.forEach((x, i) => cmp(a[i], x, `${p}[${i}]`)); return; }
  if (b && typeof b === 'object') { for (const k of Object.keys(b)) { if (!(k in a)) { bad.push(p + '.' + k + ' missing in python'); continue; } cmp(a[k], b[k], p + '.' + k); } return; }
  if (typeof b === 'number') { n++; const d = Math.abs(a - b); worst = Math.max(worst, d); if (!(d <= 1e-12)) bad.push(`${p}: python ${a} lab ${b}`); return; }
  if (a !== b) bad.push(`${p}: python ${a} lab ${b}`);
}
cmp(py, js, '');
const html = fs.readFileSync(path.join(here, 'index.html'), 'utf8');
const embedded = /<textarea id="corpus"[^>]*>([\s\S]*?)<\/textarea>/.exec(html);
if (!embedded || embedded[1].trim() !== corpus.trim()) bad.push('index.html default corpus differs from examples/data/corpus.txt');
const cfg = MB.parseConfig(config);
for (const [id, v] of [['lr', cfg.learning_rate], ['seed', cfg.seed], ['batch', cfg.walkthrough_batch], ['epochs', cfg.curve_epochs]]) {
  const m = new RegExp(`id="${id}"[^>]*value="([^"]+)"`).exec(html);
  if (!m || Number(m[1]) !== v) bad.push(`index.html default ${id} ${m && m[1]} != config ${v}`);
}
console.log(JSON.stringify({ check: 'lab engine vs python-result.json', numbersCompared: n, worstAbsDiff: worst, mismatches: bad.slice(0, 10), pass: !bad.length }, null, 1));
process.exit(bad.length ? 1 : 0);

// Runs the practice page's core logic (the <script id="segtree-core"> block of index.html, unchanged) in node and
// compares it with the example program's real results: examples/expected_output.txt, examples/random-expected.txt
// and every visit / update step in data/trace.json (written from examples/segment_tree.py).
// usage: node films/segment-tree-20261023/practice/check_core.cjs   → prints JSON, exit 0 PASS / 1 FAIL
'use strict';
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const FILM = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(__dirname, 'index.html'), 'utf8');
const m = html.match(/<script id="segtree-core">([\s\S]*?)<\/script>/);
if (!m) { console.log(JSON.stringify({ pass: false, error: 'segtree-core script not found' })); process.exit(1); }
const sandbox = {};
sandbox.globalThis = sandbox;
vm.runInNewContext(m[1], sandbox);
const S = sandbox.SegTree;
const read = p => fs.readFileSync(path.join(FILM, p), 'utf8');
const lines = s => s.trim().split('\n');
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

const checks = [];
const check = (name, ok, detail) => checks.push({ name, pass: !!ok, ...(ok ? {} : { detail }) });

const ex = S.runText(read('examples/input.txt'));
check('input.txt outputs = expected_output.txt', same(ex, lines(read('examples/expected_output.txt'))), ex);
const rnd = S.runText(read('examples/random-input.txt'));
check('random-input.txt outputs = random-expected.txt', same(rnd, lines(read('examples/random-expected.txt'))), rnd.slice(0, 5));

const tr = JSON.parse(read('data/trace.json'));
const T = S.build(tr.array);
check('built tree = trace nodes', tr.nodes.every(d => T.tree[d.node] === d.value), null);
tr.ops.forEach((op, k) => {
  if (op.op === 'query') {
    const r = S.query(T, op.l, op.r);
    check(`op ${k} query ${op.l} ${op.r}: answer`, r.answer === op.answer, r.answer);
    check(`op ${k} query ${op.l} ${op.r}: visits`, same(r.visits.map(v => [v.node, v.start, v.end, v.kind, v.ret]), op.visits.map(v => [v.node, v.start, v.end, v.kind, v.ret])), r.visits);
  } else {
    const r = S.update(T, op.i, op.x);
    check(`op ${k} update ${op.i} ${op.x}: path`, same(r.path.map(p => [p.node, p.start, p.end, p.before, p.after]), op.path.map(p => [p.node, p.start, p.end, p.before, p.after])), r.path);
    check(`op ${k} update: tree after`, op.nodesAfter.every(d => T.tree[d.node] === d.value), null);
  }
});
check('layout = trace node intervals', same(S.layout(tr.n).map(d => [d.node, d.start, d.end, d.depth]), tr.nodes.map(d => [d.node, d.start, d.end, d.depth])), null);

const pass = checks.every(c => c.pass);
console.log(JSON.stringify({ pass, checks }, null, 1));
process.exit(pass ? 0 : 1);

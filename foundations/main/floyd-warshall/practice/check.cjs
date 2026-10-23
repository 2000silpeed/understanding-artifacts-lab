// Node 확인용: practice/fw.js 가 Python 예제와 같은 값을 내는지, 연습 문제 정답이 실제 계산과 맞는지.
//   node practice/check.cjs report <graph.txt>   → examples/floyd_warshall.py --json 과 비교할 JSON
//   node practice/check.cjs exercises            → 연습 문제마다 { id, stated, computed, ok } (모두 맞으면 exit 0)
const fs = require('fs');
const path = require('path');
const FW = require('./fw.js');
const EX = require('./exercises.js');

const [cmd, file] = process.argv.slice(2);
if (cmd === 'report') {
  const g = FW.parseGraph(fs.readFileSync(file, 'utf8'));
  process.stdout.write(JSON.stringify(FW.report(g, path.basename(file)), null, 1) + '\n');
} else if (cmd === 'exercises') {
  const rows = EX.exercises.map(e => {
    const computed = EX.answer(FW, e);
    return { id: e.id, stated: e.answer, computed, ok: computed === e.answer };
  });
  process.stdout.write(JSON.stringify(rows, null, 1) + '\n');
  process.exit(rows.every(r => r.ok) ? 0 : 1);
} else {
  console.error('usage: node practice/check.cjs report <graph.txt> | exercises');
  process.exit(2);
}

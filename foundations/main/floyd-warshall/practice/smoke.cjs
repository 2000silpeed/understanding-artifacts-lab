// 실습 HTML 브라우저 확인 (headless Chrome, puppeteer):
//   node films/floyd-warshall-20261023/practice/smoke.cjs [screenshot.png]
// 페이지 오류 없음, 처음 표 = 초기 표, "한 칸 비교" 1번 뒤 안내문, "끝까지" 뒤 표 = trace.json final,
// 경로 B→A, 실수 토글의 빨간 칸, 음수 사이클 예의 대각선 경고를 확인하고 JSON 한 줄을 출력한다. 하나라도 틀리면 exit 1.
const path = require('path');
const fs = require('fs');
const puppeteer = require('puppeteer-core');
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'; // same lookup as pipeline/render.cjs

const HERE = __dirname;
const trace = JSON.parse(fs.readFileSync(path.join(HERE, '..', 'trace.json'), 'utf8'));
const cell = x => (x === null ? '∞' : String(x));

(async () => {
  const browser = await puppeteer.launch({ headless: true, executablePath: CHROME, args: ['--allow-file-access-from-files'] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 1400 });
  const errors = [];
  page.on('pageerror', e => errors.push(String(e)));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto('file://' + path.join(HERE, 'index.html'));
  const table = () => page.$$eval('#table tr', trs => trs.slice(1).map(tr => [...tr.querySelectorAll('td')].map(td => td.textContent)));
  const checks = {};
  checks.initial = JSON.stringify(await table()) === JSON.stringify(trace.initial.map(r => r.map(cell)));
  await page.click('#step');
  checks.firstStep = (await page.$eval('#now', e => e.textContent)).includes('경유지 A');
  await page.click('#all');
  checks.final = JSON.stringify(await table()) === JSON.stringify(trace.final.map(r => r.map(cell)));
  checks.finalText = (await page.$eval('#now', e => e.textContent)).includes(`바뀐 칸 ${trace.rounds.reduce((a, r) => a + r.changes.length, 0)}개`);
  await page.select('#from', '1');
  await page.select('#to', '0');
  checks.pathBA = (await page.$eval('#pathText', e => e.textContent)) === `${trace.paths.BA.nodes.join(' → ')} (거리 ${trace.paths.BA.dist})`;
  if (process.argv[2]) await page.screenshot({ path: process.argv[2], fullPage: false });
  await page.click('#wrong');
  checks.wrongCells = JSON.stringify(await page.$$eval('#table td.wrong', tds => tds.map(td => td.textContent))) === JSON.stringify(trace.wrongOrder.diff.map(d => cell(d.wrong)));
  await page.click('#wrong');
  await page.click('#loadNeg');
  await page.click('#all');
  checks.negative = (await page.$eval('#now', e => e.textContent)).includes('음수 사이클');
  await browser.close();
  checks.noPageErrors = errors.length === 0;
  const ok = Object.values(checks).every(Boolean);
  console.log(JSON.stringify({ ok, checks, errors }));
  process.exit(ok ? 0 : 1);
})().catch(e => { console.error(e); process.exit(1); });

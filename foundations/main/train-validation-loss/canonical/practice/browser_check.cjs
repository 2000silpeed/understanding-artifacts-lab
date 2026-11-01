// usage: node films/<id>/practice/browser_check.cjs practice/index.html <shot.png> <out.json>
// Loads the practice page in headless Chrome (network blocked), clicks through it, saves a screenshot.
const puppeteer = require('puppeteer-core'); const path = require('path'); const fs = require('fs');
const [page_, shot, out] = process.argv.slice(2);
(async () => {
  const b = await puppeteer.launch({ headless: true, executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' });
  const p = await b.newPage(); await p.setViewport({ width: 1100, height: 900 });
  const errors = [], requests = [];
  await p.setRequestInterception(true);
  p.on('request', r => { if (!r.url().startsWith('file:')) { requests.push(r.url()); r.abort(); } else r.continue(); });
  p.on('pageerror', e => errors.push(String(e))); p.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await p.goto('file://' + path.resolve(page_));
  const r = {};
  r.loss_at_half = await p.$eval('#lv', e => e.textContent);
  r.step550 = await p.evaluate(() => [document.getElementById('tv').textContent, document.getElementById('vv').textContent]);
  await p.click('#stop'); r.verdict = await p.$eval('#verdict', e => e.textContent);
  await p.click('#b-large'); r.large550 = await p.evaluate(() => [document.getElementById('tv').textContent, document.getElementById('vv').textContent]);
  await p.click('#b-small');
  const btns = await p.$$('#quiz tbody button'); for (const x of btns.filter((_, i) => i % 2 === 1)) await x.click();
  r.quiz = await p.$$eval('#quiz tbody tr', rows => rows.map(tr => tr.lastChild.textContent));
  r.probeRows = await p.$$eval('#probe tbody tr', rows => rows.map(tr => tr.textContent));
  await p.screenshot({ path: shot, fullPage: true });
  r.errors = errors; r.externalRequests = requests;
  fs.writeFileSync(out, JSON.stringify(r, null, 1)); console.log(JSON.stringify(r)); await b.close();
  process.exit(errors.length || requests.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });

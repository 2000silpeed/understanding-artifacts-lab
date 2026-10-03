#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');
const http = require('http');
const { spawn, execFileSync } = require('child_process');

function loadPlaywright() {
  const candidates = [
    process.env.PLAYWRIGHT_PATH,
    'playwright'
  ].filter(Boolean);
  try { candidates.push(path.join(execFileSync('npm', ['root', '-g'], { encoding: 'utf8' }).trim(), 'playwright')); } catch (error) { /* npm may not be available */ }
  for (const candidate of candidates) {
    try { return require(candidate); } catch (error) { /* try next */ }
  }
  throw new Error('Playwright not found. Set PLAYWRIGHT_PATH or install playwright.');
}
const { chromium } = loadPlaywright();
const ROOT = __dirname;
const PORT = Number(process.env.PORT || 4173);
const PAGE_URL = `http://127.0.0.1:${PORT}/index.html`;
const reportPath = path.join(ROOT, 'tests', 'web-latest.json');
const screenshotDir = path.join(ROOT, 'screenshots');
fs.mkdirSync(path.join(ROOT, 'tests'), { recursive: true });
fs.mkdirSync(screenshotDir, { recursive: true });

function nearly(a, b, eps = 1e-10) { return Math.abs(a - b) <= eps; }
function assert(condition, message) { if (!condition) throw new Error(message); }
function startServer() {
  const mime={'.html':'text/html','.svg':'image/svg+xml','.woff':'font/woff','.mp4':'video/mp4','.md':'text/plain','.json':'application/json'};
  const server=http.createServer((req,res)=>{
    let file;try{file=path.resolve(ROOT,'.'+decodeURIComponent(new URL(req.url,'http://localhost').pathname));}catch(e){res.writeHead(400);res.end();return;}
    if(!file.startsWith(ROOT+path.sep)||!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);res.end('Not found');return;}
    const size=fs.statSync(file).size,type=mime[path.extname(file)]||'application/octet-stream';
    const range=(req.headers.range||'').match(/^bytes=(\d+)-(\d*)$/);
    if(range){const start=Number(range[1]),end=range[2]?Math.min(size-1,Number(range[2])):size-1;if(start>end){res.writeHead(416);res.end();return;}res.writeHead(206,{'Content-Type':type,'Content-Range':`bytes ${start}-${end}/${size}`,'Content-Length':end-start+1,'Accept-Ranges':'bytes'});fs.createReadStream(file,{start,end}).pipe(res);}
    else{res.writeHead(200,{'Content-Type':type,'Content-Length':size,'Accept-Ranges':'bytes'});fs.createReadStream(file).pipe(res);}
  });
  return new Promise((resolve,reject)=>{server.once('error',reject);server.listen(PORT,'127.0.0.1',()=>resolve(server));});
}
async function stopServer(server) { if(server){const done=new Promise(resolve=>server.close(resolve));server.closeAllConnections();await done;} }

(async () => {
  const started = new Date().toISOString();
  const checks = [];
  const failures = [];
  let server, browser;
  const pass = (name, detail) => { checks.push({ name, pass: true, detail }); };
  try {
    for (const required of ['index.html','diagram.svg','writing.md','facts.json','package.json','assets/next-token-lab.woff','video/video.mp4','video/script.md']) assert(fs.existsSync(path.join(ROOT, required)), `missing ${required}`);
    pass('artifact files', 'index.html, diagram.svg, writing.md, facts.json, package.json present');
    const facts = JSON.parse(fs.readFileSync(path.join(ROOT, 'facts.json'), 'utf8'));
    assert(facts.logits.join(',') === '2,1,0.3,-0.4', 'facts logits mismatch');
    pass('facts.json shared inputs', 'context, four candidates, logits, caveats loaded');

    server = await startServer();
    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1440, height: 1100 }, reducedMotion: 'reduce' });
    const consoleErrors = []; const pageErrors = []; const externalRequests = [];
    page.on('console', msg => { if (msg.type() === 'error') consoleErrors.push(msg.text()); });
    page.on('pageerror', error => pageErrors.push(String(error)));
    page.on('request', req => { const u = new URL(req.url()); if ((u.protocol === 'http:' || u.protocol === 'https:') && u.hostname !== '127.0.0.1' && u.hostname !== 'localhost') externalRequests.push(req.url()); });
    await page.goto(PAGE_URL, { waitUntil: 'networkidle' });
    await page.evaluate(()=>document.fonts.ready);
    assert(await page.title() === 'Next-token lab — 출력이 만들어지는 순간', 'unexpected document title');
    pass('offline page load', 'loaded over local HTTP with no external dependency requests');

    const numbers = await page.evaluate(() => {
      const base = window.Lab.softmax([2,1,.3,-.4], 1);
      const filtered = window.Lab.topP(base, .8);
      const sampleA = window.Lab.sampleIndex(filtered.probabilities, 42);
      const sampleB = window.Lab.sampleIndex(filtered.probabilities, 42);
      return { base, filtered, sampleA, sampleB, greedy: window.Lab.greedyIndex([2,1,.3,-.4]), sum: filtered.probabilities.reduce((a,b)=>a+b,0) };
    });
    assert(numbers.base.every(Number.isFinite) && nearly(numbers.base.reduce((a,b)=>a+b,0), 1), 'softmax does not sum to one');
    assert(numbers.filtered.keep.join(',') === '0,1', `top-p keep mismatch: ${numbers.filtered.keep}`);
    assert(nearly(numbers.filtered.mass, 0.8334218875890236, 1e-12), `top-p mass mismatch: ${numbers.filtered.mass}`);
    assert(nearly(numbers.filtered.probabilities[0], .7310585786300049, 1e-12), 'renormalized mat mismatch');
    assert(nearly(numbers.filtered.probabilities[1], .2689414213699951, 1e-12), 'renormalized floor mismatch');
    assert(nearly(numbers.sum, 1), 'filtered probability sum mismatch');
    assert(numbers.sampleA.index === numbers.sampleB.index && numbers.sampleA.draw === numbers.sampleB.draw, 'seed reproducibility failed');
    assert(numbers.greedy === 0, 'greedy argmax mismatch');
    pass('window.Lab numerical oracle', 'stable softmax, prefix threshold, renormalization, greedy, seeded draw all pass');

    assert(await page.locator('#sum-metric').textContent() === '1.000', 'initial UI sum mismatch');
    assert(await page.locator('#kept-metric').textContent() === '2 / 4', 'initial UI top-p kept count mismatch');
    assert((await page.locator('#selected-token').textContent()).includes('mat'), 'initial selected token mismatch');
    pass('initial lab UI', 'default T=1, top-p=.8, seeded sample renders');

    await page.locator('#top-p').fill('0.95');
    await page.locator('#top-p').dispatchEvent('input');
    assert(await page.locator('#kept-metric').textContent() === '4 / 4', 'top-p slider did not update retained set');
    await page.locator('#temperature').fill('2');
    await page.locator('#temperature').dispatchEvent('input');
    const broadSum = await page.locator('#sum-metric').textContent();
    assert(broadSum === '1.000', 'temperature update broke normalization');
    pass('live controls', 'top-p and temperature update the bars and metrics');

    await page.locator('[data-choice="greedy"]').click();
    assert((await page.locator('#selected-token').textContent()).includes('mat'), 'greedy selection not mat');
    assert((await page.locator('#draw-value').textContent()).includes('argmax'), 'greedy readout not explicit');
    await page.locator('#reset').click();
    assert(await page.locator('#kept-metric').textContent() === '2 / 4', 'reset did not restore top-p');
    assert((await page.locator('#status').textContent()).includes('seed 42'), 'reset did not restore seed');
    pass('greedy and reset', 'greedy is separate from sampling and reset restores defaults');

    for (const mode of ['diagram','writing','video','lab']) {
      await page.locator(`[data-mode="${mode}"]`).click();
      assert(await page.locator(`#mode-${mode}`).evaluate(el => el.classList.contains('active')), `${mode} mode not active`);
    }
    assert(await page.locator('svg[role="img"]').count() === 1, 'causal SVG missing');
    assert(await page.locator('video[src="video/video.mp4"]').count() === 1, 'relative video slot missing');
    pass('four modes', 'lab, causal diagram, writing comparison, and relative video slot are navigable');

    await page.screenshot({ path: path.join(screenshotDir, 'lab-desktop.png'), fullPage: true });
    await page.locator('[data-mode="diagram"]').click();
    await page.screenshot({ path: path.join(screenshotDir, 'diagram-desktop.png'), fullPage: true });
    const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
    await mobile.goto(PAGE_URL, { waitUntil: 'networkidle' });
    const mobileLayout = await mobile.evaluate(() => ({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth }));
    assert(mobileLayout.scrollWidth <= mobileLayout.clientWidth + 1, `mobile horizontal overflow ${JSON.stringify(mobileLayout)}`);
    await mobile.screenshot({ path: path.join(screenshotDir, 'lab-mobile-390.png'), fullPage: true });
    pass('responsive and reduced motion', `390px layout has no page overflow (${mobileLayout.clientWidth}px)`);
    await mobile.close();

    assert(consoleErrors.length === 0, `console errors: ${consoleErrors.join('; ')}`);
    assert(pageErrors.length === 0, `page errors: ${pageErrors.join('; ')}`);
    assert(externalRequests.length === 0, `external requests: ${externalRequests.join('; ')}`);
    pass('runtime health', 'zero console/page errors and zero external requests');

    const report = { schema_version: 1, started, finished: new Date().toISOString(), url: PAGE_URL, status: 'passed', checks, failures, screenshots: ['screenshots/lab-desktop.png','screenshots/diagram-desktop.png','screenshots/lab-mobile-390.png'], notes: ['Deterministic invariants are asserted. No comprehension or factual-accuracy claim is made.', 'Final test requires actual MP4 presence and tolerates zero console errors. Separate parent checks exercise media playback and fonts.'] };
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
    console.log(JSON.stringify({ status: report.status, checks: checks.length, failures: 0, report: reportPath, screenshots: report.screenshots }, null, 2));
  } catch (error) {
    failures.push({ message: error.message, stack: error.stack });
    const report = { schema_version: 1, started, finished: new Date().toISOString(), url: PAGE_URL, status: 'failed', checks, failures };
    fs.writeFileSync(reportPath, JSON.stringify(report, null, 2) + '\n');
    console.error(JSON.stringify(report, null, 2));
    process.exitCode = 1;
  } finally {if(browser)await browser.close();if(server)await stopServer(server);}
})();

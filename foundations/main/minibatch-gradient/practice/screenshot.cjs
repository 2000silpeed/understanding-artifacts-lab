// Opens lab/index.html in headless Chrome (file://, no network), records page errors and saves a full-page PNG.
// usage: node films/minibatch-gradient-20261023/lab/screenshot.cjs [out.png]   exit 0 = no page errors
const path = require('path');
const puppeteer = require(path.resolve(__dirname, '../../../node_modules/puppeteer-core'));
const CHROME = process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
(async () => {
  const out = process.argv[2] || path.join(__dirname, '..', 'qa', 'lab-screenshot.png');
  const browser = await puppeteer.launch({ headless: true, executablePath: CHROME });
  const errors = [], requests = [];
  try {
    const page = await browser.newPage();
    await page.setViewport({ width: 1200, height: 900 });
    page.on('pageerror', e => errors.push(String(e)));
    page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
    page.on('request', r => { if (!r.url().startsWith('file:')) requests.push(r.url()); });
    await page.goto('file://' + path.join(__dirname, 'index.html'));
    const status = await page.$eval('#status', e => e.textContent);
    const fullLoss = await page.$eval('#stepView', e => (e.textContent.match(/전체 손실 ([\d.]+) → ([\d.]+)/) || []).slice(1));
    await page.screenshot({ path: out, fullPage: true });
    console.log(JSON.stringify({ status, firstStepFullLoss: fullLoss, errors, externalRequests: requests, screenshot: path.relative(process.cwd(), out) }, null, 1));
  } finally { await browser.close(); }
  process.exit(errors.length || requests.length ? 1 : 0);
})().catch(e => { console.error(e); process.exit(1); });

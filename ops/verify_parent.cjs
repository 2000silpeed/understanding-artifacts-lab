const fs=require('fs'),path=require('path');
let pw;try{pw=require(process.env.PLAYWRIGHT_PATH||'playwright');}catch(e){pw=require(path.join(require('child_process').execFileSync('npm',['root','-g'],{encoding:'utf8'}).trim(),'playwright'));}
const {chromium}=pw;
const ROOT=path.resolve(__dirname,'..');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
 const reports=[];
 try{
  await page.goto('file://'+ROOT+'/index.html');
  const oracle=JSON.parse(fs.readFileSync(ROOT+'/tests/python-oracle.json'));
  const results=await page.evaluate(rows=>rows.map(r=>{
   const base=Lab.softmax(Lab.LOGITS,r.temperature),f=Lab.topP(base,r.top_p);
   const close=(x,y)=>Math.abs(x-y)<1e-12;
   return {t:r.temperature,p:r.top_p,pass:base.every((v,i)=>close(v,r.base[i]))&&f.keep.join(',')===r.keep.join(',')&&f.probabilities.every((v,i)=>close(v,r.probabilities[i]))};
  }),oracle.rows);
  reports.push({name:'python_oracle_25_cases',passed:results.every(x=>x.pass),cases:results});
  const special=await page.evaluate(()=>({extreme:Lab.softmax([10000,9999,-10000],1),ties:Lab.topP([.25,.25,.25,.25],.5).keep}));
  reports.push({name:'extreme_logits_and_ties',passed:Math.abs(special.extreme[0]-oracle.special_cases.extreme_logits[0])<1e-12&&special.ties.join(',')==='0,1',actual:special});
  const samples=await page.evaluate(()=>{const p=Lab.topP(Lab.softmax(Lab.LOGITS,1),.8).probabilities;const n=10000,counts=[0,0,0,0];for(let s=0;s<n;s++)counts[Lab.sampleIndex(p,s).index]++;return {n,counts,expected:p}});
  reports.push({name:'seeded_sampling_smoke_10000',passed:samples.counts[2]===0&&samples.counts[3]===0&&samples.counts.every((n,i)=>Math.abs(n/samples.n-samples.expected[i])<.025),actual:samples,limit:'Deterministic PRNG smoke, not statistical proof of correctness'});
  const bars=await page.locator('.bar-fill').evaluateAll(els=>els.map(e=>{const r=e.getBoundingClientRect();return {w:r.width,h:r.height,prob:parseFloat(e.style.width)}}));
  reports.push({name:'visible_kept_probability_bars',passed:bars.filter(b=>b.prob>0).every(b=>b.w>2&&b.h>2),actual:bars});
  await page.setViewportSize({width:390,height:844});
  const tabs=await page.locator('[data-mode]').evaluateAll(els=>els.map(e=>{const r=e.getBoundingClientRect();return {mode:e.dataset.mode,left:r.left,right:r.right}}));
  reports.push({name:'four_modes_visible_mobile',passed:tabs.every(x=>x.left>=0&&x.right<=390),actual:tabs});
  await page.evaluate(()=>document.fonts.ready);
  const fonts=await page.evaluate(()=>Array.from(document.fonts).map(f=>({family:f.family,status:f.status})));
  reports.push({name:'offline_Korean_font_loaded',passed:fonts.some(f=>f.family==='NextTokenLabSubset'&&f.status==='loaded'),actual:fonts});
  await page.locator('#reset').click();
  const sampleMarker=await page.locator('#sample-ribbon .ribbon-marker').evaluate(e=>parseFloat(e.style.left)/100);
  const expectedDraw=await page.evaluate(()=>Lab.seededUniform(42));
  reports.push({name:'sampling_marker_on_normalized_distribution',passed:Math.abs(sampleMarker-expectedDraw)<1e-6&&(await page.locator('#sample-ribbon .ribbon-segment').count())===2,actual:{sampleMarker,expectedDraw}});
  await page.locator('#top-p').fill('0.05');await page.locator('#top-p').dispatchEvent('input');
  reports.push({name:'dynamic_retained_set_legend',passed:!(await page.locator('#ribbon .ribbon-legend').textContent()).includes('floor')&&(await page.locator('#sample-ribbon .ribbon-segment').count())===1});
  await page.locator('#reset').click();await page.locator('#temperature').focus();await page.keyboard.press('ArrowRight');
  reports.push({name:'keyboard_range_control',passed:Math.abs(Number(await page.locator('#temperature').inputValue())-1.05)<1e-12});
  await page.locator('#reset').click();
  await page.evaluate(()=>{window.lastScrollBehavior=null;const native=Element.prototype.scrollIntoView;Element.prototype.scrollIntoView=function(o){window.lastScrollBehavior=o?.behavior;return native.call(this,o);};});
  await page.locator('[data-mode="diagram"]').click();
  reports.push({name:'reduced_motion_and_selected_mode',passed:(await page.evaluate(()=>window.lastScrollBehavior))==='auto'&&(await page.locator('[data-mode="diagram"]').getAttribute('aria-current'))==='page'});
  if(process.env.FINAL_MEDIA==='1'){
   await page.locator('[data-mode="video"]').click();
   await page.waitForFunction(()=>document.querySelector('video').readyState>=1,null,{timeout:15000});
   const media=await page.locator('video').evaluate(e=>({duration:e.duration,width:e.videoWidth,height:e.videoHeight}));
   await page.locator('video').evaluate(async e=>{await e.play();});await page.waitForFunction(()=>document.querySelector('video').currentTime>.2,null,{timeout:15000});await page.locator('video').evaluate(e=>e.pause());
   reports.push({name:'actual_MP4_browser_playback',passed:media.duration>1&&media.width===1920&&media.height===1080,actual:media});
  }
 }finally{await browser.close();}
 const r={generated_at:new Date().toISOString(),scope:'Independent parent checks; illustrative inputs',passed:reports.every(x=>x.passed),checks:reports};
 fs.writeFileSync(ROOT+'/tests/parent-web.json',JSON.stringify(r,null,2));console.log(JSON.stringify({passed:r.passed,checks:reports.length,failed:reports.filter(x=>!x.passed),media_exercised:process.env.FINAL_MEDIA==='1'},null,2));process.exitCode=r.passed?0:1;
})().catch(e=>{console.error(e);process.exitCode=1});

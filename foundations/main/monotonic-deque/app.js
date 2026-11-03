'use strict';
// Indices in the deque are ordered by time; their values strictly decrease.
function buildTrace(a,k){
 if(!Array.isArray(a)||!a.length||!a.every(Number.isSafeInteger)||!Number.isInteger(k)||k<1||k>a.length) throw new Error('1 ≤ k ≤ n인 정수 배열이 필요합니다.');
 const dq=[],steps=[],answers=[];
 for(let i=0;i<a.length;i++){
  const frontOut=[],backOut=[];
  if(dq.length&&dq[0]<=i-k) frontOut.push(dq.shift());
  while(dq.length&&a[dq[dq.length-1]]<=a[i]) backOut.unshift(dq.pop());
  dq.push(i); const max=i>=k-1?a[dq[0]]:null;
  if(max!==null) answers.push(max);
  steps.push({i,v:a[i],frontOut,backOut,deque:[...dq],window:[Math.max(0,i-k+1),i],max});
 }
 return {steps,answers};
}
if(typeof module!=='undefined') module.exports={buildTrace};
if(typeof document!=='undefined'){
 const fixtures={video:{a:[5,3,4,1,2,8,6,3,7,1],k:3},exercise:{a:[2,7,7,1,3,6,2,5,4,9,1,3],k:4}};
 const $=id=>document.getElementById(id); let i=0,revealed=false,trace;
 function setup(){i=0;revealed=false;trace=buildTrace(fixtures[$('fixture').value].a,fixtures[$('fixture').value].k);$('guess').value='';render()}
 function render(){const {a,k}=fixtures[$('fixture').value],s=trace.steps[i];
 $('context').innerHTML=`<p class="context-line"><strong>입력:</strong> [${a.join(', ')}] · <strong>k = ${k}</strong></p><p class="context-line"><strong>단계 ${i+1} / ${a.length}</strong> · 새 인덱스 i = ${i}, 값 ${a[i]} · 현재 창 [${s.window[0]}, ${s.window[1]}] (${i+1<k?'채우는 중':k+'개'})</p><div class="strip" aria-label="입력 배열">${a.map((v,j)=>`<div class="cell ${j>=s.window[0]&&j<=i?'window':''} ${j===i?'current':''}"><small>${j}</small><strong>${v}</strong></div>`).join('')}</div><p class="context-line">초록 테두리: 현재 창 · 진한 칸: 새 값 · 위 숫자: 인덱스</p><p class="context-line"><strong>질문:</strong> 이 창의 최댓값은? (k개가 되기 전에는 답 없음)</p>`;
 $('result').innerHTML='';$('prev').disabled=i===0;$('next').disabled=!revealed||i===a.length-1;$('reveal').disabled=revealed;
 if(revealed){const pairs=xs=>xs.length?xs.map(j=>`${j}:${a[j]}`).join(', '):'없음';const raw=$('guess').value.trim();const correct=s.max===null?raw==='':raw!==''&&Number(raw)===s.max;
 $('result').innerHTML=`<p><strong>${correct?'맞았어요!':'다시 살펴보세요.'}</strong> ${s.max===null?'아직 창이 차지 않아 답이 없습니다.':`현재 최댓값은 ${s.max}입니다.`}</p><p>앞에서 만료 (인덱스 ≤ ${i-k}): <strong>${pairs(s.frontOut)}</strong></p><p>뒤에서 제거 (값 ≤ ${s.v}): <strong>${pairs(s.backOut)}</strong>${s.backOut.length?' (표시는 앞 → 뒤 순서)':''}</p><p>새 인덱스 ${i}를 넣은 덱 (앞 → 뒤): <strong>${pairs(s.deque)}</strong></p><p>${s.max===null?'창을 더 채웁니다.':`덱 맨 앞 ${s.deque[0]}의 값 ${s.max}가 답입니다.`}</p>`;}
 }
 $('reveal').onclick=()=>{revealed=true;render()};$('next').onclick=()=>{if(i<trace.steps.length-1){i++;revealed=false;$('guess').value='';render()}};$('prev').onclick=()=>{if(i>0){i--;revealed=false;$('guess').value='';render()}};$('reset').onclick=setup;$('fixture').onchange=setup;setup();
}

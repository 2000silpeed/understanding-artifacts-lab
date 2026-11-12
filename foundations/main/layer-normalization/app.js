(() => {
  const initial=[2,4,6,8], eps=0.00001, qs=s=>document.querySelector(s);
  const inputs=qs('#inputs');
  initial.forEach((v,i)=>{const l=document.createElement('label');l.textContent=`x${i+1}`;l.innerHTML+=`<input inputmode="decimal" aria-label="x${i+1}" value="${v}">`;inputs.appendChild(l)});
  const vals=()=>[...inputs.querySelectorAll('input')].map(x=>x.value.trim()===''?NaN:Number(x.value));
  const fmt=x=>Number.isFinite(x)?(Math.abs(x)<0.0000005?'0':x.toFixed(6)): '오류';
  function compute(x){if(x.length!==4||x.some(v=>!Number.isFinite(v)))throw Error('네 칸 모두 유한한 숫자를 입력해 주세요.');const d=x.length,mean=x.reduce((a,b)=>a+b,0)/d,varr=x.reduce((a,v)=>a+(v-mean)**2,0)/d,denom=Math.sqrt(varr+eps),xhat=x.map(v=>(v-mean)/denom),g=qs('#affine').checked?[1,1,2,1]:[1,1,1,1],b=qs('#affine').checked?[0,.5,0,0]:[0,0,0,0],y=xhat.map((v,i)=>g[i]*v+b[i]),ym=y.reduce((a,v)=>a+v,0)/d,yv=y.reduce((a,v)=>a+(v-ym)**2,0)/d;return {mean,varr,denom,xhat,y,ym,yv,g,b}}
  function render(r){qs('#result').innerHTML=`<div class="row"><b>평균 μ</b><span class="num">${fmt(r.mean)}</span></div><div class="row"><b>편향 분산 σ² (÷ d)</b><span class="num">${fmt(r.varr)}</span></div><div class="row"><b>분모 √(σ²+ε)</b><span class="num">${fmt(r.denom)}</span></div><div class="row"><b>정규화 x̂</b><span class="num">[${r.xhat.map(fmt).join(', ')}]</span></div><div class="row"><b>affine y = γx̂+β</b><span class="num">[${r.y.map(fmt).join(', ')}]</span></div><p class="note">x̂ 통계: 평균 ${fmt(r.xhat.reduce((a,v)=>a+v,0)/4)}, 분산 ${fmt(r.xhat.reduce((a,v)=>a+v*v,0)/4)} · y 통계는 γ·β 적용 후라 별개입니다.</p>`}
  qs('#calc').onclick=()=>{qs('#error').textContent='';try{render(compute(vals()));qs('#progress').textContent='2 / 3'}catch(e){qs('#result').innerHTML='';qs('#error').textContent=e.message}};
  qs('#reset').onclick=()=>{inputs.querySelectorAll('input').forEach((x,i)=>x.value=initial[i]);qs('#affine').checked=false;qs('#error').textContent='';qs('#result').innerHTML='<p class="note">처음 값으로 돌아왔습니다. 다시 계산해 보세요.</p>';qs('#feedback').textContent='';qs('#answer').classList.add('hidden');qs('#progress').textContent='1 / 3'};
  qs('#clear').onclick=()=>{inputs.querySelectorAll('input').forEach(x=>x.value='');qs('#error').textContent='';qs('#result').innerHTML='<p class="note">값을 지웠습니다. 네 칸을 채워 주세요.</p>'};
  qs('#predictZero').onclick=()=>qs('#feedback').textContent='선택: 0에 가깝다. 정답을 보기 전에 이유를 생각해 보세요.';
  qs('#predictOne').onclick=()=>qs('#feedback').textContent='선택: 1에 가깝다. 상수 입력의 (x−μ)를 먼저 떠올려 보세요.';
  qs('#reveal').onclick=()=>{qs('#answer').classList.remove('hidden');qs('#feedback').textContent='정답을 공개했습니다. 이제 입력을 [5,5,5,5]로 바꿔 직접 계산해 보세요.';qs('#progress').textContent='3 / 3'};
})();

(function(){
'use strict';
const L=window.Lab,$=id=>document.getElementById(id),kind=document.body.dataset.lab;
let trace=null,step=0;
const error=e=>{$('error').textContent=e?e.message:'';};
function parse(s){
 if(!s.trim())return [];
 const parts=s.split(','),a=parts.map(x=>Number(x.trim()));
 if(parts.some(x=>!x.trim())||!a.every(Number.isSafeInteger)||a.length>8)throw Error('쉼표로 구분한 정확한 정수를 최대 8개 입력하세요.');
 return a;
}
function draw(){
 const focus=document.activeElement,s=trace.states[step],d=$('diagram');
 $('message').textContent=s.message;$('progress').textContent=(step+1)+' / '+trace.states.length;
 $('counts').textContent=Object.entries(s.counts).map(([k,v])=>({traversals:'링크 이동',visited:'방문 노드',writes:'논리 쓰기',comparisons:'값 비교',shifts:'이동',inserts:'삽입'}[k])+': '+v).join(' · ');
 d.replaceChildren();
 if(kind==='linked'){
  const g=s.graph,byId=new Map(g.nodes.map(n=>[n.id,n])),seen=new Set;
  $('variables').textContent='head = '+g.head+' · tail = '+g.tail;
  let id=g.head;
  while(id!==null&&!seen.has(id)){
   const n=byId.get(id);if(!n)break;seen.add(id);
   const el=document.createElement('div');el.className='node'+(s.current===n.id?' active':'');
   el.textContent=n.id+' | 값 '+n.value+' | next → '+n.next;d.append(el);
   if(n.next!==null){const arrow=document.createElement('span');arrow.textContent='→';arrow.setAttribute('aria-hidden','true');d.append(arrow);}
   id=n.next;
  }
  g.nodes.filter(n=>!seen.has(n.id)).forEach(n=>{
   const el=document.createElement('div');el.className='node detached';
   el.textContent='분리된 노드 '+n.id+' | 값 '+n.value+' | next → '+n.next;d.append(el);
  });
 }else{
  $('variables').textContent='i = '+s.i+' · j = '+s.j+' · key = '+(s.key?s.key.value+' (#'+s.key.tag+')':'없음')+' · 정렬 구간 길이 = '+s.prefix;
  s.items.forEach((n,k)=>{const el=document.createElement('div');el.className='cell'+(!n?' hole':'')+(k<s.prefix?' active':'');el.textContent=n?n.value+' (#'+n.tag+')':'빈칸';d.append(el);});
 }
 $('back').disabled=step===0;$('next').disabled=step===trace.states.length-1;$('run').disabled=step===trace.states.length-1;
 if(kind==='linked'){
  document.querySelectorAll('[data-op]').forEach(b=>b.disabled=step>0&&step<trace.states.length-1);
  $('boundary').textContent=step>0&&step<trace.states.length-1?'작업 진행 중입니다. 새 작업은 완료하거나 초기화한 뒤 시작하세요.':'모든 새 작업은 입력의 원본 그래프에서 시작합니다.';
 }
 if(focus?.disabled)$('reset').focus();
}
function reset(){
 error();
 try{
  const values=parse($('values').value);
  if(kind==='sort')trace=L.insertionTrace(values);
  else{
   const g=L.linkedCreate(values);$('pred').replaceChildren();
   g.nodes.forEach((n,i)=>{const o=document.createElement('option');o.value=n.id;o.textContent=n.id+' · 인덱스 '+i+' · 값 '+n.value;$('pred').append(o);});
   if(g.nodes.length>1)$('pred').value=g.nodes[1].id;
   trace={states:[{graph:g,counts:{traversals:0,visited:0,writes:0},message:'원본 그래프: 작업을 선택하세요.',current:null}]};
  }
  step=0;draw();
 }catch(e){
  trace=null;step=0;$('diagram').replaceChildren();$('message').textContent='입력이 잘못되어 이전 결과를 폐기했어요. 원본 값을 수정해 주세요.';
  $('variables').textContent='';$('counts').textContent='';$('progress').textContent='—';
  document.querySelectorAll('[data-op],#next,#back,#run').forEach(b=>b.disabled=true);error(e);
 }
}
if(kind==='linked'||kind==='sort'){
 $('reset').onclick=reset;$('values').oninput=reset;
 document.querySelectorAll('[data-fixture]').forEach(b=>b.onclick=()=>{$('values').value=b.dataset.fixture;reset();});
 $('next').onclick=()=>{if(trace&&step<trace.states.length-1){step++;draw();}};
 $('back').onclick=()=>{if(trace&&step>0){step--;draw();}};
 $('run').onclick=()=>{if(trace){step=trace.states.length-1;draw();}};
 if(kind==='linked')document.querySelectorAll('[data-op]').forEach(b=>b.onclick=()=>{
  error();try{
   if(b.dataset.op==='find'&&!$('target').value.trim())throw Error('검색 대상을 입력하세요.');
   if(b.dataset.op==='insert'&&!$('newvalue').value.trim())throw Error('삽입 값을 입력하세요.');
   if(b.dataset.op==='find'&&!Number.isSafeInteger(Number($('target').value)))throw Error('검색 대상은 정확한 정수여야 해요.');
   if(b.dataset.op==='insert'&&!Number.isSafeInteger(Number($('newvalue').value)))throw Error('삽입 값은 정확한 정수여야 해요.');
   const g=L.linkedCreate(parse($('values').value)),id=$('pred').value,known=$('known').checked;
   trace=b.dataset.op==='find'?L.linkedSearch(g,{mode:$('mode').value,target:Number($('target').value)}):b.dataset.op==='insert'?L.linkedInsert(g,id,Number($('newvalue').value),{known}):L.linkedDelete(g,id,{known});step=0;draw();
  }catch(e){error(e);}
 });
 reset();
}
if(kind==='embedding'){
 let phase=3,parts=[];
 function renderEmbedding(){
  const focus=document.activeElement;
  if(parts.length)$('single').textContent=parts.slice(0,phase+1).join('\n');
  $('embedback').disabled=phase===0;$('embednext').disabled=phase===3;$('embedrun').disabled=phase===3;
  if(focus?.disabled)$('recompute').focus();
 }
 function update(){
  error();try{
   const m=Array.from({length:3},(_,i)=>[0,1].map(j=>{const raw=$('m'+i+j).value;if(!raw.trim())throw Error('행렬의 빈 셀을 채우세요.');const v=Number(raw);if(!Number.isFinite(v)||Math.abs(v)>100)throw Error('행렬 값은 -100~100의 유한한 숫자여야 합니다.');return v;}));
   const idraw=$('id').value;if(!idraw.trim())throw Error('ID를 입력하세요.');
   const r=L.embeddingLookup(m,Number(idraw)),ids=parse($('sequence').value),seq=L.embeddingSequence(m,ids);
   document.querySelectorAll('.matrix input').forEach(e=>e.classList.toggle('selected-row',e.id.startsWith('m'+r.id)));
   parts=['ID '+r.id+' → E['+r.id+'] = '+JSON.stringify(r.row),'one-hot = '+JSON.stringify(r.onehot),'가중 행 = '+JSON.stringify(r.weighted),'행 합 = '+JSON.stringify(r.sum)+'\n직접 조회와 동일: '+(r.equal?'확인 ✓':'실패')];
   renderEmbedding();$('sequenceout').textContent=seq.lookups.map(x=>'ID '+x.id+' → '+JSON.stringify(x.row)).join('\n')+'\nOUTPUT shape '+seq.shape.join('×')+'\n'+JSON.stringify(seq.result);
  }catch(e){document.querySelectorAll('.matrix input').forEach(e=>e.classList.remove('selected-row'));parts=[];$('single').textContent='입력을 수정하면 다시 계산합니다.';$('sequenceout').textContent='';error(e);}
 }
 document.querySelectorAll('input').forEach(x=>x.oninput=()=>{phase=0;update();});
 $('recompute').onclick=()=>{phase=3;update();};$('embedback').onclick=()=>{phase=Math.max(0,phase-1);renderEmbedding();};
 $('embednext').onclick=()=>{phase=Math.min(3,phase+1);renderEmbedding();};$('embedrun').onclick=()=>{phase=3;update();};
 $('embedreset').onclick=()=>{phase=0;update();};update();
}
})();

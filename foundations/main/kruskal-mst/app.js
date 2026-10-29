/* Pure deterministic companion logic mirrors examples/kruskal.py and kruskal.cpp. */
const FIXTURES={
 default:{title:'graph.txt · 기본 6정점',names:['A','B','C','D','E','F'],edges:[['A','B',8],['B','C',6],['A','D',4],['D','E',7],['E','F',1],['B','E',2],['C','F',5],['B','F',3],['A','E',9]]},
 tie:{title:'tie.txt · 같은 비용',names:['P','Q','R','S'],edges:[['P','Q',2],['Q','R',2],['R','P',2],['R','S',1],['P','S',3]]},
 disconnected:{title:'disconnected.txt · 두 섬',names:['A','B','C','D','E'],edges:[['A','B',3],['B','C',1],['A','C',2],['D','E',4]]}
};
const $=id=>document.getElementById(id); let fixtureKey='default', trace, cursor=0, prediction=null, revealed=false;
function edge(u,v,w){return {u,v,w,id:`${u}-${v}`}}
function buildTrace(input){
 const parent=Object.fromEntries(input.names.map(v=>[v,v])), size=Object.fromEntries(input.names.map(v=>[v,1]));
 const find=v=>{let root=v;while(parent[root]!==root)root=parent[root];while(v!==root){const nxt=parent[v];parent[v]=root;v=nxt}return root};
 const rootOf=v=>{while(parent[v]!==v)v=parent[v];return v};
 const groups=()=>{const by={};for(const v of input.names){const r=rootOf(v);(by[r]??=[]).push(v)}return Object.values(by)};
 const sorted=input.edges.map((x,i)=>({...edge(...x),i})).sort((a,b)=>a.w-b.w||a.i-b.i), tree=[], steps=[], totalRef={v:0};
 for(const e of sorted){if(tree.length===input.names.length-1)break;const before=groups().map(g=>[...g]);const ru=find(e.u),rv=find(e.v);let take=ru!==rv;if(take){let ra=ru,rb=rv;if(size[ra]<size[rb])[ra,rb]=[rb,ra];parent[rb]=ra;size[ra]+=size[rb];tree.push(e);totalRef.v+=e.w}steps.push({k:steps.length+1,...e,findU:ru,findV:rv,take,total:totalRef.v,treeEdges:tree.length,groupsBefore:before,groupsAfter:groups().map(g=>[...g]),parentAfter:{...parent}})}
 return {input,sorted,steps,tree,total:totalRef.v,groups:groups()};
}
function resetState(){trace=buildTrace(FIXTURES[fixtureKey]);cursor=0;prediction=null;revealed=false;render()}
function currentStep(){return cursor?trace.steps[cursor-1]:null} function nextStep(){return trace.steps[cursor]||null}
function choose(value){if(revealed||!nextStep())return;prediction=value;cursor++;revealed=true;render();$('answer').focus()}
function advance(){if(!revealed||!nextStep())return;prediction=null;revealed=false;render();$('predict-take').focus()}
function back(){const previous=cursor-(revealed?2:1);if(previous<0)return;cursor=previous;prediction=null;revealed=false;render();$('predict-take').focus()}
function retryCurrent(){if(!revealed)return;cursor--;prediction=null;revealed=false;render();$('predict-take').focus()}
function render(){renderGraph();renderDecision();renderState();$('progress').textContent=`${cursor} / ${trace.steps.length}개 간선 확인`}
function renderDecision(){const s=revealed?currentStep():nextStep(), done=revealed&&!nextStep();$('step-badge').textContent=done?'연습 완료':`${revealed?cursor:cursor+1}번째 간선`;$('decision-title').textContent=done?'연습을 마쳤어요':revealed?'판단 결과':'이 길을 선택할까요?';$('candidate').innerHTML=s?`<strong>${s.u} — ${s.v}</strong> · 비용 ${s.w}<small>${revealed?'방금 살펴본 길':'비용이 가장 낮은 남은 길'}</small>`:'';const a=$('answer');if(!revealed){a.className='answer';a.textContent='두 마을이 다른 덩어리라면 선택하고, 이미 이어져 있다면 건너뛰세요.'}else{const beforeU=s.groupsBefore.find(g=>g.includes(s.u)).join(', '),beforeV=s.groupsBefore.find(g=>g.includes(s.v)).join(', ');a.className=`answer ${prediction===s.take?'good':'bad'}`;a.textContent=`${prediction===s.take?'맞았어요!':'아쉬워요. 다시 생각해 보세요.'} ${s.take?'선택합니다':'건너뜁니다'}. ${s.take?`${s.u}는 {${beforeU}}, ${s.v}는 {${beforeV}}에 있어 서로 다른 덩어리입니다. 두 덩어리를 합치고 비용 ${s.w}을 더했어요.`:`두 마을 모두 {${beforeU}}에 이미 이어져 있어 다시 이으면 사이클이 생깁니다. 비용은 그대로예요.`}${done?` 완료: 간선 ${trace.tree.length}개, 비용 ${trace.total}, 덩어리 ${trace.groups.length}개. ${trace.groups.length>1?'서로 떨어진 섬마다 연결한 신장 숲입니다.':'모든 마을이 연결되었습니다.'}`:''}`}$('predict-take').disabled=revealed;$('predict-skip').disabled=revealed;$('prev').disabled=revealed?cursor<=1:cursor===0;$('retry').disabled=!revealed;$('next').disabled=!revealed||!nextStep()}
function renderState(){const s=currentStep();const groups=s?s.groupsAfter:trace.input.names.map(v=>[v]);$('groups').innerHTML=groups.map(g=>`<span class="group">{${g.join(', ')}}</span>`).join('');$('metric-edges').textContent=s?s.treeEdges:0;$('metric-total').textContent=s?s.total:0;$('metric-components').textContent=groups.length}
function nodePositions(names){const out={};const cx=340,cy=176,rx=245,ry=123;names.forEach((n,i)=>{const a=-Math.PI/2+i*2*Math.PI/names.length;out[n]={x:cx+rx*Math.cos(a),y:cy+ry*Math.sin(a)}});return out}
function renderGraph(){const s=currentStep(), n=revealed?null:nextStep(), pos=nodePositions(trace.input.names), statuses={};trace.steps.slice(0,cursor).forEach(x=>statuses[x.id]=x.take?'taken':'skipped');if(n)statuses[n.id]='current';let svg='';for(const e of trace.sorted){const a=pos[e.u],b=pos[e.v],st=statuses[e.id]||'';svg+=`<line x1="${a.x}" y1="${a.y}" x2="${b.x}" y2="${b.y}" class="edge ${st}"/><text x="${a.x+(b.x-a.x)*.35+(Math.abs(a.x-b.x)<1?32:0)}" y="${a.y+(b.y-a.y)*.35-9}" class="weight ${st}">${e.w}</text>`}for(const v of trace.input.names){const p=pos[v];svg+=`<circle cx="${p.x}" cy="${p.y}" r="24" class="node"/><text x="${p.x}" y="${p.y+6}" class="node-label">${v}</text>`}$('graph').innerHTML=svg;$('graph').setAttribute('aria-label',`${FIXTURES[fixtureKey].title}, 현재 ${cursor}단계`);$('graph-title').textContent=({default:'마을 6곳의 길',tie:'같은 비용의 길',disconnected:'서로 떨어진 두 섬'})[fixtureKey];$('edge-list').innerHTML=trace.sorted.map(e=>`<span class="edge-pill ${statuses[e.id]||''}">${e.id} : ${e.w}</span>`).join('')}
$('fixture').addEventListener('change',e=>{fixtureKey=e.target.value;resetState()});$('reset').addEventListener('click',resetState);$('prev').addEventListener('click',back);$('retry').addEventListener('click',retryCurrent);$('next').addEventListener('click',advance);$('predict-take').addEventListener('click',()=>choose(true));$('predict-skip').addEventListener('click',()=>choose(false));
resetState();

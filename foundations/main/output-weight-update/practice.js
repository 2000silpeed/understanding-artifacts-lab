import {TRACE,compute} from './trace-shared.js';
export function apply(h,w,target,lr){const q=compute(h,w,target,lr);return {...q,next:q.WPrime};}
export function validate(h,w,target,lr){compute(h,w,target,lr);}
export function transfer(){return apply([1,0],TRACE.WPrime,2,.3)}
export function makeLab(){let state={h:[1,2],w:TRACE.W.map(r=>r.slice()),target:2,lr:.3,revealed:false};return {state:()=>structuredClone(state),set(p){state={...state,...p,result:undefined,revealed:false}},reset(){state={h:[1,2],w:TRACE.W.map(r=>r.slice()),target:2,lr:.3,revealed:false}},run(){state={...state,result:apply(state.h,state.w,state.target,state.lr),revealed:false};return state.result},reveal(){if(!state.result)throw new Error('먼저 계산해 주세요');state={...state,revealed:true};return state}}}

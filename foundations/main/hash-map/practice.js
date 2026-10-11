// Pure controller shared by offline page and Node source tests.
export function createPractice(trace) {
 let index=0,revealed=false,completed=false,prediction=null;
 const view=()=>({index,revealed,completed,prediction,
   operation:trace.records[index].op,key:trace.records[index].key,value:trace.records[index].value,
   buckets:completed?trace.records.at(-1).after:(revealed?trace.records[index].after:trace.records[index].before),
   answer:revealed?trace.records[index]:null});
 return {
  view,
  predict(bucket,comparisons,result){prediction={bucket,comparisons,result};return view();},
  reveal(){revealed=true;return view();},
  next(){if(!revealed)return view();if(index===trace.records.length-1){completed=true;return view();}index++;revealed=false;prediction=null;return view();},
  select(i){if(!Number.isInteger(i)||i<0||i>=trace.records.length)throw Error('invalid index');index=i;revealed=false;completed=false;prediction=null;return view();},
  reset(){index=0;revealed=false;completed=false;prediction=null;return view();}
 };
}

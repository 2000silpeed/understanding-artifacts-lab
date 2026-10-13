export function validateLabInput(logits, targetId, learningRate = 0.4) {
  if (!Array.isArray(logits) || logits.length === 0 || !logits.every(Number.isFinite)) return '로짓은 비어 있지 않은 유한한 숫자 배열이어야 해요.';
  if (!Number.isInteger(targetId) || targetId < 0 || targetId >= logits.length) return '타깃 ID가 로짓 범위를 벗어났어요.';
  if (!Number.isFinite(learningRate) || learningRate < 0) return '학습률은 0 이상의 유한한 숫자여야 해요.';
  return '';
}
export function stableSoftmax(logits) {
  const error = validateLabInput(logits, 0, 0); if (error) throw Error(error);
  const shift = Math.max(...logits), weights = logits.map(z => Math.exp(z - shift));
  const denominator = weights.reduce((a,b) => a+b,0);
  return weights.map(w => w/denominator);
}
export function stableLoss(logits, targetId) {
  const error = validateLabInput(logits, targetId, 0); if (error) throw Error(error);
  const m = Math.max(...logits), d = logits.reduce((sum,z)=>sum+Math.exp(z-m),0);
  const loss = (m-logits[targetId])+Math.log(d);
  if (!Number.isFinite(loss)) throw Error('손실이 표현 가능한 숫자 범위를 벗어났어요.');
  return loss;
}
export function applyGradientUpdate(logits, targetId, learningRate) {
  const error = validateLabInput(logits,targetId,learningRate); if(error) throw Error(error);
  const probabilities=stableSoftmax(logits), gradient=probabilities.map((p,i)=>p-(i===targetId?1:0));
  const nextLogits=logits.map((z,i)=>z-learningRate*gradient[i]);
  const nextError=validateLabInput(nextLogits,targetId,learningRate); if(nextError) throw Error(nextError);
  return {probabilities, gradient, nextLogits, nextProbabilities:stableSoftmax(nextLogits), loss:stableLoss(logits,targetId), nextLoss:stableLoss(nextLogits,targetId)};
}
export function createPredictionSession(logits=[1,0,-.5], targetId=1, learningRate=.4) {
  let input={logits:[...logits],targetId,learningRate}, prediction=null, revealed=false;
  return {
    set(z,t,eta) { const e=validateLabInput(z,t,eta); if(e) throw Error(e); input={logits:[...z],targetId:t,learningRate:eta}; prediction=null; revealed=false; },
    predict(value) { if(!['up','down','same'].includes(value)) throw Error('예측을 선택해 주세요.'); prediction=value; revealed=false; },
    reveal() { if(prediction===null) throw Error('먼저 예측해 주세요.'); revealed=true; return this.state(); },
    reset() {input={logits:[1,0,-.5],targetId:1,learningRate:.4};prediction=null;revealed=false;},
    state() {const out={input:{...input,logits:[...input.logits]},prediction,revealed};if(revealed){out.result=applyGradientUpdate(input.logits,input.targetId,input.learningRate);const delta=out.result.nextLogits[input.targetId]-input.logits[input.targetId];out.direction=delta>0?'up':delta<0?'down':'same';out.correct=out.direction===prediction;}return out;}
  };
}

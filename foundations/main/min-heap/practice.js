export function createPractice(trace) {
  let index = 0;
  let revealed = false;
  let prediction = null;
  const states = [
    { question: 'push(3) 뒤 루트는?', expected: trace.canonical.initial_heap[0] },
    { question: 'pop_min() 결과는?', expected: trace.canonical.pop_min },
    { question: 'pop 뒤 배열은?', expected: trace.canonical.after_pop },
  ];
  return {
    view() { return { index, revealed, prediction, state: {question:states[index].question, input:trace.canonical.input, ...(revealed?{expected:states[index].expected}:{})} }; },
    predict(answer) { prediction = answer; revealed = false; return this.view(); },
    reveal() { revealed = true; return { ...this.view(), correct: JSON.stringify(prediction) === JSON.stringify(states[index].expected), answer: states[index].expected }; },
    next() { if (!revealed) throw new Error('먼저 공개하세요'); index = Math.min(index + 1, states.length - 1); revealed = false; prediction = null; return this.view(); },
    reset() { index = 0; revealed = false; prediction = null; return this.view(); },
  };
}

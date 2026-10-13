// Shared numeric constants for the offline lab and source tests.
export const TRACE = Object.freeze({
  logits: Object.freeze([1.0, 0.0, -0.5]),
  targetId: 1,
  epsilon: 0.00001,
  learningRate: 0.4,
  largeLearningRate: 20.0,
  initialLoss: 1.464368784107945,
  updatedLoss: 1.0905862216873305,
});
export const stableSoftmax = logits => { const shift = Math.max(...logits); const w = logits.map(z => Math.exp(z - shift)); const d = w.reduce((a,b) => a+b, 0); return w.map(x => x/d); };
export const oneHotGradient = (p, targetId) => p.map((v, i) => v - (i === targetId ? 1 : 0));

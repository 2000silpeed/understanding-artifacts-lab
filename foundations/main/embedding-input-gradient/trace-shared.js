export const W = [[-0.1, -0.1, 0.2], [-0.2, -0.2, 0.4]];
export const E = [[0, 1], [1, 2], [-1, 1]];
export const INPUT_ID = 1;
export const TARGET_ID = 2;
export const LEARNING_RATE = 0.3;
export const EPSILON = 1e-6;

function cloneMatrix(m) { return m.map((row) => row.slice()); }
function validate(w, e, inputId, targetId, lr) {
  if (!Array.isArray(w) || w.length !== 2 || w.some((row) => !Array.isArray(row) || row.length !== 3 || !row.every(Number.isFinite))) throw new Error('W shape/finite');
  if (!Array.isArray(e) || e.length !== 3 || e.some((row) => !Array.isArray(row) || row.length !== 2 || !row.every(Number.isFinite))) throw new Error('E shape/finite');
  if (!Number.isInteger(inputId) || inputId < 0 || inputId >= 3) throw new Error('input_id');
  if (!Number.isInteger(targetId) || targetId < 0 || targetId >= 3) throw new Error('target_id');
  if (!Number.isFinite(lr) || lr < 0) throw new Error('learning_rate');
}
export function stableSoftmax(z) {
  if (!Array.isArray(z) || z.length !== 3 || !z.every(Number.isFinite)) throw new Error('logits');
  const top = Math.max(...z);
  const ex = z.map((x) => Math.exp(x - top));
  const total = ex.reduce((a, b) => a + b, 0);
  return ex.map((x) => x / total);
}
export function logits(h, w) {
  if (!Array.isArray(h) || h.length !== 2 || !h.every(Number.isFinite)) throw new Error('h');
  return [0, 1, 2].map((j) => h.reduce((sum, x, i) => sum + x * w[i][j], 0));
}
export function forward(h, w, targetId) {
  const z = logits(h, w);
  const p = stableSoftmax(z);
  const y = p.map((_, j) => (j === targetId ? 1 : 0));
  const g = p.map((x, j) => x - y[j]);
  return { z, p, loss: -Math.log(p[targetId]), g };
}
export function inputGradient(w, g) {
  return [0, 1].map((i) => [0, 1, 2].reduce((sum, j) => sum + w[i][j] * g[j], 0));
}
export function selectedGradient(inputId, dh) {
  const dE = [[0, 0], [0, 0], [0, 0]];
  dE[inputId] = dh.slice();
  return dE;
}
export function updateEmbedding(e, inputId, dh, lr) {
  const out = cloneMatrix(e);
  out[inputId] = e[inputId].map((x, i) => x - lr * dh[i]);
  return out;
}
export function finiteDifference(e, inputId, w, targetId, eps = EPSILON) {
  return [0, 1].map((i) => {
    const plus = cloneMatrix(e), minus = cloneMatrix(e);
    plus[inputId][i] += eps;
    minus[inputId][i] -= eps;
    return (forward(plus[inputId], w, targetId).loss - forward(minus[inputId], w, targetId).loss) / (2 * eps);
  });
}
export function compute({ w = W, e = E, inputId = INPUT_ID, targetId = TARGET_ID, lr = LEARNING_RATE } = {}) {
  validate(w, e, inputId, targetId, lr);
  const h = e[inputId].slice();
  const initial = forward(h, w, targetId);
  const dh = inputGradient(w, initial.g);
  const dE = selectedGradient(inputId, dh);
  const ePrime = updateEmbedding(e, inputId, dh, lr);
  const hPrime = ePrime[inputId].slice();
  const updated = forward(hPrime, w, targetId);
  return { w: cloneMatrix(w), e: cloneMatrix(e), input_id: inputId, target_id: targetId, learning_rate: lr, selected_row: inputId, h, initial, dh, dE, finite_difference: finiteDifference(e, inputId, w, targetId), E_prime: ePrime, h_prime: hPrime, updated };
}
export const TRACE = {
  contract: { W: cloneMatrix(W), E: cloneMatrix(E), input_id: INPUT_ID, target_id: TARGET_ID, learning_rate: LEARNING_RATE, selected_row: INPUT_ID, bias: false },
  main: compute(),
  transfer: compute({ inputId: 0 }),
  zero_W: (() => { const c = compute({ w: [[0, 0, 0], [0, 0, 0]] }); return { dh: c.dh, dE: c.dE, g: c.initial.g }; })(),
  zero_input: (() => { const c = compute({ e: [[0, 0], [0, 0], [0, 0]], inputId: 1 }); return { dh: c.dh, dE: c.dE }; })(),
};
export const fmt = (n) => (Math.abs(n) < 0.0000005 ? 0 : n).toFixed(6);

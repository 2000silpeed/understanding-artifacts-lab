export const TOKENS = ['a', 'b', 'c'];
export const E = [[1, 0], [0, 1], [1, 1]];
export const W = [[1, 0, -1], [0, 1, 0], [0, -1, 1], [1, 0, 0]];
export const SEQUENCE = ['a', 'b', 'c', 'a'];
export const IDS = {a: 0, b: 1, c: 2};

export function stableSoftmax(z) {
  const maxZ = Math.max(...z);
  const weights = z.map((value) => Math.exp(value - maxZ));
  const total = weights.reduce((sum, value) => sum + value, 0);
  return weights.map((value) => value / total);
}

export function dotProducts(h) {
  return W[0].map((_, j) => {
    let total = 0;
    const terms = h.map((value, i) => {
      const raw = value * W[i][j];
      const product = raw === 0 ? 0 : raw;
      total += product;
      if (total === 0) total = 0;
      return {left: value, right: W[i][j], product};
    });
    return {output_id: j, terms, partial_sums: terms.map((_, i) => h.slice(0, i + 1).reduce((sum, value, k) => sum + (value * W[k][j] === 0 ? 0 : value * W[k][j]), 0)), result: total};
  });
}

export function forward(contextIds) {
  const h = [...E[contextIds[0]], ...E[contextIds[1]]];
  const dot_products = dotProducts(h);
  const z = dot_products.map((column) => column.result);
  const p = stableSoftmax(z);
  return {context_ids: contextIds, h, dot_products, z, p, prediction_id: p.indexOf(Math.max(...p))};
}

export function buildTrainingPairs(sequence = SEQUENCE) {
  return sequence.slice(0, -2).map((_, i) => ({context: sequence.slice(i, i + 2), context_ids: sequence.slice(i, i + 2).map((token) => IDS[token]), target: sequence[i + 2], target_id: IDS[sequence[i + 2]], future_tokens_excluded: sequence.slice(i + 3)}));
}

export const TRACE = {
  contract: {tokens: TOKENS, E, W, context_length: 2, embedding_dim: 2, hidden_width: 4, vocab_size: 3, window: 2},
  main: forward([0, 1]),
  reverse: forward([1, 0]),
  transfer: forward([2, 0]),
  average: {ab: [(E[0][0] + E[1][0]) / 2, (E[0][1] + E[1][1]) / 2], ba: [(E[1][0] + E[0][0]) / 2, (E[1][1] + E[0][1]) / 2], same: true},
  training_pairs: buildTrainingPairs(),
  stable_softmax_sum: forward([0, 1]).p.reduce((a, b) => a + b, 0),
};

export const fmt = (n) => Number(n).toFixed(6);

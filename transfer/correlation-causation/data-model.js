(function (root) {
  'use strict';
  const TEMPERATURES = [10, 14, 18, 22, 26, 30, 34];
  const X_NOISE = [-1.4, -0.6, 0.3, 1.1, -0.9, 1.5];
  const Y_NOISE = [-1.3, 1.0, -0.4, 1.4, 0.2, -0.8];

  function clamp(value, min, max) { return Math.min(max, Math.max(min, value)); }
  function pearson(xs, ys) {
    if (xs.length !== ys.length || xs.length < 2) return NaN;
    const mx = xs.reduce((a, b) => a + b, 0) / xs.length;
    const my = ys.reduce((a, b) => a + b, 0) / ys.length;
    let num = 0, dx = 0, dy = 0;
    for (let i = 0; i < xs.length; i += 1) {
      const ax = xs[i] - mx, ay = ys[i] - my;
      num += ax * ay; dx += ax * ax; dy += ay * ay;
    }
    return dx && dy ? num / Math.sqrt(dx * dy) : NaN;
  }

  // Educational synthetic data. Temperature is a simulation variable, not a measurement.
  // The generator encodes T -> X and T -> Y, with no X -> Y path.
  function generateData(mode, selectedTemperature) {
    const selected = TEMPERATURES.includes(Number(selectedTemperature)) ? Number(selectedTemperature) : 22;
    const rows = [];
    if (mode === 'unconfounded') {
      for (let i = 0; i < 7; i += 1) {
        const x = 18 + i * 8;
        const y = 3 + 1.72 * selected + Y_NOISE[i % Y_NOISE.length] * 3;
        rows.push({ id: `I${i + 1}`, temperature: selected, x, y, group: 'fixed-T', intervention: true });
      }
      return rows;
    }
    TEMPERATURES.forEach((temperature) => {
      for (let rep = 0; rep < 6; rep += 1) {
        const x = 12 + 2.55 * temperature + X_NOISE[rep] * 4;
        const y = 3 + 1.72 * temperature + Y_NOISE[rep] * 3;
        rows.push({ id: `T${temperature}-${rep + 1}`, temperature, x, y, group: `T=${temperature}`, intervention: false });
      }
    });
    return rows;
  }

  function aggregateStats(rows) {
    return {
      n: rows.length,
      r: pearson(rows.map(d => d.x), rows.map(d => d.y)),
      xMean: rows.reduce((a, d) => a + d.x, 0) / rows.length,
      yMean: rows.reduce((a, d) => a + d.y, 0) / rows.length,
    };
  }

  function selectedGroup(rows, temperature) {
    const t = Number(temperature);
    return rows.filter(d => d.temperature === t);
  }

  function summarize(mode, temperature) {
    const rows = generateData(mode, temperature);
    const group = mode === 'unconfounded' ? rows : selectedGroup(rows, temperature);
    return { all: aggregateStats(rows), group: aggregateStats(group), nGroup: group.length, temperature: Number(temperature), mode };
  }

  const api = { TEMPERATURES, clamp, pearson, generateData, aggregateStats, selectedGroup, summarize };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  root.CausalLab = api;
})(typeof window !== 'undefined' ? window : globalThis);

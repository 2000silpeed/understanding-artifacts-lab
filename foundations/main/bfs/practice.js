export function createPractice(trace) {
  const records = trace.canonical.records;
  const steps = records.filter(r => r.kind === 'dequeue').map((record, index, all) => {
    const nextDequeue = records.indexOf(all[index + 1]);
    const end = nextDequeue < 0 ? records.length : nextDequeue;
    const newVertices = records
      .slice(records.indexOf(record) + 1, end)
      .filter(r => r.kind === 'enqueue' && r.from === record.vertex)
      .map(r => r.vertex);
    return { record, newVertices };
  });
  let index = 0;
  let prediction = null;
  let revealed = false;

  const view = () => ({
    index,
    answer: prediction,
    revealed,
    completed: index >= steps.length,
    record: steps[index]?.record ?? null,
  });

  return {
    view,
    predict(distance, next) {
      if (revealed) throw new Error('reset or advance before predicting');
      prediction = { distance: String(distance), next: String(next).trim() };
      return view();
    },
    reveal() {
      const step = steps[index];
      if (!step) return view();
      revealed = true;
      return {
        ...view(),
        answer: {
          prediction,
          record: step.record,
          expected: {
            distance: String(trace.canonical.distance.F),
            next: step.newVertices.join(','),
          },
        },
      };
    },
    next() {
      if (!revealed) throw new Error('reveal first');
      index += 1;
      prediction = null;
      revealed = false;
      return view();
    },
    reset() {
      index = 0;
      prediction = null;
      revealed = false;
      return view();
    },
  };
}

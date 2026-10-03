# How an LLM chooses the next token

## English — STE-inspired, not certified

Use the context `The cat sat on the`. The model gives each possible next token a score. This score is a **logit**.

For this teaching example, use four candidate labels: ` mat`, ` floor`, ` sofa`, and ` roof`. Use the scores `2.0`, `1.0`, `0.3`, and `−0.4`. These scores are illustrative. They are not outputs from a real model.

Softmax converts the scores into probabilities. At temperature `T = 1`, the probabilities are about `60.9%`, `22.4%`, `11.1%`, and `5.5%`. A lower temperature makes this distribution sharper. A higher temperature makes it flatter.

Top-p sorts candidates from highest to lowest probability. Add their probabilities until the total reaches or exceeds `p`. Keep the candidate that crosses the threshold.

At `p = 0.8`, `mat` alone reaches only `60.9%`. Add `floor`, and the total reaches `83.3%`. Keep both candidates. Divide each retained probability by their total. The new probabilities are `73.1%` and `26.9%`.

Greedy decoding selects the largest score. Sampling draws a uniform number between zero and one. The cumulative probability intervals determine the selected token. Sampling can select a token that is not the most likely token.

After each choice, a real model adds the token to the context. It then calculates new scores. This page explains one choice. It does not run that model calculation.

### Check your reasoning
At `T = 1` and `p = 0.8`, does `floor` remain a candidate? Explain why before reading the answer.

Answer: Yes. `mat` alone is below the threshold. Adding `floor` crosses it. Top-p compares the accumulated probabilities, not each token's probability with `p`.

## 한국어 — 같은 조건의 쉬운 설명

문맥은 `The cat sat on the`입니다. 모델은 가능한 다음 토큰마다 점수를 매깁니다. 이 점수가 **logit**입니다.

여기서는 후보를 ` mat`, ` floor`, ` sofa`, ` roof` 네 개로 줄였습니다. 점수는 `2.0`, `1.0`, `0.3`, `−0.4`로 직접 정했습니다. 실제 모델에서 측정한 값이 아닙니다.

softmax는 점수를 확률로 바꿉니다. 온도 `T = 1`에서는 대략 `60.9%`, `22.4%`, `11.1%`, `5.5%`입니다. 온도를 낮추면 이 분포가 뾰족해지고, 높이면 평평해집니다.

top-p는 확률이 큰 후보부터 정렬합니다. 확률을 하나씩 더하다가 합이 `p` 이상이 되면 멈춥니다. 임계값을 넘게 만든 마지막 후보도 남깁니다.

`p = 0.8`일 때 `mat`의 `60.9%`만으로는 부족합니다. `floor`까지 더하면 `83.3%`가 됩니다. 두 후보를 남기고 각각의 확률을 그 합으로 나눕니다. 그러면 `73.1%`와 `26.9%`가 됩니다.

greedy는 가장 큰 점수를 고릅니다. sampling은 영과 일 사이에서 균등 난수를 뽑습니다. 그 수가 들어간 누적 확률 구간의 토큰을 고르므로, 가장 높은 후보가 아닌 토큰도 선택할 수 있습니다.

실제 모델은 선택한 토큰을 문맥에 붙인 뒤 점수를 다시 계산합니다. 이 페이지는 한 번의 선택만 보여줍니다. 모델의 다음 계산까지 실행하지는 않습니다.

### 생각해 보기
`T = 1`, `p = 0.8`이면 `floor`는 후보로 남을까요? 이유를 먼저 설명해 보세요.

답: 남습니다. `mat`만으로는 임계값에 못 미치지만, `floor`까지 더하면 넘습니다. top-p는 토큰 하나의 확률과 `p`를 비교하지 않고, 앞에서부터 더한 확률과 비교합니다.

## Limits / 한계
- A token can be a word, part of a word, or punctuation. The labels do not prove real tokenizer boundaries.
- 전체 어휘를 네 후보로 줄인 교육용 예제이며, 실제 모델의 추론 결과가 아닙니다.
- 표시를 반올림하면 합이 100%와 조금 다를 수 있습니다. 내부 계산은 정규화된 값으로 합니다.
- 영어는 STE-inspired 문체입니다. ASD-STE100 준수 인증을 받았다는 뜻이 아닙니다.
- 다음 토큰의 예측 확률은 내용의 사실성을 보증하지 않습니다.
- 사람 대상 이해도 실험은 하지 않았습니다. 계산·기능·미디어 테스트와 학습 효과는 별개입니다.

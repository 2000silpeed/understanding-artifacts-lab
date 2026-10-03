# Sources and evidence boundaries

## Source-backed mechanisms
- Hugging Face Transformers, [generation configuration](https://huggingface.co/docs/transformers/en/main_classes/text_generation): temperature modulates next-token probabilities; top-p keeps a smallest highest-probability set reaching the specified probability mass. Retrieved successfully (HTTP 200) during production.
- Hugging Face LLM Course, [tokenizers introduction](https://huggingface.co/learn/llm-course/en/chapter6/1): tokenizers map text into token units; token units are not necessarily whole words. Retrieved successfully (HTTP 200).
- ASD, [Simplified Technical English](https://www.asd-ste100.org/): primary reference for the English writing-style inspiration. The sample is **STE-inspired**, not certified ASD-STE100 documentation.
- Andrej Karpathy, [original post](https://x.com/karpathy/status/2105819303471976479): the inspiration to explain ideas with writing, diagrams, interactive HTML and bespoke videos. Original post was read directly in the browser; quoted text matched the supplied source.

## Illustrative inputs, computed outputs
`The cat sat on the` is a short teaching context. The four labels ` mat`, ` floor`, ` sofa`, ` roof` and scores `[2.0, 1.0, 0.3, -0.4]` are manually selected educational inputs. They are not measured outputs from a language model or a claim about a particular tokenizer. A real model supplies scores over its full vocabulary and recomputes them after a token is appended.

The demo computes stable softmax after temperature scaling. It sorts probabilities for nucleus filtering, includes the threshold-crossing candidate, and renormalizes retained mass. Greedy selection is a separate mode. Sampling may select a candidate other than the maximum.

## Limits
- This is an inspectable, one-step educational simulation, not a language model implementation.
- Predictive probability is not independently verified factual correctness. Neither temperature nor top-p certifies accuracy.
- Tests establish properties of calculations, interactions, layout and media files. No human learning study was conducted, and no comprehension improvement is claimed.
- Video narration uses the installed local English Kokoro voice; on-screen explanations are Korean. No additional paid API is required for the production pipeline.

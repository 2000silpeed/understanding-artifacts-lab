# Evidence rubric for inspectable explanations

## Five independent review layers
1. Semantic: verify each explanatory claim and calculation against the source and canonical contract. Distinguish observations, computed values, illustrative inputs and conjecture. Any incorrect central mechanism blocks publication.
2. Executable: pure-function unit tests, browser interaction and state/reset tests, deterministic rendering, offline requests, dependency integrity. A successful unit suite is not a guarantee of semantic accuracy.
3. Perceptual: inspect full video sheet and final decoded stills, desktop/mobile screenshots, glyph rendering, arrow meaning, overlaps, readable labels, cue synchronization and signal-to-noise. Actual visible issues drive revisions, not generic praise.
4. Accessible: keyboard use, labels, focus, contrast measurement, reduced motion, captions/transcript, responsive layout. Limited checks are not WCAG certification. Audio evidence includes actual loudness/silence/speech check outputs where available; missing checks stay disclosed.
5. Learning: ask a learner to predict a changed case and explain why, compare outcomes with a baseline only with consent and an appropriate study design. Without people tested, report design intent, not measured comprehension gains.

## Report shape
Use JSON with artifact hashes, commands, timestamps from the system, exit codes, assertions, evidence paths, reviewer findings, fixed issues and remaining limits. Every metric needs a producing command or source. Retain failure reports; don't rename planned tests as passed. Re-run relevant tests after final revisions.

## Minimal comparison
Use the same core example, terminology and caveats in all four formats. Writing supplies precise lookup; diagram shows relationships; web supports variable intervention; video can introduce an idea with timed visual causality. This is a design interpretation, not a universal ranking. Include a misconception and an intervention learners can reason about.

## Publishing
Reveal what is illustrative. A concise SNS post can say 'same example in writing, diagram, web and narrated video; checked calculations and interactions; no user comprehension study'. Include reproducible prompt/source and original post via a real quote-repost when authorized. Technical counts come from final test output. Publish once, space chain replies, read back media/text and verify survival; stop on gates, don't repeatedly click ambiguous submit outcomes.

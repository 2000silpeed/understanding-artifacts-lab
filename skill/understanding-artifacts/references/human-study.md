# Actual human listening and learning evaluation

## Evidence boundary
A consent page, working quiz, browser automation, synthetic fixture, ASR transcript and AI review are not participating people. Keep technical quality, translation review, listening judgments and measured learning outcomes separate. Until actual responses arrive, report human outcomes as NOT_MEASURED, not a zero-percent learning gain or a passed study.

## Minimal protocol
1. Explain purpose, voluntary participation, data collected and withdrawal before beginning. Do not collect names, contacts or sensitive information. Do not silently upload answers. Static hosting can still receive normal asset requests; distinguish this from uploading questionnaire answers.
2. Use separate listening and learning flows. Showing videos or transcripts before a learning pretest contaminates that measurement. Record prior topic knowledge, prior artifact exposure and subsequent cross-format exposure.
3. Freeze question-bank version and exact artifact SHA-256 identities. Assign topic/format with unbiased randomness or a declared counterbalanced schedule. Comparisons need sufficient real participants per condition; a one-person pilot is not evidence of format superiority.
4. Use a baseline question set, one assigned format, posttest and optional delayed recall. Prevent accidental access to the other formats where possible, and record unavoidable exposure. Delayed recall needs an actual elapsed-time gate and a recorded completion time; do not substitute immediate repeated answers.
5. Ask listeners concrete questions about sound, subtitle readability, clause coverage, synchronization and overlapping visuals. Include short comments without soliciting identifying information. These are subjective judgments, not automatic timing certification.
6. Export an anonymous response locally. Obtain real participant submissions through the user's approved channel. Keep raw submissions out of public repositories and distributions. Describe responses as self-declared human unless identity was independently verified; do not promise authentication the protocol cannot provide.
7. Mark every automated/synthetic QA response prominently and exclude it from human analysis. Rerun scoring against the frozen question bank, validate timestamps and consent, deduplicate sessions, and report excluded/incomplete counts. A missing input directory is an error, not evidence that no people participated.
8. Publish only appropriately consented aggregate findings. Include sample counts, per-condition counts, missing data, exposure limitations and uncertainty. Avoid causal learning claims from an uncontrolled pilot. Leave unmeasured outcomes explicitly unmeasured.

## Verification
Run pure-core and analyzer tests with clearly synthetic fixtures; then exercise consent, assignment, all available real content, video controls, response export, withdrawal and delayed-recall gates in a browser. Check actual question/artifact hashes and final media identities after staging. Those tests establish that the evaluation tooling works, not that human evaluation happened.

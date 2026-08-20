# Benchmark

Deterministic shape metrics for output styles. No LLM judge: "is this better?"
conflates completeness with quality, so it cannot fairly score a style whose job
is saying less.

    python3 score.py answers/*.jsonl          # metrics table
    python3 build_tastetest.py answers/*.jsonl > tastetest.html   # blind A/B/C/D

`score.py` reports words, time-to-point (words before the first emphasized
claim), longest unanchored paragraph, mean paragraph length, answer-first rate,
and deliverable purity.

**Known bias:** time-to-point and answer-first key on `**` bold. Styles that
mandate bolding score well by construction; a style that leads with the point in
plain prose scores as though it buried it. Treat those two as directional and
weight purity, which is convention-independent.

Design owes its ideas to alexgreensh/attention-span's benchmark (measure work
and output separately, refuse an LLM judge, time-to-point over reading grade).
Code here is original and MIT; theirs is AGPL-3.0 and is not vendored.

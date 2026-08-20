#!/usr/bin/env python3
"""Deterministic shape metrics for an output style's answers.

No LLM judge. "Is this better?" conflates completeness with quality, so it
cannot fairly score a style whose whole job is saying less. Everything here is
computed from the text itself and is reproducible.

Input:  a .jsonl of {"arm", "id", "text"}
Output: per-arm aggregates + per-answer rows.

    python3 score.py answers.jsonl
"""
import json, re, sys, statistics
from collections import defaultdict

# --- deliverable purity -------------------------------------------------
# When asked to PRODUCE a thing, does the reply hand over the thing, or wrap it?
OPENER = re.compile(
    r"^\s*\**(here'?s|here is|sure|certainly|of course|below is|this is|"
    r"the following|absolutely|happy to|got it|no problem|i'?ve\s+"
    r"(drafted|written|put together|got))\b", re.I)
CLOSER = re.compile(
    r"(let me know if you|want me to|happy to (adjust|tweak|revise|change|"
    r"shorten|expand|help)|i can (adjust|tweak|revise|shorten|expand)|"
    r"does this work|if you'?d like me to|just say the word|hope this helps|"
    r"feel free to (adjust|tweak|customize|edit))", re.I)
LEAD_IN = re.compile(r"[:.]\s*\n+\s*(>|```|\*\*|\")", re.S)

def purity(text):
    t = text.strip()
    first = next((l for l in t.splitlines() if l.strip()), "")
    why = []
    if OPENER.search(first):                       why.append("opener")
    if CLOSER.search(t):                           why.append("closer-offer")
    if OPENER.search(first) and LEAD_IN.search(t[:200]): why.append("lead-in")
    return (not why), why

# --- scannability -------------------------------------------------------
ANCHOR = re.compile(r"(\*\*|^\s*[-*+]\s|^\s*\d+\.\s|^\s*\||^#)", re.M)
WORD = re.compile(r"\b[\w'-]+\b")

def words(s):        return len(WORD.findall(s))
def paras(t):        return [p for p in re.split(r"\n\s*\n", t.strip()) if p.strip()]

def time_to_point(t):
    """Words you read before the first emphasized claim. Lower is better."""
    m = re.search(r"\*\*", t)
    return words(t[:m.start()]) if m else words(t)

def answer_first(t):
    """1 if the first non-empty line already carries a point (bold or list)."""
    first = next((l for l in t.strip().splitlines() if l.strip()), "")
    return int(bool(ANCHOR.search(first)))

def longest_wall(t):
    """Longest paragraph carrying no anchor at all. The wall-of-text metric."""
    return max((words(p) for p in paras(t) if not ANCHOR.search(p)), default=0)

def metrics(t):
    ps = paras(t)
    pure, why = purity(t)
    return {"words": words(t), "ttp": time_to_point(t), "first": answer_first(t),
            "wall": longest_wall(t), "para": round(statistics.mean(
                [words(p) for p in ps]) if ps else 0, 1),
            "pure": int(pure), "why": why}

def main(path):
    rows = [json.loads(l) for l in open(path) if l.strip()]
    by = defaultdict(list)
    for r in rows:
        m = metrics(r["text"]); m["id"] = r["id"]; by[r["arm"]].append(m)
    keys = [("words", "words"), ("ttp", "time-to-point"), ("wall", "longest wall"),
            ("para", "mean para"), ("first", "answer-first %"), ("pure", "pure %")]
    print(f"{'arm':<12}" + "".join(f"{lbl:>16}" for _, lbl in keys))
    for arm, ms in by.items():
        out = f"{arm:<12}"
        for k, _ in keys:
            v = statistics.mean(m[k] for m in ms)
            out += f"{v*100:>15.0f}%" if k in ("first", "pure") else f"{v:>16.1f}"
        print(out)
    json.dump({a: ms for a, ms in by.items()},
              open(path.replace(".jsonl", "-scored.json"), "w"), indent=2)

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "answers.jsonl")

"""POST-HOC re-scoring of the Q3 mask-check gate. NOT the registered analysis.

Read `analyze_phase3.py` first — that is the frozen §3/§7b result and it governs. This script exists
because the registered gate metric turned out to be a poor proxy for the §7b criterion it implemented,
and the run's own stored continuations show it failing in BOTH directions (see prediction.md §9,
2026-07-21 "Q3 gate flaw"). It is reported as a clearly-labelled secondary, exactly as v1's §5
correction was: the frozen verdict is not overwritten by it.

**Honest provenance.** This rule was written AFTER seeing the frozen gate's output and after reading
the d=10 continuations. That is a researcher degree of freedom and is stated rather than hidden. Two
things limit it: the rule is fixed before being computed, and it uses the least tunable threshold
available (binary presence of any scene-specific content word, not a tuned count).

**The rule.** §7b's actual criterion is: "under scene ablation the model can no longer answer 'what did
NAME do?', and under the matched control ablation it still can." The greedy continuation answers that
question directly, so score it directly:

  scene_overlap(continuation) = # distinct content words (>=4 chars, minus stopwords) shared with the
                                character's `inferred` sentence, EXCLUDING any word that also appears
                                in the shared opening.

  Excluding opening words is what makes this meaningful: with the scene masked the model falls back to
  reciting the occupation, which must score 0, not count as "still reporting".

  Gate passes iff:  baseline >= 1  AND  scene-masked == 0  AND  control-masked >= 1.

Runs off `phase3/phase3_scene_continuations.csv` + the stimuli file. No GPU, no new measurement.
"""
import csv, pathlib, re, sys, math

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import trait_persistence_v2_stimuli as S

DEC_D = 10
R_RETRIEVABLE, HELD_LATENT_RATIO, HELD_SCENE_RATIO = 50.0, 2.0, 5.0

STOP = {
    "that", "this", "with", "from", "have", "been", "were", "what", "when", "then", "than", "they",
    "them", "their", "there", "here", "into", "onto", "over", "under", "about", "after", "before",
    "again", "also", "just", "only", "very", "much", "more", "most", "some", "such", "each", "every",
    "other", "which", "would", "could", "should", "never", "always", "down", "back", "away",
    "through", "without", "once", "else", "while", "until", "whole", "twice", "long",
}


def content_words(text):
    ws = re.findall(r"[a-z]+", (text or "").lower())
    return {w for w in ws if len(w) >= 4 and w not in STOP}


def scene_overlap(continuation, char):
    scene = content_words(char["inferred"])
    opening = content_words(char["opening"])
    return len(content_words(continuation) & (scene - opening))


def _f(x):
    try:
        v = float(x)
        return v if not math.isnan(v) else None
    except (TypeError, ValueError):
        return None


def _find(fname):
    for p in (HERE / "phase3" / fname, HERE / fname):
        if p.exists():
            return p
    raise FileNotFoundError(fname)


# ---- load -------------------------------------------------------------------------------------
CONT = {}
for x in csv.DictReader(open(_find("phase3_scene_continuations.csv"), newline="", encoding="utf-8")):
    CONT[(x["name"], int(x["distance"]), x["condition"])] = x["continuation"]

ABL = {}
NAMES = []
for x in csv.DictReader(open(_find("phase3_ablation.csv"), newline="", encoding="utf-8")):
    ABL[(x["name"], int(x["distance"]), x["condition"])] = _f(x["trait_j_median_rank"])
    if x["name"] not in NAMES:
        NAMES.append(x["name"])
NAMES = sorted(NAMES)


def verdict(name, d):
    R_i, R_ii, R_iii = (ABL.get((name, d, c)) for c in ("baseline", "scene", "control"))
    if None in (R_i, R_ii, R_iii):
        return "n/a", None
    if R_i > R_RETRIEVABLE:
        return "(c) underpowered", None
    rr = R_ii / R_iii if R_iii else float("inf")
    if R_ii <= R_RETRIEVABLE and rr <= HELD_LATENT_RATIO:
        return "(a) HELD LATENT", rr
    if rr >= HELD_SCENE_RATIO:
        return "(b) HELD SCENE", rr
    return "partial", rr


print("POST-HOC gate re-scoring (NOT the registered result — see analyze_phase3.py).")
print(f"Rule: scene-specific content-word overlap in the generated answer; pass iff base>=1, scene==0, ctrl>=1.")
print(f"\n{'='*100}\nd = {DEC_D}\n{'='*100}")
print(f"{'char':<8}{'base':>6}{'scene':>7}{'ctrl':>6}  {'gate':<10}{'verdict':<18}{'ratio':>9}")

tally = {}
for name in NAMES:
    c = S.by_name(name)
    ov = {cond: scene_overlap(CONT.get((name, DEC_D, cond), ""), c)
          for cond in ("baseline", "scene", "control")}
    passed = ov["baseline"] >= 1 and ov["scene"] == 0 and ov["control"] >= 1
    if passed:
        tag, rr = verdict(name, DEC_D)
    else:
        tag, rr = "NOT-RUN (gate)", None
    tally[tag] = tally.get(tag, 0) + 1
    print(f"{name:<8}{ov['baseline']:>6}{ov['scene']:>7}{ov['control']:>6}  "
          f"{'PASS' if passed else 'FAIL':<10}{tag:<18}{(f'{rr:.1f}x' if rr else ''):>9}")

print("\n  tally: " + ", ".join(f"{k}={v}" for k, v in sorted(tally.items())))
print("\nContinuations behind the scoring (d=10):")
for name in NAMES:
    print(f"\n  {name}:")
    for cond in ("baseline", "scene", "control"):
        print(f"    {cond:<9}: {(CONT.get((name, DEC_D, cond), '') or '').strip()[:88]}")

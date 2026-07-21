"""Phase 3 — analysis of the Phase 2 sweep against the FROZEN criteria in prediction.md §3.

Pure stdlib (no numpy/scipy): the Wilcoxon signed-rank test is computed exactly by enumerating all
2^n sign assignments, which is trivial and exact at n = 7. Reads phase2/phase2_reads.csv and
phase2/phase2_logit_posctrl.csv; writes nothing (prints a report). The results doc is written by hand
from this output so a human sees every number before it is committed.

Nothing here may reinterpret a criterion. Where a rule is a judgement call (the §7a extension trigger),
the ambiguity is reported, not silently resolved.
"""
import csv, itertools, statistics, pathlib

HERE = pathlib.Path(__file__).resolve().parent
DIST_PERSIST = [1, 2, 4, 7, 10]          # d0 excluded from persistence (§3)
CUE = "cue_b"                            # the primary Q1/Q2 cue (§7)

# ---- load -------------------------------------------------------------------------------------
R = {}   # (name, arm, d, cue, measure) -> {"j": float, "l": float}
NAMES, TRAITS = [], {}
with open(HERE / "phase2" / "phase2_reads.csv", newline="", encoding="utf-8") as f:
    for x in csv.DictReader(f):
        key = (x["name"], x["arm"], int(x["distance"]), x["cue"], x["measure"])
        R[key] = {"j": float(x["j_median_rank_band"]), "l": float(x["logit_median_rank_band"])}
        if x["name"] not in NAMES:
            NAMES.append(x["name"]); TRAITS[x["name"]] = x["trait"]

POSCTRL = {}
with open(HERE / "phase2" / "phase2_logit_posctrl.csv", newline="", encoding="utf-8") as f:
    for x in csv.DictReader(f):
        POSCTRL[x["name"]] = x["logit_positive_control"].strip().lower() == "true"

NAMES = sorted(NAMES)
N = len(NAMES)


def med(xs):
    return statistics.median(xs)


def ratio(name, arm, d, measure="trait", lens="j"):
    """R(arm, d, cue) / R(control, d, cue), same measure/cue/lens. Lower = more retrievable."""
    num = R[(name, arm, d, CUE, measure)][lens]
    den = R[(name, "control", d, CUE, measure)][lens]
    return num / den if den else float("inf")


# ---- exact Wilcoxon signed-rank (two-sided) ---------------------------------------------------
def wilcoxon_exact(diffs):
    """Exact two-sided signed-rank p over 2^n sign flips. diffs: paired (a-b), zeros dropped."""
    d = [x for x in diffs if x != 0]
    n = len(d)
    if n == 0:
        return None, None, None
    mags = sorted((abs(x), i) for i, x in enumerate(d))
    ranks = [0.0] * n
    i = 0
    while i < n:                                   # average-rank tie handling
        j = i
        while j + 1 < n and mags[j + 1][0] == mags[i][0]:
            j += 1
        avg = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[mags[k][1]] = avg
        i = j + 1
    w_plus = sum(r for r, x in zip(ranks, d) if x > 0)
    # exact null: each rank's sign is +/- with equal prob; distribution of W+ over all 2^n flips.
    total = 2 ** n
    at_least = 0
    obs_dev = abs(w_plus - sum(ranks) / 2.0)
    for signs in itertools.product((0, 1), repeat=n):
        wp = sum(r for r, s in zip(ranks, signs) if s)
        if abs(wp - sum(ranks) / 2.0) >= obs_dev - 1e-9:
            at_least += 1
    return w_plus, at_least / total, n


# =================================================================================================
print("=" * 90)
print("PHASE 3 ANALYSIS — Phase 2 sweep vs frozen prediction.md §3 criteria")
print(f"n = {N} survivors: {NAMES}   |   primary cue = {CUE}   |   persistence distances = {DIST_PERSIST}")
print("=" * 90)

# ---- Q1 -----------------------------------------------------------------------------------------
print("\n" + "#" * 90)
print("# Q1 — does the STATED trait stay more retrievable than the INFERRED one? (primary measure)")
print("#" * 90)
print("\nPer-character ratio-to-control at each distance (Cue B, trait lexicon). Lower = more retrievable.")
print("  D = direct/control   I = inferred/control   *=direct more retrievable (D<I)\n")
hdr = "  {:<7}".format("name") + "".join(f"  d{d:<2}D  d{d:<2}I ".rjust(8) for d in DIST_PERSIST)
print(hdr)

char_dir_med, char_inf_med = {}, {}
win_count = {d: 0 for d in DIST_PERSIST}
char_win = {}
for name in NAMES:
    dr = {d: ratio(name, "direct", d) for d in DIST_PERSIST}
    ir = {d: ratio(name, "inferred", d) for d in DIST_PERSIST}
    char_dir_med[name] = med(list(dr.values()))
    char_inf_med[name] = med(list(ir.values()))
    line = f"  {name:<7}"
    wins = 0
    for d in DIST_PERSIST:
        star = "*" if dr[d] < ir[d] else " "
        if dr[d] < ir[d]:
            win_count[d] += 1; wins += 1
        line += f"  {dr[d]:.3f} {ir[d]:.3f}{star}"
    char_win[name] = wins
    print(line + f"   [{wins}/5 d where direct wins]")

print("\n  per-distance: # of characters where direct is more retrievable than inferred:")
print("   " + "  ".join(f"d{d}={win_count[d]}/{N}" for d in DIST_PERSIST))
char_majority = sum(1 for name in NAMES if char_win[name] >= 3)
print(f"  characters where direct wins at a majority (>=3/5) of distances: {char_majority}/{N}")
maj_maj = char_majority > N / 2
print(f"  'majority of characters at a majority of distances' (outcome-1 direction): "
      f"{'MET' if maj_maj else 'NOT met'}")

# Wilcoxon: primary = per-character, d collapsed by median (n=7, registered weak).
diffs = [char_dir_med[name] - char_inf_med[name] for name in NAMES]   # negative => direct better
wp, p, nz = wilcoxon_exact(diffs)
print(f"\n  Wilcoxon signed-rank (PRIMARY, per-character median over d; n={nz} non-zero pairs):")
print(f"    median direct ratio across chars = {med(list(char_dir_med.values())):.4f}")
print(f"    median inferred ratio across chars = {med(list(char_inf_med.values())):.4f}")
print(f"    W+ = {wp}, exact two-sided p = {p:.4f}  ->  "
      f"{'clears p<0.05' if p is not None and p < 0.05 else 'does NOT clear p<0.05'}")

print("\n  Wilcoxon per distance (secondary breakdown, 7 pairs each):")
for d in DIST_PERSIST:
    dd = [ratio(name, "direct", d) - ratio(name, "inferred", d) for name in NAMES]
    _, pd_, nzd = wilcoxon_exact(dd)
    print(f"    d={d:<2}: p = {pd_:.4f} (n={nzd})  {'*' if pd_ < 0.05 else ''}")

# Retrievability classification (R<=50 AND ratio<=0.8) at each d, per arm.
print("\n  Retrievable per §3 (R<=50 AND ratio<=0.8), count of characters:")
for arm in ("direct", "inferred"):
    cells = []
    for d in DIST_PERSIST:
        c = sum(1 for name in NAMES
                if R[(name, arm, d, CUE, "trait")]["j"] <= 50 and ratio(name, arm, d) <= 0.8)
        cells.append(f"d{d}={c}/{N}")
    print(f"    {arm:<9}: " + "  ".join(cells))

# ---- Q2 -----------------------------------------------------------------------------------------
print("\n" + "#" * 90)
print("# Q2 — is the DIRECT arm's persistence trait-specific, or generic token-echo? (tracer control)")
print("#" * 90)
print("\n  Per character, median over d>=1 (Cue B):")
print("    trait ratio  = R(direct,trait)/R(control,trait)")
print("    tracer ratio = R(direct,tracer)/R(control,tracer)\n")
trait_ratios, tracer_ratios = {}, {}
for name in NAMES:
    tr = med([ratio(name, "direct", d, "trait") for d in DIST_PERSIST])
    kr = med([ratio(name, "direct", d, "tracer") for d in DIST_PERSIST])
    trait_ratios[name], tracer_ratios[name] = tr, kr
    print(f"    {name:<7} trait={tr:.3f}   tracer={kr:.3f}")
trait_med = med(list(trait_ratios.values()))
tracer_med = med(list(tracer_ratios.values()))
print(f"\n  median across characters:  trait={trait_med:.3f}   tracer={tracer_med:.3f}")
gap = abs(tracer_med - trait_med)
if gap <= 0.15:
    q2 = "OUTCOME (b): COPY BIAS — tracer persists comparably to the trait (within 0.15)."
elif tracer_med >= 0.95 and trait_med <= 0.8:
    q2 = "OUTCOME (a): TRAIT-SPECIFIC — tracer at floor while the trait clears 0.8."
else:
    q2 = "AMBIGUOUS/PARTIAL — neither (a) nor (b); Q1 rests on the cued reads alone."
print(f"  |tracer - trait| = {gap:.3f}   ->  {q2}")

# ---- Q5 -----------------------------------------------------------------------------------------
print("\n" + "#" * 90)
print("# Q5 — does the J-lens read the INFERRED (never-tokenised) trait where the logit lens cannot?")
print("#   Only interpretable where the logit positive control PASSED (§4a).")
print("#" * 90)
passed = [n for n in NAMES if POSCTRL.get(n)]
print(f"\n  positive control passed: {passed}  (logit nulls void for the rest)\n")
print("  Inferred arm, Cue B, J-lens vs logit-lens median rank by distance:")
for name in passed:
    print(f"\n    {name} ({TRAITS[name]}):")
    for d in [0] + DIST_PERSIST:
        j = R[(name, "inferred", d, CUE, "trait")]["j"]
        l = R[(name, "inferred", d, CUE, "trait")]["l"]
        note = "  J surfaces, logit buried" if (j <= 50 and l > 5 * j) else ""
        print(f"      d={d:<2}  J={j:>7.1f}   logit={l:>7.1f}{note}")

# ---- §7a extension trigger ----------------------------------------------------------------------
print("\n" + "#" * 90)
print("# §7a — registered conditional extension past d=10 (evaluation only; would need another run)")
print("#" * 90)
dir_d10 = med([ratio(name, "direct", 10) for name in NAMES])
dir_d4  = med([ratio(name, "direct", 4)  for name in NAMES])
inf_d10 = med([ratio(name, "inferred", 10) for name in NAMES])
inf_d4  = med([ratio(name, "inferred", 4)  for name in NAMES])
contrast_d4  = inf_d4 - dir_d4
contrast_d10 = inf_d10 - dir_d10
cond1 = dir_d10 <= 0.8
print(f"\n  direct median ratio-to-control: d4={dir_d4:.3f}  d10={dir_d10:.3f}")
print(f"  inferred median ratio-to-control: d4={inf_d4:.3f}  d10={inf_d10:.3f}")
print(f"  direct<=0.8 at d10 (still retrievable, not decayed to control): {cond1}")
print(f"  direct-vs-inferred contrast (inferred-direct): d4={contrast_d4:+.4f}  d10={contrast_d10:+.4f}")
print(f"  -> the separation has {'NOT opened up' if contrast_d10 <= contrast_d4 * 1.2 else 'OPENED up'} "
      f"from d4 to d10")
print("  NOTE the interpretive tension: direct ratio ~0.02 also means the direct rank is near the")
print("  rank FLOOR (rank 1-a few), a dynamic-range concern §7a itself raises. Report, do not auto-decide.")
print("  OVERRIDE: if Q2 == (b) copy bias, the extension does NOT run regardless of the trigger.")

print("\n" + "=" * 90)
print("END. Numbers above feed PHASE2_RESULTS.md, written by hand so a human sees them first.")
print("=" * 90)

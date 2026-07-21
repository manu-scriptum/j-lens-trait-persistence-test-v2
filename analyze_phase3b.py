"""Phase 3b analysis — the Q3 re-run with the CORRECTED gate, registered in advance.

Governed by prediction.md §9, "Phase 3b: corrected gate registered as primary". The §3 verdict rule is
unchanged and used verbatim; only the mask-check realisation is repaired.

  * PRIMARY gate   — continuation-scored `scene_overlap` (imported from `analyze_phase3_posthoc` so the
                     rule is byte-identical to the one registered, never a drifting copy):
                     pass iff baseline >= 1, scene-masked == 0, control-masked >= 1.
  * SECONDARY gate — repaired rank read: best scene-keyword rank across the first 12 GENERATED
                     positions; pass iff kw_i <= 50, kw_ii/kw_i >= 5.0, kw_iii/kw_i <= 2.0.

Both are reported. Agreement closes the instrument question; **disagreement is reported as an open
instrument problem, not resolved in favour of whichever is convenient.**

Also reported, because §9 registered them:
  * the replication comparison of Phase 3b trait reads against Phase 3 (they should reproduce);
  * a check of the registered expectations — above all, **did Elias fail as predicted?** A gate that
    certifies everything, Elias included, is a gate that is too permissive, and is reported as such.

Standing honesty note: the corrected gate is "pre-registered for THIS run, derived from the previous
one". Better than post-hoc; not the same as having specified it correctly the first time.
"""
import csv, pathlib, math, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import trait_persistence_v2_stimuli as S
from analyze_phase3_posthoc import scene_overlap          # the frozen rule, imported not copied

DEC_D, EXPL_D = 10, 30
R_RETRIEVABLE, HELD_LATENT_RATIO, HELD_SCENE_RATIO = 50.0, 2.0, 5.0
GATE_BASE_MAX, GATE_REMOVE, GATE_SPARE = 50.0, 5.0, 2.0

# Registered expectations (prediction.md §9, before this run existed).
EXPECTED = {
    "Elias": "NOT-RUN (gate)", "Marek": "(c) underpowered",
    "Greta": "(b) HELD SCENE", "Nadia": "(b) HELD SCENE", "Maria": "(b) HELD SCENE",
    "Simon": "(b) HELD SCENE", "Bruno": "(b) HELD SCENE",
}


def _f(x):
    try:
        v = float(x)
        return v if not math.isnan(v) else None
    except (TypeError, ValueError):
        return None


def _find(fname, sub="phase3b"):
    for p in (HERE / sub / fname, HERE / fname):
        if p.exists():
            return p
    raise FileNotFoundError(f"{fname} not found in {sub}/ or the repo root.")


# ---- load -------------------------------------------------------------------------------------
ABL, CONT, KWGEN, NAMES = {}, {}, {}, []
for x in csv.DictReader(open(_find("phase3b_ablation.csv"), newline="", encoding="utf-8")):
    ABL[(x["name"], int(x["distance"]), x["condition"])] = _f(x["trait_j_median_rank"])
    if x["name"] not in NAMES:
        NAMES.append(x["name"])
for x in csv.DictReader(open(_find("phase3b_gate.csv"), newline="", encoding="utf-8")):
    k = (x["name"], int(x["distance"]), x["condition"])
    CONT[k] = x["continuation"]
    KWGEN[k] = _f(x["scene_kw_rank_gen"])
NAMES = sorted(NAMES)

DIRECT = {}
try:
    for x in csv.DictReader(open(_find("phase3b_direct.csv"), newline="", encoding="utf-8")):
        DIRECT[(x["name"], int(x["distance"]), x["condition"])] = _f(x["trait_j_median_rank"])
except FileNotFoundError:
    pass

# Phase 3 trait reads, for the replication comparison (optional).
P3 = {}
try:
    for x in csv.DictReader(open(HERE / "phase3" / "phase3_ablation.csv", newline="", encoding="utf-8")):
        P3[(x["name"], int(x["distance"]), x["condition"])] = _f(x["trait_j_median_rank"])
except FileNotFoundError:
    pass


# ---- gates + verdict --------------------------------------------------------------------------
def primary_gate(name, d):
    c = S.by_name(name)
    ov = {k: scene_overlap(CONT.get((name, d, k), ""), c) for k in ("baseline", "scene", "control")}
    ok = ov["baseline"] >= 1 and ov["scene"] == 0 and ov["control"] >= 1
    return ok, ov


def secondary_gate(name, d):
    ki, kii, kiii = (KWGEN.get((name, d, k)) for k in ("baseline", "scene", "control"))
    if None in (ki, kii, kiii) or ki <= 0:
        return None, (ki, kii, kiii)
    ok = ki <= GATE_BASE_MAX and kii >= GATE_REMOVE * ki and kiii <= GATE_SPARE * ki
    return ok, (ki, kii, kiii)


def verdict(name, d):
    R_i, R_ii, R_iii = (ABL.get((name, d, k)) for k in ("baseline", "scene", "control"))
    if None in (R_i, R_ii, R_iii):
        return "n/a", None, (R_i, R_ii, R_iii)
    if R_i > R_RETRIEVABLE:
        return "(c) underpowered", None, (R_i, R_ii, R_iii)
    rr = R_ii / R_iii if R_iii else float("inf")
    if R_ii <= R_RETRIEVABLE and rr <= HELD_LATENT_RATIO:
        tag = "(a) HELD LATENT"
    elif rr >= HELD_SCENE_RATIO:
        tag = "(b) HELD SCENE"
    else:
        tag = "partial"
    return tag, rr, (R_i, R_ii, R_iii)


def block(d, is_decision):
    print(f"\n{'='*104}\nd = {d}  —  {'DECISION CHECKPOINT' if is_decision else 'EXPLORATORY (no verdict)'}\n{'='*104}")
    print(f"{'char':<8}{'primary':>9}{'secondary':>11}  {'verdict':<18}{'ratio':>10}   R i/ii/iii")
    tally, disagree, results = {}, [], {}
    for name in NAMES:
        p_ok, ov = primary_gate(name, d)
        s_ok, kw = secondary_gate(name, d)
        if s_ok is not None and s_ok != p_ok:
            disagree.append((name, p_ok, s_ok, ov, kw))
        if p_ok:
            tag, rr, R = verdict(name, d)
        else:
            tag, rr, R = "NOT-RUN (gate)", None, verdict(name, d)[2]
        results[name] = tag
        tally[tag] = tally.get(tag, 0) + 1
        rs = "/".join(f"{v:.1f}" if v is not None else "-" for v in R)
        print(f"{name:<8}{'PASS' if p_ok else 'FAIL':>9}"
              f"{('PASS' if s_ok else 'FAIL') if s_ok is not None else 'n/a':>11}  "
              f"{tag:<18}{(f'{rr:.1f}x' if rr else ''):>10}   {rs}")
    print(f"\n  tally: " + ", ".join(f"{k}={v}" for k, v in sorted(tally.items())))

    if disagree:
        print("\n  ** GATES DISAGREE — reported as an open instrument problem, not resolved: **")
        for name, p, s, ov, kw in disagree:
            print(f"     {name}: primary={'PASS' if p else 'FAIL'} (overlap {ov['baseline']}/{ov['scene']}/{ov['control']})  "
                  f"secondary={'PASS' if s else 'FAIL'} (kw {kw[0]:.0f}/{kw[1]:.0f}/{kw[2]:.0f})")
    else:
        print("\n  both gates agree on every character — the instrument question is closed for this run.")
    return results


print("Phase 3b — Q3 re-run with the corrected, pre-registered gate.")
print(f"n = {len(NAMES)}: {NAMES}")
print("Gate provenance: pre-registered for THIS run, derived from Phase 3. Not laundered by re-running.")

res = block(DEC_D, True)
block(EXPL_D, False)

# ---- registered expectations ------------------------------------------------------------------
print(f"\n{'='*104}\nREGISTERED EXPECTATIONS (prediction.md §9, recorded before this run)\n{'='*104}")
hits = 0
for name in sorted(EXPECTED):
    exp, got = EXPECTED[name], res.get(name, "n/a")
    ok = (exp == got)
    hits += ok
    print(f"  {name:<8} expected {exp:<18} got {got:<18} {'match' if ok else '** MISMATCH **'}")
print(f"\n  {hits}/{len(EXPECTED)} matched.")
if res.get("Elias") != "NOT-RUN (gate)":
    print("  ** Elias PASSED the corrected gate. §9 predicted he would fail (his scene was never")
    print("     elicited in Phase 3). This means the corrected gate is MORE PERMISSIVE than intended —")
    print("     report it as a gate problem, not as an extra certification. **")
else:
    print("  Elias failed as predicted — the corrected gate rejects as well as admits.")
if any(v == "(a) HELD LATENT" for v in res.values()):
    print("  ** A HELD LATENT appeared. This is the genuine surprise outcome — report it prominently. **")

# ---- replication ------------------------------------------------------------------------------
if P3:
    print(f"\n{'='*104}\nREPLICATION vs Phase 3 (trait rank, d={DEC_D}) — these should reproduce\n{'='*104}")
    print(f"{'char':<8}{'cond':<10}{'Phase3':>10}{'Phase3b':>10}{'delta':>9}")
    worst = 0.0
    for name in NAMES:
        for cond in ("baseline", "scene", "control"):
            a, b = P3.get((name, DEC_D, cond)), ABL.get((name, DEC_D, cond))
            if a is None or b is None:
                continue
            d_ = b - a
            worst = max(worst, abs(d_) / max(a, 1.0))
            print(f"{name:<8}{cond:<10}{a:>10.1f}{b:>10.1f}{d_:>+9.1f}")
    print(f"\n  largest relative deviation: {worst*100:.1f}%  (bf16/eager tie-shuffling; see §9)")

# ---- direct arm -------------------------------------------------------------------------------
if DIRECT:
    print(f"\n{'='*104}\nDIRECT-ARM symmetric test at d={DEC_D} (descriptive, not part of the verdict)\n{'='*104}")
    for name in NAMES:
        b, tt, tr = (DIRECT.get((name, DEC_D, k)) for k in ("baseline", "trait_tok", "tracer_tok"))
        if None in (b, tt, tr):
            continue
        print(f"{name:<8} baseline={b:>7.1f}  trait-masked={tt:>8.1f} (x{tt/b:>6.2f})  "
              f"tracer-masked={tr:>7.1f} (x{tr/b:>5.2f})")

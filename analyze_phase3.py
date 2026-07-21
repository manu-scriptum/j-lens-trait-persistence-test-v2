"""Analysis of the Phase 3 KV-ablation (Q3) against the FROZEN criteria in prediction.md §3 + §7b.

Naming note: the *notebook* `trait_persistence_v2_phase3.ipynb` is the Q3 ablation run (the next arm in
the phaseN sequence after phase1/phase2/phase2ext). This script is its off-GPU analysis, the same
division of labour `analyze_phase2.py` has for the Phase 2 sweep. Pure stdlib; reads the phase3_*.csv
files; writes nothing (prints a report a human turns into the results doc).

The order of operations is dictated by §7b: **the mask-check gate is applied first, per character.** A
character that fails the gate is reported `not-run`, NEVER a null — a failed mask manufactures exactly
the collapse that reads as the more-surprising outcome (b). Only gated-in characters get a §3 verdict.

Frozen numbers (do not edit here; change only via a dated prediction.md §9 amendment):
  * Gate (§9 "Q3 implementation"): scene-keyword model-output rank kw_i<=50 AND kw_ii/kw_i>=5.0 AND
    kw_iii/kw_i<=2.0  (baseline reportable, scene-mask removes it, control-mask spares it).
  * §3 verdict on the inferred-arm trait rank R (J-lens band median), at d=10 Cue B:
        R_i>50               -> (c) underpowered (declared before looking at ii/iii)
        R_ii<=50 and R_ii/R_iii<=2.0 -> (a) held latent
        R_ii/R_iii>=5.0      -> (b) held scene
        otherwise            -> partial
  * d=30 is exploratory (§9): the same logic is reported to check the verdict is not distance-specific,
    but it carries NO §3 verdict.
"""
import csv, pathlib, math

HERE = pathlib.Path(__file__).resolve().parent
DEC_D = 10           # frozen decision checkpoint (prediction.md §9)
EXPL_D = 30          # exploratory distance-robustness check (no verdict)

# Frozen thresholds
GATE_BASE_MAX = 50.0
GATE_REMOVE   = 5.0
GATE_SPARE    = 2.0
R_RETRIEVABLE = 50.0
HELD_LATENT_RATIO = 2.0
HELD_SCENE_RATIO  = 5.0


def _f(x):
    try:
        v = float(x)
        return v if not math.isnan(v) else None
    except (TypeError, ValueError):
        return None


# ---- load -------------------------------------------------------------------------------------
ABL = {}   # (name, d, cond) -> R (inferred-arm trait j-median rank)
MASK = {}  # (name, d, cond) -> scene_kw model-output rank
DIRECT = {}  # (name, d, cond) -> direct-arm trait j-median rank
NAMES, TRAITS, NKW = [], {}, {}

with open(HERE / "phase3_ablation.csv", newline="", encoding="utf-8") as f:
    for x in csv.DictReader(f):
        ABL[(x["name"], int(x["distance"]), x["condition"])] = _f(x["trait_j_median_rank"])
        if x["name"] not in NAMES:
            NAMES.append(x["name"]); TRAITS[x["name"]] = x["trait"]

with open(HERE / "phase3_maskcheck.csv", newline="", encoding="utf-8") as f:
    for x in csv.DictReader(f):
        MASK[(x["name"], int(x["distance"]), x["condition"])] = _f(x["scene_kw_out_rank"])
        NKW[x["name"]] = int(x["n_scene_kw_ids"])

direct_path = HERE / "phase3_direct.csv"
if direct_path.exists():
    with open(direct_path, newline="", encoding="utf-8") as f:
        for x in csv.DictReader(f):
            DIRECT[(x["name"], int(x["distance"]), x["condition"])] = _f(x["trait_j_median_rank"])

NAMES = sorted(NAMES)


# ---- gate + verdict ---------------------------------------------------------------------------
def gate(name, d):
    """(-> passed:bool, reason:str) for the §7b scene-report mask-check at distance d."""
    if NKW.get(name, 0) == 0:
        return False, "no single-token scene keywords survived (cannot gate)"
    kw_i = MASK.get((name, d, "baseline"))
    kw_ii = MASK.get((name, d, "scene"))
    kw_iii = MASK.get((name, d, "control"))
    if kw_i is None or kw_ii is None or kw_iii is None:
        return False, "missing a mask-check condition (control undefined?)"
    if kw_i > GATE_BASE_MAX:
        return False, f"baseline scene-report too weak to gate (kw_i={kw_i:.0f} > {GATE_BASE_MAX:.0f})"
    removed = kw_ii >= GATE_REMOVE * kw_i
    spared  = kw_iii <= GATE_SPARE * kw_i
    if removed and spared:
        return True, f"kw i/ii/iii={kw_i:.0f}/{kw_ii:.0f}/{kw_iii:.0f} (removed & spared)"
    parts = []
    if not removed:
        parts.append(f"scene-mask did NOT remove the scene (kw_ii/kw_i={kw_ii/kw_i:.2f} < {GATE_REMOVE})")
    if not spared:
        parts.append(f"control-mask did NOT spare the scene (kw_iii/kw_i={kw_iii/kw_i:.2f} > {GATE_SPARE})")
    return False, "; ".join(parts)


def verdict(name, d):
    """§3 held-latent/held-scene/partial/underpowered on the inferred-arm trait rank at distance d."""
    R_i = ABL.get((name, d, "baseline"))
    R_ii = ABL.get((name, d, "scene"))
    R_iii = ABL.get((name, d, "control"))
    if R_i is None or R_ii is None or R_iii is None:
        return "n/a", f"missing a condition (R_i={R_i}, R_ii={R_ii}, R_iii={R_iii})", (R_i, R_ii, R_iii)
    if R_i > R_RETRIEVABLE:                      # (c) declared before looking at ii/iii
        return "(c) underpowered", f"R_i={R_i:.1f} > {R_RETRIEVABLE:.0f} (inferred trait not retrievable at baseline)", (R_i, R_ii, R_iii)
    rr = (R_ii / R_iii) if R_iii else float("inf")
    if R_ii <= R_RETRIEVABLE and rr <= HELD_LATENT_RATIO:
        tag = "(a) HELD LATENT"
    elif rr >= HELD_SCENE_RATIO:
        tag = "(b) HELD SCENE"
    else:
        tag = "partial"
    return tag, f"R i/ii/iii={R_i:.1f}/{R_ii:.1f}/{R_iii:.1f}  R_ii/R_iii={rr:.2f}  R_ii<=50={R_ii<=R_RETRIEVABLE}", (R_i, R_ii, R_iii)


def report_block(d, is_decision):
    label = "DECISION CHECKPOINT" if is_decision else "EXPLORATORY (no §3 verdict)"
    print(f"\n{'='*94}\nd = {d}  —  {label}\n{'='*94}")
    tally = {}
    for name in NAMES:
        passed, greason = gate(name, d)
        if not passed:
            print(f"{name:<7} {TRAITS[name]:<10}  GATE FAIL -> Q3 NOT-RUN   [{greason}]")
            tally["not-run"] = tally.get("not-run", 0) + 1
            continue
        tag, vreason, _ = verdict(name, d)
        print(f"{name:<7} {TRAITS[name]:<10}  {tag:<16} {vreason}")
        print(f"{'':<19}gate: {greason}")
        tally[tag] = tally.get(tag, 0) + 1
    print(f"\n  tally (d={d}): " + ", ".join(f"{k}={v}" for k, v in sorted(tally.items())))
    if is_decision:
        print("  NOTE: verdict is per-character; with n=7 the aggregate is descriptive and one item "
              "can dominate (watch Elias — the weak/anomalous cue in Phase 2).")
    return tally


def direct_block(d):
    if not DIRECT:
        return
    print(f"\n{'='*94}\nDIRECT-ARM symmetric test at d = {d}  (descriptive; NOT part of the §3 verdict)\n{'='*94}")
    print("How much of stated-arm retrieval is the literal trait symbol? trait rank when the trait word")
    print("is masked vs when the tracer word is masked (matched control). Higher rank = more disrupted.\n")
    for name in NAMES:
        b = DIRECT.get((name, d, "baseline"))
        tt = DIRECT.get((name, d, "trait_tok"))
        tr = DIRECT.get((name, d, "tracer_tok"))
        if b is None or tt is None or tr is None:
            print(f"{name:<7} {TRAITS[name]:<10}  (missing a condition)")
            continue
        f_trait = (tt / b) if b else float("inf")
        f_tracer = (tr / b) if b else float("inf")
        print(f"{name:<7} {TRAITS[name]:<10}  baseline={b:>7.1f}  trait-masked={tt:>7.1f} (x{f_trait:>5.2f})  "
              f"tracer-masked={tr:>7.1f} (x{f_tracer:>5.2f})")
    print("\nReading: a large trait-masked factor with a ~1 tracer-masked factor => stated-arm retrieval "
          "leans on the literal symbol. Both ~1 => it does not.")


# ---- run --------------------------------------------------------------------------------------
print("Phase 3 (Q3) analysis — held latent vs held scene, against frozen prediction.md §3 + §7b.")
print(f"n = {len(NAMES)} survivors: {NAMES}")
print(f"decision checkpoint d = {DEC_D} (Cue B); exploratory d = {EXPL_D} (distance-robustness, no verdict).")

dec_tally = report_block(DEC_D, is_decision=True)
report_block(EXPL_D, is_decision=False)
direct_block(DEC_D)

print(f"\n{'='*94}\nSUMMARY (frozen §3 verdict at d={DEC_D}, per §7b gate)\n{'='*94}")
print("  " + ", ".join(f"{k}={v}" for k, v in sorted(dec_tally.items())))
print("  Every gate-fail character is NOT-RUN, not a null (prediction.md §7b). Held-scene and held-latent")
print("  are both publishable outcomes; the write-up reports the per-character table, not just the tally.")

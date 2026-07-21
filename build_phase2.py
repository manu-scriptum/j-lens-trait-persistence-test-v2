"""Generate trait_persistence_v2_phase2.ipynb (the cued-retrieval sweep: Q1 + Q2 + Q5).

Phase 2 runs the main experiment specified in `prediction.md` after Phase 1 fixed the band and the
roster. It reads the calibrated band from `calibration.json` and the surviving roster from
`screening_roster.json` — never from a literal — so a re-run cannot silently diverge from what
Phase 1 actually decided.

Scope, per `prediction.md` §1a and the §9 amendments: **Q1 + Q2 + Q5 only.** Q3 (KV-ablation) and
Q4 (interference) are deferred and not built here.

Mirrors `build_phase1.py`'s structure and reuses its lens machinery verbatim where possible (the
logit-lens resolve + the two-part validation, `_best_rank_per_layer`, `single_token_id`) so the
instrument is identical across phases.
"""
import json, pathlib

md = lambda s: {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)}
code = lambda s: {"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": s.strip("\n").splitlines(keepends=True)}

cells = []

cells.append(md(r"""
# Trait persistence v2 — Phase 2: the cued-retrieval sweep (Q1 + Q2 + Q5)

**Pre-registered.** `prediction.md` and `trait_persistence_v2_stimuli.py` were committed to git
*before* any Phase 2 code existed. Nothing here may change a criterion in that document; if something
shows a criterion was miscalibrated, it goes in `prediction.md` §9 as a dated amendment with the data
shown, never as a silent edit.

This is the main event. Phase 1 did two things this notebook now depends on and **reads from files**:

1. the **band** (`calibration.json` → layers 13–26 on the run of record) — Phase 2 reads it, never a
   literal, so the depths analysed are exactly the depths Phase 1 justified;
2. the **roster** (`screening_roster.json` → the 7 survivors) — likewise read, not retyped.

**Scope of this run, stated plainly** (`prediction.md` §1a, §9 amendments):

- **Q1 (primary).** Under cued retrieval, does a *stated* trait stay more retrievable than an
  *inferred* one across intervening text? Measured as the J-lens best-lexicon rank, median over the
  band, per (arm, distance, cue), always against the **control arm at the same distance and cue**.
- **Q2 (primary).** Is the direct arm's persistence trait-specific or generic token-echo? A neutral
  **tracer** word embedded in each direct trigger is tracked with the identical machinery, against its
  own control-arm floor.
- **Q5 (secondary, free).** The `{direct, inferred} × {logit, J-lens}` discriminant. The logit lens
  rides along on every read; it **gates no Q1/Q2 conclusion**.

**Deferred, not built here:** Q3 (KV-ablation) and Q4 (interference). See `prediction.md` §1a.

**Run n = 7**, not 8 — three candidates failed Phase 1 screening with no back-fill
(`prediction.md` §9, 2026-07-21 later). The decision rules read n = 7 throughout.

**Before running:** `Runtime → Change runtime type → T4 GPU`. Gemma-3-4B-IT is gated: accept the
license at https://huggingface.co/google/gemma-3-4b-it and store an HF token as a Colab secret named
`HF_token` (key icon, left sidebar; enable notebook access). Upload `trait_persistence_v2_stimuli.py`
**and the Phase 1 `phase1/` folder** (or at least `calibration.json` and `screening_roster.json`).
""".strip()))

cells.append(code(r"""
# jlens pinned to the SAME commit as v1 and Phase 1, so the instrument is byte-identical across
# the whole series and any difference is the design, never the tool.
JLENS_COMMIT = "581d398613e5602a5af361e1c34d3a92ea82ba8e"
!pip install -q "git+https://github.com/anthropics/jacobian-lens.git@{JLENS_COMMIT}"
!pip install -q huggingface_hub datasets scipy
""".strip()))

cells.append(code(r"""
from huggingface_hub import login
from google.colab import userdata

login(token=userdata.get("HF_token"))
""".strip()))

cells.append(md(r"""
## Get the pre-registered stimuli and the Phase 1 outputs

`trait_persistence_v2_stimuli.py` is the canonical committed copy — fetch it, never paste it. Phase 2
also needs two Phase 1 result files, and reads the band and roster **out of them** rather than from
any number typed into this notebook:

- `calibration.json` — the band Phase 2 analyses;
- `screening_roster.json` — the survivors Phase 2 runs.

Both cells fail loudly if a file is absent; neither falls back to an inline copy. A file looked for in
two places: `phase1/<file>` (repo layout) or `<file>` (uploaded flat into the Colab session).
""".strip()))

cells.append(code(r"""
import os, sys, json

if not os.path.exists("trait_persistence_v2_stimuli.py"):
    raise FileNotFoundError(
        "trait_persistence_v2_stimuli.py not found. Upload it (folder icon, left sidebar) or clone "
        "the repo. Deliberately no inline fallback: an inline copy could silently diverge from the "
        "committed pre-registration."
    )
import trait_persistence_v2_stimuli as S


def _find(fname):
    for p in (os.path.join("phase1", fname), fname):
        if os.path.exists(p):
            return p
    raise FileNotFoundError(
        f"{fname} not found in phase1/ or the working dir. Upload the Phase 1 outputs. "
        "Phase 2 reads the band and roster from these files and will not invent them."
    )


with open(_find("calibration.json")) as f:
    CALIB = json.load(f)
with open(_find("screening_roster.json")) as f:
    ROSTER = json.load(f)

BAND_LAYERS = [int(l) for l in CALIB["band_layers"]]
SURVIVORS   = list(ROSTER["survivors"])

print(f"band read from calibration.json: layers {BAND_LAYERS[0]}..{BAND_LAYERS[-1]} "
      f"({len(BAND_LAYERS)} layers, depth {CALIB['band_depth_frac'][0]:.2f}"
      f"-{CALIB['band_depth_frac'][1]:.2f})")
print(f"roster read from screening_roster.json: {len(SURVIVORS)} survivors "
      f"({ROSTER['n_positive']}+ / {ROSTER['n_negative']}-): {SURVIVORS}")
print(f"distances: {S.DISTANCES}   arms: {S.ARMS}")
if len(SURVIVORS) < 5:
    raise RuntimeError("roster has <5 survivors — Phase 1 should have halted (§3 failure rule).")
if min(ROSTER["n_positive"], ROSTER["n_negative"]) < 3:
    print("NOTE: valence balance is broken (see prediction.md §5 / §9 2026-07-21 later). "
          "Reported as a caveat; not corrected.")
""".strip()))

cells.append(md(r"""
## Load model and lens

Same checkpoint, same lens file, same pin as v1 and Phase 1. Environment printed into the output so
the run is reproducible from the notebook alone.
""".strip()))

cells.append(code(r"""
import torch
import transformers
import jlens
import numpy as np
import pandas as pd

jlens.configure_logging()

print("python      ", sys.version.split()[0])
print("torch       ", torch.__version__)
print("transformers", transformers.__version__)
print("jlens       ", getattr(jlens, "__version__", "n/a"), "@", JLENS_COMMIT[:12])
print("cuda        ", torch.version.cuda, "| device:",
      torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")

MODEL_NAME = "google/gemma-3-4b-it"
LENS_REPO  = "neuronpedia/jacobian-lens"
LENS_FILE  = "gemma-3-4b-it/jlens/Salesforce-wikitext/gemma-3-4b-it_jacobian_lens.pt"

hf_model  = transformers.AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, dtype=torch.bfloat16
).cuda()
tokenizer = transformers.AutoTokenizer.from_pretrained(MODEL_NAME)
model     = jlens.from_hf(hf_model, tokenizer)
lens      = jlens.JacobianLens.from_pretrained(LENS_REPO, filename=LENS_FILE)

N_LAYERS   = model.n_layers
ALL_LAYERS = list(range(N_LAYERS - 1))   # lens has no fitted Jacobian for the final layer
print(f"\nn_layers={N_LAYERS}; lens-readable layers: {ALL_LAYERS[0]}..{ALL_LAYERS[-1]}")

# The band was calibrated on THIS model; guard against a mismatched calibration.json.
assert CALIB["n_layers"] == N_LAYERS, (
    f"calibration.json was written for n_layers={CALIB['n_layers']} but this model has {N_LAYERS}. "
    "Wrong calibration file — do not proceed."
)
assert BAND_LAYERS[0] >= ALL_LAYERS[0] and BAND_LAYERS[-1] <= ALL_LAYERS[-1], (
    "calibrated band falls outside the lens-readable layers."
)
print("band <-> model consistency check passed.")
""".strip()))

cells.append(md(r"""
### Logit-lens robustness stream (identical wiring to Phase 1)

Registered in `prediction.md` §4a: a plain unembedding readout computed alongside every J-lens read.
Secondary, **gates no conclusion** — it answers whether the J-lens is load-bearing (Q5). The final
norm and LM head are resolved defensively and printed; a silently wrong `norm` produces
plausible-looking nonsense, which is worse than a crash, so resolution failure raises.
""".strip()))

cells.append(code(r"""
def _resolve(obj, paths):
    for p in paths:
        cur = obj
        try:
            for part in p.split("."):
                cur = getattr(cur, part)
            return cur, p
        except AttributeError:
            continue
    return None, None

FINAL_NORM, _np = _resolve(hf_model, ["model.norm", "model.language_model.norm",
                                      "language_model.model.norm", "model.model.norm"])
LM_HEAD, _hp = _resolve(hf_model, ["lm_head", "language_model.lm_head"])
if FINAL_NORM is None or LM_HEAD is None:
    raise RuntimeError(
        "Could not locate the final norm / lm_head on this checkpoint. Print `hf_model` to "
        "inspect the module tree and set FINAL_NORM / LM_HEAD by hand. Do NOT guess: a wrong "
        "norm yields plausible-looking garbage rather than an error."
    )
print(f"logit lens: norm <- hf_model.{_np}   head <- hf_model.{_hp}")


@torch.no_grad()
def logit_lens_logits(text, layers, positions):
    '''Plain-unembedding readout: {layer: [len(positions), vocab]}.'''
    enc = tokenizer(text, return_tensors="pt").to(hf_model.device)
    hs = hf_model(**enc, output_hidden_states=True).hidden_states
    # hidden_states[0] is the embedding output, so layer L is hidden_states[L + 1].
    return {L: LM_HEAD(FINAL_NORM(hs[L + 1][0, positions, :])).float() for L in layers}

# Any final-logit softcapping is a monotone transform and cannot change ranks, the only statistic taken.
""".strip()))

cells.append(md(r"""
### Validate the logit-lens wiring before trusting it

Same two checks as Phase 1 (both from the corrected `j-lens-self-recruitment-test` version). Q5 rests
entirely on this channel, so it is re-validated here rather than assumed to have survived from Phase 1.

1. **`LM_HEAD` on the final hidden state reproduces the model's own next-token top-k** — no
   `FINAL_NORM` (HF's `hs[-1]` is already normed; double-norm is the classic silent failure).
2. **Known-answer trajectory** — ` Paris` climbs in the late layers with `FINAL_NORM` on the raw
   intermediates, the path the readout actually uses.

Check (1) **raises** on failure: a bad logit channel voids every Q5 claim.
""".strip()))

cells.append(code(r"""
_ptxt = "The Eiffel Tower stands in the French capital city of"
_enc = tokenizer(_ptxt, return_tensors="pt").to(hf_model.device)
with torch.no_grad():
    _out = hf_model(**_enc, output_hidden_states=True)

def _decode_ids(ids):
    return [tokenizer.decode([i]) for i in ids]

# Check (1): final hidden state -> model's own next-token ranking. NO FINAL_NORM (hs[-1] already normed).
_real_logits = _out.logits[0, -1].float()
_lens_logits = LM_HEAD(_out.hidden_states[-1][0, -1].unsqueeze(0))[0].float()
_real = _decode_ids(_real_logits.topk(8).indices.tolist())
_llf  = _decode_ids(_lens_logits.topk(8).indices.tolist())
_maxdiff = (_lens_logits - _real_logits).abs().max().item()
print("real model next-token top8 :", _real)
print("logit-lens(final)     top8 :", _llf)
print("TOP-8 SETS MATCH           :", set(_real) == set(_llf), "  <-- must be True")
print("TOP-8 EXACT ORDER MATCH    :", _real == _llf)
print(f"max|lens - real| logits    : {_maxdiff:.4g}   <-- expect ~1 bf16 ULP (<=0.25), not exactly 0")
assert set(_real) == set(_llf), (
    "logit-lens FAILED check (1): LM_HEAD(hs[-1]) does not match the model's own next token. "
    "Do NOT trust the logit channel or any Q5 claim -- fix FINAL_NORM / LM_HEAD / indexing first."
)

# Check (2): known-answer trajectory over the readout's real path, LM_HEAD(FINAL_NORM(raw residual)).
print("\nlogit-lens trajectory (' Paris' should climb in the late layers):")
for _L in list(ALL_LAYERS[::4]) + [ALL_LAYERS[-1]]:
    _h = _out.hidden_states[_L + 1][0, -1].unsqueeze(0)   # raw residual -> FINAL_NORM IS needed here
    _t = _decode_ids(LM_HEAD(FINAL_NORM(_h))[0].float().topk(5).indices.tolist())
    print(f"  layer {_L:2d} (depth {_L/(N_LAYERS-1):.2f}): {_t}")
""".strip()))

cells.append(md(r"""
## Token ids: lexicons, secondary adjective, tracers

Recomputed here from `trait_persistence_v2_stimuli.py` with the **same** single-token check Phase 1
used (leading-space form), so Phase 2 is self-contained and cannot inherit a stale id table. Three
token groups per character, all read from the *same* forward pass so Q2 costs no extra passes:

- **`trait`** — the concept lexicon (primary measure): best rank across surviving single-token members.
- **`adj`** — the bare trait adjective alone (secondary measure, for v1 comparability). Empty if the
  adjective is not single-token; that character is then primary-measure only.
- **`tracer`** — the neutral D4 word (Q2). Meaningful in the `direct` and `control` arms; recorded in
  `inferred` too (free, and a useful floor).
""".strip()))

cells.append(code(r"""
def single_token_id(word):
    '''Token id for the leading-space form, or None if it is not single-token.'''
    ids = tokenizer.encode(" " + word, add_special_tokens=False)
    return ids[0] if len(ids) == 1 else None


# Lexicon ids per trait (drop + log multi-token entries, never substitute).
LEXICON_IDS = {}
for trait, words in S.TRAIT_LEXICONS.items():
    kept = {w: single_token_id(w) for w in words}
    kept = {w: t for w, t in kept.items() if t is not None}
    LEXICON_IDS[trait] = kept

# Deterministic run order: positives first ('+' < '-'), then alphabetical.
SURVIVOR_CHARS = sorted((S.by_name(n) for n in SURVIVORS),
                        key=lambda c: (c["valence"], c["name"]))

CHAR_GROUPS = {}
for c in SURVIVOR_CHARS:
    trait_ids = list(LEXICON_IDS[c["trait"]].values())
    adj_id    = single_token_id(c["trait"])
    tracer_id = single_token_id(c["tracer"])
    CHAR_GROUPS[c["name"]] = {
        "trait":  trait_ids,
        "adj":    [adj_id] if adj_id is not None else [],
        "tracer": [tracer_id] if tracer_id is not None else [],
    }
    under = "  <-- UNDERPOWERED (<4), secondary measure only" if len(trait_ids) < 4 else ""
    print(f"{c['name']:<7} {c['trait']:<10} lexicon={len(trait_ids):>2}{under}   "
          f"adj={'ok' if adj_id is not None else 'NOT single-token'}   "
          f"tracer={c['tracer']} ({'ok' if tracer_id is not None else 'NOT single-token!'})")
""".strip()))

cells.append(md(r"""
## Read machinery

One forward pass per lens per checkpoint; every token group scored off the same logits. Ranks are
best (lowest) across the lexicon **and** across the read positions, per layer, then the **median over
the band** — exactly `prediction.md` §3's primary measure.

**Read positions per cue** (`prediction.md` §7):
- **Cue B** (`"…NAME is"`) and the **passive** period-read: the final position, where a trait
  adjective is contextually possible. Passive carries **no persistence claim** — v1 comparability only.
- **Cue A** (`"Tom glances at NAME."`): the tokens *following* the name (the trailing punctuation),
  i.e. the reactivation positions. The name's absolute index differs across arms because the trigger
  sentences differ in length; that is correct — the cue text read is identical, only shifted, and
  every contrast is arm-vs-control at the *same* cue, so the shift cancels.

The **reintroduction** checkpoint (D3) is Cue A at the maximum distance; flagged `is_reintro`, with a
short greedy continuation captured for the qualitative v1 comparison.
""".strip()))

cells.append(code(r"""
def _best_rank_per_layer(logits_by_layer, token_ids, layers):
    '''Lowest rank across the lexicon AND across read positions, at each layer.'''
    per_layer = {}
    for layer in layers:
        lg = logits_by_layer[layer]              # [P, vocab]
        best = None
        for pi in range(lg.shape[0]):
            row = lg[pi]
            for tid in token_ids:
                r = int((row > row[tid]).sum().item()) + 1
                best = r if best is None else min(best, r)
        per_layer[layer] = best
    return per_layer


def cue_read_positions(prefix, full_text, cue, name):
    '''Positions to read for a given cue. See markdown above for the rationale.'''
    n = tokenizer(full_text, return_tensors="pt")["input_ids"].shape[1]
    if cue in ("cue_b", "passive"):
        return [n - 1]
    # cue_a: tokens following the LAST occurrence of the name in the appended cue region.
    p = tokenizer(prefix, return_tensors="pt")["input_ids"].shape[1]
    name_ids = tokenizer.encode(" " + name, add_special_tokens=False)
    full_ids = tokenizer(full_text, return_tensors="pt")["input_ids"][0].tolist()
    L, after = len(name_ids), None
    for i in range(max(p - 1, 0), n - L + 1):
        if full_ids[i:i + L] == name_ids:
            after = i + L        # first position AFTER the name
    if after is None or after >= n:
        return [n - 1]           # fall back to final position if the name did not tokenize as expected
    return list(range(after, n))


def read_checkpoint(text, positions, groups):
    '''Both lenses, all token groups, one forward pass each. Returns (per_group, top20).'''
    jl_raw, _, _ = lens.apply(model, text, layers=BAND_LAYERS, positions=positions)
    jl = {L: jl_raw[L].float() for L in BAND_LAYERS}
    ll = logit_lens_logits(text, BAND_LAYERS, positions)

    per_group = {}
    for gname, ids in groups.items():
        if not ids:
            continue
        pj = _best_rank_per_layer(jl, ids, BAND_LAYERS)
        pl = _best_rank_per_layer(ll, ids, BAND_LAYERS)
        vj, vl = list(pj.values()), list(pl.values())
        per_group[gname] = {
            "j_median": float(np.median(vj)), "j_best": int(min(vj)),
            "l_median": float(np.median(vl)), "l_best": int(min(vl)),
            "per_layer_j": pj, "per_layer_l": pl,
        }
    # top-20 J-lens vocabulary at the last read position, every band layer (§8: stored so v1's E4
    # "did the median hide a sub-band signal?" check can be repeated, and for post-hoc correction).
    top20 = {L: [tokenizer.decode([t]) for t in jl[L][-1].topk(20).indices] for L in BAND_LAYERS}

    del jl_raw, jl, ll
    torch.cuda.empty_cache()
    return per_group, top20
""".strip()))

cells.append(md(r"""
# The sweep

For every survivor × arm ∈ {direct, inferred, control} × distance ∈ {0,1,2,4,7,10} × cue ∈
{cue_b, cue_a, passive}: one forward pass per lens, three token groups scored. Cue B carries the
primary Q1 contrast; the tracer group carries Q2; the logit lens rides along for Q5.

`d0` is recorded but carries **no persistence weight** for the direct arm (§3): at d0 the trait word
is surface echo. The analysis (Phase 3) enforces that; the sweep just stores everything.
""".strip()))

cells.append(code(r"""
CUES = ["cue_b", "cue_a", "passive"]
DMAX = max(S.DISTANCES)

reads_rows, perlayer_rows, top20_rows, reintro_rows = [], [], [], []
# For the §4a logit positive control, captured at the d0 / inferred / cue_b / trait checkpoint.
posctrl_capture = {}

for c in SURVIVOR_CHARS:
    groups = CHAR_GROUPS[c["name"]]
    for arm in S.ARMS:
        for d in S.DISTANCES:
            prefix = S.build_prefix(c, arm, d)
            for cue in CUES:
                text = S.build_probe(c, arm, d, cue)
                positions = cue_read_positions(prefix, text, cue, c["name"])
                per_group, top20 = read_checkpoint(text, positions, groups)
                is_reintro = (cue == "cue_a" and d == DMAX)

                for measure, r in per_group.items():
                    reads_rows.append({
                        "name": c["name"], "trait": c["trait"], "valence": c["valence"],
                        "arm": arm, "distance": d, "cue": cue, "measure": measure,
                        "is_reintro": is_reintro,
                        "j_median_rank_band": r["j_median"], "j_best_rank_band": r["j_best"],
                        "logit_median_rank_band": r["l_median"], "logit_best_rank_band": r["l_best"],
                        "n_group_tokens": len(groups[measure]),
                        "n_read_positions": len(positions), "text": text,
                    })
                    for L in BAND_LAYERS:
                        perlayer_rows.append({"name": c["name"], "arm": arm, "distance": d,
                                              "cue": cue, "measure": measure, "lens": "jlens",
                                              "layer": L, "rank": r["per_layer_j"][L]})
                        perlayer_rows.append({"name": c["name"], "arm": arm, "distance": d,
                                              "cue": cue, "measure": measure, "lens": "logit",
                                              "layer": L, "rank": r["per_layer_l"][L]})

                    if arm == "inferred" and d == 0 and cue == "cue_b" and measure == "trait":
                        posctrl_capture[c["name"]] = (r["j_median"], r["l_median"])

                for L, toks in top20.items():
                    for rk, tok in enumerate(toks, 1):
                        top20_rows.append({"name": c["name"], "arm": arm, "distance": d,
                                           "cue": cue, "layer": L, "rank": rk, "token": tok})

                # Reintroduction continuation (D3): short greedy decode, qualitative record only.
                if is_reintro:
                    try:
                        enc = tokenizer(text, return_tensors="pt").to(hf_model.device)
                        with torch.no_grad():
                            gen = hf_model.generate(**enc, max_new_tokens=12, do_sample=False)
                        cont = tokenizer.decode(gen[0][enc["input_ids"].shape[1]:],
                                                skip_special_tokens=True)
                    except Exception as e:
                        cont = f"(continuation failed: {e})"
                    reintro_rows.append({"name": c["name"], "arm": arm, "cue": cue,
                                         "continuation": cont, "text": text})
    print(f"  swept {c['name']:<7} ({c['trait']}, {c['valence']})")

reads_df = pd.DataFrame(reads_rows)
reads_df.to_csv("phase2_reads.csv", index=False)
pd.DataFrame(perlayer_rows).to_csv("phase2_per_layer.csv", index=False)
pd.DataFrame(top20_rows).to_csv("phase2_top20.csv", index=False)
pd.DataFrame(reintro_rows).to_csv("phase2_reintro.csv", index=False)
print(f"\nwrote phase2_reads.csv ({len(reads_df)} rows), phase2_per_layer.csv "
      f"({len(perlayer_rows)} rows), phase2_top20.csv, phase2_reintro.csv")
""".strip()))

cells.append(md(r"""
## Logit-lens positive control (§4a), per character

Captured from the d0 / inferred / Cue B / trait checkpoint: the logit lens **passes** for a character
if its best-lexicon median rank there is `≤ 5×` the J-lens value. Where it **fails**, a later "the
logit lens saw nothing" claim is **void** for that character (Q5). This gates *interpretation*, not
admission — everyone was still swept.

This recomputes the control from Phase 2's own reads; it should reproduce Phase 1's roster note
(only 3 of 7 passed there — Nadia, Elias, Greta). A mismatch would mean the two phases disagree on a
d0 read and must be investigated before trusting Q5.
""".strip()))

cells.append(code(r"""
LOGIT_POSCTRL_FACTOR = 5.0
posctrl_rows = []
for name, (j_med, l_med) in sorted(posctrl_capture.items()):
    passes = l_med <= LOGIT_POSCTRL_FACTOR * j_med
    posctrl_rows.append({"name": name, "j_median_d0_inferred": j_med,
                         "logit_median_d0_inferred": l_med,
                         "factor": (l_med / j_med) if j_med else float("inf"),
                         "logit_positive_control": bool(passes)})
    print(f"{name:<7} J={j_med:>8.1f}  logit={l_med:>9.1f}  "
          f"factor={l_med/j_med if j_med else float('inf'):>6.2f}  "
          f"posctrl={'PASS' if passes else 'fail (logit nulls void for this char)'}")

posctrl_df = pd.DataFrame(posctrl_rows)
posctrl_df.to_csv("phase2_logit_posctrl.csv", index=False)
_npass = int(posctrl_df["logit_positive_control"].sum())
print(f"\nlogit positive control passed for {_npass}/{len(posctrl_df)} survivors. "
      f"Wrote phase2_logit_posctrl.csv")
print("(Phase 1 recorded 3/7 — Nadia, Elias, Greta. Investigate any disagreement before trusting Q5.)")
""".strip()))

cells.append(md(r"""
## A first look — Q1 direction (descriptive only, not the decision)

`prediction.md` §3's Q1 rule is a per-character paired ratio `R(arm,d,CueB)/R(control,d,CueB)` at
d ∈ {1,2,4,7,10}, with a Wilcoxon signed-rank test (now over **n = 7**, registered as weak). That
formal test belongs in the Phase 3 analysis. This cell only previews the **direction** — the median
direct-vs-inferred ratio-to-control across characters, per distance — so a gross wiring problem shows
up before the data leaves the GPU. **No conclusion is drawn here.**
""".strip()))

cells.append(code(r"""
# Primary contrast: trait measure, Cue B, ratio of each arm's band-median rank to its control.
cb = reads_df[(reads_df["cue"] == "cue_b") & (reads_df["measure"] == "trait")]
piv = cb.pivot_table(index=["name", "distance"], columns="arm", values="j_median_rank_band")
piv = piv.reset_index()
piv["direct_ratio"]   = piv["direct"]   / piv["control"]
piv["inferred_ratio"] = piv["inferred"] / piv["control"]

print("Median ratio-to-control across survivors, by distance (lower = more retrievable):")
print("(d0 shown for completeness but carries NO persistence weight for the direct arm — §3)\n")
summary = (piv.groupby("distance")[["direct_ratio", "inferred_ratio"]]
              .median().round(3))
print(summary.to_string())
print("\nReminder: descriptive preview only. The registered Q1 decision (paired Wilcoxon, n=7) and "
      "the Q2 / Q5 analyses run in Phase 3, against the frozen criteria in prediction.md §3.")
""".strip()))

cells.append(md(r"""
## Done — Phase 2

Files to download and send back, all of them:

| file | what it is |
|---|---|
| `phase2_reads.csv` | the sweep: every (name, arm, distance, cue, measure) band-median rank, both lenses |
| `phase2_per_layer.csv` | per-layer ranks (§8: repeats v1's E4 sub-band check; both lenses) |
| `phase2_top20.csv` | top-20 J-lens vocabulary at every checkpoint (enables post-hoc correction) |
| `phase2_reintro.csv` | D3 reintroduction continuations (qualitative, v1 comparison) |
| `phase2_logit_posctrl.csv` | per-character logit positive control for Q5 |

**What Phase 3 (analysis, off-GPU) does with these — against the frozen §3 criteria:**
- **Q1:** per-character paired `R(arm,d,CueB)/R(control,d,CueB)`, Wilcoxon signed-rank over n = 7
  (registered weak), majority-of-characters-at-majority-of-distances direction as the descriptive
  fallback if it does not clear. d0 excluded from direct-arm persistence.
- **Q2:** tracer median ratio vs the stated trait's — copy bias if within 0.15; trait-specific if the
  tracer sits at floor (≥ 0.95) while the trait clears 0.8. Ambiguous otherwise, and Q1 then rests on
  the cued reads alone.
- **Q5:** the `{direct, inferred} × {logit, J-lens}` cell, **only** where the logit positive control
  passed; reported as instrument sensitivity, never as a representation claim.
- **§7a conditional extension** past d=10 is evaluated here too, with its Q2 override.

**Honest caveats to carry into the write-up now:**
- n = 7, not 8; single-item medians are draggable by one character (§8). Valence is 4:3.
- Passive-read numbers appear in the file but carry **no persistence claim** (§7) — labelled
  "spontaneous saliency" wherever used.
- No held-latent-vs-held-scene claim may be drawn from this run (Q3 deferred, §1a). The distance half
  of the fragility read is here; the interference half (Q4) is not.
""".strip()))

nb = {
    "cells": cells,
    "metadata": {
        "accelerator": "GPU",
        "colab": {"provenance": [], "gpuType": "T4"},
        "kernelspec": {"display_name": "Python 3", "name": "python3"},
        "language_info": {"name": "python"},
    },
    "nbformat": 4,
    "nbformat_minor": 0,
}

out = pathlib.Path(__file__).resolve().parent / "trait_persistence_v2_phase2.ipynb"
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"wrote {out} — {len(cells)} cells")

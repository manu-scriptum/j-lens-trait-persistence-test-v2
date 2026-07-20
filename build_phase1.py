"""Generate trait_persistence_v2_phase1.ipynb (calibration + screening)."""
import json, pathlib

md = lambda s: {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)}
code = lambda s: {"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": s.strip("\n").splitlines(keepends=True)}

cells = []

cells.append(md(r"""
# Trait persistence v2 — Phase 1: band calibration + stimulus screening

**Pre-registered.** `prediction.md` and `trait_persistence_v2_stimuli.py` were committed to git *before* this
notebook existed. Nothing in this notebook may change a criterion in that document; if something
here shows a criterion was miscalibrated, it goes in `prediction.md` §9 as a dated amendment with
the data shown, never as a silent edit.

This is Phase 1 of the v2 rerun specified in `trait_persistence_v2_spec.md`. It does **two** things,
both of which the spec requires to happen *before* the main sweep:

1. **Band calibration (spec §3).** v1 inherited a 35–90% depth band from an earlier project without
   ever checking it on this model. Here we locate the workspace band empirically over ~20 neutral
   documents — kurtosis onset, layer-to-layer autocorrelation, and the late-layer collapse into
   next-token prediction — and write the result to `calibration.json` for Phase 2 to read.
2. **Stimulus screening (spec §D0).** d0-only reads on all ten candidate characters, applying the
   frozen gate from `prediction.md` §3: `R(inferred,0) ≤ 200` **and** `R(control,0)/R(inferred,0) ≥ 5`.
   This is what v1's Peter needed and did not get — he produced no inference at all, and nobody knew
   until the full sweep was already done.

**Neither step touches a cued retrieval checkpoint, and neither can influence a Q1–Q3 criterion**
(those are already frozen in git). Screening reads are exploratory by definition — the spec says so —
and they are recorded in full.

**Before running:** `Runtime → Change runtime type → T4 GPU`. Gemma-3-4B-IT is gated: accept the
license at https://huggingface.co/google/gemma-3-4b-it and store an HF token as a Colab secret named
`HF_token` (key icon, left sidebar; enable notebook access).

**Two things to actually check in the output rather than scroll past:**
- the **single-token report** — how many lexicon entries survived per trait. A trait down to <4
  entries is underpowered on the primary measure and must be flagged, not quietly used;
- the **screening table** — which characters passed, and whether the 4:4 valence balance survived.
""".strip()))

cells.append(code(r"""
# jlens pinned to a fixed commit, not `main` (which moves). Same pin as v1, so the
# instrument is identical across v1 and v2 and any difference is the design, not the tool.
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
## Get the pre-registered stimuli

`trait_persistence_v2_stimuli.py` is the canonical, committed copy. Fetch it rather than pasting its contents here —
a pasted copy is a copy that can drift from the pre-registration, and drift between the registered
stimuli and the run stimuli is exactly the kind of thing that is invisible until it is fatal.

If you are running this in Colab, upload `trait_persistence_v2_stimuli.py` (folder icon in the left sidebar) or clone
the repo. The cell below fails loudly if the file is absent — it does not fall back to an inline copy.
""".strip()))

cells.append(code(r"""
import os, sys

if not os.path.exists("trait_persistence_v2_stimuli.py"):
    raise FileNotFoundError(
        "trait_persistence_v2_stimuli.py not found. Upload it (folder icon, left sidebar) or clone the repo. "
        "Deliberately no inline fallback: an inline copy could silently diverge from the "
        "committed pre-registration."
    )

import trait_persistence_v2_stimuli as S
print(f"{len(S.CANDIDATES)} candidates, "
      f"{sum(1 for c in S.CANDIDATES if c['valence']=='+')}+ / "
      f"{sum(1 for c in S.CANDIDATES if c['valence']=='-')}-")
print("distances:", S.DISTANCES)
""".strip()))

cells.append(md(r"""
## Load model and lens

Same checkpoint and same lens file as v1. The environment is printed into the output cell so the
run is reproducible from the notebook alone.
""".strip()))

cells.append(code(r"""
import json
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

# The lens has no fitted Jacobian for the final layer (found in the earlier
# negation-framing project on this same model/lens pairing).
N_LAYERS  = model.n_layers
ALL_LAYERS = list(range(N_LAYERS - 1))
print(f"\nn_layers={N_LAYERS}; lens-readable layers: {ALL_LAYERS[0]}..{ALL_LAYERS[-1]}")
""".strip()))

cells.append(md(r"""
### Logit-lens robustness stream

Registered in `prediction.md` §4a: a plain unembedding readout (hidden state → final norm → LM head)
computed alongside every J-lens read. It is **secondary and gates no conclusion** — it exists to
answer the skeptic's question of whether the J-lens is load-bearing.

Gemma-3's module layout differs between the text-only and multimodal wrappers, so the final norm and
LM head are resolved defensively and **printed**. A silently wrong `norm` does not crash; it produces
plausible-looking nonsense, which is worse. If resolution fails, the cell raises rather than guessing.
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

# Any final-logit softcapping is a monotone transform and therefore cannot change ranks,
# which is the only statistic taken here.
""".strip()))

cells.append(md(r"""
# Part 1 — Band calibration

**The question this answers:** at which depths does this model's residual stream carry
readable, concept-level content, as opposed to (early) undifferentiated token identity or (late)
committed next-token prediction?

v1 assumed 35–90%. That assumption is now tested. Three independent signals, all computed over ~20
neutral documents with **no stimulus content whatsoever** — this step cannot leak trait information
into anything downstream, which is why it is safe to run before the pre-registration's ink is dry:

- **Excess kurtosis** of the lens logit distribution per layer. Low kurtosis = diffuse, uncommitted
  readout; the rise marks where specific vocabulary starts to stand out.
- **Adjacent-layer cosine similarity** between readouts. Successive layers agreeing means the
  representation has stabilised into something being carried rather than rewritten.
- **Next-token agreement** — fraction of positions where the lens top-1 equals the model's actual
  argmax next token. This rises sharply at the end, where the readout stops being *about the content*
  and becomes *the output distribution*. That rise marks the top of the usable band.

The first 5 tokens of every document are skipped throughout (high-norm token artifact).
""".strip()))

cells.append(code(r"""
# Neutral calibration documents: wikitext (the corpus the lens was fitted on), so we are
# characterising the lens in its own domain rather than on out-of-distribution prose.
N_CALIB_DOCS   = 20
N_POS_PER_DOC  = 16     # evenly spaced positions per doc; keeps the logit tensor T4-sized
SKIP_FIRST     = 5      # high-norm token artifact
MIN_DOC_TOKENS = 64

try:
    from datasets import load_dataset
    _ds = load_dataset("Salesforce/wikitext", "wikitext-103-raw-v1", split="test")
    calib_docs = []
    for row in _ds:
        t = row["text"].strip()
        # skip headings ("= Title =") and short fragments
        if len(t) > 400 and not t.startswith("="):
            calib_docs.append(t[:1200])
        if len(calib_docs) >= N_CALIB_DOCS:
            break
    CALIB_SOURCE = "Salesforce/wikitext wikitext-103-raw-v1 [test]"
except Exception as e:
    print(f"wikitext load failed ({e}); falling back to the notebook's own filler prose.")
    calib_docs = [" ".join(S.FILLER_SENTENCES)] * N_CALIB_DOCS
    CALIB_SOURCE = "fallback: repeated neutral filler (WEAKER — note this in the results doc)"

print(f"{len(calib_docs)} calibration docs from {CALIB_SOURCE}")
print("first doc, truncated:", calib_docs[0][:220].replace("\n", " "), "...")
""".strip()))

cells.append(code(r"""
from scipy.stats import kurtosis as _kurtosis

def calibrate_doc(text):
    '''Per-layer (kurtosis, cos-to-next-layer, next-token agreement) for one document.'''
    enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    ids = enc["input_ids"].cuda()
    n_tok = ids.shape[1]
    if n_tok < MIN_DOC_TOKENS:
        return None

    # positions: evenly spaced, after the high-norm prefix, excluding the final token
    positions = np.linspace(SKIP_FIRST, n_tok - 2, N_POS_PER_DOC).astype(int).tolist()
    positions = sorted(set(positions))

    # what the model itself predicts next at those positions (for the collapse metric)
    with torch.no_grad():
        true_next = hf_model(ids).logits[0].argmax(-1)[positions]   # [P]

    lens_logits, _, _ = lens.apply(model, text, layers=ALL_LAYERS, positions=positions)

    kurt, cos, agree = {}, {}, {}
    prev = None
    for layer in ALL_LAYERS:
        lg = lens_logits[layer].float()                              # [P, vocab]
        kurt[layer]  = float(_kurtosis(lg.cpu().numpy(), axis=-1).mean())
        agree[layer] = float((lg.argmax(-1) == true_next).float().mean().item())
        if prev is not None:
            cos[layer - 1] = float(
                torch.nn.functional.cosine_similarity(prev, lg, dim=-1).mean().item()
            )
        prev = lg

    del lens_logits, prev
    torch.cuda.empty_cache()
    return kurt, cos, agree


calib_rows = []
for i, doc in enumerate(calib_docs):
    out = calibrate_doc(doc)
    if out is None:
        print(f"  doc {i}: too short, skipped")
        continue
    kurt, cos, agree = out
    for layer in ALL_LAYERS:
        calib_rows.append({
            "doc": i, "layer": layer, "depth_frac": layer / (N_LAYERS - 1),
            "kurtosis": kurt[layer],
            "cos_to_next": cos.get(layer, np.nan),
            "next_token_agreement": agree[layer],
        })
    print(f"  doc {i}: ok")

calib_df = pd.DataFrame(calib_rows)
calib_df.to_csv("calibration_raw.csv", index=False)
calib_by_layer = calib_df.groupby(["layer", "depth_frac"], as_index=False).mean(numeric_only=True)
calib_by_layer.to_csv("calibration_by_layer.csv", index=False)
print(f"\nWrote calibration_raw.csv ({len(calib_df)} rows) and calibration_by_layer.csv")
calib_by_layer.drop(columns=["doc"]).round(4).to_string(index=False)
""".strip()))

cells.append(code(r"""
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, (col, title) in zip(axes, [
    ("kurtosis",             "Excess kurtosis of lens logits\n(rise = readout sharpening)"),
    ("cos_to_next",          "Cosine to next layer's readout\n(rise = representation stabilising)"),
    ("next_token_agreement", "Lens top-1 == model's next token\n(rise = collapse into output)"),
]):
    ax.plot(calib_by_layer["depth_frac"], calib_by_layer[col], marker="o", ms=3)
    ax.set_title(title, fontsize=9)
    ax.set_xlabel("depth fraction")
    ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig("calibration_curves.png", dpi=150, bbox_inches="tight")
plt.show()
""".strip()))

cells.append(code(r"""
# Propose a band from the three curves. These are heuristics on smooth curves, not a
# principled estimator -- the plots above are the real evidence and a human confirms the
# band before Phase 2 uses it.
k    = calib_by_layer["kurtosis"].values
agr  = calib_by_layer["next_token_agreement"].values
lays = calib_by_layer["layer"].values

# Lower edge: first layer where kurtosis reaches 25% of its range (readout has sharpened).
k_thresh   = k.min() + 0.25 * (k.max() - k.min())
lower_idx  = int(np.argmax(k >= k_thresh))

# Upper edge: last layer BEFORE next-token agreement reaches 50% of its range (pre-collapse).
a_thresh    = agr.min() + 0.50 * (agr.max() - agr.min())
collapse_ix = int(np.argmax(agr >= a_thresh))
upper_idx   = max(lower_idx, collapse_ix - 1)

BAND_LAYERS = [int(l) for l in lays[lower_idx:upper_idx + 1]]
band_frac   = (float(BAND_LAYERS[0] / (N_LAYERS - 1)), float(BAND_LAYERS[-1] / (N_LAYERS - 1)))

print(f"kurtosis onset      layer {lays[lower_idx]}  (depth {band_frac[0]:.2f})")
print(f"collapse onset      layer {lays[collapse_ix]}  (depth {lays[collapse_ix]/(N_LAYERS-1):.2f})")
print(f"\nPROPOSED BAND: layers {BAND_LAYERS[0]}..{BAND_LAYERS[-1]} "
      f"({len(BAND_LAYERS)} layers, depth {band_frac[0]:.2f}-{band_frac[1]:.2f})")
print(f"v1 used 0.35-0.90 by inheritance. Overlap is a finding worth stating; so is a mismatch.")

calibration = {
    "band_layers": BAND_LAYERS,
    "band_depth_frac": band_frac,
    "n_layers": int(N_LAYERS),
    "v1_band_depth_frac": [0.35, 0.90],
    "calib_source": CALIB_SOURCE,
    "n_calib_docs": len(calib_docs),
    "skip_first_tokens": SKIP_FIRST,
    "jlens_commit": JLENS_COMMIT,
    "model": MODEL_NAME,
    "lens_file": LENS_FILE,
}
with open("calibration.json", "w") as f:
    json.dump(calibration, f, indent=2)
print("\nWrote calibration.json — Phase 2 reads the band from this file, never from a literal.")
""".strip()))

cells.append(md(r"""
> **Stop and look at the plots before continuing.** If the proposed band looks wrong against the
> curves — e.g. the kurtosis rise is not monotone, or agreement never really takes off — override
> `BAND_LAYERS` by hand in the cell above, re-run it, and record the override and its reason in the
> results doc. An automatic heuristic on a curve nobody looked at is exactly the kind of unchecked
> inheritance that put v1's band in question in the first place.

# Part 2 — Tokenizer verification

Every lexicon entry and every tracer, checked single-token in its **leading-space** form (the form
that actually occurs in running text — v1's own §6 pitfall list flags this). Failures are dropped
and logged. Nothing is silently substituted.

A trait whose surviving lexicon falls below **4** entries is underpowered on the primary measure
(`prediction.md` §6) and is flagged here, loudly, rather than discovered later.
""".strip()))

cells.append(code(r"""
def single_token_id(word):
    '''Token id for the leading-space form, or None if it is not single-token.'''
    ids = tokenizer.encode(" " + word, add_special_tokens=False)
    return ids[0] if len(ids) == 1 else None


LEXICON_IDS, lex_rows = {}, []
for trait, words in S.TRAIT_LEXICONS.items():
    kept = {}
    for w in words:
        tid = single_token_id(w)
        lex_rows.append({"trait": trait, "word": w, "single_token": tid is not None,
                         "token_id": tid if tid is not None else -1})
        if tid is not None:
            kept[w] = tid
    LEXICON_IDS[trait] = kept
    flag = "  <-- UNDERPOWERED (<4)" if len(kept) < 4 else ""
    print(f"{trait:<10} {len(kept):>2}/{len(words)} survive: {sorted(kept)}{flag}")

TRACER_IDS = {}
print()
for c in S.CANDIDATES:
    tid = single_token_id(c["tracer"])
    TRACER_IDS[c["name"]] = tid
    lex_rows.append({"trait": f"__tracer_{c['name']}", "word": c["tracer"],
                     "single_token": tid is not None, "token_id": tid if tid is not None else -1})
    if tid is None:
        print(f"!! tracer {c['tracer']!r} ({c['name']}) is NOT single-token — "
              f"Q2 cannot be run for this character unless it is swapped and re-registered.")
    else:
        print(f"tracer ok: {c['name']:<7} {c['tracer']}")

pd.DataFrame(lex_rows).to_csv("tokenizer_check.csv", index=False)
print("\nWrote tokenizer_check.csv")

_bad = [t for t, k in LEXICON_IDS.items() if len(k) < 4]
if _bad:
    print(f"\nFLAG: underpowered lexicons: {_bad} — record in the results doc; "
          f"analyse these on the secondary (bare adjective) measure only.")
""".strip()))

cells.append(md(r"""
# Part 3 — Screening (spec §D0)

d0-only reads on all ten candidates: the `inferred` and `control` arms at distance 0, no filler,
under **Cue B** (the trait query) — the cue that carries the primary Q1 contrast, so screening
measures the same thing the experiment will.

The gate, frozen in `prediction.md` §3 and **not** tunable here:

- `R(inferred, 0) ≤ 200`, and
- `R(control, 0) / R(inferred, 0) ≥ 5`

where `R` is the best rank across the trait's surviving lexicon, median over the calibrated band.

The `direct` arm is read too, for the record, but it does not gate anything — at d0 the direct arm
is surface echo of a word three tokens back, which is not evidence of anything.

The **logit-lens positive control** (§4a) is established here and nowhere else: the logit lens must
detect the d0 inferred-trigger signal (best rank ≤ 5× the J-lens value at the same checkpoint) for
that character. Characters failing it can still enter the sweep — the control gates *interpretation
of logit-lens nulls*, not admission — but a later "the logit lens saw nothing" claim is void for any
character that failed here.

**If fewer than 5 candidates pass, the gate cell raises and the run halts** (§3 failure rule).
""".strip()))

cells.append(code(r"""
def _best_rank_per_layer(logits_by_layer, token_ids, layers):
    '''Lowest rank across the lexicon, and across read positions, at each layer.'''
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


def read_both_lenses(text, token_ids, read_positions=None):
    '''Both streams at once. J-lens is primary; logit lens gates no conclusion (§4a).'''
    enc = tokenizer(text, return_tensors="pt")
    n_tok = enc["input_ids"].shape[1]
    positions = read_positions if read_positions is not None else [n_tok - 1]

    jl_raw, _, _ = lens.apply(model, text, layers=BAND_LAYERS, positions=positions)
    jl = {L: jl_raw[L].float() for L in BAND_LAYERS}
    ll = logit_lens_logits(text, BAND_LAYERS, positions)

    pj = _best_rank_per_layer(jl, token_ids, BAND_LAYERS)
    pl = _best_rank_per_layer(ll, token_ids, BAND_LAYERS)
    top20 = {L: [tokenizer.decode([t]) for t in jl[L][-1].topk(20).indices] for L in BAND_LAYERS}

    vj, vl = list(pj.values()), list(pl.values())
    del jl_raw, jl, ll
    torch.cuda.empty_cache()
    return {
        "j_median": float(np.median(vj)), "j_best": int(min(vj)),
        "l_median": float(np.median(vl)), "l_best": int(min(vl)),
        "per_layer_j": pj, "top20": top20,
    }


# Positive control for the logit lens (§4a): it must detect the d0 inferred-trigger
# signal, defined as logit-lens best rank <= 5x the J-lens value at the same checkpoint.
# Without this, a logit-lens null cannot be distinguished from a blind instrument.
LOGIT_POSCTRL_FACTOR = 5.0

screen_rows, screen_top20 = [], []
for c in S.CANDIDATES:
    trait = c["trait"]
    ids = list(LEXICON_IDS[trait].values())
    if not ids:
        print(f"SKIP {c['name']}: no single-token lexicon entries for {trait!r}")
        continue
    per_arm, per_arm_logit = {}, {}
    for arm in S.ARMS:
        text = S.build_probe(c, arm, 0, "cue_b")
        res = read_both_lenses(text, ids)
        per_arm[arm] = res["j_median"]
        per_arm_logit[arm] = res["l_median"]
        screen_rows.append({
            "name": c["name"], "trait": trait, "valence": c["valence"], "arm": arm,
            "median_rank_band": res["j_median"], "best_rank_band": res["j_best"],
            "logit_median_rank_band": res["l_median"], "logit_best_rank_band": res["l_best"],
            "n_lexicon": len(ids), "text": text,
        })
        for layer, toks in res["top20"].items():
            for r, tok in enumerate(toks, 1):
                screen_top20.append({"name": c["name"], "arm": arm, "layer": layer,
                                     "rank": r, "token": tok})

    ratio = per_arm["control"] / per_arm["inferred"] if per_arm["inferred"] else float("inf")
    posctrl = per_arm_logit["inferred"] <= LOGIT_POSCTRL_FACTOR * per_arm["inferred"]
    screen_rows[-1]["logit_positive_control"] = bool(posctrl)
    print(f"{c['name']:<7} {trait:<10} inferred={per_arm['inferred']:>8.1f}  "
          f"control={per_arm['control']:>9.1f}  ratio={ratio:>7.2f}  "
          f"direct={per_arm['direct']:>7.1f}   logit(inf)={per_arm_logit['inferred']:>9.1f}  "
          f"posctrl={'PASS' if posctrl else 'fail'}")

screen_df = pd.DataFrame(screen_rows)
screen_df.to_csv("screening_results.csv", index=False)
pd.DataFrame(screen_top20).to_csv("screening_top20.csv", index=False)
print(f"\nWrote screening_results.csv ({len(screen_df)} rows) and screening_top20.csv")
""".strip()))

cells.append(code(r"""
# Apply the FROZEN gate. These two numbers come from prediction.md §3 and are not
# tunable in this notebook -- that is the whole point of having committed them first.
GATE_MAX_INFERRED_RANK = 200
GATE_MIN_CONTROL_RATIO = 5.0

piv = screen_df.pivot(index="name", columns="arm", values="median_rank_band")
gate = piv.assign(
    ratio=lambda d: d["control"] / d["inferred"],
    passes_rank=lambda d: d["inferred"] <= GATE_MAX_INFERRED_RANK,
    passes_ratio=lambda d: (d["control"] / d["inferred"]) >= GATE_MIN_CONTROL_RATIO,
)
gate["PASS"] = gate["passes_rank"] & gate["passes_ratio"]
gate = gate.join(screen_df.drop_duplicates("name").set_index("name")[["trait", "valence"]])
gate = gate[["trait", "valence", "inferred", "control", "direct", "ratio",
             "passes_rank", "passes_ratio", "PASS"]].sort_values(["PASS", "ratio"], ascending=[False, False])
gate.to_csv("screening_gate.csv")

print(gate.round(2).to_string())

survivors = gate[gate["PASS"]].index.tolist()
n_pos = int((gate.loc[survivors, "valence"] == "+").sum())
n_neg = int((gate.loc[survivors, "valence"] == "-").sum())
print(f"\n{len(survivors)}/{len(gate)} pass: {survivors}")
print(f"valence balance among survivors: {n_pos} positive / {n_neg} negative")

if len(survivors) < 5:
    raise RuntimeError(
        f"HALT: only {len(survivors)} candidates passed screening (<5).\n"
        "prediction.md §3 failure rule: the run halts here. Do NOT loosen the gate to admit "
        "more -- it is pre-registered, and loosening it is only ever tempting in exactly this "
        "situation. Revise the thresholds in a dated §9 amendment, showing the table above as "
        "the justification, BEFORE any Phase 2 data exists."
    )
if min(n_pos, n_neg) < 3:
    print("\nFLAG: valence balance broken. Report it; do not back-fill replacements "
          "chosen after seeing this table (prediction.md §5).")

with open("screening_roster.json", "w") as f:
    json.dump({"survivors": survivors, "n_positive": n_pos, "n_negative": n_neg,
               "gate_max_inferred_rank": GATE_MAX_INFERRED_RANK,
               "gate_min_control_ratio": GATE_MIN_CONTROL_RATIO}, f, indent=2)
print("\nWrote screening_gate.csv and screening_roster.json")
""".strip()))

cells.append(md(r"""
## Done — Phase 1

Files to download and send back, all of them:

| file | what it is |
|---|---|
| `calibration.json` | the calibrated band — **Phase 2 reads its band from here** |
| `calibration_by_layer.csv`, `calibration_raw.csv` | the three curves, aggregated and raw |
| `calibration_curves.png` | the plots the band decision rests on |
| `tokenizer_check.csv` | which lexicon entries and tracers survived single-token |
| `screening_results.csv`, `screening_top20.csv` | d0 reads, all ten candidates, three arms |
| `screening_gate.csv`, `screening_roster.json` | gate outcome and the surviving roster |

**What Phase 2 will do, once these come back:** build the full cued-retrieval sweep (Cue A / Cue B
across d ∈ {0,1,2,4,7,10}), the tracer stream for Q2, and the KV-ablation for Q3, over the surviving
roster and the calibrated band.

**The honest caveats to carry into the write-up now, not later:**
- Screening reads are exploratory. They are recorded in full and they gate the roster; they are not
  evidence about Q1–Q3.
- If the calibrated band differs materially from v1's inherited 35–90%, then v1's numbers were read
  from the wrong depths, and v2 is not merely a better-designed replication — it is the first correct
  measurement. That is worth stating plainly either way.
- The KV-ablation (Q3) is the one part of the spec whose feasibility is **not yet verified**: it needs
  attention masking that the `jlens` public API may not expose, in which case Phase 2 will need
  forward hooks on the HF model. Flagged now rather than discovered at implementation time.
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

# Write the notebook next to this script, so it survives folder renames and
# regenerates correctly wherever the repo lives.
out = pathlib.Path(__file__).resolve().parent / "trait_persistence_v2_phase1.ipynb"
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"wrote {out} — {len(cells)} cells")

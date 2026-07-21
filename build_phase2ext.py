"""Generate trait_persistence_v2_phase2ext.ipynb — the §7a conditional extension (d in {15,20,30}).

Identical instrument, cues, measures, band, roster, lexicons, and tracers to the primary Phase 2
run (`build_phase2.py`); the ONLY change is the distance set (`S.EXT_DISTANCES`) and the output
filenames (`phase2ext_*`). The lens machinery cells are copied verbatim so the extension is
byte-for-byte the same measurement, just farther out.

Registered in prediction.md §7a; the trigger fired on the primary sweep (see §9, 2026-07-21 later
still). No positive-control cell here — Q5's per-character control was established at d0 in the
primary run and is joined back in during analysis; the extension has no d0.
"""
import json, pathlib

md = lambda s: {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)}
code = lambda s: {"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": s.strip("\n").splitlines(keepends=True)}

cells = []

cells.append(md(r"""
# Trait persistence v2 — §7a extension: distances 15, 20, 30

**Registered secondary run.** `prediction.md` §7a pre-registered this extension; the two-part trigger
fired on the primary Phase 2 sweep (direct arm still retrievable at d=10, no direct-vs-inferred
separation emerged, and Q2 was not copy bias so the override did not apply — see §9, 2026-07-21 "later
still"). It carries the **same descriptive status as the primary sweep** and draws **no new
held-latent-vs-held-scene claim** (Q3 stays deferred).

Everything is identical to the primary run except the **distances** (`S.EXT_DISTANCES = [15,20,30]`)
and the **output filenames** (`phase2ext_*`). Same model, lens, pin, band, roster, cues, measures,
lexicons, tracers. The 20 extra filler sentences (stimuli indices 10–29) are declared in `prediction.md`
§9 and verified trait/tracer/name-neutral; indices 0–9 are unchanged, so d≤10 stays byte-identical to
the primary run (not re-run here — those results stand).

**Before running:** T4 GPU; HF token as Colab secret `HF_token`; upload
`trait_persistence_v2_stimuli.py` + the `phase1/` folder (or clone the repo — recommended, so you get
the extended stimuli file automatically).
""".strip()))

cells.append(code(r"""
JLENS_COMMIT = "581d398613e5602a5af361e1c34d3a92ea82ba8e"
!pip install -q "git+https://github.com/anthropics/jacobian-lens.git@{JLENS_COMMIT}"
!pip install -q huggingface_hub datasets scipy
""".strip()))

cells.append(code(r"""
from huggingface_hub import login
from google.colab import userdata

login(token=userdata.get("HF_token"))
""".strip()))

cells.append(code(r"""
import os, sys, json

if not os.path.exists("trait_persistence_v2_stimuli.py"):
    raise FileNotFoundError(
        "trait_persistence_v2_stimuli.py not found. Upload it or clone the repo. This run needs the "
        "EXTENDED stimuli (30 filler sentences); an old 10-sentence copy will silently cap d at 10."
    )
import trait_persistence_v2_stimuli as S

# Guard against running the extension against a pre-extension stimuli file.
if not hasattr(S, "EXT_DISTANCES") or len(S.FILLER_SENTENCES) < max(S.EXT_DISTANCES):
    raise RuntimeError(
        f"stimuli file is not the §7a-extended version: need EXT_DISTANCES and >= {max([15,20,30])} "
        f"filler sentences, found {len(S.FILLER_SENTENCES)}. Clone the current repo."
    )


def _find(fname):
    for p in (os.path.join("phase1", fname), fname):
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"{fname} not found in phase1/ or cwd. Upload the Phase 1 outputs.")


with open(_find("calibration.json")) as f:
    CALIB = json.load(f)
with open(_find("screening_roster.json")) as f:
    ROSTER = json.load(f)

BAND_LAYERS  = [int(l) for l in CALIB["band_layers"]]
SURVIVORS    = list(ROSTER["survivors"])
EXT_DISTANCES = list(S.EXT_DISTANCES)

print(f"band: layers {BAND_LAYERS[0]}..{BAND_LAYERS[-1]} ({len(BAND_LAYERS)} layers)")
print(f"roster: {len(SURVIVORS)} survivors: {SURVIVORS}")
print(f"EXTENSION distances: {EXT_DISTANCES}   (filler has {len(S.FILLER_SENTENCES)} sentences)")
""".strip()))

cells.append(md(r"""
## Load model and lens (identical to Phase 1 / primary Phase 2)
""".strip()))

cells.append(code(r"""
import torch, transformers, jlens
import numpy as np, pandas as pd

jlens.configure_logging()
print("python", sys.version.split()[0], "| torch", torch.__version__,
      "| transformers", transformers.__version__, "| jlens @", JLENS_COMMIT[:12])

MODEL_NAME = "google/gemma-3-4b-it"
LENS_REPO  = "neuronpedia/jacobian-lens"
LENS_FILE  = "gemma-3-4b-it/jlens/Salesforce-wikitext/gemma-3-4b-it_jacobian_lens.pt"

hf_model  = transformers.AutoModelForCausalLM.from_pretrained(MODEL_NAME, dtype=torch.bfloat16).cuda()
tokenizer = transformers.AutoTokenizer.from_pretrained(MODEL_NAME)
model     = jlens.from_hf(hf_model, tokenizer)
lens      = jlens.JacobianLens.from_pretrained(LENS_REPO, filename=LENS_FILE)

N_LAYERS   = model.n_layers
ALL_LAYERS = list(range(N_LAYERS - 1))
assert CALIB["n_layers"] == N_LAYERS, "calibration.json is for a different model — do not proceed."
assert BAND_LAYERS[0] >= ALL_LAYERS[0] and BAND_LAYERS[-1] <= ALL_LAYERS[-1]
print(f"n_layers={N_LAYERS}; band OK")
""".strip()))

cells.append(md(r"""
## Logit-lens wiring + validation (verbatim from the primary run; Q5 depends on it)
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
    raise RuntimeError("Could not locate final norm / lm_head; do not guess (wrong norm = silent junk).")
print(f"logit lens: norm <- hf_model.{_np}   head <- hf_model.{_hp}")


@torch.no_grad()
def logit_lens_logits(text, layers, positions):
    enc = tokenizer(text, return_tensors="pt").to(hf_model.device)
    hs = hf_model(**enc, output_hidden_states=True).hidden_states
    return {L: LM_HEAD(FINAL_NORM(hs[L + 1][0, positions, :])).float() for L in layers}
""".strip()))

cells.append(code(r"""
_ptxt = "The Eiffel Tower stands in the French capital city of"
_enc = tokenizer(_ptxt, return_tensors="pt").to(hf_model.device)
with torch.no_grad():
    _out = hf_model(**_enc, output_hidden_states=True)
_dec = lambda ids: [tokenizer.decode([i]) for i in ids]
_real = _dec(_out.logits[0, -1].float().topk(8).indices.tolist())
_llf  = _dec(LM_HEAD(_out.hidden_states[-1][0, -1].unsqueeze(0))[0].float().topk(8).indices.tolist())
print("TOP-8 SETS MATCH:", set(_real) == set(_llf), "  <-- must be True")
assert set(_real) == set(_llf), "logit-lens FAILED validation — fix before trusting any Q5 number."
print("logit channel validated.")
""".strip()))

cells.append(md(r"""
## Token ids and read machinery (verbatim from the primary run)
""".strip()))

cells.append(code(r"""
def single_token_id(word):
    ids = tokenizer.encode(" " + word, add_special_tokens=False)
    return ids[0] if len(ids) == 1 else None

LEXICON_IDS = {}
for trait, words in S.TRAIT_LEXICONS.items():
    kept = {w: single_token_id(w) for w in words}
    LEXICON_IDS[trait] = {w: t for w, t in kept.items() if t is not None}

SURVIVOR_CHARS = sorted((S.by_name(n) for n in SURVIVORS), key=lambda c: (c["valence"], c["name"]))
CHAR_GROUPS = {}
for c in SURVIVOR_CHARS:
    CHAR_GROUPS[c["name"]] = {
        "trait":  list(LEXICON_IDS[c["trait"]].values()),
        "adj":    [single_token_id(c["trait"])] if single_token_id(c["trait"]) is not None else [],
        "tracer": [single_token_id(c["tracer"])] if single_token_id(c["tracer"]) is not None else [],
    }
    print(f"{c['name']:<7} {c['trait']:<10} lexicon={len(CHAR_GROUPS[c['name']]['trait'])}  "
          f"tracer={c['tracer']}")
""".strip()))

cells.append(code(r"""
def _best_rank_per_layer(logits_by_layer, token_ids, layers):
    per_layer = {}
    for layer in layers:
        lg = logits_by_layer[layer]
        best = None
        for pi in range(lg.shape[0]):
            row = lg[pi]
            for tid in token_ids:
                r = int((row > row[tid]).sum().item()) + 1
                best = r if best is None else min(best, r)
        per_layer[layer] = best
    return per_layer


def cue_read_positions(prefix, full_text, cue, name):
    n = tokenizer(full_text, return_tensors="pt")["input_ids"].shape[1]
    if cue in ("cue_b", "passive"):
        return [n - 1]
    p = tokenizer(prefix, return_tensors="pt")["input_ids"].shape[1]
    name_ids = tokenizer.encode(" " + name, add_special_tokens=False)
    full_ids = tokenizer(full_text, return_tensors="pt")["input_ids"][0].tolist()
    L, after = len(name_ids), None
    for i in range(max(p - 1, 0), n - L + 1):
        if full_ids[i:i + L] == name_ids:
            after = i + L
    if after is None or after >= n:
        return [n - 1]
    return list(range(after, n))


def read_checkpoint(text, positions, groups):
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
        per_group[gname] = {"j_median": float(np.median(vj)), "j_best": int(min(vj)),
                            "l_median": float(np.median(vl)), "l_best": int(min(vl)),
                            "per_layer_j": pj, "per_layer_l": pl}
    top20 = {L: [tokenizer.decode([t]) for t in jl[L][-1].topk(20).indices] for L in BAND_LAYERS}
    del jl_raw, jl, ll
    torch.cuda.empty_cache()
    return per_group, top20
""".strip()))

cells.append(md(r"""
# The extension sweep — d ∈ {15, 20, 30}

7 survivors × 3 arms × 3 distances × 3 cues = **189 forward passes per lens**. Same three token groups
per pass (trait / adj / tracer). Outputs are `phase2ext_*` so they never collide with the primary
`phase2_*` files; analysis concatenates the two.
""".strip()))

cells.append(code(r"""
CUES = ["cue_b", "cue_a", "passive"]
DMAX = max(EXT_DISTANCES)
reads_rows, perlayer_rows, top20_rows, reintro_rows = [], [], [], []

for c in SURVIVOR_CHARS:
    groups = CHAR_GROUPS[c["name"]]
    for arm in S.ARMS:
        for d in EXT_DISTANCES:
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
                        perlayer_rows.append({"name": c["name"], "arm": arm, "distance": d, "cue": cue,
                                              "measure": measure, "lens": "jlens", "layer": L,
                                              "rank": r["per_layer_j"][L]})
                        perlayer_rows.append({"name": c["name"], "arm": arm, "distance": d, "cue": cue,
                                              "measure": measure, "lens": "logit", "layer": L,
                                              "rank": r["per_layer_l"][L]})
                for L, toks in top20.items():
                    for rk, tok in enumerate(toks, 1):
                        top20_rows.append({"name": c["name"], "arm": arm, "distance": d, "cue": cue,
                                           "layer": L, "rank": rk, "token": tok})
                if is_reintro:
                    try:
                        enc = tokenizer(text, return_tensors="pt").to(hf_model.device)
                        with torch.no_grad():
                            gen = hf_model.generate(**enc, max_new_tokens=12, do_sample=False)
                        cont = tokenizer.decode(gen[0][enc["input_ids"].shape[1]:], skip_special_tokens=True)
                    except Exception as e:
                        cont = f"(continuation failed: {e})"
                    reintro_rows.append({"name": c["name"], "arm": arm, "cue": cue,
                                         "continuation": cont, "text": text})
    print(f"  swept {c['name']:<7} ({c['trait']}, {c['valence']})")

reads_df = pd.DataFrame(reads_rows)
reads_df.to_csv("phase2ext_reads.csv", index=False)
pd.DataFrame(perlayer_rows).to_csv("phase2ext_per_layer.csv", index=False)
pd.DataFrame(top20_rows).to_csv("phase2ext_top20.csv", index=False)
pd.DataFrame(reintro_rows).to_csv("phase2ext_reintro.csv", index=False)
print(f"\nwrote phase2ext_reads.csv ({len(reads_df)} rows), phase2ext_per_layer.csv "
      f"({len(perlayer_rows)} rows), phase2ext_top20.csv, phase2ext_reintro.csv")
""".strip()))

cells.append(code(r"""
# Quick direction preview across the extended distances (descriptive only; the frozen §3 analysis
# runs offline, joining these with the primary phase2_reads.csv over d in {4,7,10,15,20,30}).
cb = reads_df[(reads_df["cue"] == "cue_b") & (reads_df["measure"] == "trait")]
piv = cb.pivot_table(index="distance", columns="arm", values="j_median_rank_band")
print("Median band-rank by distance (Cue B, trait) — direct / inferred / control:")
print(piv.round(1).to_string())
print("\nDescriptive only. Combine with the primary sweep offline for the trend.")
""".strip()))

cells.append(md(r"""
## Done — §7a extension

Download and send back: `phase2ext_reads.csv`, `phase2ext_per_layer.csv`, `phase2ext_top20.csv`,
`phase2ext_reintro.csv` (download individually to dodge the multi-download block).

Analysis joins these with the primary `phase2_reads.csv` and reads the direct/inferred trend across
d ∈ {4, 7, 10, 15, 20, 30}. Status is the same as the primary sweep: descriptive, n = 7, no
held-latent-vs-held-scene claim.
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

out = pathlib.Path(__file__).resolve().parent / "trait_persistence_v2_phase2ext.ipynb"
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"wrote {out} — {len(cells)} cells")

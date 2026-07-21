"""Generate trait_persistence_v2_phase3b.ipynb — the Q3 re-run with the CORRECTED mask-check gate.

Phase 3 answered Q3 (held scene) but its §7b gate was a poor realisation of its own criterion: it
scored scene-keyword rank at a SINGLE position while the criterion is the behaviour "the model can no
longer answer what did NAME do". It failed in both directions — three false failures, one probable
false pass — costing three certifications (see prediction.md §9, "Q3 gate flaw").

Phase 3b re-runs the identical ablation with the gate fixed and registered in advance
(prediction.md §9, "Phase 3b: corrected gate registered as primary"):

  * PRIMARY gate   — continuation-scored: does the generated answer still contain scene-specific
                     content words (excluding anything from the opening)?
  * SECONDARY gate — the repaired rank read: best scene-keyword rank across the first 12 GENERATED
                     positions, not one position. Same thresholds as before.

**What this run is worth, and is not.** The trait numbers are expected to REPRODUCE, not change — same
model, texts, masks. Phase 3b buys (i) a verdict resting on a gate fixed before its data existed and
(ii) a replication. It buys no new information about the model. The corrected gate is
"pre-registered for this run, derived from the previous one"; the re-run does not launder that.

Everything else is byte-identical to `build_phase3.py`: band, roster, stimuli, arms, cues, distances,
the d=10 decision checkpoint, the §3 verdict rule, and the ablation mechanism. Outputs are `phase3b_*`.
"""
import json, pathlib

md = lambda s: {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)}
code = lambda s: {"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": s.strip("\n").splitlines(keepends=True)}

cells = []

cells.append(md(r"""
# Trait persistence v2 — Phase 3b: the Q3 re-run with the corrected gate

**Pre-registered for this run.** `prediction.md` §9 ("Phase 3b: corrected gate registered as primary")
was committed **before this notebook ran**. The §3 verdict rule and the §7b criterion are unchanged and
used verbatim; only the *realisation* of the mask-check is repaired.

## Why this run exists

Phase 3 answered Q3 — **held scene** — but its gate was a bad proxy for its own criterion. It scored
scene-keyword rank at a **single position** (the token after the name) while §7b asks a behavioural
question: *can the model still answer "what did NAME do?"* The scene keywords are mostly nouns the model
emits 2–5 tokens later, so the two came apart **in both directions**: three characters failed whose
masks demonstrably worked (their continuations show a clean fallback to the occupation), and Elias
passed while his continuation was identical in all three conditions — his scene was never elicited at
all.

## What is fixed

- **Primary gate — continuation-scored.** `scene_overlap` = distinct content words (≥4 chars, minus a
  fixed stopword list) shared with the character's `inferred` sentence, **excluding any word also in the
  opening** (so falling back to the occupation scores 0). Passes iff baseline ≥ 1, scene-masked = 0,
  control-masked ≥ 1.
- **Secondary gate — repaired rank.** Best scene-keyword rank across the **first 12 generated
  positions** rather than one. Thresholds unchanged (`kw_i ≤ 50`, `kw_ii/kw_i ≥ 5`, `kw_iii/kw_i ≤ 2`).
- Both are reported. Agreement closes the instrument question; **disagreement is reported as an open
  problem, not resolved in favour of whichever is convenient.**

## What is deliberately NOT changed

Scene keywords are **not** re-picked, even though Phase 3 showed the model's first-emitted words
(`covered`, `opens`) had been dropped for filler leakage — re-picking them after seeing the model's
output would tune the stimulus to the observation. The roster is not back-filled. The underpowered
characters are not replaced.

## Registered expectations (so the gate is falsifiable, not merely permissive)

A gate that certifies everything is not a gate. Recorded in §9 before this ran:

| character | predicted |
|---|---|
| Elias | **FAILS** the primary gate (scene never elicited). If he passes, the gate is too permissive — report that. |
| Marek | passes the gate, returns **(c) underpowered** |
| Greta, Nadia, Maria, Simon, Bruno | pass, return **(b) held scene** |
| any | **held latent would be a genuine surprise** and is the outcome most worth reporting |

**Honest framing of this run:** the trait numbers should *reproduce*. This buys a clean verdict and a
replication — not new information about the model.

**Before running:** T4 GPU; `HF_token` Colab secret; clone the repo in a first cell.
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
    raise FileNotFoundError("trait_persistence_v2_stimuli.py not found. Clone the repo.")
import trait_persistence_v2_stimuli as S

if not hasattr(S, "SCENE_KEYWORDS") or not hasattr(S, "scene_probe"):
    raise RuntimeError("stimuli file lacks SCENE_KEYWORDS / scene_probe — clone the current repo.")
if len(S.FILLER_SENTENCES) < 30:
    raise RuntimeError(f"filler has {len(S.FILLER_SENTENCES)} < 30 sentences; d=30 would be cut.")


def _find(fname):
    for p in (os.path.join("phase1", fname), fname):
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"{fname} not found in phase1/ or cwd.")


with open(_find("calibration.json")) as f:
    CALIB = json.load(f)
with open(_find("screening_roster.json")) as f:
    ROSTER = json.load(f)

BAND_LAYERS = [int(l) for l in CALIB["band_layers"]]
SURVIVORS   = list(ROSTER["survivors"])

DISTANCES_P3 = [0, 1, 2, 4, 7, 10, 30]
DECISION_D   = 10
GEN_N        = 12          # generation length AND the number of positions the repaired rank gate reads

print(f"band: layers {BAND_LAYERS[0]}..{BAND_LAYERS[-1]} ({len(BAND_LAYERS)} layers)")
print(f"roster: {len(SURVIVORS)} survivors: {SURVIVORS}")
print(f"distances: {DISTANCES_P3}   decision: d={DECISION_D}, Cue B   gen/rank positions: {GEN_N}")
""".strip()))

cells.append(md(r"""
## Load model and lens — eager attention (required by the mask), identical to Phase 3
""".strip()))

cells.append(code(r"""
import torch, transformers, jlens
import numpy as np, pandas as pd
import contextlib

jlens.configure_logging()
print("python", sys.version.split()[0], "| torch", torch.__version__,
      "| transformers", transformers.__version__, "| jlens @", JLENS_COMMIT[:12])

MODEL_NAME = "google/gemma-3-4b-it"
LENS_REPO  = "neuronpedia/jacobian-lens"
LENS_FILE  = "gemma-3-4b-it/jlens/Salesforce-wikitext/gemma-3-4b-it_jacobian_lens.pt"

hf_model  = transformers.AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, dtype=torch.bfloat16, attn_implementation="eager"
).cuda()
tokenizer = transformers.AutoTokenizer.from_pretrained(MODEL_NAME)
model     = jlens.from_hf(hf_model, tokenizer)
lens      = jlens.JacobianLens.from_pretrained(LENS_REPO, filename=LENS_FILE)

N_LAYERS   = model.n_layers
ALL_LAYERS = list(range(N_LAYERS - 1))
assert CALIB["n_layers"] == N_LAYERS, "calibration.json is for a different model."
assert BAND_LAYERS[0] >= ALL_LAYERS[0] and BAND_LAYERS[-1] <= ALL_LAYERS[-1]
print(f"n_layers={N_LAYERS}; attn_implementation = "
      f"{getattr(hf_model.config, '_attn_implementation', None)!r}")
""".strip()))

cells.append(code(r"""
def _resolve_layers(m):
    for path in ("model.language_model.layers", "language_model.model.layers",
                 "model.model.layers", "model.layers", "language_model.layers"):
        cur, ok = m, True
        for part in path.split("."):
            if hasattr(cur, part):
                cur = getattr(cur, part)
            else:
                ok = False
                break
        if ok and hasattr(cur, "__len__") and len(cur) > 0 and hasattr(cur[0], "self_attn"):
            return cur, path
    return None, None

DECODER_LAYERS, _lp = _resolve_layers(hf_model)
if DECODER_LAYERS is None:
    raise RuntimeError("Could not locate the decoder layers. Do NOT guess.")
print(f"decoder layers: hf_model.{_lp}  ({len(DECODER_LAYERS)} blocks)")
assert len(DECODER_LAYERS) == N_LAYERS
""".strip()))

cells.append(md(r"""
### The KV-ablation hook — unchanged from Phase 3 (§7b mechanism, verbatim)
""".strip()))

cells.append(code(r"""
def _mask_hook(cols):
    cols_t = torch.as_tensor(sorted(set(cols)), dtype=torch.long)

    def hook(module, args, kwargs):
        am, idx = kwargs.get("attention_mask", None), None
        if am is None:
            for i, a in enumerate(args):
                if torch.is_tensor(a) and a.dim() == 4 and a.is_floating_point():
                    am, idx = a, i
                    break
        if am is None:
            raise RuntimeError("No additive 4-D attention_mask reached self_attn — eager path inactive.")
        am = am.clone()
        c = cols_t.to(am.device)
        c = c[c < am.shape[-1]]
        am[..., c] = torch.finfo(am.dtype).min
        if idx is None:
            kwargs = {**kwargs, "attention_mask": am}
        else:
            args = list(args); args[idx] = am; args = tuple(args)
        return args, kwargs

    return hook


@contextlib.contextmanager
def ablate(cols, force=False):
    '''Mask attention toward key positions `cols`. `force=True` registers the hooks even when `cols`
    is empty — used by the null-mask identity check to exercise the hook machinery itself.'''
    handles = []
    if cols or force:
        h = _mask_hook(cols)
        for blk in DECODER_LAYERS:
            handles.append(blk.self_attn.register_forward_pre_hook(h, with_kwargs=True))
    try:
        yield
    finally:
        for hd in handles:
            hd.remove()
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
    raise RuntimeError("Could not locate final norm / lm_head.")

_ptxt = "The Eiffel Tower stands in the French capital city of"
_enc = tokenizer(_ptxt, return_tensors="pt").to(hf_model.device)
with torch.no_grad():
    _out = hf_model(**_enc, output_hidden_states=True)
_dec = lambda ids: [tokenizer.decode([i]) for i in ids]
_real = _dec(_out.logits[0, -1].float().topk(8).indices.tolist())
_llf  = _dec(LM_HEAD(_out.hidden_states[-1][0, -1].unsqueeze(0))[0].float().topk(8).indices.tolist())
print("TOP-8 SETS MATCH:", set(_real) == set(_llf), "  <-- must be True")
assert set(_real) == set(_llf), "logit-lens FAILED validation."
print("logit channel validated.")
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
CHAR_GROUPS, SCENE_KW_IDS = {}, {}
for c in SURVIVOR_CHARS:
    CHAR_GROUPS[c["name"]] = {"trait": list(LEXICON_IDS[c["trait"]].values())}
    SCENE_KW_IDS[c["name"]] = [t for t in (single_token_id(w) for w in S.SCENE_KEYWORDS[c["name"]])
                               if t is not None]
    print(f"{c['name']:<7} {c['trait']:<10} lexicon={len(CHAR_GROUPS[c['name']]['trait']):>2}  "
          f"scene_kw={len(SCENE_KW_IDS[c['name']])}/{len(S.SCENE_KEYWORDS[c['name']])}")
""".strip()))

cells.append(code(r"""
def find_span(full_ids, text_piece):
    for pref in (" ", ""):
        sub = tokenizer.encode(pref + text_piece, add_special_tokens=False)
        if not sub:
            continue
        for i in range(len(full_ids) - len(sub) + 1):
            if full_ids[i:i + len(sub)] == sub:
                return list(range(i, i + len(sub)))
    return None


def matched_filler_span(full_ids, distance, scene_len):
    if distance == 0 or scene_len is None:
        return None
    best, best_diff = None, None
    for f in S.FILLER_SENTENCES[:distance]:
        span = find_span(full_ids, f)
        if span is None:
            continue
        diff = abs(len(span) - scene_len)
        if best_diff is None or diff < best_diff:
            best, best_diff = span, diff
    return best


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


def read_probe(text, positions, id_groups):
    '''Trait read (unchanged from Phase 3). Wrap the call in `with ablate(cols):`.'''
    _n = tokenizer(text, return_tensors="pt")["input_ids"].shape[1]
    assert _n <= 2048, f"sequence is {_n} tokens"
    jl_raw, _, _ = lens.apply(model, text, layers=BAND_LAYERS, positions=positions, max_seq_len=2048)
    jl = {L: jl_raw[L].float() for L in BAND_LAYERS}
    enc = tokenizer(text, return_tensors="pt").to(hf_model.device)
    with torch.no_grad():
        out = hf_model(**enc, output_hidden_states=True)
    hs = out.hidden_states
    ll = {L: LM_HEAD(FINAL_NORM(hs[L + 1][0, positions, :])).float() for L in BAND_LAYERS}
    res = {}
    for g, ids in id_groups.items():
        if not ids:
            continue
        pj = _best_rank_per_layer(jl, ids, BAND_LAYERS)
        pl = _best_rank_per_layer(ll, ids, BAND_LAYERS)
        res[g] = {"j_median": float(np.median(list(pj.values()))),
                  "logit_median": float(np.median(list(pl.values()))),
                  "per_layer_j": pj, "per_layer_l": pl}
    top20 = {L: [tokenizer.decode([t]) for t in jl[L][-1].topk(20).indices] for L in BAND_LAYERS}
    del jl_raw, jl, out, hs, ll
    torch.cuda.empty_cache()
    return res, top20
""".strip()))

cells.append(md(r"""
### The corrected gate read — one generation, both gates

`scene_probe_read` runs the `"What did NAME do? NAME"` probe under the mask **once** and returns both
gate inputs from that single generation:

- the **continuation text** → the PRIMARY gate (scored off-GPU against the stimuli, in `analyze_phase3b.py`);
- the best scene-keyword rank across **all 12 generated positions** → the repaired SECONDARY gate.

Reading the rank at every generated step rather than only the first is the entire fix: the scene words
the model emits are mostly 2–5 tokens in, which is exactly what the Phase 3 gate could not see.
`use_cache=False` keeps the fixed masked span valid at every decoding step.
""".strip()))

cells.append(code(r"""
def scene_probe_read(text, cols, kw_ids, n=GEN_N):
    '''Greedy answer under the mask + best scene-keyword rank across ALL generated positions.'''
    enc = tokenizer(text, return_tensors="pt").to(hf_model.device)
    try:
        with ablate(cols or []):
            with torch.no_grad():
                gen = hf_model.generate(**enc, max_new_tokens=n, do_sample=False, use_cache=False,
                                        return_dict_in_generate=True, output_scores=True)
    except Exception as e:
        return f"(generation failed: {e})", float("nan")

    cont = tokenizer.decode(gen.sequences[0][enc["input_ids"].shape[1]:], skip_special_tokens=True)
    best = None
    if kw_ids:
        for step in gen.scores:                       # one [1, vocab] tensor per generated token
            row = step[0].float()
            for t in kw_ids:
                r = int((row > row[t]).sum().item()) + 1
                best = r if best is None else min(best, r)
    del gen
    torch.cuda.empty_cache()
    return cont, (float(best) if best is not None else float("nan"))
""".strip()))

cells.append(md(r"""
## Mechanistic mask check (unchanged) — attention to the masked span must be ~0
""".strip()))

cells.append(code(r"""
def attn_to_cols_max(text, cols):
    enc = tokenizer(text, return_tensors="pt").to(hf_model.device)
    with torch.no_grad():
        out = hf_model(**enc, output_attentions=True)
    n = enc["input_ids"].shape[1]
    c = [x for x in cols if x < n]
    mx = 0.0
    for L in BAND_LAYERS:
        mx = max(mx, float(out.attentions[L][0][:, :, c].max().item()))
    del out
    torch.cuda.empty_cache()
    return mx

_c = S.by_name("Maria")
_txt = S.build_probe(_c, "inferred", DECISION_D, "cue_b")
_ids = tokenizer(_txt, return_tensors="pt")["input_ids"][0].tolist()
_scene = find_span(_ids, _c["inferred"])
assert _scene is not None
_base = attn_to_cols_max(_txt, _scene)
with ablate(_scene):
    _masked = attn_to_cols_max(_txt, _scene)
print(f"max attention to scene columns — baseline: {_base:.4f}   masked: {_masked:.2e}")
assert _masked < 1e-6, f"MASK DID NOT TAKE ({_masked:.2e}). Do not trust any ablation read."
print("mechanistic mask check PASSED.")
print("(Phase 3 recorded baseline 0.9453 / masked 0.00 — this should reproduce closely.)")
""".strip()))

cells.append(md(r"""
### Two more instrument checks — closing the remaining ways the ablation could be silently wrong

The attention-mass check above proves the mask *removes* attention. Two failure modes it does not
cover, added here:

1. **Null-mask identity** — a hook that perturbs the model even when it masks nothing. The hook clones
   and replaces the attention mask on every call, so it must be proven **inert** when handed an empty
   span. Registering the hooks with `force=True` and an empty column set must reproduce the unhooked
   logits **bit-identically**. (This deliberately exercises the hook machinery, rather than the
   `if cols:` shortcut that skips registration.)
2. **Total-mask degradation** — a hook that fires but has no real effect, so that any observed collapse
   came from somewhere else. Masking the *entire story* must visibly wreck the trait read. Position 0 is
   spared as an attention sink: if every key a query may attend to were masked, its softmax row would be
   all −∞ and produce NaN rather than a measurement.

Together with the semantic gate, these cover the four ways this intervention could lie: not firing,
firing inertly, firing without teeth, or severing the wrong thing.
""".strip()))

cells.append(code(r"""
# --- 1. NULL-MASK IDENTITY: hooks registered, nothing masked -> must be bit-identical ------------
_enc0 = tokenizer(_txt, return_tensors="pt").to(hf_model.device)
with torch.no_grad():
    _plain = hf_model(**_enc0).logits
with ablate([], force=True):                      # hooks ACTIVE, empty span
    with torch.no_grad():
        _null = hf_model(**_enc0).logits
_identical = torch.equal(_plain, _null)
_maxdiff = (_plain - _null).abs().max().item()
print(f"null-mask identity: bit-identical = {_identical}   max|diff| = {_maxdiff:.3e}")
assert _identical, (
    "NULL-MASK IDENTITY FAILED: registering the hook with an empty span changed the logits. The hook "
    "perturbs the model independently of what it masks, so every ablation read is confounded. Fix first."
)
print("  -> the hook is inert when it masks nothing.")

# --- 2. TOTAL-MASK DEGRADATION: mask the whole story -> the trait read must be wrecked ------------
_prefix_n = tokenizer(S.build_prefix(_c, "inferred", DECISION_D),
                      return_tensors="pt")["input_ids"].shape[1]
_all_story = list(range(1, _prefix_n))             # spare position 0 as an attention sink (avoids NaN)
_trait_ids = CHAR_GROUPS["Maria"]["trait"]
_posB = [tokenizer(_txt, return_tensors="pt")["input_ids"].shape[1] - 1]

_r_base, _ = read_probe(_txt, _posB, {"trait": _trait_ids})
with ablate(_all_story):
    _r_tot, _ = read_probe(_txt, _posB, {"trait": _trait_ids})
_b, _t = _r_base["trait"]["j_median"], _r_tot["trait"]["j_median"]
_factor = _t / _b if _b else float("inf")
print(f"total-mask degradation: trait rank {_b:.1f} -> {_t:.1f}  (x{_factor:.1f}, {len(_all_story)} tokens masked)")
assert _t > _b, (
    "TOTAL-MASK DEGRADATION FAILED: masking the entire story did not worsen the trait read at all. "
    "The mask fires but has no effect; any collapse measured below came from something else."
)
if _factor < 5:
    print(f"  ** WARNING: only x{_factor:.1f} degradation from masking the whole story. The mask has "
          f"less bite than expected — treat the ablation results with suspicion and investigate. **")
else:
    print("  -> the mask has teeth.")
print("\nfour instrument checks passed: attention removed, hook inert when empty, mask has teeth, "
      "and the semantic severance gate runs during the sweep.")
""".strip()))

cells.append(md(r"""
# The re-run sweep

Identical to Phase 3 except the scene probe now yields both gate inputs from one generation. Trait reads
are expected to **reproduce** Phase 3's — that is the replication half of this run.
""".strip()))

cells.append(code(r"""
INF_CONDS    = ["baseline", "scene", "control"]
DIRECT_CONDS = ["baseline", "trait_tok", "tracer_tok"]

abl_rows, gate_rows, perlayer_rows, top20_rows, direct_rows = [], [], [], [], []

for c in SURVIVOR_CHARS:
    name = c["name"]
    trait_ids, kw_ids = CHAR_GROUPS[name]["trait"], SCENE_KW_IDS[name]

    for d in DISTANCES_P3:
        is_dec = (d == DECISION_D)

        cueB = S.build_probe(c, "inferred", d, "cue_b")
        idsB = tokenizer(cueB, return_tensors="pt")["input_ids"][0].tolist()
        scene_B = find_span(idsB, c["inferred"])
        ctrl_B  = matched_filler_span(idsB, d, len(scene_B) if scene_B else None)
        posB = [len(idsB) - 1]

        sceneP = S.build_prefix(c, "inferred", d) + S.scene_probe(name)
        idsS = tokenizer(sceneP, return_tensors="pt")["input_ids"][0].tolist()
        scene_S = find_span(idsS, c["inferred"])
        ctrl_S  = matched_filler_span(idsS, d, len(scene_S) if scene_S else None)

        cols_B = {"baseline": [], "scene": scene_B or [], "control": ctrl_B or []}
        cols_S = {"baseline": [], "scene": scene_S or [], "control": ctrl_S or []}

        for cond in INF_CONDS:
            if cond == "control" and (ctrl_B is None or ctrl_S is None):
                continue
            with ablate(cols_B[cond]):
                resB, top20B = read_probe(cueB, posB, {"trait": trait_ids})
            cont, kw_rank = scene_probe_read(sceneP, cols_S[cond], kw_ids)

            abl_rows.append({
                "name": name, "trait": c["trait"], "valence": c["valence"], "arm": "inferred",
                "distance": d, "condition": cond, "is_decision": is_dec,
                "trait_j_median_rank": resB["trait"]["j_median"],
                "trait_logit_median_rank": resB["trait"]["logit_median"],
                "n_trait_ids": len(trait_ids),
                "scene_len_tokens": len(scene_B) if scene_B else 0,
                "ctrl_len_tokens": len(ctrl_B) if ctrl_B else 0,
            })
            gate_rows.append({
                "name": name, "distance": d, "condition": cond, "is_decision": is_dec,
                "continuation": cont,                 # -> PRIMARY gate (scored off-GPU)
                "scene_kw_rank_gen": kw_rank,         # -> SECONDARY gate (repaired, 12 positions)
                "n_scene_kw_ids": len(kw_ids), "gen_positions": GEN_N,
            })
            for L in BAND_LAYERS:
                perlayer_rows.append({"name": name, "arm": "inferred", "distance": d,
                                      "condition": cond, "measure": "trait", "lens": "jlens",
                                      "layer": L, "rank": resB["trait"]["per_layer_j"][L]})
                perlayer_rows.append({"name": name, "arm": "inferred", "distance": d,
                                      "condition": cond, "measure": "trait", "lens": "logit",
                                      "layer": L, "rank": resB["trait"]["per_layer_l"][L]})
            for L, toks in top20B.items():
                for rk, tok in enumerate(toks, 1):
                    top20_rows.append({"name": name, "arm": "inferred", "distance": d,
                                       "condition": cond, "layer": L, "rank": rk, "token": tok})

        cueBD = S.build_probe(c, "direct", d, "cue_b")
        idsD = tokenizer(cueBD, return_tensors="pt")["input_ids"][0].tolist()
        d_cols = {"baseline": [], "trait_tok": find_span(idsD, c["trait"]) or [],
                  "tracer_tok": find_span(idsD, c["tracer"]) or []}
        posD = [len(idsD) - 1]
        for cond in DIRECT_CONDS:
            with ablate(d_cols[cond]):
                resD, _ = read_probe(cueBD, posD, {"trait": trait_ids})
            direct_rows.append({
                "name": name, "trait": c["trait"], "arm": "direct", "distance": d,
                "condition": cond, "is_decision": is_dec,
                "trait_j_median_rank": resD["trait"]["j_median"],
                "trait_logit_median_rank": resD["trait"]["logit_median"],
                "masked_len_tokens": len(d_cols[cond]),
            })
    print(f"  ablated {name:<7} ({c['trait']}, {c['valence']})")

pd.DataFrame(abl_rows).to_csv("phase3b_ablation.csv", index=False)
pd.DataFrame(gate_rows).to_csv("phase3b_gate.csv", index=False)
pd.DataFrame(perlayer_rows).to_csv("phase3b_per_layer.csv", index=False)
pd.DataFrame(top20_rows).to_csv("phase3b_top20.csv", index=False)
pd.DataFrame(direct_rows).to_csv("phase3b_direct.csv", index=False)
print(f"\nwrote phase3b_ablation.csv ({len(abl_rows)}), phase3b_gate.csv ({len(gate_rows)}), "
      f"phase3b_per_layer.csv ({len(perlayer_rows)}), phase3b_top20.csv, phase3b_direct.csv")
""".strip()))

cells.append(md(r"""
## Preview — the secondary (rank) gate at d = 10, and the replication check

The PRIMARY gate is scored off-GPU in `analyze_phase3b.py` (it needs the stimuli to compute
`scene_overlap`). This preview shows the **repaired secondary rank gate** and the continuations, so a
wiring problem is visible before the data leaves the GPU. **No verdict is drawn here.**
""".strip()))

cells.append(code(r"""
g = pd.DataFrame(gate_rows); g = g[g["distance"] == DECISION_D]
a = pd.DataFrame(abl_rows);  a = a[(a["distance"] == DECISION_D)]
print(f"=== d={DECISION_D}: repaired rank gate (secondary) + continuations ===\n")
for name in [c["name"] for c in SURVIVOR_CHARS]:
    gg = g[g["name"] == name].set_index("condition")["scene_kw_rank_gen"]
    aa = a[a["name"] == name].set_index("condition")["trait_j_median_rank"]
    ki, kii, kiii = gg.get("baseline"), gg.get("scene"), gg.get("control")
    ok = (ki == ki and ki <= 50 and kii >= 5 * ki and kiii <= 2 * ki)
    print(f"{name:<7} kw(gen) i/ii/iii = {ki:>7.0f}/{kii:>7.0f}/{kiii:>7.0f}  secondary={'PASS' if ok else 'FAIL'}"
          f"   trait R i/ii/iii = {aa.get('baseline',float('nan')):>7.1f}/"
          f"{aa.get('scene',float('nan')):>7.1f}/{aa.get('control',float('nan')):>7.1f}")
    for cond in ["baseline", "scene", "control"]:
        row = g[(g["name"] == name) & (g["condition"] == cond)]
        if len(row):
            print(f"          {cond:<9}: {str(row.iloc[0]['continuation']).strip()[:80]}")
print("\nReplication check: trait numbers should closely match phase3_ablation.csv (same texts/masks).")
print("Registered expectation (§9): Elias FAILS the primary gate; Marek underpowered; other five held-scene.")
""".strip()))

cells.append(md(r"""
## Done — Phase 3b

Download: `phase3b_ablation.csv`, `phase3b_gate.csv`, `phase3b_direct.csv`, `phase3b_per_layer.csv`,
`phase3b_top20.csv` (individually, to dodge the multi-download block).

`analyze_phase3b.py` then applies, off-GPU: the **primary** continuation-scored gate, the **secondary**
repaired rank gate, the frozen §3 verdict behind whichever gates pass, the replication comparison
against Phase 3, and a check of the §9 registered expectations — including whether Elias failed as
predicted. A gate that certifies everything, Elias included, is reported as a gate that is too
permissive.
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

out = pathlib.Path(__file__).resolve().parent / "trait_persistence_v2_phase3b.ipynb"
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"wrote {out} — {len(cells)} cells")

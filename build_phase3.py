"""Generate trait_persistence_v2_phase3.ipynb — the Q3 KV-ablation (held latent vs held scene).

Phase 3 runs the intervention Phases 1–2 deliberately did not: it masks the attention keys/values of
the behavioural-scene tokens so a re-mention cue cannot attend back into the still-visible scene, then
re-probes the inferred trait. Phase 2 could only *watch* — with the scene in context the whole way, a
trait re-derived from the scene on each query is indistinguishable from one held as a standing latent.
Phase 3 separates them.

Scope and rules are FROZEN in `prediction.md`:
  * §3 Q3 decision rule (held-latent / held-scene / partial / underpowered-c) — used verbatim;
  * §7b implementation gate (attention-logit −inf masking; mask-check that makes a failed mask report
    NOT-RUN, never a null) — used verbatim;
  * §9 2026-07-21 "Q3 implementation pinned" — the concrete realisations (d=10 decision checkpoint,
    scene span = inferred sentence, matched control = closest-length filler, eager-attn hook mechanism,
    the scene-keyword gate thresholds 5.0/2.0/≤50, the symmetric direct-arm test). Committed pre-data.

Mirrors `build_phase2.py` / `build_phase2ext.py`: same lens machinery, band from `calibration.json`,
roster from `screening_roster.json`, both read from files never literals. The ONLY genuinely new code
is the KV-ablation hook, span location, and the two mask-check instruments.
"""
import json, pathlib

md = lambda s: {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(keepends=True)}
code = lambda s: {"cell_type": "code", "execution_count": None, "metadata": {},
                  "outputs": [], "source": s.strip("\n").splitlines(keepends=True)}

cells = []

cells.append(md(r"""
# Trait persistence v2 — Phase 3: the KV-ablation (Q3, held latent vs held scene)

**Pre-registered.** `prediction.md` and `trait_persistence_v2_stimuli.py` were committed *before* this
code. Nothing here may change a frozen criterion; anything that shows one was miscalibrated goes in
`prediction.md` §9 as a dated amendment, never a silent edit. Q3's decision rule (§3) and its
implementation gate (§7b) are used **verbatim**; the concrete realisations are pinned in §9
(2026-07-21, "Q3 implementation pinned"), also committed before any ablation number existed.

## What this run does

On the **inferred** arm, at the re-mention checkpoint, mask the attention keys/values of the
**behavioural-scene tokens** and re-probe the trait:

- **(i) baseline** — no mask.
- **(ii) scene ablation** — mask the inferred trigger sentence's tokens (attention logits → −∞ toward
  them, every layer and head).
- **(iii) control ablation** — mask a matched-length filler sentence instead.

Let `R_i, R_ii, R_iii` be the inferred-arm trait best-lexicon band-median rank under the three
conditions at **d = 10, Cue B** (the pinned decision checkpoint, §9). Then, **frozen §3**:

- **held latent (a):** `R_ii ≤ 50` **and** `R_ii/R_iii ≤ 2.0` — masking the scene costs little more
  than masking an equally sized irrelevant span → a trait latent lives outside the scene tokens.
- **held scene (b):** `R_ii/R_iii ≥ 5.0` — scene masking specifically destroys retrieval → the trait
  is recomputed from the cached scene on demand.
- between 2.0 and 5.0 → partial; `R_i > 50` → **underpowered (c)**, declared per-character *before* any
  ablation number.

**The gate that protects this (frozen §7b).** A failed mask produces a collapse that looks exactly like
outcome (b) — the more surprising finding. So Q3 is reportable **only if the mask-check passes**: under
scene ablation the model can no longer report "what did NAME do?", under control ablation it still can.
**Gate fail → the character's Q3 is `not-run`, never a null.** This notebook computes both a mechanistic
check (attention to masked columns ≈ 0) and the semantic gate (scene-keyword recovery); the formal
verdict is applied off-GPU in `analyze_phase3.py`.

## Also run (walled off, no §3 verdict — §9 researcher calls)

- The ablation at **d ∈ {0,1,2,4,7,30}** as exploratory context; the d = 30 cell exists to check the
  d = 10 verdict is not distance-specific. (d = 30 reuses the §7a extension filler and the
  `max_seq_len` fix.)
- The **symmetric direct-arm test**: mask the stated **trait-word** token (and the **tracer** token as a
  matched single-token control) and measure the drop in direct-arm retrieval — "how much of stated-arm
  retrieval is the literal symbol" (spec D5). Descriptive; not part of the §3 verdict.

**Before running:** `Runtime → Change runtime type → T4 GPU`. Gemma-3-4B-IT is gated: accept the license
at https://huggingface.co/google/gemma-3-4b-it and store an HF token as a Colab secret named `HF_token`
(key icon). Upload `trait_persistence_v2_stimuli.py` **and** the Phase 1 `phase1/` folder (or clone the
repo — recommended).
""".strip()))

cells.append(code(r"""
# jlens pinned to the SAME commit as v1 / Phase 1 / Phase 2 — instrument byte-identical across the series.
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
## Stimuli + Phase 1 outputs (band and roster read from files, never retyped)
""".strip()))

cells.append(code(r"""
import os, sys, json

if not os.path.exists("trait_persistence_v2_stimuli.py"):
    raise FileNotFoundError(
        "trait_persistence_v2_stimuli.py not found. Upload it or clone the repo. Phase 3 needs the "
        "version carrying SCENE_KEYWORDS / scene_probe (added for the §7b gate) AND the 30-sentence "
        "filler (for the d=30 exploratory cell)."
    )
import trait_persistence_v2_stimuli as S

# Guard: this must be the Q3-ready stimuli file, not an older copy.
if not hasattr(S, "SCENE_KEYWORDS") or not hasattr(S, "scene_probe"):
    raise RuntimeError("stimuli file lacks SCENE_KEYWORDS / scene_probe — clone the current repo.")
if len(S.FILLER_SENTENCES) < 30:
    raise RuntimeError(f"stimuli filler has {len(S.FILLER_SENTENCES)} < 30 sentences; d=30 would be cut.")


def _find(fname):
    for p in (os.path.join("phase1", fname), fname):
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"{fname} not found in phase1/ or cwd. Upload the Phase 1 outputs.")


with open(_find("calibration.json")) as f:
    CALIB = json.load(f)
with open(_find("screening_roster.json")) as f:
    ROSTER = json.load(f)

BAND_LAYERS = [int(l) for l in CALIB["band_layers"]]
SURVIVORS   = list(ROSTER["survivors"])

# Phase 3 distances (§9): decision at d=10; the rest are walled-off exploratory context.
DISTANCES_P3 = [0, 1, 2, 4, 7, 10, 30]
DECISION_D   = 10

print(f"band: layers {BAND_LAYERS[0]}..{BAND_LAYERS[-1]} ({len(BAND_LAYERS)} layers)")
print(f"roster: {len(SURVIVORS)} survivors: {SURVIVORS}")
print(f"Phase 3 distances: {DISTANCES_P3}   decision checkpoint: d={DECISION_D}, Cue B")
if DECISION_D not in DISTANCES_P3:
    raise RuntimeError("decision distance not in the swept distances.")
""".strip()))

cells.append(md(r"""
## Load model and lens — **eager attention** (required by the §7b mask mechanism)

The §7b/§9 mask is an additive −∞ on attention logits; that needs an attention implementation that
honours an additive bias, so the model is loaded `attn_implementation="eager"`. This is a **requirement
of the pinned mechanism, not a deviation from it** (V-zeroing, the deviation clause, is not used). The
resolved attention implementation is printed so a silent fallback is visible.
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
assert CALIB["n_layers"] == N_LAYERS, "calibration.json is for a different model — do not proceed."
assert BAND_LAYERS[0] >= ALL_LAYERS[0] and BAND_LAYERS[-1] <= ALL_LAYERS[-1]

# Confirm eager actually took (a silent SDPA/flash fallback would make the additive mask a no-op and
# the mask-check would then fail loudly downstream — but catch it here anyway).
_attn_impl = getattr(hf_model.config, "_attn_implementation", None)
print(f"n_layers={N_LAYERS}; band OK; attn_implementation = {_attn_impl!r}")
if _attn_impl not in ("eager", None):
    print(f"WARNING: attn_implementation is {_attn_impl!r}, not 'eager'. The additive-mask hook may be "
          f"a no-op; the mechanistic mask check below is the authority — do not proceed if it fails.")
""".strip()))

cells.append(md(r"""
### Locate the decoder layers (defensive — Gemma-3-4B-IT is the multimodal build)

The text stack is nested under a `language_model` on this checkpoint (the same reason Phase 2 resolved
the final norm defensively). Resolve the `self_attn`-bearing decoder `ModuleList` by trying the known
paths; fail loudly rather than guess.
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
    raise RuntimeError(
        "Could not locate the decoder layers (a ModuleList whose blocks have .self_attn). "
        "Print `hf_model` and set DECODER_LAYERS by hand. Do NOT guess."
    )
print(f"decoder layers: hf_model.{_lp}  ({len(DECODER_LAYERS)} blocks, "
      f"self_attn = {type(DECODER_LAYERS[0].self_attn).__name__})")
assert len(DECODER_LAYERS) == N_LAYERS, (
    f"found {len(DECODER_LAYERS)} decoder blocks but n_layers={N_LAYERS} — wrong module."
)
""".strip()))

cells.append(md(r"""
### The KV-ablation hook (§7b preferred mechanism, realised literally)

A forward pre-hook on **every** `self_attn` clones the additive 4-D attention mask it is handed and
sets the masked **key columns** to the dtype minimum, for all query rows. The `[batch, 1, q, kv]` mask
broadcasts over heads, so this is "attention logits → −∞ toward the span, at every layer and head".
V is untouched — **not** V-zeroing, so the §7b deviation clause does not apply. `ablate([])` is a
no-op (baseline). The hooks are active during **both** lens reads because both share `hf_model`.
""".strip()))

cells.append(code(r"""
def _mask_hook(cols):
    '''Pre-hook factory: add -inf to attention logits at key columns `cols`, every layer/head.'''
    cols_t = torch.as_tensor(sorted(set(cols)), dtype=torch.long)

    def hook(module, args, kwargs):
        am, idx = kwargs.get("attention_mask", None), None
        if am is None:                                   # some versions pass it positionally
            for i, a in enumerate(args):
                if torch.is_tensor(a) and a.dim() == 4 and a.is_floating_point():
                    am, idx = a, i
                    break
        if am is None:
            raise RuntimeError(
                "No additive 4-D attention_mask reached self_attn — the eager additive-mask path is "
                "not active. The KV-ablation cannot be applied this way; do not trust any ablation read."
            )
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
def ablate(cols):
    '''Mask attention toward key positions `cols` (a list) for the duration of the block. [] = baseline.'''
    handles = []
    if cols:
        h = _mask_hook(cols)
        for blk in DECODER_LAYERS:
            handles.append(blk.self_attn.register_forward_pre_hook(h, with_kwargs=True))
    try:
        yield
    finally:
        for hd in handles:
            hd.remove()
""".strip()))

cells.append(md(r"""
### Logit-lens wiring + validation (verbatim from Phase 2; Q5-style robustness rides along)
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

_ptxt = "The Eiffel Tower stands in the French capital city of"
_enc = tokenizer(_ptxt, return_tensors="pt").to(hf_model.device)
with torch.no_grad():
    _out = hf_model(**_enc, output_hidden_states=True)
_dec = lambda ids: [tokenizer.decode([i]) for i in ids]
_real = _dec(_out.logits[0, -1].float().topk(8).indices.tolist())
_llf  = _dec(LM_HEAD(_out.hidden_states[-1][0, -1].unsqueeze(0))[0].float().topk(8).indices.tolist())
print("TOP-8 SETS MATCH:", set(_real) == set(_llf), "  <-- must be True")
assert set(_real) == set(_llf), "logit-lens FAILED validation — fix before trusting any logit number."
print("logit channel validated.")
""".strip()))

cells.append(md(r"""
## Token ids: trait lexicons, adjective, tracer, scene keywords

Same single-token (leading-space) check as Phases 1–2. Scene keywords (`S.SCENE_KEYWORDS`, the §7b gate
targets) are resolved the same way; multi-token entries are dropped and logged. A character whose
surviving scene-keyword set is empty **cannot be gated** and its Q3 is `not-run` (recorded).
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
    trait_ids = list(LEXICON_IDS[c["trait"]].values())
    CHAR_GROUPS[c["name"]] = {"trait": trait_ids}
    kw_kept = [(w, single_token_id(w)) for w in S.SCENE_KEYWORDS[c["name"]]]
    kw_ids  = [t for _, t in kw_kept if t is not None]
    kw_drop = [w for w, t in kw_kept if t is None]
    SCENE_KW_IDS[c["name"]] = kw_ids
    warn = "  <-- NO scene keywords survive: Q3 NOT-RUN for this char" if not kw_ids else ""
    print(f"{c['name']:<7} {c['trait']:<10} lexicon={len(trait_ids):>2}  "
          f"scene_kw={len(kw_ids)}/{len(S.SCENE_KEYWORDS[c['name']])}"
          f"{' (dropped ' + ','.join(kw_drop) + ')' if kw_drop else ''}{warn}")
""".strip()))

cells.append(md(r"""
## Span location — scene, matched-filler control, trait-word, tracer-word

All masks target a **token span** located inside the full probe text by matching the leading-space
encoding of the sentence/word (the same trick Cue A uses to find the name). The **matched control span**
is the filler sentence present at that distance whose token length is nearest the scene span's (ties →
earliest); at d = 0 there is no filler, so the control condition is undefined and skipped there.
""".strip()))

cells.append(code(r"""
def find_span(full_ids, text_piece):
    '''Token positions of `text_piece` inside full_ids (leading-space form preferred). None if absent.'''
    for pref in (" ", ""):
        sub = tokenizer.encode(pref + text_piece, add_special_tokens=False)
        if not sub:
            continue
        for i in range(len(full_ids) - len(sub) + 1):
            if full_ids[i:i + len(sub)] == sub:
                return list(range(i, i + len(sub)))
    return None


def matched_filler_span(full_ids, distance, scene_len):
    '''Closest-token-length filler sentence present at this distance; ties break to the earliest.'''
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
""".strip()))

cells.append(md(r"""
## Read machinery (Phase 2's, plus the model-output rank the gate needs)

One J-lens pass + one HF pass per probe; every token group scored off the same logits. `read_probe`
also returns, when asked, the **model's own next-token best rank** for a group at a position — that is
the "can the model say it?" quantity the §7b scene-report gate is decided on. `max_seq_len=2048` keeps
the d = 30 sequences (~600 tokens) from being silently truncated (the Phase-2-extension fix).
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


def read_probe(text, positions, id_groups, model_out_pos=None):
    '''Both lenses (band ranks) + optional model-output next-token rank. Ablation hooks, if any, are
    active for the caller (wrap the call in `with ablate(cols):`).'''
    _n = tokenizer(text, return_tensors="pt")["input_ids"].shape[1]
    assert _n <= 2048, f"sequence is {_n} tokens; raise max_seq_len above it"
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

    model_out = {}
    if model_out_pos is not None:
        row = out.logits[0, model_out_pos].float()
        for g, ids in id_groups.items():
            if ids:
                model_out[g] = min(int((row > row[t]).sum().item()) + 1 for t in ids)

    top20 = {L: [tokenizer.decode([t]) for t in jl[L][-1].topk(20).indices] for L in BAND_LAYERS}
    del jl_raw, jl, out, hs, ll
    torch.cuda.empty_cache()
    return res, model_out, top20


def greedy_cont(text, cols, n=12):
    '''Short greedy continuation under the mask (use_cache=False so the fixed span stays masked each
    step). Human-readable record for the gate; the decision uses ranks, not this string.'''
    enc = tokenizer(text, return_tensors="pt").to(hf_model.device)
    try:
        with ablate(cols or []):
            with torch.no_grad():
                gen = hf_model.generate(**enc, max_new_tokens=n, do_sample=False, use_cache=False)
        return tokenizer.decode(gen[0][enc["input_ids"].shape[1]:], skip_special_tokens=True)
    except Exception as e:
        return f"(continuation failed: {e})"
""".strip()))

cells.append(md(r"""
## Mechanistic mask check — does attention to the masked span actually go to zero?

Independent of any meaning: one `output_attentions=True` pass with the scene mask active must show
attention probability from **every** query position to **every** masked key column ≈ 0 across all band
layers and heads; without the mask it is clearly non-zero. This proves the "logits → −∞" lever works
before a single trait number is read. (This is the mechanistic half of the §7b gate; the semantic half
— scene-keyword recovery — is measured during the sweep and decided in `analyze_phase3.py`.)
""".strip()))

cells.append(code(r"""
def attn_to_cols_max(text, cols):
    '''Max attention probability landing on key columns `cols`, over band layers/heads/queries.'''
    enc = tokenizer(text, return_tensors="pt").to(hf_model.device)
    with torch.no_grad():
        out = hf_model(**enc, output_attentions=True)
    n = enc["input_ids"].shape[1]
    c = [x for x in cols if x < n]
    mx = 0.0
    for L in BAND_LAYERS:
        a = out.attentions[L][0]           # [heads, q, kv]
        mx = max(mx, float(a[:, :, c].max().item()))
    del out
    torch.cuda.empty_cache()
    return mx

# Validate on one example: Maria / inferred / d = DECISION_D / Cue B, scene span.
_c = S.by_name("Maria")
_txt = S.build_probe(_c, "inferred", DECISION_D, "cue_b")
_ids = tokenizer(_txt, return_tensors="pt")["input_ids"][0].tolist()
_scene = find_span(_ids, _c["inferred"])
assert _scene is not None, "scene span not found for the mechanistic check — investigate tokenization."
_base = attn_to_cols_max(_txt, _scene)
with ablate(_scene):
    _masked = attn_to_cols_max(_txt, _scene)
print(f"Maria d={DECISION_D} scene span = {len(_scene)} tokens (positions {_scene[0]}..{_scene[-1]})")
print(f"max attention to scene columns  — baseline: {_base:.4f}   masked: {_masked:.2e}")
assert _masked < 1e-6, (
    f"MASK DID NOT TAKE: attention to masked columns is {_masked:.2e}, not ~0. The eager additive-mask "
    f"hook is not working on this build. Do NOT trust any ablation read; fix the hook first."
)
print("mechanistic mask check PASSED — attention to the masked span is ~0 at every band layer/head.")
""".strip()))

cells.append(md(r"""
# The ablation sweep

For each survivor × distance ∈ {0,1,2,4,7,10,30}:

**Inferred arm** — under conditions {baseline, scene, control} (control skipped at d = 0):
- **Cue B** → trait best-lexicon band rank (the §3 measure, `R`).
- **Scene probe** (`"What did NAME do? NAME"`) → scene-keyword rank, incl. the **model-output** rank
  the gate is decided on, plus a short greedy continuation for the human-readable record.

**Direct arm** (symmetric test) — Cue B trait rank under {baseline, trait-word masked, tracer-word
masked}.

d = 10 rows are flagged `is_decision`. Everything is stored; the frozen §3 verdict and the §7b gate are
applied off-GPU in `analyze_phase3.py`.
""".strip()))

cells.append(code(r"""
INF_CONDS    = ["baseline", "scene", "control"]
DIRECT_CONDS = ["baseline", "trait_tok", "tracer_tok"]

abl_rows, maskcheck_rows, perlayer_rows, top20_rows, cont_rows, direct_rows = [], [], [], [], [], []

for c in SURVIVOR_CHARS:
    name = c["name"]
    trait_ids = CHAR_GROUPS[name]["trait"]
    scene_kw_ids = SCENE_KW_IDS[name]

    for d in DISTANCES_P3:
        is_dec = (d == DECISION_D)

        # ----- INFERRED ARM -----
        cueB = S.build_probe(c, "inferred", d, "cue_b")
        idsB = tokenizer(cueB, return_tensors="pt")["input_ids"][0].tolist()
        scene_B = find_span(idsB, c["inferred"])
        ctrl_B  = matched_filler_span(idsB, d, len(scene_B) if scene_B else None)
        posB = [len(idsB) - 1]

        sceneP = S.build_prefix(c, "inferred", d) + S.scene_probe(name)
        idsS = tokenizer(sceneP, return_tensors="pt")["input_ids"][0].tolist()
        scene_S = find_span(idsS, c["inferred"])
        ctrl_S  = matched_filler_span(idsS, d, len(scene_S) if scene_S else None)
        posS = [len(idsS) - 1]

        cols_B = {"baseline": [], "scene": scene_B or [], "control": ctrl_B or []}
        cols_S = {"baseline": [], "scene": scene_S or [], "control": ctrl_S or []}

        for cond in INF_CONDS:
            if cond == "control" and (ctrl_B is None or ctrl_S is None):
                continue                                  # d=0: no filler to match
            with ablate(cols_B[cond]):
                resB, _, top20B = read_probe(cueB, posB, {"trait": trait_ids})
            with ablate(cols_S[cond]):
                resS, moS, _ = read_probe(sceneP, posS, {"scene_kw": scene_kw_ids},
                                          model_out_pos=posS[-1])
            cont = greedy_cont(sceneP, cols_S[cond])

            trait_j = resB["trait"]["j_median"] if "trait" in resB else float("nan")
            trait_l = resB["trait"]["logit_median"] if "trait" in resB else float("nan")
            kw_out  = moS.get("scene_kw", float("nan")) if scene_kw_ids else float("nan")
            kw_j    = resS["scene_kw"]["j_median"] if "scene_kw" in resS else float("nan")

            abl_rows.append({
                "name": name, "trait": c["trait"], "valence": c["valence"], "arm": "inferred",
                "distance": d, "condition": cond, "is_decision": is_dec,
                "trait_j_median_rank": trait_j, "trait_logit_median_rank": trait_l,
                "n_trait_ids": len(trait_ids),
                "scene_len_tokens": len(scene_B) if scene_B else 0,
                "ctrl_len_tokens": len(ctrl_B) if ctrl_B else 0,
            })
            maskcheck_rows.append({
                "name": name, "distance": d, "condition": cond, "is_decision": is_dec,
                "scene_kw_out_rank": kw_out, "scene_kw_j_median_rank": kw_j,
                "n_scene_kw_ids": len(scene_kw_ids),
            })
            cont_rows.append({"name": name, "distance": d, "condition": cond,
                              "continuation": cont, "probe": sceneP})
            if "trait" in resB:
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

        # ----- DIRECT ARM (symmetric test) -----
        cueBD = S.build_probe(c, "direct", d, "cue_b")
        idsD = tokenizer(cueBD, return_tensors="pt")["input_ids"][0].tolist()
        trait_word = find_span(idsD, c["trait"])
        tracer_word = find_span(idsD, c["tracer"])
        posD = [len(idsD) - 1]
        d_cols = {"baseline": [], "trait_tok": trait_word or [], "tracer_tok": tracer_word or []}
        for cond in DIRECT_CONDS:
            with ablate(d_cols[cond]):
                resD, _, _ = read_probe(cueBD, posD, {"trait": trait_ids})
            direct_rows.append({
                "name": name, "trait": c["trait"], "arm": "direct", "distance": d,
                "condition": cond, "is_decision": is_dec,
                "trait_j_median_rank": resD["trait"]["j_median"] if "trait" in resD else float("nan"),
                "trait_logit_median_rank": resD["trait"]["logit_median"] if "trait" in resD else float("nan"),
                "masked_len_tokens": len(d_cols[cond]),
            })
    print(f"  ablated {name:<7} ({c['trait']}, {c['valence']})")

abl_df = pd.DataFrame(abl_rows)
abl_df.to_csv("phase3_ablation.csv", index=False)
pd.DataFrame(maskcheck_rows).to_csv("phase3_maskcheck.csv", index=False)
pd.DataFrame(perlayer_rows).to_csv("phase3_per_layer.csv", index=False)
pd.DataFrame(top20_rows).to_csv("phase3_top20.csv", index=False)
pd.DataFrame(cont_rows).to_csv("phase3_scene_continuations.csv", index=False)
pd.DataFrame(direct_rows).to_csv("phase3_direct.csv", index=False)
print(f"\nwrote phase3_ablation.csv ({len(abl_df)} rows), phase3_maskcheck.csv "
      f"({len(maskcheck_rows)} rows), phase3_per_layer.csv ({len(perlayer_rows)} rows), "
      f"phase3_top20.csv, phase3_scene_continuations.csv, phase3_direct.csv")
""".strip()))

cells.append(md(r"""
## In-notebook preview — the §7b gate and the §3 ratios at d = 10 (descriptive; not the verdict)

The formal verdict is `analyze_phase3.py`, off-GPU, against the frozen criteria. This cell only shows
the decision-checkpoint numbers so a gross wiring problem is visible before the data leaves the GPU.
For each character at d = 10: the mask-check (scene-keyword model-output rank under the three
conditions, gate thresholds 5.0/2.0/≤50 from §9) and the §3 trait ratios `R_ii/R_iii`, `R_ii ≤ 50`.
**No conclusion drawn here.**
""".strip()))

cells.append(code(r"""
dec_a = abl_df[(abl_df["distance"] == DECISION_D) & (abl_df["arm"] == "inferred")]
dec_m = pd.DataFrame(maskcheck_rows)
dec_m = dec_m[dec_m["distance"] == DECISION_D]

print(f"=== d={DECISION_D} decision checkpoint (Cue B). Preview only — verdict is analyze_phase3.py ===\n")
for name in [c["name"] for c in SURVIVOR_CHARS]:
    a = dec_a[dec_a["name"] == name].set_index("condition")["trait_j_median_rank"]
    m = dec_m[dec_m["name"] == name].set_index("condition")["scene_kw_out_rank"]
    Ri  = a.get("baseline", float("nan"))
    Rii = a.get("scene", float("nan"))
    Riii = a.get("control", float("nan"))
    ratio = (Rii / Riii) if (Riii and Riii == Riii and Riii != 0) else float("nan")
    kw_i, kw_ii, kw_iii = m.get("baseline", float("nan")), m.get("scene", float("nan")), m.get("control", float("nan"))
    gate_removed = (kw_ii >= 5.0 * kw_i) if kw_i == kw_i and kw_i > 0 else False
    gate_spared  = (kw_iii <= 2.0 * kw_i) if kw_i == kw_i and kw_i > 0 else False
    gate_base_ok = (kw_i == kw_i and kw_i <= 50)
    gate = "PASS" if (gate_base_ok and gate_removed and gate_spared) else "FAIL -> Q3 not-run"
    print(f"{name:<7} trait R  i/ii/iii = {Ri:>7.1f}/{Rii:>7.1f}/{Riii:>7.1f}  "
          f"R_ii/R_iii={ratio:>6.2f}  R_ii<=50={Rii<=50}   | "
          f"scene_kw i/ii/iii={kw_i:>6.0f}/{kw_ii:>6.0f}/{kw_iii:>6.0f}  gate {gate}")
print("\nReminder: descriptive preview. The frozen §3 verdict (held-latent / held-scene / partial / "
      "underpowered-c) and the §7b gate run in analyze_phase3.py. A FAIL gate => that character is "
      "reported not-run, never a null.")
""".strip()))

cells.append(md(r"""
## Done — Phase 3

Download and send back **all** of these (download individually to dodge the multi-download block):

| file | what it is |
|---|---|
| `phase3_ablation.csv` | inferred-arm trait rank under {baseline, scene, control}, every distance — the §3 measure |
| `phase3_maskcheck.csv` | scene-keyword rank (model-output + J-lens) under the three conditions — the §7b gate |
| `phase3_direct.csv` | direct-arm symmetric test (trait-word / tracer-word masked) |
| `phase3_per_layer.csv` | per-layer trait ranks (repeats v1's E4 sub-band check) |
| `phase3_top20.csv` | top-20 J-lens vocabulary at every inferred Cue B checkpoint (post-hoc audit) |
| `phase3_scene_continuations.csv` | greedy "what did NAME do?" continuations (human-readable gate record) |

**Off-GPU analysis (`analyze_phase3.py`), against the frozen criteria:**
- **§7b gate first, per character:** at d = 10, is the scene-report removed under scene-masking
  (`kw_ii/kw_i ≥ 5`) and spared under control-masking (`kw_iii/kw_i ≤ 2`), with a reportable baseline
  (`kw_i ≤ 50`)? **Gate fail → that character's Q3 is `not-run`, never a null.**
- **§3 verdict** (gated characters only): `R_i>50` → underpowered (c); else held-latent (a) if
  `R_ii≤50 and R_ii/R_iii≤2`, held-scene (b) if `R_ii/R_iii≥5`, else partial.
- **d = 30 exploratory** re-run of the same logic to check the verdict is not distance-specific;
  carries no §3 verdict (§9).
- **Direct-arm** drop under trait-word masking vs tracer-word masking (descriptive).

**Honest caveats to carry into the write-up:** n = 7, single-character medians draggable by one item
(Elias was the weak/anomalous cue in Phase 2, watch him here); the gate mechanism is the load-bearing
guard, so any character whose mask-check fails is `not-run`, not evidence for either outcome.
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

out = pathlib.Path(__file__).resolve().parent / "trait_persistence_v2_phase3.ipynb"
out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"wrote {out} — {len(cells)} cells")

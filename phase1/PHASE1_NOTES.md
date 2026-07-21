# Phase 1 results — band calibration + stimulus screening

**Run 2026-07-21, Colab T4.** This records what Phase 1 produced and every decision taken from it.
Phase 1 is instrument-building and screening only — it calibrates the read band and gates the
character roster. **It tests no Q1/Q2/Q5 hypothesis**; all criteria were frozen in
[`../prediction.md`](../prediction.md) before this run. Screening reads are exploratory by
definition (prediction.md §D0). Raw outputs live beside this file in `phase1/`.

## Environment / provenance

- Model `google/gemma-3-4b-it`; lens `neuronpedia/jacobian-lens`, file
  `gemma-3-4b-it/jlens/Salesforce-wikitext/gemma-3-4b-it_jacobian_lens.pt`; `jlens` pinned
  `581d398613e5602a5af361e1c34d3a92ea82ba8e` (v1's pin — same instrument).
- `n_layers = 34`; lens-readable layers `0..32` (final layer has no fitted Jacobian).
- Logit-lens final norm resolved at `hf_model.model.language_model.norm` (the second fallback path;
  transformers nests Gemma-3's norm under `language_model`). LM head at `hf_model.lm_head`.
- **TODO — fill exact `torch` / `transformers` versions** from the run's model-load cell output
  (not captured in this session). The norm path implies a transformers 5.12.x-style layout.
- Calibration corpus: `Salesforce/wikitext` wikitext-103-raw-v1 [test], 20 docs, first 5 tokens
  skipped (high-norm artifact).

## 1. Logit-lens validation — PASSED

The logit wiring is ours (not pre-validated like the J-lens), so it was checked in-flight, using the
corrected logic ported from the sibling project `j-lens-self-recruitment-test` (same model/lens, which
once shipped this with a silent double-norm bug):

- **Check (1) — final hidden state vs. model's own next token:** `TOP-8 SETS MATCH: True` **and**
  `EXACT ORDER MATCH: True`; `max|lens − real| = 0.0625` (one bf16 ULP at this logit magnitude →
  numerically identical). This top-8 is bit-for-bit the value the sibling project logged on this
  stack. No `FINAL_NORM` applied here — `hs[-1]` is already normed; applying it twice is the failure
  mode being guarded against.
- **Check (2) — known-answer trajectory** (`"…French capital city of"`): ` Paris` absent early
  (junk through layer 12), emerges at layer 24, dominant 28–32. Classic logit-lens sharpening on the
  readout's real path (`LM_HEAD(FINAL_NORM(raw residual))`).

**Verdict: the logit channel is trusted.** Q5 rests on a validated instrument.

## 2. Band calibration — OVERRIDE to layers 13–26

**Final band: layers 13–26 (depth 0.394–0.788), 14 layers.** Written to `calibration.json`; Phase 2
reads the band from that file.

**The auto-heuristic was overridden, and this is the important part.** It proposed `layers 0..26`,
putting the **lower edge at layer 0** — an artifact. The kurtosis of the lens-logit distribution
carries a high-norm spike in the earliest layers (layer 0 = 1.476), drops to a mid-plateau trough
(layer 13 = 0.680, the global min), then does its *real* rise into concept-sharpening (peak layer 25 =
1.941). The heuristic's "first layer above 25% of the kurtosis range" therefore fires at the layer-0
spike, not the genuine rise. The logit-lens trajectory (§1, check 2) independently shows layers 0–12
are uninterpretable, confirming a band starting at layer 0 is wrong.

Lower edge set to **13** on triangulated evidence, not the kurtosis rise alone:

| source | lower edge |
|---|---|
| Workspace paper ("empty" before ~38% depth) | layer ~13 (0.38) |
| v1's inherited band | layer 12 (0.35) |
| This run's ` Paris` logit-lens trajectory (junk ≤12, `cities` at 16, `Paris` at 24) | layer ~13–16 |
| This run's kurtosis rise (concept-sharpening onset) — the lone late signal | layer ~22 (0.66) |

Three of four point to ~13–16; the band was set to 13, its lower edge landing exactly at the kurtosis
trough and rising through the band to the kurtosis peak. Decision owned by N., recorded here.

**Finding: v1's inherited 0.35–0.90 was too generous at the top.** Next-token agreement (the collapse
metric) at our upper edge, **layer 26 (0.788), is 0.34** — 34% of positions where the lens top-1 is
already the model's literal next token. At **v1's ~0.90 upper edge (layer 30) it is 0.58.** So v1 read
its top layers well into next-token collapse (~58%), where the readout is increasingly *the output
distribution* rather than *about the content*. v1's lower edge (~layer 12, agreement 0.003) was fine;
the over-reach was at the top. v2's tighter 0.788 ceiling is deliberate.

## 3. Lexicon single-token report — all traits powered

Every trait cleared the ≥4 single-token threshold (prediction.md §6); **no underpowered lexicons.**
Thinnest: `lazy` 5/8, `cowardly` 5/8, `greedy` 6/9. Full survival in `tokenizer_check.csv`.

## 4. Tracer single-token check — 3 fail, 2 of them matter

Three tracers are **not single-token** in the Gemma tokenizer, so Q2 (the token-echo control) cannot
run for those characters as declared: `stapler` (Priya), `crowbar` (Elias), `trowel` (Greta).

- **Priya failed screening (§5), so her tracer is moot.** Of the 7 survivors, only **Elias** and
  **Greta** are affected.
- **Done (2026-07-21): swapped and re-registered** in `prediction.md §9` — `Elias: crowbar → bucket`,
  `Greta: trowel → mirror` (neutral objects, no tie to the character's trait/occupation/scene).
  `trait_persistence_v2_stimuli.py` updated. **Confirmed single-token on the real gemma-3-4b-it
  tokenizer (2026-07-21):** `bucket` id 24211, `mirror` id 14701. Priya's `stapler` left unchanged (out of roster).
  Tracers do not enter screening, so this changes nothing about §5.

## 5. Screening — 7/10 pass; run proceeds on the survivors

Gate (frozen, prediction.md §3): `R(inferred,0) ≤ 200` **and** `R(control,0)/R(inferred,0) ≥ 5`,
under Cue B, best-lexicon-rank median over the calibrated band. **7 of 10 passed — above the §3 halt
floor of 5, so the run does not halt.** Full table in `screening_gate.csv`; roster in
`screening_roster.json`.

**Survivors (7):** Maria (generous +), Nadia (brave +), Simon (curious +), Elias (loyal +),
Greta (dishonest −), Bruno (lazy −), Marek (cowardly −).

**Valence: 4 positive / 3 negative** — short of the 4:4 target for a roster of eight. Per
prediction.md §5 this triggers the pre-registered contingency: **report the imbalance, run Phase 2 on
the survivors, do not back-fill replacements chosen after seeing data.** No valence dropped below the
notebook's frozen tolerance (min ≥ 3), so no `FLAG` fired. Final roster size for Phase 2: **n = 7**
(the Q1 Wilcoxon, already weak at n=8, is weaker still — descriptive reporting applies if it does not
clear, per §3).

**Failures (3) — screening working as designed (v1's F5/"Peter" problem, caught pre-sweep):**

| char | trait | inferred R | control R | ratio | why it failed |
|---|---|---|---|---|---|
| Viktor | cruel | 174.5 | 568.0 | 3.26 | inferred readable (≤200) but control leaked cruelty-adjacent content → ratio < 5 |
| Otto | greedy | 251.0 | 551.5 | 2.20 | weak inference (>200) **and** ratio < 5 — "never let a coin leave his hand" underspecified greed |
| Priya | patient | 165.5 | 227.5 | 1.37 | control not patience-neutral — a long afternoon at the ticket window reads as patient too |

## 6. Logit positive-control (§4a) — read this before any Q5/logit-null claim in Phase 2

Established here and nowhere else (prediction.md §4a): the logit lens must detect the d0 inferred
signal (logit inferred median ≤ 5× the J-lens value) for that character, or a later "the logit lens
saw nothing" claim is **void** — indistinguishable from an instrument blind at these depths.

**Among the 7 survivors:**

- **PASS (logit nulls interpretable): Nadia, Elias, Greta** (3).
- **FAIL (logit nulls NOT interpretable): Maria, Simon, Bruno, Marek** (4).

So for Q5, only **3 of 7** survivors can support a "J-lens sees it, logit lens doesn't" reading. Note
**Bruno** especially: J-lens inferred rank **3** vs. logit inferred **177** — a dramatic J≫logit
divergence that *looks* like the Q5 signal, but Bruno **failed** the positive control, so under the
frozen rule its logit null is uninterpretable. Flagged for Phase 2, not to be over-read (per §4a,
logit = J-lens with J=I, so divergence is expected, not a discovery).

## 7. What Phase 2 inherits

- **Band:** layers 13–26, from `calibration.json` (never a literal).
- **Roster:** the 7 survivors above (4+/3−), no back-fill.
- **Tracers:** swap Elias→bucket, Greta→mirror and re-register (§9 amendment) before the Q2 stream.
- **Q5 constraint:** logit nulls interpretable only for Nadia, Elias, Greta.
- **Measures/cues:** unchanged from prediction.md §3/§7 (Cue A/B × d∈{0,1,2,4,7,10}, arm-vs-own-control).

## 8. Open caveats

- **Single run — determinism not re-verified for v2.** The sibling project established bit-exact
  reproducibility on this exact model/lens/T4, so each n=1 read is expected to be an *exact*
  measurement (no GPU jitter), but this was not re-run for v2's stimuli. A one-Colab-run repeat would
  confirm it cheaply.
- **Band override is a human judgement**, recorded in §2 with its reasoning and the dissenting signal
  (this run's kurtosis rise would argue for a later lower edge, ~22). The plots in
  `calibration_curves.png` are the evidence; the override is not a silent edit.
- **Screening reads are exploratory** and gate only the roster; they are not evidence about Q1/Q2/Q5.

# Phase 3 results — the KV-ablation (Q3): held latent vs held scene

> **This run was superseded the same day — but not corrected.** Its gate turned out to be a poor
> realisation of the §7b criterion (§3 below), so only 3 of 7 characters could be certified here.
> **Phase 3b** re-ran the identical ablation with a corrected gate registered in advance and produced
> the **certified verdict: 5 held-scene / 1 underpowered / 1 not-run, 0 held-latent**, with every trait
> read reproducing this run **exactly** (0.0% deviation). Read
> [`../phase3b/PHASE3B_RESULTS.md`](../phase3b/PHASE3B_RESULTS.md) for the verdict of record.
>
> This document stays as the dated record of the first run and of the gate flaw — which is worth
> keeping, since the flaw and its handling are more instructive than the certification.

Run 2026-07-21, `trait_persistence_v2_phase3.ipynb` on Colab T4; analysed with
[`analyze_phase3.py`](../analyze_phase3.py) against the **frozen** criteria in
[`prediction.md`](../prediction.md) §3 + §7b. n = 7 survivors, band 13–26, decision checkpoint
**d = 10, Cue B** (pinned in §9 before the run). Every number here is descriptive.

## Headline

1. **The inferred trait is not stored. It is recomputed from the scene on demand.** Masking the
   behavioural sentence's attention keys collapses inferred-trait retrievability; masking a matched
   filler sentence does essentially nothing. **Q3 outcome (b), "held scene."**
2. **Zero characters show held latent** — under either the frozen gate or the post-hoc re-scoring, at
   either distance. There is no counterexample in this dataset.
3. **The registered verdict is 3 held-scene / 1 underpowered / 3 not-run**, because the mask-check gate
   as operationalised failed three characters whose masks demonstrably worked. That gate flaw is
   documented in `prediction.md` §9 and re-scored in a **clearly walled-off** section below (which gives
   5 / 1 / 1). **The frozen verdict is not overwritten.**
4. **The stated trait is not stored either.** The symmetric direct-arm test: masking the literal trait
   word wrecks stated retrieval (median ×56) while masking a neutral tracer word does nothing
   (median ×0.90). Both arms are reconstructed on demand — from different sources.

---

## 1. The registered result (frozen §3, d = 10, Cue B)

`R_i` = baseline, `R_ii` = scene ablated, `R_iii` = matched-filler ablated; inferred-arm best-lexicon
J-lens rank, median over band. Lower = more retrievable. Verdict rule: held-latent if `R_ii ≤ 50` and
`R_ii/R_iii ≤ 2.0`; held-scene if `R_ii/R_iii ≥ 5.0`; underpowered (c) if `R_i > 50`, declared before
looking at ii/iii.

| character | `R_i` | `R_ii` (scene) | `R_iii` (control) | `R_ii/R_iii` | registered verdict |
|---|---:|---:|---:|---:|---|
| Greta (dishonest) | 18.0 | 2462.5 | 19.5 | **126.3×** | **(b) held scene** |
| Nadia (brave) | 3.5 | 320.0 | 3.0 | **106.7×** | **(b) held scene** |
| Elias (loyal) | 47.5 | 300.0 | 44.0 | **6.8×** | **(b) held scene** — but see §3 |
| Marek (cowardly) | 897.5 | 2084.0 | 721.0 | 2.9× | (c) underpowered |
| Maria (generous) | 26.0 | 714.5 | 23.5 | 30.4× | not-run (gate) |
| Simon (curious) | 2.0 | 295.5 | 2.0 | 147.8× | not-run (gate) |
| Bruno (lazy) | 4.0 | 687.5 | 4.0 | 171.9× | not-run (gate) |

**Registered tally: 3 held-scene, 1 underpowered, 3 not-run, 0 held-latent.**

Two things are worth reading off this table beyond the verdict:

- **`R_iii ≈ R_i` for every single character** (18/19.5, 3.5/3.0, 47.5/44, 26/23.5, 2.0/2.0, 4.0/4.0).
  Ablating an equally sized irrelevant span costs essentially nothing. The effect is specific to the
  scene, not a general consequence of masking text.
- **Every character with a retrievable baseline collapses**, including the three the gate could not
  certify. The direction is uniform across the dataset; only the certification is partial.

## 2. The mask worked — instrument evidence

Two independent checks, both run before any trait number was trusted.

**Mechanistic.** With the scene masked, attention probability landing on the scene's key columns is
**0.00** across all band layers and heads, against **0.945** unmasked (Maria, d = 10). The
"attention logits → −∞" lever works exactly as §7b specifies. V-zeroing was not used, so §7b's
deviation clause does not apply.

**Semantic.** The greedy answer to `"What did NAME do? NAME"` — with the scene masked, the model falls
back to reciting the **opening** (the occupation, never masked), and snaps back to the scene when only
filler is masked:

| character | baseline | scene masked | control masked |
|---|---|---|---|
| Greta | "wrote down a weight that was never there." | "weighed produce at the market scale." | scene restored |
| Nadia | "pulled a worker clear from under a freight stack." | "sorted freight at the rail yard." | scene restored |
| Marek | "slipped through the back door and waited until the voices stopped." | "set type at the print shop." | scene restored |
| Maria | "covered her colleague's rent." | "kept the ledgers." | scene restored |
| Simon | "opened every unlabelled crate that came through." | "stacked crates at a warehouse." | scene restored |
| Bruno | "left the gates half-raised and sat out the shift in" | "tended the canal lock." | scene restored |
| Elias | "drove a delivery van out of a yard." | *identical* | *identical* |

Six of seven are textbook. Elias is the exception, and it matters — see next section.

## 3. The gate flaw (and why three characters are `not-run`)

Full account in `prediction.md` §9, "Q3 gate flaw". In short: the registered gate scored scene-keyword
**rank at a single position** — the token right after the name — whereas §7b's criterion is the broader
*"the model can no longer answer 'what did NAME do?'"* The scene keywords are mostly nouns the model
emits 2–5 tokens later, so the proxy and the criterion came apart, **in both directions**:

- **Three false failures** (Maria, Simon, Bruno). Their masks demonstrably worked. Compounding cause:
  the words the model actually emits first — `covered`, `opens` — are exactly the ones dropped from
  `SCENE_KEYWORDS` earlier the same day for leaking into filler sentences.
- **One probable false pass** (Elias). He cleared the thresholds numerically (kw 32/270/26) while his
  continuation is identical in all three conditions — the probe never elicited his scene at all. §7b's
  "can *no longer* answer" presupposes it could. **Elias's held-scene verdict is the weakest of the
  three**, on the smallest ratio (6.8×) and a borderline baseline (47.5, just under the 50 line). He was
  also the anomalous character in Phase 2 (Q1 ratio > 1, Q5 negative). "Loyal" is a weak cue in every
  phase of this project.

**The three not-run characters are not promoted.** §7b exists precisely for this case, and the pull to
promote is strongest when it would strengthen a conclusion one already finds convincing.

### 3a. Post-hoc re-scoring — SECONDARY, not the registered result

*Walled off deliberately. This rule was written **after** seeing the frozen gate's output and after
reading the d = 10 continuations — a researcher degree of freedom, stated rather than hidden. It is
bounded by being fixed before computation and by using the least tunable threshold available (binary
presence, not a tuned count). It does not overwrite anything above.* Same discipline as v1's §5
correction. Script: [`analyze_phase3_posthoc.py`](../analyze_phase3_posthoc.py).

**Rule.** Score §7b's criterion directly on the generated answer. `scene_overlap` = distinct content
words (≥ 4 chars, minus a fixed stopword list) shared with the character's `inferred` sentence,
**excluding any word also present in the opening** — so falling back to the occupation scores 0. Gate
passes iff baseline ≥ 1, scene-masked = 0, control-masked ≥ 1.

| character | overlap base/scene/ctrl | gate | verdict | ratio |
|---|---|---|---|---:|
| Bruno | 4 / 0 / 4 | pass | held scene | 171.9× |
| Simon | 2 / 0 / 2 | pass | held scene | 147.8× |
| Greta | 1 / 0 / 1 | pass | held scene | 126.3× |
| Nadia | 3 / 0 / 3 | pass | held scene | 106.7× |
| Maria | 3 / 0 / 3 | pass | held scene | 30.4× |
| Marek | 5 / 0 / 5 | pass | (c) underpowered | — |
| Elias | 0 / 0 / 0 | **fail** | not-run | — |

**Post-hoc tally: 5 held-scene, 1 underpowered, 1 not-run, 0 held-latent.**

`scene_overlap` under scene-masking is **0 for all seven characters**, and baseline equals control for
all seven — the control ablation did nothing, the scene ablation removed scene-reporting universally.

**The rule is not tuned to inflate the finding:** it *removes* Elias, who supported held-scene under the
frozen gate, as well as admitting three characters. A metric chosen to maximise the result would not
discard a supporting case.

## 4. Distance robustness (exploratory, no §3 verdict)

The ablation was also run at d ∈ {0, 1, 2, 4, 7, 30}; d = 30 exists to check the d = 10 verdict is not
distance-specific (§9). Under the post-hoc rule at d = 30: **4 held-scene / 2 underpowered / 1 not-run,
0 held-latent** — and the ratios *grow*: Bruno 172× → **681×**, Simon 148× → **536×**, Nadia 107× →
**235×**, Greta 126× → **192×**. Maria joins Marek as underpowered (her inferred trait is no longer
retrievable at baseline that far out).

The verdict is not an artifact of the chosen distance. If anything the scene-dependence is stronger the
further the cue sits from the scene.

## 5. The symmetric direct-arm test (descriptive; not part of the §3 verdict)

Spec D5's mirror: on the `direct` arm, mask the **literal trait word**, and — as a matched control —
mask the neutral **tracer word**. d = 10, trait rank; higher = more disrupted.

| character | baseline | trait word masked | tracer masked |
|---|---:|---:|---:|
| Greta | 6.5 | 2668.5 (**×410**) | 6.5 (×1.00) |
| Marek | 7.5 | 1310.5 (**×175**) | 9.5 (×1.27) |
| Bruno | 3.5 | 217.0 (**×62**) | 4.0 (×1.14) |
| Maria | 8.5 | 473.0 (**×56**) | 6.5 (×0.76) |
| Simon | 26.0 | 472.0 (**×18**) | 16.5 (×0.63) |
| Nadia | 26.0 | 372.5 (**×14**) | 23.5 (×0.90) |
| Elias | 184.5 | 397.5 (×2.2) | 167.5 (×0.91) |
| **median** | | **×56** | **×0.90** |

Six of seven show a large, specific collapse when the literal symbol is hidden, and **no effect
whatever** from hiding an equally sized neutral word. Elias is again the exception — his stated trait
was barely retrievable to begin with (baseline 184.5).

## 6. What this run licenses, and what it does not

**Licensed.**
- Under cued retrieval on this model, an inferred trait is **not maintained as a standing latent**
  independent of the text it was inferred from. Remove access to the scene and it goes.
- The effect is **specific**: an equally sized irrelevant ablation leaves retrievability untouched.
- The stated trait is **likewise** dependent on its literal token remaining readable.

**Not licensed.**
- **No claim that nothing whatsoever is stored.** These lenses read *disposition to say the trait word*.
  A trait could be held in some form that never approaches the tip of the tongue, and nothing here would
  see it. Retrievability, expression, and representation remain three different questions.
- **No general claim about transformers.** One 4B open model, n = 7, one lens, one prompt family.
- **Nothing about characters that were not certified.** Their numbers point the same way and are shown,
  but the frozen verdict rests on three characters (five under the labelled post-hoc rule).

## 7. Interpretation (beyond the pre-registered analysis)

*Interpretation, not registered result — held to a lower evidential bar than §3's frozen criteria. Read
the results first, then disagree freely.*

**The arc closes, and it closes differently than anyone expected.**

v1 watched the model at sentence endings and concluded the inferred trait collapses within one sentence
while the stated trait persists, proposing **re-read vs re-derive**: the stated trait leaves a literal
token to glance back at, the inferred one was never written down. v2 pointed out you cannot test a cache
by watching it, made every checkpoint a query, and found the collapse was an artifact of *where v1 read* —
when you *ask*, the inferred trait is retrievable 30 sentences out, and is no less retrievable than the
stated one. That looked like it killed the mechanism.

Phase 3 says the mechanism was right and the inference from it was wrong. **Neither trait is held.**
Both are reconstructed on demand from source text that never left the context — the stated one from its
literal word (×56 collapse when hidden), the inferred one from its behavioural scene (×30–172 collapse
when hidden), each untouched by an equally sized irrelevant ablation. Phase 2's null was not "no
difference in storage." It was **"no difference because neither is stored."** The two arms looked
equally retrievable because both of their sources remained equally available the whole way out.

The corrected reading of v1's mechanism: re-derivation is real, but it is *cheap* — apparently about as
cheap and reliable as re-reading a word. That is why distance did nothing in Phase 2 and why the
stated-vs-inferred contrast never opened up across 30 sentences. The asymmetry v1 thought it had
measured was in what the model *spontaneously emits*, not in what it *holds*.

**Where this sits relative to the source paper.** The workspace paper's selectivity finding is that
fluent, automatic processing flows *around* the reportable slice while deliberate, multi-step content
routes *through* it. A trait that is recomputed from still-visible evidence on each query looks much
more like the former than the latter: nothing needs to be carried, because nothing was evicted. That
also suggests the obvious next probe — this design never made the model *let go* of the scene. Every
result here is about a context where the evidence remains on the page.

**The honest shape of the finding:** this is a clean, uniform, well-controlled negative about *storage*,
on a small sample, with an instrument flaw that cost three certifications and is documented rather than
patched over.

## 8. Limitations

- **n = 7**, three certified under the frozen gate (five post-hoc; five again under Phase 3b's
  pre-registered gate). Single-character results are visible in every table precisely because aggregates
  at this size are draggable.
- **The registered gate was a poor proxy** for its own criterion, in both directions (§3). The corrected
  scoring is post-hoc and labelled as such; it is not the registered result.
- **Elias is unreliable throughout** — weak cue in Phase 1, anomalous in Phase 2's Q1 and Q5, probable
  false gate pass here. His inclusion in the frozen tally and exclusion from the post-hoc one is the
  single largest difference between the two.
- **Marek was underpowered** (inferred trait at rank ~900 at baseline); Maria too at d = 30. The gate is
  fine for them; the trait simply was not retrievable to ablate.
- **Instrument note:** Phase 3 runs `eager` attention (required by the mask), Phases 1–2 ran the SDPA
  default. Baseline reads reproduce Phase 2 to within 0–3.5 rank positions rather than exactly. All
  three ablation conditions share one eager pass, so this cancels in every ratio reported (§9).
- **Q4 (two-entity interference) remains a stub**, and v1's direction probe — reading the trait as a
  linear direction rather than a word — remains the natural complement, since it could see a held
  representation that these vocabulary-projection lenses cannot.

## Files

| file | what it is |
|---|---|
| `phase3_ablation.csv` | 140 rows: inferred-arm trait rank under {baseline, scene, control} × 7 distances |
| `phase3_maskcheck.csv` | 140 rows: scene-keyword ranks — the registered gate |
| `phase3_direct.csv` | 147 rows: the symmetric direct-arm test |
| `phase3_per_layer.csv` | 3,920 rows: per-layer ranks, both lenses (repeats v1's E4 sub-band check) |
| `phase3_top20.csv` | 39,200 rows: top-20 J-lens vocabulary at every inferred Cue B checkpoint |
| `phase3_scene_continuations.csv` | 140 greedy "what did NAME do?" answers — the semantic gate evidence |
| `../analyze_phase3.py` | the frozen §3 verdict behind the §7b gate |
| `../analyze_phase3_posthoc.py` | the labelled post-hoc re-scoring (§3a) |

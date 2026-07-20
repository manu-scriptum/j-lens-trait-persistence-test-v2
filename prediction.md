# Pre-registration: trait retrieval under cued probes — stated vs. inferred (v2)

Committed **before any v2 code was written or run**, including before the calibration sweep and
before the stimulus screening gate. Supersedes the pre-registration of the v1 run
([`j-lens-trait-persistence-test/prediction.md`](https://github.com/manu-scriptum/j-lens-trait-persistence-test/blob/master/prediction.md),
2026-07-13), which remains frozen as the record of that run and is not edited.

Design authority for this document is `trait-persistence-v2-spec.md` (in this repo). Where this
document is more specific than the spec — exact numeric criteria, exact stimuli, exact lexicons —
this document governs, and the spec's own instruction is that these be pinned in advance:

> Decide and write down, in advance, the exact numeric criterion for "retrievable" and "survives".
> The v1 lesson: the metric you don't pre-commit is the metric that betrays you.

---

## 0. Why there is a v2 at all

v1 asked whether a trait introduced by *statement* ("Maria is generous") differs from one introduced
by *implication* ("Maria brings the unsold bread to a shelter") in how long it stays readable in
J-lens readouts, and whether re-mentioning the character by bare name reactivates it.

v1's substantive findings (after its own 2026-07-14 correction) were: inference is readable at the
trigger but collapses within one filler sentence; the stated trait persists 25–54% below its own
frequency floor across all ten checkpoints for 3/5 characters; and bare-name reintroduction
reactivates the *inferred* trait above control in 3/5. The proposed mechanism was **re-read vs.
re-derive** — the stated trait leaves a literal token to attend back to, the inferred trait was never
tokenized, so re-cueing it requires re-running the inference.

The problem is that 11 of v1's 13 checkpoints were passive reads at sentence-final periods. That
measures what the model spontaneously tends to emit at a period — largely sentence-openers — not
whether a concept can be *retrieved* when something asks for it. **A cache can only be tested by
querying it.** v1 contained exactly one valid cache-read, the reintroduction, and that one produced
its most interesting result. v2 exists to make every checkpoint a cache-read.

The full flaw list v2 addresses is F1–F7 in the spec §0. This document pins the parts that must not
move once data exists.

---

## 1. Research questions

- **Q1 (primary).** Under cued retrieval, does a stated trait remain more retrievable than an
  inferred trait across intervening text?
- **Q2 (primary).** Is direct-arm persistence trait-specific, or generic token-echo?
- **Q3 (primary).** Is an inferred trait, when retrievable at re-mention, a **held latent** (a trait
  representation stored independently of the scene tokens) or a **held scene** (nothing trait-specific
  stored; the trait is re-derived from cached behaviour tokens on demand)?
- **Q4 (secondary, cuttable).** Does an inferred trait stay bound to the correct entity when a second,
  trait-neutral entity is present?

Q4 will not be run in the first pass. It is built as a documented stub. The spec's instruction —
"do not let Q4 endanger Q1–Q3" — is followed literally.

## 2. Predictions

**No directional prediction is registered for Q1.** v1's corrected result and the re-read/re-derive
mechanism both point to outcome (1), and it would be dishonest to pretend otherwise; but v1's
persistence result is exactly the one that Q2 may reclassify as copy bias, so it is not a prior
strong enough to register. Every outcome below is reportable and none is a "win".

**Q1 — three outcomes:**
1. Stated more retrievable than inferred at all distances d ≥ 1.
2. No detectable difference.
3. Inferred more retrievable.

**Q2 — two outcomes:**
- (a) The tracer word does **not** show below-floor persistence comparable to the stated trait →
  direct-arm persistence is trait/content-specific.
- (b) The tracer persists comparably → the direct arm's passive persistence is substantially
  copy/repetition bias. Q1 then rests entirely on the cued reads, which is what they exist for. This
  outcome does not invalidate v2; it invalidates a specific reading of v1.

**Q3 — three outcomes:**
- (a) Inferred-arm retrieval survives behaviour-KV ablation above the level of the matched control
  ablation → a trait latent exists outside the scene tokens (**held latent**).
- (b) Retrieval collapses under scene ablation but not under control ablation → **held scene**;
  the trait is recomputed on demand.
- (c) Retrieval was too weak pre-ablation for the ablation to be interpretable → underpowered,
  reported as such and not spun.

Q3(a) and Q3(b) are both publishable and roughly equally interesting. That is the property that makes
this experiment worth running, and it is protected by writing it down here.

## 3. Numeric criteria, pinned

All criteria below are frozen as of this commit. Any later change is an amendment, dated and appended
to §9, never a silent edit.

**Primary measure.** For a trait with concept lexicon `L`: at a given (arm, distance, cue), take the
J-lens **best rank across `L`** — the minimum rank over all single-token lexicon members — at each
layer in the calibrated band, then the **median of that quantity over the band**. Call this
`R(arm, d, cue)`. Lower is stronger.

**Secondary measure.** The bare trait adjective alone, same statistic, for v1 comparability.

**"Retrievable"** at (arm, d, cue) requires **both**:
- `R(arm, d, cue) ≤ 50`, and
- `R(arm, d, cue) / R(control, d, cue) ≤ 0.8`.

The ratio is always against the **control arm at the same distance and the same cue**. Never against
the same arm at d0 (v1's F3 error). Never against a different trait word (base-frequency floors are
not commensurable).

**Q1 decision rule.** At each d ∈ {1, 2, 4, 7, 10}, per character, compute
`ratio(arm, d) = R(arm, d, CueB) / R(control, d, CueB)`. Outcome (1) is supported if the direct arm's
ratio is lower than the inferred arm's for a majority of characters at a majority of distances, **and**
a Wilcoxon signed-rank test on the per-character paired ratios (pooled over d, then per-d as a
secondary breakdown) reaches p < 0.05. With n = 8, this test is weak; if it does not clear, the result
is reported descriptively as direction-and-consistency, not as a finding.

**d0 is excluded from all persistence claims for the direct arm** — at d0 the trait word is surface
echo. d0 is reported, and used for screening, but carries no persistence weight.

**Q2 decision rule.** Outcome (b) — copy bias — is declared if the tracer's median
`R(tracer, d)/R(tracer_control, d)` over d ≥ 1 falls within 0.15 of the stated trait's corresponding
median ratio. Outcome (a) is declared if the tracer's ratio is ≥ 0.95 (essentially at floor) while the
trait's is ≤ 0.8. Anything in between is reported as partial/ambiguous, and Q1's interpretation then
rests on the cued reads alone.

**Q3 decision rule.** Let `R_i`, `R_ii`, `R_iii` be inferred-arm best-lexicon-rank medians under
baseline, scene ablation, and matched-filler control ablation, at the reintroduction Cue B checkpoint.
- Outcome (a) held latent: `R_ii ≤ 50` **and** `R_ii / R_iii ≤ 2.0` — i.e. ablating the scene costs
  little more than ablating an equally sized irrelevant span.
- Outcome (b) held scene: `R_ii / R_iii ≥ 5.0` — scene ablation specifically destroys retrieval.
- Between 2.0 and 5.0: partial, reported as such.
- Outcome (c): declared in advance if `R_i > 50`, in which case (a)/(b) are not evaluated for that
  character. This check is made **per character, before** looking at any ablation number.

**Screening gate (D0).** A character enters the main sweep only if, at d0:
`R(inferred, 0) ≤ 200` **and** `R(control, 0) / R(inferred, 0) ≥ 5`.
Thresholds are frozen here rather than tuned on the first two characters as the spec permits, because
tuning them after seeing screening data is the one remaining researcher degree of freedom in the
screening step. If these thresholds prove badly miscalibrated for this model — e.g. they admit zero
or all candidates — that is itself reported, and any revision is an amendment in §9 with the screening
data shown.

**Failure rule (added 2026-07-20, pre-data).** If fewer than **5** candidates pass screening, the run
**halts**. Thresholds are then revised in a dated §9 amendment, with the screening table shown, before
any Phase 2 data exists. The gate is not loosened mid-run to admit more characters. This keeps the
gate honest in the failure case, which is the only case where loosening it would be tempting.

**Why screening does not contaminate Q1.** The gate selects on **d0 inference strength**; Q1 is about
**persistence at d ≥ 1 relative to control**. These are different quantities. To the extent they
correlate, selecting high-d0 items biases the inferred arm *toward* regression to the mean at later
distances, i.e. against Q1 outcome (1), the outcome the mechanism predicts. The bias is conservative
with respect to the prediction we would otherwise be accused of favouring.

## 4. Model, lens, band

- Model: `google/gemma-3-4b-it`, for continuity with v1.
- Lens: `neuronpedia/jacobian-lens`, file
  `gemma-3-4b-it/jlens/Salesforce-wikitext/gemma-3-4b-it_jacobian_lens.pt`; `jlens` pinned to commit
  `581d398613e5602a5af361e1c34d3a92ea82ba8e` (v1's pin), recorded again in the run output.
- **The band is not inherited from v1.** v1 used 35–90% depth by inheritance from an earlier project.
  v2 determines the band empirically in a calibration sweep over ~20 neutral documents, before any
  stimulus is constructed, using three criteria: excess-kurtosis onset of the per-layer lens logit
  distribution; layer-to-layer readout autocorrelation onset; and the late-layer collapse into
  next-token prediction (agreement between lens top-1 and the model's actual next-token top-1).
  The band and its justification plots go in the results doc. If the calibrated band happens to match
  35–90%, that is a finding worth stating, not a formality.
- First 5 tokens of every document are excluded from all aggregate statistics (high-norm token
  artifact).
- Raw text throughout; no chat template.

## 4a. Logit-lens robustness stream (added 2026-07-20, pre-data)

Secondary, **gates no conclusion**. All primary readouts are additionally computed with the plain
unembedding (logit lens) over the same band. Interpretation is fixed in advance and asymmetric:

- (a) If the logit lens reproduces a J-lens effect, the effect is **not instrument-specific**.
- (b) A logit-lens null is **uninterpretable** unless the logit lens passed its per-character
  **positive control**, defined as detecting the d0 inferred-trigger signal: concept-lexicon best
  rank ≤ 5× the J-lens value at the same checkpoint.
- Where the positive control passes and a specific effect is still absent, we report *"visible to the
  J-lens, not the logit lens"* as a **descriptive observation about instrument sensitivity**, not as
  evidence about the model.

That last clause is load-bearing. Even with the positive control passed, "J-lens sees it, logit lens
doesn't" is a statement about the two lenses' relative sensitivity to this signal — **not** proof of a
J-space-privileged representation. The source paper needed its whole structural section to earn that
stronger reading; this experiment does not get to borrow it.

No Q1–Q3 criterion in §3 references the logit lens. The J-lens is primary throughout.

## 5. Stimuli

Ten candidate characters, five positive-valence traits and five negative, screened down to a target of
eight (minimum 4:4 balance retained; if screening breaks the balance, that is reported and the sweep
runs on what survives rather than on back-filled replacements chosen after seeing data).

All characters share an invented town (**Vellin** — no real place-name, fixing v1's "Lyon"), a
trait-neutral occupation chosen so the role does not itself imply the trait (fixing v1's clinic-worker
/ `brave` confound), and an identical filler block and cue set.

Each character has three arms:
- `direct` — trait stated outright, with the tracer word embedded (see §6).
- `inferred` — trait implied by one behavioural sentence; the trait word and close derivatives absent.
- `control` — a behavioural sentence implying no trait, matched to the inferred sentence in length and
  in topic domain (same objects and setting where possible, only the action differing). v1's controls
  differed from its inferred triggers in topic as well as in trait content; that confound is what this
  matching removes.

Exact stimulus text, lexicons, and tracers are declared in `stimuli_v2.py` in this repo, committed in
the same commit as this document. They are part of the pre-registration; the file is the canonical
copy to avoid transcription drift between doc and code.

## 6. Concept lexicons and tracers

**Lexicons (D1).** Each trait gets 6–12 candidate lexicon entries covering the adjective, its
synonyms, and noun forms. Every entry is verified single-token in the leading-space form in the Gemma
tokenizer at run time; multi-token entries are **dropped and logged**, never silently substituted. A
trait whose surviving lexicon falls below 4 entries is reported as underpowered for the primary
measure and analysed on the secondary measure only.

**Tracers (D4).** Each `direct` trigger embeds one pre-declared neutral content word of broadly
comparable frequency to the trait word, with no semantic relation to the trait, the character, the
occupation, or the filler — e.g. "Maria is generous, she thinks, setting down the **lantern**." The
tracer is tracked against its own control-arm floor with the identical machinery. Tracers are declared
in `stimuli_v2.py` alongside the lexicons.

## 7. Cues and checkpoints (D2)

Distances d ∈ {0, 1, 2, 4, 7, 10} filler sentences. At each d, the text through distance d is
**byte-identical across arms up to the trigger sentence**, and each cue is a **separate forked forward
pass** on (prefix + cue), so all differences are attributable to arm and cue.

- **Cue A (entity cue, topic-free):** `"Tom glances at NAME."` — read at the tokens *following* the
  name. Note: this introduces a second name, Tom. It is identical across all arms and all distances,
  so it cancels in every arm-vs-control contrast, which are the only contrasts drawn. It is not used
  for any absolute claim. **Note (2026-07-20):** "Tom" is now *spent* as a neutral name. If Q4/D6 is
  ever unstubbed, its second entity must use a different name, or the interference test would be run
  against a name already present in every prefix.
- **Cue B (trait query):** `"What kind of person is NAME? NAME is"` — read at the final position,
  where a trait adjective is contextually possible. This is the position v1's sentence-final periods
  made structurally impossible, and it carries the primary Q1 contrast.
- **Passive period-read:** retained as a cheap third stream for v1 comparability only. Labelled
  "spontaneous saliency" everywhere it appears. **It carries no persistence claim in v2.**
- **Reintroduction (D3):** v1's bare-name reintroduction after the full filler, kept as a distinguished
  checkpoint (Cue A at maximum distance plus a continuation read).

## 7a. Registered conditional extension (added 2026-07-20, pre-data)

If, at d=10 under Cue B, the direct arm's median ratio-to-control across screened characters is
**≤ 0.8** (retrievable, no approach to floor) **AND** the direct-vs-inferred ratio contrast at d=10 is
smaller than at d=4 by **less than 20%** (no separation trend has emerged), extend the sweep to
d ∈ {15, 20, 30}, identical cues and measures, as a **registered secondary analysis**. The extension
is triggered by **lack of dynamic range, not by any substantive result**, and its findings carry the
same status as the primary sweep.

The trigger is deliberately two-part: extend only if the direct arm is *both* still comfortably
retrievable *and* the contrast has not already opened up. If separation is visible by d=10, the
question is answered and the extension is decoration.

**Override.** If Q2 returns outcome (b) — the tracer persists comparably, i.e. copy bias — the
extension does **not** run, regardless of trigger. The quantity whose range would be extended is then
contaminated, and extending it would mean measuring the decay curve of a repetition artifact.

The unconditional "find the verbatim half-life" version is explicitly **not** registered. That
question was posed about a *passive-read* quantity, and passive reads carry no persistence claims in
v2 (§7). Chasing its half-life would spend forward passes on Q2's null hypothesis.

## 7b. D5 implementation gate (added 2026-07-20, pre-data)

- **Preferred mechanism:** forward pre-hooks on the HF attention modules setting attention logits to
  **−inf** toward the scene-token span, at every layer and head.
- **V-zeroing is not an accepted silent substitute.** Zeroed values still let attention mass land on
  the span, changing the softmax denominator differently than masking does. If V-zeroing is used, it
  is **recorded as a deviation** in the results doc.
- **Registered gate:** D5 results are reportable **only if the mask check passes** — under scene
  ablation the model can no longer answer "what did NAME do?", and under the matched control ablation
  it still can. **If the gate fails, D5 is reported as not-run, never as a null.** A failed mask
  produces a null that looks exactly like Q3 outcome (b), and reporting it as such would manufacture
  the more surprising of the two findings out of a bug.

## 8. Analysis constraints, fixed in advance

- Arm vs. its own control, same checkpoint, same cue. Always.
- No d0-normalisation of anything, ever (F3).
- No cross-trait absolute rank comparison (different base-frequency floors).
- Reads land on cue tokens, not on the period preceding them.
- Median over the calibrated band is primary; per-layer values are stored so the v1 E4 check —
  did the median hide a sub-band signal? — can be repeated.
- Top-20 lens vocabulary stored at every checkpoint. v1's post-hoc correction was only possible
  because this existed.
- If a result hinges on one character, that is stated. n = 8 medians are draggable by one item.
- If the lens shows nothing anywhere: check band calibration and tokenizer leading-space forms before
  concluding absence. Instrument first, phenomenon second.
- Anything not clearing a pre-registered criterion is described in descriptive language, not as a
  finding.

## 9. Amendments

Amendments are appended here with a date, the reason, and the data visible at the time of the change.
Superseded lines above are marked inline, never deleted — same discipline that made v1's correction
possible.

### 2026-07-20 — pre-data revision (spec review)

**Data visible at the time: none.** Nothing had been run — no calibration sweep, no screening reads,
no main sweep. This is a revision of an untested pre-registration, not a post-hoc amendment, and it
therefore costs nothing epistemically. It is logged here anyway, because the value of the log is that
it is complete.

**Origin.** `trait-persistence-v2-spec.md` was written from the source paper and v1's `results.md`
only. Its author had not seen v1's `prediction.md`, v1's notebook, `stimuli.csv`, or a design decision
tree compiled 2026-07-14 that had marked several decisions *locked*. Two locked decisions were absent
from the spec — not rejected, never seen. Both were put back to the spec's author for a ruling, and
these are the rulings.

1. **§4a added — logit-lens robustness stream.** Restores a locked 07-14 decision. The skeptic's
   question, "is the fancy lens load-bearing?", deserves a registered answer, and it is
   computationally free. The d0 positive control is the review's addition and is what makes a
   logit-lens null interpretable at all; the original framing had no way to distinguish "the model
   doesn't represent it" from "this lens can't see at these depths."
2. **§7a added — registered conditional extension past d=10.** The unconditional 07-14 version
   ("find the verbatim half-life") stays **rejected**: it targets a passive-read quantity that Q2 may
   reclassify as copy bias. The dynamic-range concern for the *cued* measure is real, so the
   extension is registered as conditional, with a two-part trigger and a Q2 override.
3. **§7b added — D5 implementation gate.** The spec's verification guard is elevated from advice to a
   registered gate, and the masking mechanism is pinned. Rationale: a failed mask yields a null
   indistinguishable from Q3 outcome (b), which is the more surprising finding — so a bug could
   manufacture a result.
4. **§3 failure rule added.** Fewer than 5 screening survivors halts the run rather than loosening a
   pre-registered gate.
5. **§7 note added.** "Tom" is spent as a neutral name; D6 needs a different one if unstubbed.

**Deviations from the spec, reviewed and approved in the same pass:** screening thresholds frozen
rather than tuned on the first two characters (the spec's tuning window was a researcher degree of
freedom; closing it was accepted as an improvement); 10 pre-declared candidates rather than 8;
Q4/D6 stubbed; Cue A's "Tom" retained verbatim.

**Process note for future runs.** Spec-writing from results-plus-paper reproduces the *analysis* but
cannot reproduce *decisions*, because decisions are not derivable from the flaws. The design decision
tree travels with the results doc in any future handoff.

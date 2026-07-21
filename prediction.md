# Pre-registration: trait retrieval under cued probes — stated vs. inferred (v2)

Committed **before any v2 code was written or run**, including before the calibration sweep and
before the stimulus screening gate. Supersedes the pre-registration of the v1 run
([`j-lens-trait-persistence-test/prediction.md`](https://github.com/manu-scriptum/j-lens-trait-persistence-test/blob/master/prediction.md),
2026-07-13), which remains frozen as the record of that run and is not edited.

Design authority for this document is `trait_persistence_v2_spec.md` (in this repo). Where this
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
- **Q3 — DEFERRED, not run in this pass (see §1a).** Is an inferred trait, when retrievable at
  re-mention, a **held latent** or a **held scene**?
- **Q4 (secondary, cuttable).** Does an inferred trait stay bound to the correct entity when a second,
  trait-neutral entity is present? **Not run in this pass**; built as a documented stub.
- **Q5 (secondary, free).** Does the J-lens read content the logit lens cannot — specifically, does it
  surface the *inferred* (never-tokenised) trait where a plain unembedding readout surfaces only the
  *stated* one? An instrument-discriminant question, added 2026-07-20. See §4a.

## 1a. Why Q3 is deferred (added 2026-07-20, pre-data)

Q3's KV-ablation requires attention/KV-patching scaffolding and its own validation — proving the
ablation removed the intended trace rather than simply breaking the model. That is an *intervention*,
not a readout, and it is out of reach of a Colab-T4 read-only lens rig.
**[Superseded 2026-07-21 (post-run) — this was a misjudgement; the ablation *can* be run on this
setup after all. Deferral lifted; see §9.]**

This is not a new judgement. v1's own `prediction.md` reached it first, in its "Design spec for a
future run" section, before the v2 spec existed:

> the ablation is out of the read-only lab … park the causal ablation as a proper-lab / agentic-run
> step, **not the immediate next run** … **Primary next run = cued retrieval + interference + this
> fragility read; the KV-ablation is the eventual causal confirmation, elsewhere.**

`trait_persistence_v2_spec.md` promoted that deferred item to its primary novel result (Q3/D5). Its
author was working from the source paper and v1's `results.md` only, and had not seen v1's
`prediction.md`, where the deferral was recorded. The promotion was therefore made without knowledge
of the prior feasibility judgement, not against it.

**This run is the corrected replication: Q1 + Q2, plus the free Q5 discriminant.** That is what v1's
spec called the primary next run, and it is worth doing on its own terms — v1 could measure cued
retrievability at exactly one accidental checkpoint.

**What survives of Q3 here.** v1's spec proposed an observational shadow, *differential fragility*:
stress both arms with reads only and see which retrieval mode breaks first. Its distance half **is
already Q1** — cued retrieval across d ∈ {0,1,2,4,7,10} measures precisely whether the inferred arm
craters faster than the stated arm as distance accumulates. Its interference half needs Q4 and is not
run. So Q1 delivers a partial fragility read; it is correlational, motivates the ablation rather than
replacing it, and **no held-latent-vs-held-scene claim may be drawn from it**. §7b's ablation gate
stays registered for whenever Q3 becomes runnable.

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

**Q5 — instrument discriminant, two outcomes.** Read as the `{direct, inferred} × {logit, J-lens}`
contrast, wording carried over from v1's follow-up spec:
- (a) The logit lens surfaces the *stated* trait but not the *inferred* one, while the J-lens surfaces
  both → the J-lens is doing its claimed job of reading unexpressed latent content. This is the
  strongest available justification for using it on this task.
- (b) All lenses agree → the J-lens buys nothing here, and the finding is instrument-independent
  (which is good for the finding and bad for the instrument's claimed advantage).

Caveat fixed in advance: both are vocabulary-projection transports, so this is a readout-robustness
and discriminant check, **not** a representation probe. It cannot see a held-but-unexpressed concept.
Q5 gates no Q1/Q2 conclusion.

**Q3 — DEFERRED; outcomes retained for whenever it is runnable:**
- (a) Inferred-arm retrieval survives behaviour-KV ablation above the level of the matched control
  ablation → a trait latent exists outside the scene tokens (**held latent**).
- (b) Retrieval collapses under scene ablation but not under control ablation → **held scene**;
  the trait is recomputed on demand.
- (c) Retrieval was too weak pre-ablation for the ablation to be interpretable → underpowered,
  reported as such and not spun.

Q3(a) and Q3(b) are both publishable and roughly equally interesting. That is the property that makes
this experiment worth running, and it is protected by writing it down here. **[Superseded 2026-07-20
— Q3 is deferred (§1a); it is not run in this pass. The statement stays true of Q3 whenever it
becomes runnable, but it is no longer what makes *this* run worth doing. This run is the corrected
replication: Q1 + Q2 + Q5.]**

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
secondary breakdown) reaches p < 0.05. With n = 8 [n = 7 for this run — §9 2026-07-21 (later)], this test is weak; if it does not clear, the result
is reported descriptively as direction-and-consistency, not as a finding.

**d0 is excluded from all persistence claims for the direct arm** — at d0 the trait word is surface
echo. d0 is reported, and used for screening, but carries no persistence weight.

**Q2 decision rule.** Outcome (b) — copy bias — is declared if the tracer's median
`R(tracer, d)/R(tracer_control, d)` over d ≥ 1 falls within 0.15 of the stated trait's corresponding
median ratio. Outcome (a) is declared if the tracer's ratio is ≥ 0.95 (essentially at floor) while the
trait's is ≤ 0.8. Anything in between is reported as partial/ambiguous, and Q1's interpretation then
rests on the cued reads alone.

**Q3 decision rule** — *deferred with Q3 (§1a); retained verbatim for whenever it is runnable.* Let
`R_i`, `R_ii`, `R_iii` be inferred-arm best-lexicon-rank medians under
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

No Q1/Q2 criterion in §3 references the logit lens. The J-lens is primary throughout.

**Q5 discriminant reading (added 2026-07-20).** Beyond robustness, the same stream answers whether
the J-lens earns its place, via the `{direct, inferred} × {logit, J-lens}` contrast (§2, Q5). The
informative cell is the **inferred** arm: it is the one whose trait was never tokenised, so a plain
unembedding readout has no symbol to project. If the J-lens surfaces it and the logit lens does not —
with the logit lens having passed its positive control, so the null is interpretable — that is the
instrument reading unexpressed latent content. Report per character; n = 8 [n = 7 for this run — §9 2026-07-21 (later)], descriptive.

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

Exact stimulus text, lexicons, and tracers are declared in `trait_persistence_v2_stimuli.py` in this repo, committed in
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
in `trait_persistence_v2_stimuli.py` alongside the lexicons.

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
- If a result hinges on one character, that is stated. n = 8 [n = 7 for this run — §9 2026-07-21 (later)] medians are draggable by one item.
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

**Origin.** `trait_persistence_v2_spec.md` was written from the source paper and v1's `results.md`
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

### 2026-07-20 (later same day) — Q3 deferred, Q5 added

**Data visible at the time: none.** Still nothing run.

v1's `prediction.md` was read in full for the first time and found to contain a **"Design spec for a
future run"** section (lines 360–483) that neither the v2 spec's author nor this pre-registration had
seen. It records a prior feasibility judgement deferring the KV-ablation out of the read-only lab and
naming "cued retrieval + interference + fragility read" as the primary next run. `trait_persistence_v2_spec.md`
had promoted that deferred item to its primary novel result without knowledge of the deferral.

- **Q3 deferred** (§1a). Requires intervention scaffolding and its own validation; not available.
  Outcomes and the §7b gate are retained for whenever it becomes runnable. Q1 delivers the *distance*
  half of the proposed differential-fragility shadow; the interference half needs Q4 and is not run.
  **No held-latent-vs-held-scene claim may be drawn from this run.**
- **Q5 added** — instrument discriminant, `{direct, inferred} × {logit, J-lens}`, wording carried over
  from v1's follow-up spec. Free: it rides on the §4a stream already registered. With Q3 gone this is
  the run's only genuinely new question, and it is a question about the *instrument*, not the model —
  stated as such, not dressed up as more.
- **Lexicon:** `heroism` added to `brave` (v1's refinement 1 prefers noun lexicalisations and names it
  explicitly). No other lexicon changed.

**Scope of this run, stated plainly:** a corrected replication of v1 under cued retrieval (Q1), with a
copy-bias control (Q2) and a free instrument check (Q5). It is not the held-concept experiment. The
held-concept question needs either the KV-ablation (proper lab) or v1's Redesign 3 direction probe —
which v1's spec judged *cleaner than the ablation* for that question and, being a readout rather than
an intervention, **within reach of this lab**. That is the natural next run, and it is not this one.

### 2026-07-20 (later same day) — direct-trigger phrasing and one name

**Data visible at the time: none.** Two stimulus edits, both pre-data.

1. **Direct-trigger phrasing.** The spec's D4 example embedded the tracer as
   `"Maria is generous, she thinks, setting down the lantern."` That construction has two defects a
   human reader flagged: the speaker of "she thinks" is ambiguous (the character about herself, or an
   unnamed onlooker?), and — more consequential — "she thinks" reframes the trait from a *stated fact*
   into a *reported opinion*, weakening the very manipulation the `direct` arm exists to make. All ten
   direct triggers are rephrased to state the trait as a clean sentence, then carry the tracer in a
   separate neutral action clause: `"<Name> is <trait>. <Subj> sets the <tracer> down and heads home."`
   D4's requirements are unchanged — the tracer is still a pre-declared neutral content word resident
   only in the direct trigger, tracked against its control-arm floor. "heads home" is trait-neutral for
   every character. This is a strict improvement to construct validity, not a design change.
2. **One character renamed** Hanna → **Greta** (dishonest arm). Non-scientific: the prior name matched
   a family member's, and no experimental property depends on the choice. She/her, occupation, tracer,
   and both behavioural sentences are unchanged apart from the name token.

`trait_persistence_v2_stimuli.py` self-checks still pass; no trait word leaks into any inferred/control arm; every tracer
is present in its direct trigger.

### 2026-07-21 — two tracers swapped to single-token forms (Phase 1 tokenizer check)

**Data visible at the time: Phase 1 only (calibration + screening). No Phase 2 / Q2 data exists.**
Phase 1's Part-2 tokenizer check (`phase1/tokenizer_check.csv`) found three declared tracers are
**not single-token** in the Gemma tokenizer — `stapler` (Priya), `crowbar` (Elias), `trowel` (Greta) —
so the single-token tracer machinery cannot measure them, and Q2 cannot run for those characters as
declared. This is the exact contingency §6/D4 and the notebook already name: *swap and re-register,
never silently substitute.*

- **Elias:** tracer `crowbar` → **`bucket`**; direct trigger becomes
  `"Elias is loyal. He sets the bucket down and heads home."`
- **Greta:** tracer `trowel` → **`mirror`**; direct trigger becomes
  `"Greta is dishonest. She sets the mirror down and heads home."`
- **Priya (`stapler`) is left unchanged** — she failed Phase 1 screening and is not in the Phase 2
  roster, so no swap is owed; recorded here for completeness.

Each replacement is a neutral concrete object with no semantic relation to the character's trait,
occupation, or scene (D4), of register comparable to the surviving tracers (lantern, kettle, thermos,
umbrella, canteen, compass, mallet). Only the tracer token and the neutral action clause change; the
`inferred` and `control` arms are untouched.

**Why this is not a researcher degree of freedom on Q2.** The swap is made *after* Phase 1 screening
but *before any Q2 data exists*. Tracers do not enter screening (the gate reads only inferred/control
against the trait lexicon), so the survivor roster could not have informed the word choice, and the
choice cannot have been tuned to a Q2 result that has not been measured. The words are chosen for
neutrality, not for any outcome.

**Confirmed 2026-07-21 (same day):** both replacements verified **single-token** in the leading-space
form on the real `google/gemma-3-4b-it` tokenizer (`tok.encode(" "+w, add_special_tokens=False)`):
`bucket` → id 24211, `mirror` → id 14701, each a length-1 encoding. (A tiktokenizer pre-check on the
*gemma-7b* tokenizer had agreed but returned different ids — 24951 / 15978 — confirming Gemma-3 uses a
distinct tokenizer build, which is why the pre-check was not treated as authoritative.) The swap is now
fully registered; no follow-up owed. `trait_persistence_v2_stimuli.py` self-checks pass (tracer present
in its direct trigger; no trait word leaks into inferred/control).

### 2026-07-21 (later same day) — run n fixed at 7 (Phase 1 screening outcome)

**Data visible at the time: Phase 1 (calibration + screening + tokenizer check). No Phase 2 —
no Q1 / Q2 / Q5 data exists.**

Phase 1 applied the frozen D0 screening gate (§3) to the ten pre-declared candidates. Seven passed;
three failed and are out with **no back-fill** (§5): Viktor (control leaked cruelty, ratio 3.26), Otto
(weak inference, R = 251 > 200), Priya (control not trait-neutral, ratio 1.37). The surviving Phase 2
roster is **n = 7**: Maria (generous), Nadia (brave), Simon (curious), Elias (loyal) — 4 positive — and
Greta (dishonest), Bruno (lazy), Marek (cowardly) — 3 negative.

**This is a determined outcome, not a choice.** n = 7 is what the pre-registered gate returned on the
screening data; it was not selected, and no threshold was moved to reach it. 7 ≥ 5, so the §3 failure
rule does not trigger and the run proceeds without loosening the gate. The 4:4 valence target of §5 is
not met (**4:3**, one negative trait short); per §5 this is reported and the sweep runs on survivors
rather than on back-filled replacements chosen after seeing data. The imbalance is carried as a
reporting caveat, not corrected.

**Consequence for the decision rules.** Wherever §3 and §4a fix the sample at "n = 8", read **n = 7**
for this run (marked inline at each occurrence). No numeric threshold in §3 changes — only the n they
are evaluated over. Specifically: the §3 Q1 Wilcoxon is now over 7 paired ratios (already registered as
weak at 8, weaker at 7 — if it does not clear, the direction-and-consistency descriptive fallback
governs, as already written); §4a / Q5 is per character over 7; the §3 "draggable by one item" caution
is now 1-in-7.

**Why this costs nothing on Q1 / Q2 / Q5.** The roster was set by the D0 gate, which reads only the
inferred and control arms against the trait lexicon at d0. It is blind to persistence at d ≥ 1 (Q1), to
the tracer stream (Q2), and to the logit-vs-J-lens contrast (Q5) — none of which has been measured. The
n therefore cannot have been tuned to a result that does not yet exist.

### 2026-07-21 (later still) — §7a conditional extension fired; extension filler declared

**Data visible at the time: the full Phase 2 primary sweep** (Q1 + Q2 + Q5 over d ∈ {0,1,2,4,7,10}),
analysed in [`phase2/PHASE2_RESULTS.md`](phase2/PHASE2_RESULTS.md). This entry is therefore *not*
pre-data — but the action it records was itself **pre-registered** in §7a, so running it follows the
plan rather than adding a degree of freedom. What is genuinely new — the 20 extra filler sentences — is
declared here before the extension is run, and is chosen for neutrality, not for any outcome.

**The §7a trigger, evaluated on the primary data.** §7a extends the sweep to d ∈ {15,20,30} iff, at
d=10 under Cue B, (i) the direct arm's median ratio-to-control across survivors is ≤ 0.8 *and* (ii) the
direct-vs-inferred contrast has not opened up from d4 to d10 — with a Q2 override if Q2 returned copy
bias. Observed: direct median ratio-to-control **d10 = 0.020 ≤ 0.8** (i ✔); contrast (inferred−direct)
**d4 = +0.009, d10 = −0.001**, i.e. no separation emerged (ii ✔); **Q2 was not outcome (b)** (it was
partial, leaning trait-specific), so the override does **not** apply. **The extension is triggered.**

The honest caveat §7a itself raises is recorded with the trigger: direct ratio ≈ 0.02 also means the
direct rank sits near the **rank floor**, so the absent separation may be a dynamic-range ceiling rather
than true convergence — which is exactly what a longer-distance probe is for. The extension carries the
**same descriptive status as the primary sweep**; it is a dynamic-range probe, not a result chase, and
draws **no new held-latent-vs-held-scene claim** (Q3 stays deferred, §1a).

**Extension filler (D2, extended).** Reaching d=30 needs more than the 10 filler sentences of the
primary run. `trait_persistence_v2_stimuli.py` now carries **20 additional** town-generic sentences
(indices 10–29). The original 10 (indices 0–9) are **unchanged and still first**, so every d ≤ 10
prefix is **byte-identical** to the primary run and the primary results stay reproducible. The 20 new
sentences continue the same dull physical-description register and are verified (self-check) to contain
**no trait-lexicon word, no tracer word, and no character name** — the same neutrality the original
filler meets. They were written for neutrality before any extension read exists; they cannot have been
tuned to an extension result.

**Measures, cues, arms, band, roster, lexicons, tracers: all unchanged** from the primary run. Only the
distance set changes, to `EXT_DISTANCES = [15, 20, 30]`. The extension run is
`trait_persistence_v2_phase2ext.ipynb`; its reads are analysed together with the primary sweep across
d ∈ {4, 7, 10, 15, 20, 30} to read the trend.

### 2026-07-21 (post-run) — Q3 feasibility revised: the KV-ablation can run here after all

**Data visible at the time: the full primary + §7a-extension results.** This changes no result and no
frozen criterion — it lifts a *feasibility* judgement, and it is logged rather than silently applied,
same as everything else.

Q3 was deferred throughout this document (§1a, and the 2026-07-20 amendments) on the belief that a
KV-ablation was **out of reach of a read-only Colab-T4 lens rig** — an *intervention* needing
attention/KV-patching scaffolding that the setup did not have. **That belief was wrong.** The
researcher underestimated what this setup can do; on reviewing the results, **Fable pointed out that a
full KV-ablation of `gemma-3-4b-it` is in fact runnable here** (forward pre-hooks on the HF attention
modules — exactly the mechanism §7b already pins). We are, for this purpose, a lab.

**Consequence.** Q3's *infeasibility* deferral is **lifted**. Q3 becomes the **planned next arm**. What
does **not** change: its decision rule (§3, retained verbatim) and its implementation gate (§7b) —
including the load-bearing mask-check that makes a failed mask report **not-run, never a null**, so a
bug cannot manufacture the more-surprising outcome (b). Those were kept frozen precisely so this moment
would be a clean start, not a rewrite. The prior "out of reach / proper-lab / elsewhere" language in
§1a and above stays as the dated record of what was believed; it is superseded, not deleted.

Nothing about the completed Q1 / Q2 / Q5 run changes. The held-latent-vs-held-scene question remains
**unanswered by this run** — it is what the now-runnable Q3 exists to settle.

### 2026-07-21 (post-run) — Q3 implementation pinned (Phase 3 build)

**Data visible at the time: the full primary + §7a-extension results — but no Q3 / ablation data of
any kind.** This entry pins the implementation details Q3 needs to *run*, and it is written and
committed **before a single ablation number exists**. Per the discipline of the 2026-07-20 entries,
registering a to-be-run procedure pre-data costs nothing epistemically. Nothing frozen is changed: the
§3 Q3 decision rule and the §7b mask-check gate are used **verbatim**. What is pinned here is *how* the
scene span, the control span, the mask, and the gate are realised in code, so those realisations are on
record before any result and cannot be tuned to one.

The choices marked **(researcher call)** were decided by the researcher on 2026-07-21 when the build
was scoped; the rest follow directly from §3 / §7b / spec D5 and are recorded for completeness.

1. **Decision checkpoint — pinned to d = 10, Cue B (researcher call).** §3's "reintroduction Cue B
   checkpoint" is realised as **distance d = 10** (the D3 reintroduction — the primary run's maximum
   distance, whose prefix is byte-identical to Phase 2). The §3 held-latent / held-scene verdict is
   computed **only here**, one verdict per character. The ablation is *also* run at
   d ∈ {0, 1, 2, 4, 7, 30} as **walled-off exploratory context that carries no verdict**; the d = 30
   cell exists specifically to check the pinned verdict is not an artifact of the d = 10 distance. (The
   d = 30 reads reuse the §7a extension filler, indices 0–29, and the `max_seq_len` fix from
   `build_phase2ext.py`.) No §3 threshold changes; only the checkpoint at which the frozen rule is
   evaluated is named.

2. **Scene span (condition ii) = the inferred trigger sentence's tokens.** The masked span is the token
   subsequence of `char["inferred"]` located inside the full text (found by matching the leading-space
   encoding, the same way Cue A locates the name). Nothing else is masked.

3. **Matched control span (condition iii) = the closest-length filler sentence.** Among the filler
   sentences actually present at that distance, the one whose token-span length is nearest the scene
   span's length is masked, at its own positions — "an equally sized irrelevant span" (§3). Ties break
   to the earliest such sentence. **At d = 0 no filler is present, so condition iii is undefined and not
   evaluated there;** d = 0 is exploratory only, and the pinned d = 10 checkpoint always has ten filler
   sentences to match against.

4. **Mask mechanism = additive −∞ on attention logits, every layer and head (§7b preferred; not
   V-zeroing).** The model is loaded with `attn_implementation="eager"` so an additive attention bias is
   honoured; forward pre-hooks on every decoder `self_attn` module set the masked key columns to the
   dtype minimum for all query rows, at every layer and head. This is the §7b *preferred* mechanism
   realised literally — **V-zeroing is not used**, so the §7b deviation clause does not apply. Loading in
   eager is a requirement of this mechanism, not a deviation from it, and is printed into the run output.
   The hooks are active during **both** lens reads (the J-lens `apply` pass and the logit-lens
   hidden-states pass share the same `hf_model`), so the ablation is in force for every measurement.

5. **Two independent instrument checks that the mask does what it claims, run before any trait number
   is trusted:**
   - **Mechanistic:** one `output_attentions=True` forward pass with the hook active must show
     attention probability from every query position to every masked key column ≈ 0 across all
     band layers and heads. This proves "attention logits → −∞" took effect, independent of meaning.
   - **Semantic — the §7b gate itself.** A `"What did NAME do?"` probe (`S.scene_probe`) reads the best
     rank across per-character **scene keywords** (`S.SCENE_KEYWORDS`, declared in
     `trait_persistence_v2_stimuli.py`; each a single content word resident only in the inferred
     sentence, absent from opening and every filler, never a trait word — string-checked in that file,
     single-token-checked at run time). The gate **passes for a character** iff, mirroring §3's own
     ratio logic applied to the *scene* rather than the *trait*: baseline scene-keyword best rank
     `R^kw_i ≤ 50` (the scene is reportable at all — else the probe is too weak to gate), **and**
     scene-masking removes it (`R^kw_ii / R^kw_i ≥ 5.0`), **and** the matched control mask spares it
     (`R^kw_iii / R^kw_i ≤ 2.0`). **If the gate fails for a character, that character's Q3 is reported
     `not-run`, never a null** (§7b) — a failed mask produces exactly the collapse that would otherwise
     read as the more-surprising outcome (b). These thresholds (5.0 / 2.0 / ≤50) are the §3 Q3 numbers
     reused on the scene keyword; they are pinned here, pre-data.

6. **Symmetric direct-arm test included (researcher call; spec D5).** On the `direct` arm at the same
   checkpoints, the **trait-word span** is masked and the drop in direct-arm trait retrievability is
   measured — "how much of stated-arm retrieval is the literal symbol" (D5). The **tracer-word span** is
   masked as an equally-sized single-token(-ish) matched control. This is **descriptive and carries no
   part of the §3 held-latent / held-scene verdict**, which is an inferred-arm quantity; it is the
   mechanistic counterpart, reported alongside.

7. **New stimulus content registered here:** `SCENE_KEYWORDS` (7 survivors, 26 keywords total after the
   file's own string self-checks dropped `covered`/`opens`/`sits` for leaking into filler) and
   `scene_probe(name)` in `trait_persistence_v2_stimuli.py`. Both are for the mask-check gate only, do
   not touch the trait measure, and were written for scene-reporting before any ablation read exists.

Build artifacts for this arm: `build_phase3.py` → `trait_persistence_v2_phase3.ipynb` (the run) and
`analyze_phase3.py` (the frozen-rule analysis, off-GPU). Same file discipline as Phases 1–2.

### 2026-07-21 (post-run) — Q3 gate flaw: the registered mask-check was a poor proxy, in both directions

**Data visible at the time: the full Phase 3 ablation run.** This is a post-hoc entry. It changes **no
frozen criterion and no reported verdict** — the §3 result stands exactly as `analyze_phase3.py`
returns it. What it records is that the *gate metric pinned earlier today* turned out to be a bad
realisation of the §7b criterion, and what was done about that.

**The registered gate** (§9, "Q3 implementation pinned", item 5) scored scene-keyword **best rank at a
single position** — the token immediately after the name in `"What did NAME do? NAME"`. The §7b
criterion it was implementing is broader: *"the model can no longer answer 'what did NAME do?'"*

**Why the proxy fails.** The scene keywords are largely nouns that the model emits 2–5 tokens later,
not at the read position. The run's own stored continuations (`phase3_scene_continuations.csv`, a
registered artifact) show the mask behaving correctly where the rank gate said it had not:

| character | baseline continuation | scene-masked continuation | rank gate |
|---|---|---|---|
| Maria | "covered her colleague's rent." | "kept the ledgers." | **FAIL** |
| Simon | "opened every unlabelled crate that came through." | "stacked crates at a warehouse." | **FAIL** |
| Bruno | "left the gates half-raised and sat out the shift in" | "tended the canal lock." | **FAIL** |
| Greta | "wrote down a weight that was never there." | "weighed produce at the market scale." | pass |
| Nadia | "pulled a worker clear from under a freight stack." | "sorted freight at the rail yard." | pass |
| Marek | "slipped through the back door and waited…" | "set type at the print shop." | pass |
| Elias | "drove a delivery van out of a yard." | *identical* | **pass** |

In every masked row the model falls back to reciting the **opening** (the occupation, never masked) —
the signature of a mask that worked. The failure is **two-directional**:

- **Three false failures** (Maria, Simon, Bruno). Compounding cause: the words the model actually emits
  first — `covered`, `opens` — are precisely the ones dropped from `SCENE_KEYWORDS` earlier the same
  day for leaking into filler. The drops removed the words sitting at the read position.
- **One probable false pass** (Elias). He cleared the thresholds numerically (kw 32/270/26) while his
  continuation is *identical across all three conditions* — the probe never elicited his scene at all.
  §7b's "can **no longer** answer" presupposes that it could; for Elias it never did. He was also the
  anomalous character in Phase 2 (Q1 ratio > 1, Q5 negative); "loyal" is a weak cue in every phase.

**What does not change.** The frozen §3 verdict at the pinned d = 10 checkpoint remains
**3 held-scene (Greta, Nadia, Elias) / 1 underpowered (Marek) / 3 not-run (Maria, Simon, Bruno);
0 held-latent.** The three not-run characters are **not** promoted. §7b exists for exactly this
situation, and the temptation to promote is strongest when the promotion would strengthen a result one
already believes.

**Post-hoc re-scoring, reported as a labelled secondary** (`analyze_phase3_posthoc.py`), on the same
discipline v1 used for its §5 correction. §7b's criterion is scored **directly on the generated
answer**: `scene_overlap` = distinct content words (≥4 chars, minus a fixed stopword list) shared with
the character's `inferred` sentence, **excluding any word also in the opening** — so falling back to the
occupation scores 0. Gate passes iff baseline ≥ 1, scene-masked = 0, control-masked ≥ 1.

*Provenance, stated plainly:* this rule was written **after** seeing the frozen gate's output and after
reading the d = 10 continuations. That is a researcher degree of freedom. Two things bound it — the rule
was fixed before being computed, and its threshold is the least tunable available (binary presence, not
a tuned count). It is **secondary and never overwrites the frozen verdict.**

*Result:* **5 held-scene / 1 underpowered / 1 not-run; still 0 held-latent.** `scene_overlap` under
scene-masking is **0 for all seven characters**, and baseline equals control for all seven — the control
ablation did nothing while the scene ablation removed scene-reporting universally. Note the rule
**removes Elias**, who *supported* the conclusion under the frozen gate, as well as admitting three:
a metric tuned to inflate the finding would not discard a supporting case.

**For any future run: register the continuation-based gate as primary from the start**, keeping the
single-position rank read only as a secondary. The lesson generalises — the gate was specified in terms
of a *behaviour* ("can no longer answer") but operationalised as a *single-token rank*, and the two came
apart. Pin the operationalisation against the behaviour it is meant to detect, not against convenience.

**Also logged (instrument note, no verdict impact).** Phase 3 loads the model `attn_implementation=
"eager"` (required by the §7b mask mechanism); Phases 1–2 used the transformers default (SDPA). The two
compute the same attention with different numerical kernels, so bf16 rank ties resolve differently:
Phase 3's *baseline* condition reproduces Phase 2's d = 10 inferred/Cue B reads to within 0–3.5 rank
positions (Bruno 4.0/4.0, Simon 2.0/2.0, Nadia 3.0/3.5, Elias 47.0/47.5, Greta 17.0/18.0, Maria
22.5/26.0, Marek 901.0/897.5) rather than exactly. This is immaterial to every ratio reported here,
because all three ablation conditions are measured **within the same eager pass**, so the kernel
difference cancels; it appears only in the cross-phase comparison, which is where it is harmless.

### 2026-07-21 — Phase 3b: corrected gate registered as primary (pre-data FOR THE RE-RUN)

**Data visible at the time: the complete Phase 3 run.** This entry is **post-data with respect to
Phase 3** and **pre-data with respect to Phase 3b**, the re-run it governs. That distinction is the
whole point of writing it, and the honest description of the corrected gate's status is:
**pre-registered for this run, derived from the previous one.** That is meaningfully better than
post-hoc; it is *not* the same as having specified it correctly the first time, and the re-run does not
launder it. This sentence stays attached to the result permanently.

**What the re-run is worth, stated up front so it is never oversold.** The trait measurements are
expected to *reproduce*, not to change — same model, same texts, same masks. Phase 3b therefore buys
exactly two things: (i) a verdict resting on a gate fixed before that run's data existed, and (ii) an
independent replication of the ablation effect. It buys **no new information about the model**, and any
write-up saying otherwise is wrong.

**Everything not named below is unchanged from Phase 3** — model, lens, pin, band (13–26), roster (n=7),
stimuli, arms, cues, distances, the d=10 Cue B decision checkpoint, and the §3 verdict rule. Phase 3b's
trait reads are directly comparable to Phase 3's and serve as the replication.

**1. Primary gate (new): continuation-scored.** §7b's criterion is a *behaviour* — "the model can no
longer answer 'what did NAME do?'" — so it is scored on the generated answer, not on a proxy:

> `scene_overlap(continuation)` = number of distinct content words (≥ 4 characters, minus a fixed
> stopword list, both frozen in `analyze_phase3_posthoc.py`) shared with that character's `inferred`
> sentence, **excluding any word that also occurs in the shared opening**.
>
> The gate **passes** iff `scene_overlap` is **≥ 1 at baseline**, **= 0 under scene ablation**, and
> **≥ 1 under matched-filler ablation**.

Excluding opening words is load-bearing: with the scene masked the model falls back to reciting the
occupation, and that fallback must score 0 rather than count as "still reporting".

**2. Secondary gate (repaired, not abandoned): position-agnostic rank.** The Phase 3 gate failed because
it read scene-keyword rank at a **single** position. It is retained, repaired, as a secondary: best
scene-keyword rank across the **first 12 generated positions** (the generation length), thresholds
unchanged from §9 "Q3 implementation pinned" (`kw_i ≤ 50`, `kw_ii/kw_i ≥ 5.0`, `kw_iii/kw_i ≤ 2.0`).
Both gates are reported. **Agreement closes the instrument question; disagreement is reported as an
open instrument problem, not resolved in favour of whichever is more convenient.**

**3. Registered expectations, so the corrected gate is falsifiable rather than merely permissive.**
A gate that certifies everything is not a gate. Predicted outcomes for Phase 3b, recorded before it runs:

- **Elias FAILS the primary gate** (`scene_overlap` = 0 at baseline — his probe never elicited the scene
  in Phase 3, identical continuations in all three conditions). If Elias *passes*, the corrected gate is
  more permissive than intended and that is reported as a problem with the gate.
- **Marek passes the gate but returns (c) underpowered** (baseline trait rank ≈ 900).
- **The remaining five — Greta, Nadia, Maria, Simon, Bruno — pass and return (b) held scene.**
- **No character returns held latent.** A held-latent result would be a genuine surprise and is the
  outcome most worth reporting if it appears.

Recording the expected answer costs nothing when the analysis is mechanical, and it converts "the gate
let more characters through" from a reassuring observation into a checkable one.

**4. Deliberately NOT changed.** Scene keywords are **not** re-picked, despite the Phase 3 finding that
the model's first-emitted words (`covered`, `opens`) had been dropped for filler leakage. Re-picking
keywords after seeing which ones the model says would tune the stimulus to the observed output; the
position-agnostic secondary gate addresses the same problem without touching the pre-registered word
lists. The roster is likewise not back-filled and the underpowered characters are not replaced.

Build artifacts: `build_phase3b.py` → `trait_persistence_v2_phase3b.ipynb`, analysed by
`analyze_phase3b.py`. Outputs are `phase3b_*` so they never collide with Phase 3's.

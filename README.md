# j-lens-trait-persistence-test-v2

*Independent research — no affiliated lab, no funding, single author, run on a free Colab T4. Small-n,
single-model, exploratory; stated as such throughout. Experiments designed and pre-registered by the
author; code, analysis scripts, and much of the prose written with Claude (Anthropic). Not
peer-reviewed.*

**Findings and full write-up → [`phase2/PHASE2_RESULTS.md`](phase2/PHASE2_RESULTS.md) (Q1/Q2/Q5) and
[`phase3/PHASE3_RESULTS.md`](phase3/PHASE3_RESULTS.md) (Q3, the KV-ablation)**

Does a character trait that is **stated outright** ("Maria is generous") stay *retrievable* in a
language model's internal state differently from one that must be **inferred from behaviour**
("Maria covered a colleague's rent and never mentioned it")? And when an inferred trait is
retrievable later, is it because the model **stored** it — or because it **re-derives** it on demand
from the scene it originally read?

Measured with the **Jacobian lens** on `google/gemma-3-4b-it`.

> **Status: complete (Q1 + Q2 + Q5), run 2026-07-21.** Pre-registration committed before any code.
> Phase 1 (calibration + screening) and Phase 2 (the cued sweep + the §7a extension to d=30) have run
> on Colab T4. **Headline: no detectable stated-vs-inferred retrievability difference at any distance
> — and, contra v1, the inferred trait does not collapse.** Full write-up in
> [`phase2/PHASE2_RESULTS.md`](phase2/PHASE2_RESULTS.md). Q3 and Q4 remain deferred by design.

This supersedes
[`j-lens-trait-persistence-test`](https://github.com/manu-scriptum/j-lens-trait-persistence-test)
(v1, run 2026-07-13), which stays frozen as the record of that run. The design authority for v2 is
[`trait_persistence_v2_spec.md`](trait_persistence_v2_spec.md).

## Why there is a v2

v1's central problem: 11 of its 13 checkpoints were passive reads at sentence-final periods. That
measures what the model spontaneously tends to emit at a period — mostly sentence-openers — not
whether a concept can be **retrieved when something asks for it**. A cache can only be tested by
querying it. v1 contained exactly one accidental cache-read, the bare-name reintroduction, and that
one produced its most interesting result.

v2 makes every checkpoint a query. It also fixes: a single-token target that badly undercounted the
concept (now a concept lexicon), a normalisation that masked the real effect (now always arm vs. its
own control, never d0-normalised), an inherited layer band nobody checked on this model (now
calibrated), unscreened stimuli (now gated), and a real place-name and role-priming in the shared
opening (now neutralised).

## Questions

| | question | status | result |
|---|---|---|---|
| **Q1** | Under *cued* retrieval, does a stated trait stay more retrievable than an inferred one across intervening text? | answered | **no detectable difference** (Wilcoxon p=0.81; holds to d=30) |
| **Q2** | Is the stated arm's persistence trait-specific, or generic token-echo? | answered | **not word-echo** — content-specific (tracer near its own floor) |
| **Q5** | Does the J-lens read what the logit lens can't? | answered | mixed, n=3: clean for Greta, partial Nadia, none Elias |
| **Q3** | Is a retrievable inferred trait a **held latent** or a **held scene**? | answered | **held scene** — 0/7 held-latent; mask the scene and the trait goes |
| **Q4** | Does an inferred trait stay bound to the right entity under interference? | stub; not this run | — |

**Q3 is deferred, and that is deliberate.** Answering it means ablating the behavioural sentence's
keys and values and re-probing — an *intervention*, needing KV-patching scaffolding plus its own
validation that the ablation removed the trace rather than just breaking the model. That is out of
reach of a read-only lens rig on a Colab T4. v1's own follow-up spec reached this conclusion first:
*"park the causal ablation as a proper-lab step, not the immediate next run."*

> **Update (2026-07-21, post-run):** the "out of reach / proper lab" call was a misjudgement. A full
> KV-ablation of `gemma-3-4b-it` *is* runnable on this setup — forward pre-hooks on the attention
> modules, the mechanism `prediction.md` §7b already pins. The researcher underestimated the setup;
> Fable caught it. **Q3's infeasibility deferral is lifted and the ablation is the planned next arm**
> — decision rule (§3) and mask-check gate (§7b) already frozen and unchanged. The text above stays as
> the dated record of what was believed. See `prediction.md` §9 (2026-07-21, post-run).

So this run is **the corrected replication, done properly** — which v1 could not do, because it could
measure cued retrievability at exactly one accidental checkpoint out of thirteen. Q1's cued sweep
across distance also delivers the *distance* half of the "differential fragility" read v1 proposed as
the ablation's observational shadow. It is correlational, and **no held-latent-vs-held-scene claim is
drawn from it.**

The held-concept question's natural next step is not the ablation but v1's **direction probe** —
reading the trait as a linear direction rather than a word, which v1's spec judged *cleaner than the
ablation* for this question and, being a readout, within reach. That is a separate run.

## Findings

Run 2026-07-21 on `gemma-3-4b-it`; n = 7 survivors (screening dropped 3 of 10, no back-fill), band
13–26. All results descriptive, against the frozen §3 criteria. Full detail and per-character tables
in [`phase2/PHASE2_RESULTS.md`](phase2/PHASE2_RESULTS.md).

- **Q1 — no detectable stated-vs-inferred difference.** Wilcoxon p = 0.81 in the primary window and
  p = 0.94 across the §7a extension to d = 30; the median ratio-to-control is effectively identical
  for the two arms throughout. Not a finding of "stated wins", per the pre-registered rule.
- **The headline is what did *not* happen: the inferred trait does not collapse.** Under cued
  retrieval it stays retrievable out to **d = 30** (5–6 of 7 characters) — the direct opposite of v1's
  passive-read result, where inference vanished after a *single* filler sentence. v1's "collapse" was
  an artifact of reading at sentence-ends instead of querying.
- **The null is real, not a range ceiling.** The §7a extension was run precisely to check whether the
  absent separation was both arms pinned near the rank floor. It is not: control ranks sit at ~200–300
  at long distance (ample room), yet the arms stay indistinguishable.
- **Strong per-character heterogeneity.** Greta, Marek, Maria lean stated-more-retrievable; Nadia,
  Simon lean the other way; **Elias ("loyal") is anomalous** — the stated trait reads *worse* than the
  no-trait control, a weak-cue failure flagged rather than dropped.
- **Q2 — the direct arm's persistence is content-specific, not word-echo.** The neutral tracer sits
  near its own control floor while the trait persists near ceiling. (Formally "ambiguous" by the frozen
  threshold, but the direction is unambiguous.)
- **Q5 — mixed, n = 3** (only where the logit positive control passed): a clean J-lens > logit-lens
  advantage for Greta (reads the never-tokenised trait the logit lens has buried), partial for Nadia,
  none for Elias. Reported as instrument sensitivity, not a representation claim.

**No held-latent-vs-held-scene claim is drawn** (Q3 deferred). The natural next run is v1's direction
probe, above.

> **Update (2026-07-21) — Q3 has since run.** The KV-ablation answers it: **held scene.** Masking the
> behavioural sentence's attention keys collapses inferred-trait retrievability (30–172× at d=10) while
> an equally sized filler ablation does nothing; **0 of 7 characters show a held latent.** The
> symmetric direct-arm test shows the *stated* trait is equally dependent on its literal token (median
> ×56 when masked, ×0.90 for a neutral word). So Phase 2's null reads as **"no difference because
> neither is stored"** — both arms are reconstructed on demand from source text that never left the
> context. Full write-up, including a documented gate flaw that cost three certifications:
> [`phase3/PHASE3_RESULTS.md`](phase3/PHASE3_RESULTS.md).

## Design

Ten candidate characters (5 positive / 5 negative traits), screened to a target of eight. Each has
three arms sharing an identical opening, filler block, and cue set — only the trigger differs:

- **direct** — trait stated, with a neutral **tracer** word embedded (the Q2 control)
- **inferred** — trait implied by one behavioural sentence; the trait word never appears
- **control** — a trait-neutral behavioural sentence, matched to the inferred one in length *and
  topic domain* (same objects, same setting, different action)

At each distance d ∈ {0, 1, 2, 4, 7, 10} filler sentences (extended to {15, 20, 30} by the
pre-registered §7a conditional run), a **separate forked forward pass** appends a retrieval cue to a
byte-identical prefix:

- **Cue A** — `"Tom glances at NAME."` (entity cue, topic-free)
- **Cue B** — `"What kind of person is NAME? NAME is"` (trait query; carries the primary contrast)

Primary measure: **best rank across the trait's concept lexicon, median over the calibrated band**,
always as a ratio against the control arm at the same distance and cue.

Every read is also computed with a plain **logit lens** as a registered robustness stream that gates
no conclusion. It answers the question of whether the J-lens is load-bearing: if a plain unembedding
readout shows the same effect, the finding is not instrument-specific. A logit-lens *null* is only
interpretable where the logit lens passed a per-character positive control at d0 — otherwise it can't
be told apart from an instrument that simply can't see at these depths.

## Files

- [`prediction.md`](prediction.md) — the pre-registration. **Read this first.** All numeric criteria
  are pinned there; §9 logs every dated amendment (n=7, the tracer swaps, the §7a extension).
- [`trait_persistence_v2_stimuli.py`](trait_persistence_v2_stimuli.py) — canonical stimuli, lexicons, tracers, cues, filler. Part of the
  pre-registration, not implementation; the notebooks import it rather than restating any string.
- [`trait_persistence_v2_spec.md`](trait_persistence_v2_spec.md) — the design spec.
- **Primers (plain-language):** [`PHASE2_PRIMER.md`](PHASE2_PRIMER.md) walks through the Phase 2 run;
  [`PHASE3_PRIMER.md`](PHASE3_PRIMER.md) walks through the Q3 ablation.
- **Notebooks (Colab T4):** [`trait_persistence_v2_phase1.ipynb`](trait_persistence_v2_phase1.ipynb) (calibration + screening),
  [`trait_persistence_v2_phase2.ipynb`](trait_persistence_v2_phase2.ipynb) (the cued sweep),
  [`trait_persistence_v2_phase2ext.ipynb`](trait_persistence_v2_phase2ext.ipynb) (the §7a extension),
  [`trait_persistence_v2_phase3.ipynb`](trait_persistence_v2_phase3.ipynb) (the Q3 KV-ablation — built, not yet run).
  Built by the matching `build_*.py`.
- **Data + write-ups:** [`phase1/`](phase1/) (band + screening outputs, `PHASE1_NOTES.md`),
  [`phase2/`](phase2/) (the sweep + extension CSVs, `PHASE2_RESULTS.md`), and
  [`phase3/`](phase3/) (the ablation CSVs, [`PHASE3_RESULTS.md`](phase3/PHASE3_RESULTS.md)).
- **Analysis:** [`analyze_phase2.py`](analyze_phase2.py) (primary) and
  [`analyze_phase2ext.py`](analyze_phase2ext.py) (combined trend); [`analyze_phase3.py`](analyze_phase3.py)
  (the Q3 verdict behind the §7b gate) and [`analyze_phase3_posthoc.py`](analyze_phase3_posthoc.py)
  (the labelled post-hoc gate re-scoring). Pure stdlib; exact Wilcoxon.

## Running the notebooks

Each runs on a Colab **T4 GPU**; no local GPU needed. Open a notebook from GitHub, set
`Runtime → Change runtime type → T4 GPU`, and clone this repo in a first cell so the stimuli and the
Phase 1 outputs are present:

```
!git clone https://github.com/manu-scriptum/j-lens-trait-persistence-test-v2.git
%cd j-lens-trait-persistence-test-v2
```

`google/gemma-3-4b-it` is gated: accept the license on Hugging Face, then add your token as a Colab
secret named `HF_token` (key icon; enable notebook access). Run top to bottom and download the outputs
listed in the final cell. Phase 2 and the extension read the band and roster from `phase1/`, never
from a literal. (Note: jlens truncates at 512 tokens by default; the extension notebook raises
`max_seq_len` so the long d=30 sequences are not silently cut — see the fix in `build_phase2ext.py`.)

## Registered but not run

Q3's KV-ablation stays fully specified in `prediction.md` (§3 decision rule, §7b implementation gate)
so it can be picked up unchanged if the tooling ever becomes available. The gate is the part worth
keeping visible: a failed attention mask produces a null **indistinguishable from Q3 outcome (b)**,
which is the more surprising of the two findings — so D5 is reportable only if the mask demonstrably
removes the scene, and a failed check reports **not-run, never a null**. Without that, a bug could
manufacture the more interesting result.

> **Update (2026-07-21, post-run):** "if the tooling ever becomes available" — it already is. The
> ablation runs on this setup (forward pre-hooks, the §7b mechanism). Q3 has moved from *registered
> but not run* to **the planned next arm**; the frozen §3/§7b machinery above governs it unchanged.
> See `prediction.md` §9.
>
> **Update (2026-07-21, Q3 build):** Q3 is now **built and ready to run** — not yet run, no results.
> [`trait_persistence_v2_phase3.ipynb`](trait_persistence_v2_phase3.ipynb) (from
> [`build_phase3.py`](build_phase3.py)) does the ablation on Colab; [`analyze_phase3.py`](analyze_phase3.py)
> applies the frozen §3 verdict behind the §7b gate. The concrete realisations — d=10 decision
> checkpoint, scene span, matched-filler control, the eager-attention mask hook, the scene-keyword gate
> thresholds, the symmetric direct-arm test — are pinned in `prediction.md` §9 ("Q3 implementation
> pinned"), committed **before any ablation number exists**. Plain-language walkthrough:
> [`PHASE3_PRIMER.md`](PHASE3_PRIMER.md).

Q4 (two-entity interference) is a documented stub. Note that "Tom" is spent as a neutral name — it
appears in Cue A in every prefix — so Q4 needs a different second entity if unstubbed.

## Scope and honesty

A small measurement on one open 4B model through one interpretability tool. It probes
**trait-concept retrievability in the residual stream via the J-lens** — not "the global workspace"
in any theory-laden sense. n = 7 (screening dropped 3 of 10, no back-fill) is small and single-item
medians are draggable by one character — Elias demonstrably drags this one; per-character results are
reported alongside any aggregate, and anything that does not clear a pre-registered criterion is
described in descriptive language, not as a finding.

`LICENSE` (MIT) — code. `LICENSE-docs` (CC BY 4.0) — writeup and data.

# j-lens-trait-recall-test (v2)

Does a character trait that is **stated outright** ("Maria is generous") stay *retrievable* in a
language model's internal state differently from one that must be **inferred from behaviour**
("Maria covered a colleague's rent and never mentioned it")? And when an inferred trait is
retrievable later, is it because the model **stored** it — or because it **re-derives** it on demand
from the scene it originally read?

Measured with the **Jacobian lens** on `google/gemma-3-4b-it`.

> **Status: Phase 1 built, not yet run.** Pre-registration committed before any code. Phase 1
> (calibration + screening) runs in Colab; Phase 2 (main sweep + ablation) is written once Phase 1's
> outputs come back.

This supersedes
[`j-lens-trait-persistence-test`](https://github.com/manu-scriptum/j-lens-trait-persistence-test)
(v1, run 2026-07-13), which stays frozen as the record of that run. The design authority for v2 is
[`trait_recall_v2_spec.md`](trait_recall_v2_spec.md).

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

| | question | status |
|---|---|---|
| **Q1** | Under *cued* retrieval, does a stated trait stay more retrievable than an inferred one across intervening text? | corrected replication |
| **Q2** | Is the stated arm's persistence trait-specific, or generic token-echo? | tracer control |
| **Q5** | Does the J-lens read what the logit lens can't? | free instrument check |
| **Q3** | Is a retrievable inferred trait a **held latent** or a **held scene**? | **deferred — not this run** |
| **Q4** | Does an inferred trait stay bound to the right entity under interference? | stub; not this run |

**Q3 is deferred, and that is deliberate.** Answering it means ablating the behavioural sentence's
keys and values and re-probing — an *intervention*, needing KV-patching scaffolding plus its own
validation that the ablation removed the trace rather than just breaking the model. That is out of
reach of a read-only lens rig on a Colab T4. v1's own follow-up spec reached this conclusion first:
*"park the causal ablation as a proper-lab step, not the immediate next run."*

So this run is **the corrected replication, done properly** — which v1 could not do, because it could
measure cued retrievability at exactly one accidental checkpoint out of thirteen. Q1's cued sweep
across distance also delivers the *distance* half of the "differential fragility" read v1 proposed as
the ablation's observational shadow. It is correlational, and **no held-latent-vs-held-scene claim is
drawn from it.**

The held-concept question's natural next step is not the ablation but v1's **direction probe** —
reading the trait as a linear direction rather than a word, which v1's spec judged *cleaner than the
ablation* for this question and, being a readout, within reach. That is a separate run.

## Design

Ten candidate characters (5 positive / 5 negative traits), screened to a target of eight. Each has
three arms sharing an identical opening, filler block, and cue set — only the trigger differs:

- **direct** — trait stated, with a neutral **tracer** word embedded (the Q2 control)
- **inferred** — trait implied by one behavioural sentence; the trait word never appears
- **control** — a trait-neutral behavioural sentence, matched to the inferred one in length *and
  topic domain* (same objects, same setting, different action)

At each distance d ∈ {0, 1, 2, 4, 7, 10} filler sentences, a **separate forked forward pass** appends
a retrieval cue to a byte-identical prefix:

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
  are pinned there, including the screening thresholds, which were frozen rather than tuned.
- [`trait_recall_v2_stimuli.py`](trait_recall_v2_stimuli.py) — canonical stimuli, lexicons, tracers, cues. Part of the
  pre-registration, not implementation; the notebook imports it rather than restating any string.
- [`trait_recall_v2_spec.md`](trait_recall_v2_spec.md) — the design spec.
- [`trait_recall_v2_phase1.ipynb`](trait_recall_v2_phase1.ipynb) — Phase 1: calibration + screening.

## Running Phase 1

Runs on a Colab **T4 GPU**; no local GPU needed.

1. Open `trait_recall_v2_phase1.ipynb` in Colab; `Runtime → Change runtime type → T4 GPU`.
2. Upload `trait_recall_v2_stimuli.py` alongside it (folder icon, left sidebar), or clone this repo.
3. `google/gemma-3-4b-it` is gated: accept the license on Hugging Face, then add your token as a
   Colab secret named `HF_token` (key icon; enable notebook access).
4. Run top to bottom, then download every file listed in the final cell.

Two outputs to actually read rather than scroll past: the **single-token report** (a trait down to
fewer than 4 surviving lexicon entries is underpowered and must be flagged) and the **screening
table** (which characters passed, and whether the valence balance survived).

## Registered but not run

Q3's KV-ablation stays fully specified in `prediction.md` (§3 decision rule, §7b implementation gate)
so it can be picked up unchanged if the tooling ever becomes available. The gate is the part worth
keeping visible: a failed attention mask produces a null **indistinguishable from Q3 outcome (b)**,
which is the more surprising of the two findings — so D5 is reportable only if the mask demonstrably
removes the scene, and a failed check reports **not-run, never a null**. Without that, a bug could
manufacture the more interesting result.

Q4 (two-entity interference) is a documented stub. Note that "Tom" is spent as a neutral name — it
appears in Cue A in every prefix — so Q4 needs a different second entity if unstubbed.

## Scope and honesty

A small measurement on one open 4B model through one interpretability tool. It probes
**trait-concept retrievability in the residual stream via the J-lens** — not "the global workspace"
in any theory-laden sense. n = 8 is small; per-character results are reported alongside any
aggregate, and anything that does not clear a pre-registered criterion is described in descriptive
language, not as a finding.

`LICENSE` (MIT) — code. `LICENSE-docs` (CC BY 4.0) — writeup and data.

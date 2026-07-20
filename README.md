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

This supersedes [`workspace-stickiness-test`](../workspace-stickiness-test) (v1, run 2026-07-13),
which stays frozen as the record of that run. The design authority for v2 is
[`trait-persistence-v2-spec.md`](trait-persistence-v2-spec.md).

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
| **Q3** | Is a retrievable inferred trait a **held latent** or a **held scene**? | the new science |
| **Q4** | Does an inferred trait stay bound to the right entity under interference? | stub; cuttable |

Q3 is the one worth running this for. Ablate the behavioural sentence's keys/values and re-probe:
if retrieval survives, the model wrote a trait representation somewhere outside the scene tokens. If
it collapses, there was never a stored trait — only cached behaviour, re-read on demand. **Both
outcomes are publishable**, which is the property the pre-registration exists to protect.

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

## Files

- [`prediction.md`](prediction.md) — the pre-registration. **Read this first.** All numeric criteria
  are pinned there, including the screening thresholds, which were frozen rather than tuned.
- [`stimuli_v2.py`](stimuli_v2.py) — canonical stimuli, lexicons, tracers, cues. Part of the
  pre-registration, not implementation; the notebook imports it rather than restating any string.
- [`trait-persistence-v2-spec.md`](trait-persistence-v2-spec.md) — the design spec.
- [`trait_recall_v2_phase1.ipynb`](trait_recall_v2_phase1.ipynb) — Phase 1: calibration + screening.

## Running Phase 1

Runs on a Colab **T4 GPU**; no local GPU needed.

1. Open `trait_recall_v2_phase1.ipynb` in Colab; `Runtime → Change runtime type → T4 GPU`.
2. Upload `stimuli_v2.py` alongside it (folder icon, left sidebar), or clone this repo.
3. `google/gemma-3-4b-it` is gated: accept the license on Hugging Face, then add your token as a
   Colab secret named `HF_token` (key icon; enable notebook access).
4. Run top to bottom, then download every file listed in the final cell.

Two outputs to actually read rather than scroll past: the **single-token report** (a trait down to
fewer than 4 surviving lexicon entries is underpowered and must be flagged) and the **screening
table** (which characters passed, and whether the valence balance survived).

## Known open risk

The Q3 KV-ablation needs attention masking over a token span. Whether the public `jlens` API exposes
this is **not yet verified** — if it does not, Phase 2 will drive it with forward hooks on the
underlying HF model. Flagged here rather than discovered at implementation time. The spec's own
guard applies: verify on one example that the mask actually removes the scene (the model can no
longer answer "what did NAME do?") *before* trusting any trait measurement taken under it.

## Scope and honesty

A small measurement on one open 4B model through one interpretability tool. It probes
**trait-concept retrievability in the residual stream via the J-lens** — not "the global workspace"
in any theory-laden sense. n = 8 is small; per-character results are reported alongside any
aggregate, and anything that does not clear a pre-registered criterion is described in descriptive
language, not as a finding.

`LICENSE` (MIT) — code. `LICENSE-docs` (CC BY 4.0) — writeup and data.

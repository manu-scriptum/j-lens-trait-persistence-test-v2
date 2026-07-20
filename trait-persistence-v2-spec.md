# Trait persistence and retrieval, v2 — experiment specification

Status: design spec for a fresh implementation. Supersedes the v1 run of 2026-07-13
(`workspace_stickiness.ipynb`). Written to be handed to a Claude Code instance together with the v1
results document and `prediction.md`; the implementer should read both before writing code, but this
spec is self-contained.

---

## 0. Context for the implementer

v1 asked whether a character trait introduced by *statement* ("Maria is generous") versus by
*implication* ("Maria gave her last bread to a stranger and offered him shelter") differs in (a) how
long it persists in J-lens readouts across neutral filler text, and (b) whether re-mentioning the
character by bare name reactivates it.

v1's headline findings, after the 2026-07-14 correction:

1. Inference is readable at the trigger (4/5 characters) but collapses within one filler sentence.
2. The **verbatim (stated) trait persists** — 25–54% below its own frequency-floor control at all ten
   filler checkpoints for 3/5 characters (registered outcome #2, "direct decays slower").
3. Bare-name reintroduction reactivates the **inferred** trait above its control in 3/5 — modest,
   deep-rank, but topic-free and therefore the cleanest evidence of entity-binding in the dataset.
4. Proposed mechanism: **re-read vs. re-derive.** The stated trait leaves a literal token whose
   key/value the model can attend back to (symbol lookup). The inferred trait was never tokenized —
   only the behavioural scene is cached — so re-cueing it requires re-running the inference.

v1's design flaws, all identified in its own §3–§5, which v2 exists to fix:

- **F1.** 11 of 13 checkpoints were passive reads at sentence-final periods, which measure spontaneous
  saliency ("what wants to be said at a period" — mostly sentence-openers), not cued retrievability.
  A cache can only be tested by querying it. v1 accidentally had exactly one valid cache-read (the
  reintroduction).
- **F2.** The registered target was a single-token adjective, which badly undercounted the concept
  (Maria: `generous` at rank 768 while `donations/charity/kindness` sat at rank 1 across most of the
  band). Single-token restriction is a known J-lens limitation; the measure must be a concept lexicon.
- **F3.** The decay metric normalized each arm to its own d0, which the direct arm's surface echo
  (rank ≈ 3) dominated — producing a trivial "no shape difference" that masked the real persistence
  difference. All v2 comparisons are **arm vs. its own control at the same checkpoint**, never
  d0-normalized shape.
- **F4.** Open fork: direct-arm persistence could be trait-specific holding OR generic token-echo
  (any trigger word getting a downstream rank boost from repetition/copy bias). Unresolved in v1;
  v2 resolves it with a tracer control (D4).
- **F5.** One character (Peter/`patient`) produced no d0 inference at all — stimuli were not screened
  for inference strength before the full sweep.
- **F6.** Uncontrolled associations in the shared opening (real city name "Lyon", role-priming from
  occupations, lexical adjacency in control behaviours).
- **F7.** Single entity per text — no test of binding fidelity under interference.
- n = 5, no statistics, non-balanced trait valence.

---

## 1. Research questions, in priority order

- **Q1 (primary).** Under *cued retrieval*, does a stated trait remain more retrievable than an
  inferred trait across intervening text? (v1 could only show this at one accidental checkpoint.)
- **Q2 (primary).** Is direct-arm persistence trait-specific or generic token-echo? (F4 tracer test.)
- **Q3 (primary).** Is the inferred trait, when retrievable at re-mention, a **held latent** (a
  trait representation stored somewhere at/after the trigger, independent of the scene tokens) or a
  **held scene** (nothing trait-specific stored; the trait is re-inferred from the cached behaviour
  tokens on demand)? This is the KV-ablation experiment (D5) and the potentially novel result.
- **Q4 (secondary).** Does an inferred trait stay bound to the *correct* entity when a second,
  trait-neutral entity is present? (Interference/binding-fidelity; addresses F7. Can be cut if
  budget is tight.)

Q1+Q2 are the corrected replication. Q3 is the new science. Do not let Q4 endanger Q1–Q3.

## 2. Registered outcomes (write these into prediction.md BEFORE running the main sweep)

For Q1, three outcomes: (1) stated more retrievable at all distances; (2) no detectable difference;
(3) inferred more retrievable. No directional prediction registered, though v1 + mechanism predict (1).

For Q2, two outcomes: (a) tracer word does NOT show below-floor persistence comparable to the stated
trait → persistence is trait/content-specific; (b) tracer persists comparably → direct-arm result is
substantially copy/repetition bias, and only cued-retrieval and reintroduction contrasts remain
interpretable for the stated arm.

For Q3, three outcomes: (a) retrieval in the inferred arm survives behaviour-KV ablation at least
partially → held latent exists; (b) retrieval goes to zero → pure re-inference from scene; (c)
retrieval was too weak pre-ablation to measure → underpowered, report as such.

Decide and write down, in advance, the exact numeric criterion for "retrievable" and "survives"
(suggested: concept-lexicon best rank within top-50 over the workspace band; ratio-to-control < 0.8).
The v1 lesson: the metric you don't pre-commit is the metric that betrays you.

---

## 3. Model, tooling, calibration

- Model: `google/gemma-3-4b-it` for continuity with v1. If compute allows, replicate headline
  contrasts on one larger open model (e.g. a 12B–27B instruct model) — v1 is a 4B-only result and
  inference strength should scale.
- Lens: same jlens implementation, pinned commit recorded in the results doc.
- **Calibration step (run first, before any stimuli):** sweep the lens over ~20 neutral documents and
  locate the workspace band for this model empirically — kurtosis onset, autocorrelation onset, and
  the late layer where readouts collapse into next-token prediction. Record the band. All "median
  over band" statistics use this band. Do not inherit v1's layers 12–29 without checking; justify
  the band in the doc with the calibration plots.
- Skip the first 4–5 tokens of every document in any aggregate statistic (high-norm token artifact).

## 4. Design

### D0. Stimulus construction and screening (fixes F5, F6)

- 8 characters minimum (up from 5), traits balanced: 4 positive, 4 negative (v1 was 4:1).
- Each character exists in three text variants sharing an identical opening and identical filler:
  - `direct`: trait stated in one sentence ("Maria is generous.")
  - `inferred`: trait implied by one behavioural sentence, trait word and close derivatives absent.
  - `control`: matched behavioural sentence implying no trait, matched in length and, as far as
    possible, in topic domain (F6: v1's control triggers differed in topic from inferred triggers;
    minimize this — e.g. both sentences involve the same objects/setting, only the action differs).
- Neutralize the opening: invented town name (no "Lyon"), occupations chosen to be trait-neutral for
  that character's trait (no clinic worker for `brave`), no control behaviours lexically adjacent to
  the trait (no tool-laying for `patient`).
- **Screening gate:** before the main sweep, run d0-only reads on all candidate stimuli. A character
  enters the main experiment only if the inferred trigger produces concept-lexicon best rank ≤ 200
  vs. control ≥ 5× worse (tune thresholds on the first two characters; then freeze). Replace failing
  stimuli (this is what Peter needed). Screening reads are exploratory by definition; record them.

### D1. Concept-lexicon targets (fixes F2)

For each trait, declare BEFORE running: a lexicon of 6–12 single tokens covering the adjective,
synonyms, and noun forms (`generous, generosity, charity, charitable, giving, kindness, donations`…),
each verified to be a single token (leading-space form) in the model's tokenizer; drop multi-token
entries. Primary measure: **best rank within the lexicon**, median over the workspace band. Keep the
bare adjective as a secondary measure for v1 comparability. Also record top-20 vocabulary at every
checkpoint (v1's E-analyses were only possible because this was stored — keep doing it).

### D2. Cued retrieval at every checkpoint (fixes F1 — the core design change)

Replace passive period-reads with **query probes**. At each distance d ∈ {0, 1, 2, 4, 7, 10} filler
sentences, create a separate forked continuation of the text that appends a retrieval cue, and read
the lens on the cue tokens:

- Cue A (entity cue, topic-free): a sentence that re-mentions the name with no content, e.g.
  "Tom glances at NAME." Read at the tokens following the name.
- Cue B (trait query): an explicit question, "What kind of person is NAME? NAME is". Read at the
  final position (pre-answer), where a trait adjective is contextually *possible* — the exact thing
  v1's periods made impossible.

Each fork is a fresh forward pass on (shared prefix + cue); the prefix through distance d is
byte-identical across arms and checkpoints, so all differences are attributable to arm and cue.
Passive period-reads can be kept as a cheap third stream for v1 comparability, but they are explicitly
labeled "spontaneous saliency" and carry no persistence claims.

Primary Q1 contrast: at each d, lexicon best-rank under Cue B, each arm vs. its own control
(ratio < 1 = retrievable above floor). Never d0-normalized shape (F3).

### D3. Reintroduction

Keep v1's topic-free bare-name reintroduction after the full filler as a distinguished checkpoint
(it is Cue A at max distance, plus a continuation read). v1's inferred-above-control 3/5 result
should replicate here with more power.

### D4. Token-echo tracer control (resolves F4 / Q2)

In every `direct` trigger sentence, embed a pre-declared neutral content word of comparable frequency
to the trait word (e.g. "Maria is generous, she thinks, setting down the **lantern**."). Track the
tracer's rank vs. its own control-arm floor across all checkpoints with the identical machinery. If
the tracer shows the same below-floor persistence as the trait word, the stated arm's passive
persistence is copy-bias; the interpretation of Q1 then rests entirely on the cued reads (which is
fine — that is what they are for). Choose tracers with no semantic relation to trait, character, or
filler; declare them in prediction.md.

### D5. KV-ablation: held latent vs. held scene (Q3 — run only on characters that pass D2/D3)

On the `inferred` arm, at the reintroduction/Cue-B checkpoint:

- Condition i (baseline): normal forward pass. Measure trait retrievability.
- Condition ii (scene ablation): zero/mask the keys and values of the behavioural-trigger sentence's
  token positions (all layers, or per-band if the implementation allows) so the cue positions cannot
  attend back into the scene. Measure retrievability again.
- Condition iii (control ablation): identically sized KV mask over a matched filler sentence.

Interpretation: retrieval surviving (ii) at above (iii)-level → a trait latent was written somewhere
outside the scene tokens (candidate positions: end of trigger sentence, subsequent name mentions) —
a held latent. Retrieval collapsing in (ii) but not (iii) → pure re-inference from the cached scene.
Symmetric test on the `direct` arm: ablate only the trait-token position's KV; the drop isolates how
much of stated-arm retrieval is the literal symbol.

Implementation note: masking attention to a position-set is the cleanest form (set attention logits
to −inf toward those source positions at every layer/head); zeroing V for those positions is an
acceptable alternative. Verify on one example that the mask actually removes the scene (model can no
longer answer "what did NAME do?") before trusting the trait measurements.

### D6 (optional, Q4). Two-entity interference

Add a second, trait-neutral named character to the text before the trigger. At reintroduction, cue
each name separately; measure whether the inferred trait selectively follows the correct entity
(trait rank under "NAME1" cue vs. under "NAME2" cue). Only run if D2–D5 are healthy.

## 5. Checkpoints, bookkeeping, statistics

- Distances: d ∈ {0, 1, 2, 4, 7, 10}; each with Cue A and Cue B forks per arm; plus the
  reintroduction. This is ~3 arms × 6 distances × 2 cues × 8 characters ≈ 300 forward passes plus
  ablations — cheap on a T4 for a 4B model, but budget it.
- With n = 8 per cell, report per-character results plus sign-test / Wilcoxon on the arm-vs-control
  ratios across characters. Still small; say so. Descriptive language for anything that doesn't
  clear the pre-registered criterion.
- Store: full rank sweep CSV, top-20 vocab CSV, summary CSV, exact stimuli with checkpoint token
  indices, pinned environment, lens commit, calibration plots. Same file discipline as v1 — it is
  the reason v1's correction was even possible.
- Results doc structure: replicate v1's (at-a-glance → confirmatory → exploratory walled off →
  interpretation → limitations), and keep the habit of dating any post-hoc correction and marking
  superseded lines inline rather than editing them away.

## 6. Analysis pitfalls to hand the implementer explicitly

- Never compare absolute ranks across different trait words (base-frequency floors differ); only
  ever arm vs. its own control at the same checkpoint and cue.
- Never d0-normalize (F3).
- The direct arm at d0 is surface echo; exclude d0 from any persistence claim for that arm.
- Reads on cue tokens, not on the period before them.
- Median over the calibrated band, but also store per-layer — v1's E4 check (did the median hide a
  sub-band signal?) should be repeated.
- If a result seems to hinge on one character, say so; n = 8 medians can be dragged by one item.
- If the lens shows nothing anywhere, check band calibration and tokenizer forms (leading space!)
  before concluding absence. Instrument first, phenomenon second.

## 7. What would count as the headline, in advance

- Q1 outcome (1) + Q2 outcome (a): "Stated traits are more retrievable than inferred traits across
  intervening text, and this is content-specific, not copy bias" — a clean, corrected replication
  with the re-read vs. re-derive mechanism intact.
- Q3 outcome (a): "A trait inferred from behaviour leaves a retrievable latent independent of the
  scene it was inferred from" — a held entity-bound concept, demonstrated by ablation. This is the
  result worth writing up properly if it lands.
- Q3 outcome (b) is also publishable-as-a-note: "inferred traits are not stored; they are recomputed
  from the cached scene on demand" — a concrete statement about where transformer 'memory' lives.

Either Q3 outcome is interesting. That is the mark of a good experiment; protect it.

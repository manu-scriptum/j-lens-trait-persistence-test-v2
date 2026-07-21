# Phase 3b results — Q3 re-run with the corrected gate

Run 2026-07-21 (same day as Phase 3), `trait_persistence_v2_phase3b.ipynb` on Colab T4; analysed with
[`analyze_phase3b.py`](../analyze_phase3b.py). Governed by [`prediction.md`](../prediction.md) §9,
"Phase 3b: corrected gate registered as primary", committed **before this run**. The §3 verdict rule and
the §7b criterion are unchanged and used verbatim; only the *realisation* of the mask-check was repaired.

**Read [`phase3/PHASE3_RESULTS.md`](../phase3/PHASE3_RESULTS.md) first.** This run does not supersede it;
it certifies it.

## Headline

1. **Q3 answer, now properly certified: held scene.** 5 held-scene, 1 underpowered, 1 not-run,
   **0 held-latent**, on a gate fixed before the data existed.
2. **All 7 registered expectations matched — including the one that mattered: Elias failed.** §9 recorded
   in advance that the corrected gate must *reject* Elias or stand accused of being merely permissive.
   It rejected him. The gate admits and rejects.
3. **The replication is exact.** Every trait read reproduces Phase 3 to the digit — largest relative
   deviation **0.0%**, across two separate Colab sessions.
4. **The two gates disagree on Elias.** Reported as an open instrument problem, per the registered rule,
   not resolved in favour of the convenient one.

## 1. Verdict (d = 10, Cue B — the pinned decision checkpoint)

| character | primary gate | secondary gate | verdict | `R_ii/R_iii` | `R_i / R_ii / R_iii` |
|---|---|---|---|---:|---|
| Bruno (lazy) | PASS | PASS | **(b) held scene** | 171.9× | 4.0 / 687.5 / 4.0 |
| Simon (curious) | PASS | PASS | **(b) held scene** | 147.8× | 2.0 / 295.5 / 2.0 |
| Greta (dishonest) | PASS | PASS | **(b) held scene** | 126.3× | 18.0 / 2462.5 / 19.5 |
| Nadia (brave) | PASS | PASS | **(b) held scene** | 106.7× | 3.5 / 320.0 / 3.0 |
| Maria (generous) | PASS | PASS | **(b) held scene** | 30.4× | 26.0 / 714.5 / 23.5 |
| Marek (cowardly) | PASS | PASS | (c) underpowered | — | 897.5 / 2084.0 / 721.0 |
| Elias (loyal) | **FAIL** | PASS | **not-run** | — | 47.5 / 300.0 / 44.0 |

**5 held-scene / 1 underpowered / 1 not-run. Zero held-latent.**

`R_iii ≈ R_i` for every character — ablating an equally sized irrelevant span costs essentially nothing.
The collapse is specific to the scene.

### d = 30 (exploratory, no verdict)

4 held-scene / 2 underpowered / 1 not-run; still **0 held-latent**. Maria joins Marek as underpowered
(baseline 55.5 > 50). Ratios at d = 30: Bruno 681.3×, Simon 535.5×, Nadia 235.0×, Greta 191.8×. The
verdict is not distance-specific — but see the caveat on non-monotonicity in §5.

## 2. Registered expectations — 7/7

Recorded in §9 *before* the run, so the corrected gate would be falsifiable rather than merely permissive:

| character | predicted | observed |
|---|---|---|
| Elias | **fails the primary gate** | **failed** |
| Marek | passes gate, underpowered | matched |
| Greta, Nadia, Maria, Simon, Bruno | pass, held scene | matched |
| any | held latent would be a genuine surprise | none appeared |

**Elias failing is the load-bearing result here**, not an inconvenience. A gate that certified all seven —
including the character whose scene was demonstrably never elicited — would have been a rubber stamp, and
the five certifications would have been worth nothing.

## 3. Replication — exact

Phase 3b re-measures the same texts under the same masks, so the trait reads should reproduce. They do,
to the digit:

| character | condition | Phase 3 | Phase 3b | Δ |
|---|---|---:|---:|---:|
| Bruno | scene | 687.5 | 687.5 | +0.0 |
| Greta | scene | 2462.5 | 2462.5 | +0.0 |
| Maria | scene | 714.5 | 714.5 | +0.0 |
| … | *(all 21 cells)* | | | **+0.0** |

**Largest relative deviation: 0.0%.** Every one of the 21 (character × condition) cells is identical.

This corrects an expectation recorded in §9: bf16 + eager was predicted to shuffle rank ties slightly
between sessions. It does not — the pipeline is fully deterministic on this hardware. (The 0–3.5 rank
differences logged in §9 are between *Phase 2 and Phase 3*, i.e. **SDPA vs eager**, which remains the
correct explanation for that comparison.)

**Internal check that this is a genuine re-run and not a stale file:** what *should* have changed did, and
what *should not* have didn't. The secondary gate's numbers moved (Elias's baseline scene-keyword rank
32 → 4, because it now reads 12 generated positions instead of one) while every trait read stayed
identical. A misdirected file read could not produce that pattern.

## 4. The gates disagree — an open instrument problem

Reported, not resolved, exactly as §9 requires:

| where | primary (continuation) | secondary (repaired rank) |
|---|---|---|
| **Elias, d = 10** | **FAIL** — overlap 0/0/0 | PASS — kw 4/270/5 |
| **Elias, d = 30** | **FAIL** — overlap 0/0/0 | PASS — kw 7/304/11 |
| **Greta, d = 30** | PASS — overlap 1/0/1 | **FAIL** — kw 5/174/12 |

**What this shows: even repaired, a rank proxy is not equivalent to the behavioural criterion.** Elias's
scene keywords rank well *somewhere* in his 12 generated tokens, so the rank gate passes him — while his
actual generated answer never mentions the scene in any condition. The proxy measures whether a keyword is
*available*; §7b asks whether the model *reported the scene*. Those come apart, and the position-agnostic
repair narrows the gap without closing it.

Greta's d = 30 disagreement is a threshold artifact in the other direction (`kw_iii = 12` against a
threshold of `2 × 5 = 10`) — the rank gate is brittle near its cut-offs.

**Consequence for future work:** the continuation-scored gate is the better realisation of §7b, and this
is now an empirical claim rather than an argument. Keep the rank read as a secondary; do not let it decide.

## 5. Instrument checks

Four, three of which passed cleanly. All ran before any result was read.

| check | result | what it rules out |
|---|---|---|
| Attention mass on masked span | **0.9453 → 0.00** | the mask not firing |
| Null-mask identity | **bit-identical, max diff 0.000e+00** | the hook perturbing the model when it masks nothing |
| Semantic severance gate | passes for 6/7 (Elias excepted) | severing the wrong thing |
| Total-mask degradation | **warning: only ×2.1** | *(premise was wrong — see below)* |

### 5a. The total-mask check fired a warning, and the investigation was informative

Masking the **entire story** (214 tokens) moved Maria's trait rank 26.0 → 55.5 (×2.1), while masking
**just the 19-token scene** moved it 26.0 → 714.5 (×30). Masking *more* hurt *less*, which tripped the
registered warning threshold.

**The mask is not at fault; the check's premise was.** It assumed removing context monotonically reduces
trait retrievability. For a `"NAME is ___"` probe that is false: with no context at all, the model falls
back on a generic prior in which trait adjectives are perfectly natural completions. Empty context is not
a floor — it is a moderate prior.

The stored top-20 vocabulary (§8's rule) shows what actually happens. Maria, layer 22:

| condition | top completions after "Maria is…" |
|---|---|
| baseline | hardworking, **trustworthy**, empathetic, **selfless** |
| **scene masked** | likely, someone, tasked, **accountant, librarian** |
| control masked | hardworking, **trustworthy**, empathetic, **selfless** |

With the scene hidden the model does not go blank: the **surviving opening** ("Maria keeps the ledgers at
a shipping office") steers it toward *occupation* nouns. The trait falls to rank 714 partly because the
evidence is gone and partly because **something else moved into the slot**. Mask the whole story and that
competitor disappears too, so trait adjectives float back up on prior alone.

**Two consequences, one strengthening and one qualifying:**

- **A specificity control we did not design.** Masking **214** tokens gives ×2.1; masking the **right 19**
  gives ×30. The effect tracks *which* tokens are masked, not *how many*. That answers "maybe masking just
  confuses the model" far more decisively than the matched-filler control alone.
- **A qualification on effect size.** Part of `R_ii`'s magnitude is the surviving context competing, not
  pure evidence-removal. The `R_ii/R_iii` ratio remains valid — both conditions retain that surviving
  context — but the magnitude should not be read as "pure scene removal."

**Methodological lesson worth more than the check was:** a rank measure reports the winner of a
competition, so *"the concept dropped"* and *"something else arrived"* are indistinguishable without
inspecting what took its place. That inspection is only possible because §8 mandates storing top-20
vocabulary at every checkpoint — a rule adopted after v1's correction depended on it, and now the second
time it has paid for itself.

This also rhymes with the source paper's capacity finding — that a topic switch *evicts* prior contents,
i.e. **displacement rather than decay** clears the workspace. Hedged: theirs is J-space occupancy analysis,
ours is a vocabulary-projection readout at one probe position. Not the same experiment; the same shape.

## 6. The symmetric direct-arm test (unchanged from Phase 3)

Identical numbers. Masking the literal trait word wrecks stated-arm retrieval (median **×56**, 6 of 7);
masking an equally sized neutral tracer does nothing (median **×0.90**). Greta ×410, Marek ×175, Bruno ×62,
Maria ×56, Simon ×18, Nadia ×14; Elias ×2.2, whose stated trait was barely retrievable at baseline (184.5).

## 7. What this run does and does not add

**Adds:** a verdict resting on a gate fixed before the data; an exact replication; evidence that the
continuation-scored gate is the better instrument; and a specificity control obtained by accident.

**Does not add:** any new information about the model. The trait numbers are Phase 3's, to the digit. The
corrected gate is **pre-registered for this run, derived from the previous one** — better than post-hoc,
not the same as having specified it correctly the first time. That provenance stays attached permanently.

**Still not licensed:** any claim that nothing whatsoever is stored. Both lenses read *disposition to say
the trait word*; a trait held in a non-verbalizable form would be invisible to them. Retrievability,
expression, and representation remain three different questions, and this measures the middle one.

## 8. Limitations

- **n = 7, five certified.** Per-character tables throughout, because aggregates this small are draggable.
- **Elias remains unreliable across every phase** — weak cue in Phase 1, anomalous in Phase 2's Q1 and Q5,
  probable false gate pass in Phase 3, and the gates disagree on him here. "Loyal" is a weak, abstract
  relational cue and behaves unlike the behavioural traits.
- **Ratios are noisy and non-monotone across distance.** They are large at every distance from d = 1 to
  d = 30, but do not increase smoothly: Greta runs 164 / 17 / 30 / 46 / 126 / 192 and Maria reverses
  outright (61 / 44 / 70 / 13 / 30 / 5.5). No character is monotone. Any "grows with distance" claim would
  be cherry-picking a noisy series.
- **The gate disagreement is unresolved** and is reported as such.
- **Q4 (two-entity interference)** remains a stub, and v1's **direction probe** remains the natural
  complement — it could see a held representation these vocabulary-projection lenses structurally cannot.

## Files

| file | what it is |
|---|---|
| `phase3b_ablation.csv` | 140 rows: inferred-arm trait rank under {baseline, scene, control} × 7 distances |
| `phase3b_gate.csv` | 140 rows: continuations (primary gate) + 12-position keyword rank (secondary) |
| `phase3b_direct.csv` | 147 rows: the symmetric direct-arm test |
| `phase3b_per_layer.csv` | 3,920 rows: per-layer ranks, both lenses |
| `phase3b_top20.csv` | 39,200 rows: top-20 J-lens vocabulary at every checkpoint |
| `../analyze_phase3b.py` | both gates, the §3 verdict, the replication check, the §9 expectations check |

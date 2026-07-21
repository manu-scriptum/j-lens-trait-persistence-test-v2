# Phase 2 results — the cued-retrieval sweep (Q1 + Q2 + Q5)

Analysis run: 2026-07-21, `analyze_phase2.py` over `phase2/phase2_reads.csv` (1134 reads) and
`phase2/phase2_logit_posctrl.csv`, against the **frozen** criteria in
[`prediction.md`](../prediction.md) §3. n = 7 survivors, band 13–26, primary cue = Cue B, persistence
distances d ∈ {1,2,4,7,10} (d0 excluded from persistence per §3). Every number here is descriptive;
nothing was re-tuned after seeing data.

## Headline

1. **Q1 does not reach significance. There is no detectable stated-vs-inferred difference in
   retrievability** — Wilcoxon p = 0.81 (primary, per-character), and the median ratio-to-control is
   **identical to three decimals for the two arms (0.0385)**. Per §3 this is reported descriptively as
   direction-and-consistency, **not as a finding**. Direction weakly leans toward "stated more
   retrievable" (4/7 characters) but is **not consistent** — two characters lean the other way and one
   is anomalous.
2. **The real result is what did *not* happen: the inferred trait does not collapse.** Under cued
   retrieval it stays retrievable out to d = 10 for **6 of 7** characters — the direct opposite of v1's
   passive-read finding, where the inferred trait vanished after a single filler sentence. This is the
   corrected-replication payoff: *when you ask instead of watch, the model retrieves the inferred trait
   about as readily as the stated one.*
3. **Q2: the direct arm's persistence is not generic word-echo** (though formally "ambiguous" by the
   frozen threshold). The neutral tracer sits near its own control floor (median 0.88) while the trait
   persists near ceiling (0.038) — the lingering is content-specific, not repetition.
4. **Q5: the J-lens earns its keep for Greta, partly for Nadia, not for Elias.** For Greta the J-lens
   reads the never-tokenised inferred trait at every distance while the logit lens has it buried
   (J ≈ 11–31 vs logit ≈ 116–219). n = 3, descriptive.

---

## Q1 — stated vs inferred retrievability

Per-character ratio-to-control at each distance (Cue B, trait lexicon; lower = more retrievable;
`*` = direct more retrievable than inferred):

| character | d1 D/I | d2 D/I | d4 D/I | d7 D/I | d10 D/I | direct wins |
|---|---|---|---|---|---|---|
| Bruno (lazy) | 0.023/0.043* | 0.025/0.030* | 0.025/0.028* | 0.028/0.018 | 0.014/0.016* | 4/5 |
| Elias (loyal) | 0.323/0.329* | 0.642/0.390 | 1.451/0.353 | 1.990/0.466 | 1.587/0.422 | 1/5 |
| Greta (dishonest) | 0.018/0.040* | 0.011/0.038* | 0.005/0.007* | 0.004/0.007* | 0.003/0.008* | 5/5 |
| Marek (cowardly) | 0.006/0.215* | 0.007/0.493* | 0.009/0.610* | 0.006/0.444* | 0.005/0.479* | 5/5 |
| Maria (generous) | 0.060/0.052 | 0.038/0.038 | 0.028/0.037* | 0.040/0.098* | 0.020/0.052* | 3/5 |
| Nadia (brave) | 0.769/0.038 | 0.362/0.053 | 0.145/0.088 | 0.159/0.023 | 0.119/0.013 | 0/5 |
| Simon (curious) | 0.165/0.025 | 0.110/0.028 | 0.217/0.026 | 0.298/0.030 | 0.243/0.019 | 0/5 |

**Decision (frozen §3 rule).** Outcome (1) requires *both* the majority-of-characters-at-majority-of-
distances direction *and* a Wilcoxon p < 0.05.
- Direction: **met but marginal** — 4/7 characters have direct more retrievable at ≥ 3/5 distances.
- Wilcoxon signed-rank, per-character median over d (n = 7, registered weak): **W+ = 16, exact
  two-sided p = 0.8125 — does not clear.** Per-distance breakdown: all p ≥ 0.58.

So outcome (1) is **not supported**. The honest reading is **Q1 outcome (2): no detectable difference**,
with the arms' median ratios coincidentally identical (0.0385 each).

**The heterogeneity is the story, and it is real, not noise.**
- **Greta, Marek** show the predicted pattern strongly — the stated trait is far more retrievable than
  the inferred one at every distance (Marek: direct ≈ 0.006 vs inferred ≈ 0.5).
- **Nadia, Simon** show the *reverse* — the *inferred* trait is more retrievable than the stated one
  throughout. For these two the stated trigger ("Nadia is brave.") is a weaker cue than the vivid
  behavioural scene.
- **Elias (loyal) is anomalous:** the direct arm's ratio *exceeds 1* at distance (d4–d10), i.e. the
  stated trait becomes *less* retrievable than in the no-trait control. "Loyal" is the likely culprit —
  a weak, abstract adjective — and Elias also fails Q5 below. Flagged, not smoothed over. With n = 7 he
  drags the mean; the per-character table is the honest picture.

**Retrievability (§3: R ≤ 50 AND ratio ≤ 0.8), count of characters:** direct 6/7 at every distance;
inferred 5/7 (d1–d2) rising to 6/7 (d4–d10). **Both arms stay broadly retrievable across the whole
sweep** — neither craters.

## Q2 — is the direct arm's persistence trait-specific or word-echo?

Per character, median over d ≥ 1 (Cue B): trait ratio = R(direct,trait)/R(control,trait); tracer
ratio = R(direct,tracer)/R(control,tracer).

| character | trait ratio | tracer ratio |
|---|---|---|
| Bruno | 0.025 | 1.515 |
| Elias | 1.451 | 0.609 |
| Greta | 0.005 | 0.694 |
| Marek | 0.006 | 0.883 |
| Maria | 0.038 | 1.345 |
| Nadia | 0.159 | 0.861 |
| Simon | 0.217 | 0.912 |
| **median** | **0.038** | **0.883** |

**Decision (frozen §3 rule).** Copy bias (b) needs the tracer within 0.15 of the trait; trait-specific
(a) needs tracer ≥ 0.95 while trait ≤ 0.8. Here the gap is **0.845**, and the tracer median is 0.883 —
just short of the 0.95 (a) threshold — so the formal verdict is **partial/ambiguous**. But the
direction is unambiguous: **the tracer sits near its own control floor (≈ 0.88, i.e. it barely
persists above a story that never contained it) while the trait persists near ceiling (0.038).** The
direct arm's persistence is **content-specific, not repetition echo.** This defends the reads as real;
it does not rescue a Q1 difference that was not there.

**Consequence for §7a:** because Q2 is *not* outcome (b), the copy-bias override on the extension does
**not** apply.

## Q5 — does the J-lens read what the logit lens cannot?

Only interpretable where the logit positive control passed (§4a): **Elias, Greta, Nadia**. Inferred
arm, Cue B, J-lens vs logit-lens median rank:

- **Greta (dishonest) — clean positive.** J ≈ 11–31 while logit ≈ 116–219 at *every* distance d1–d10:
  the J-lens reads the never-tokenised inferred trait where the plain unembedding has it buried. This
  is the single strongest available justification for the J-lens on this task.
- **Nadia (brave) — partial.** J below logit throughout; the ≥ 5× gap holds at d1–d2 (J 1–2.5 vs logit
  15.5) but narrows later.
- **Elias (loyal) — negative.** The logit lens reads the inferred trait *better* than the J-lens
  (logit ≈ 20–27 vs J ≈ 38–61). No J-lens advantage here — consistent with Elias being the weak/anomalous
  case in Q1.

**Verdict:** descriptive, n = 3, mixed — a clean J-lens advantage for Greta, partial for Nadia, none
for Elias. Reported as instrument sensitivity, **not** as evidence of a J-space-privileged
representation (§4a's load-bearing caveat).

## §7a — the registered conditional extension past d = 10

Both trigger conditions are met, and the Q2 override does not apply:
- direct median ratio-to-control at d10 = **0.020 ≤ 0.8** (still retrievable) ✔
- direct-vs-inferred contrast: d4 = +0.009, d10 = −0.001 → **the separation has not opened up** ✔

So the extension to d ∈ {15, 20, 30} is **triggered as a registered secondary run.** One honest
caveat, which §7a itself anticipates: the direct ratio ≈ 0.02 means the direct rank is near the **rank
floor** (rank 1–a few), so the lack of separation may be a dynamic-range ceiling rather than true
convergence — which is precisely the "lack of dynamic range" the extension exists to probe. It is a
dynamic-range probe, not a result-chase, and would carry the same status as the primary sweep.
Whether to spend the run is a judgement call for the researcher.

## What this run does and does not license

- It is a **corrected replication under cued retrieval**, and its cleanest positive result is the
  **absence of the v1 collapse**: the inferred trait remains retrievable under questioning across the
  whole sweep. v1's "inference evaporates after one sentence" was an artifact of passive reads.
- It finds **no reliable stated > inferred retrievability difference** (Q1 outcome 2), against a
  backdrop of strong per-character heterogeneity that a re-read/re-derive story does not by itself
  predict.
- **No held-latent-vs-held-scene claim is drawn** (Q3 deferred, §1a). The distance half of the
  differential-fragility read is here; the interference half (Q4) is not.
- n = 7, single-item medians draggable by one character (Elias demonstrably so); one trait ("loyal")
  behaved as a weak cue and is flagged rather than dropped.

## §7a extension results — distances 15, 20, 30

Ran 2026-07-21 (`trait_persistence_v2_phase2ext.ipynb`, 567 reads), analysed with
`analyze_phase2ext.py` jointly with the primary sweep across d ∈ {4,7,10,15,20,30}. The extension
existed to test whether the *absence* of a stated-vs-inferred separation in the primary window was a
**dynamic-range ceiling** (both arms pinned near the rank floor) rather than a true null.

**Answer: it is a true null. Pushing distance to 30 does not open up a separation.**

Median (robust) ratio-to-control across characters, Cue B, trait lexicon:

| d | direct rank | inf rank | ctrl rank | direct ratio | inf ratio | inf/direct |
|---|---|---|---|---|---|---|
| 4 | 7.0 | 11.0 | 229.5 | 0.028 | 0.037 | 1.31× |
| 7 | 12.5 | 15.5 | 248.0 | 0.040 | 0.030 | 0.74× |
| 10 | 8.5 | 17.0 | 243.5 | 0.020 | 0.019 | 0.96× |
| 15 | 11.0 | 25.0 | 204.5 | 0.028 | 0.012 | 0.42× |
| 20 | 6.5 | 28.5 | 233.5 | 0.015 | 0.013 | 0.86× |
| 30 | 5.0 | 26.5 | 297.0 | 0.008 | 0.015 | 1.76× |

The `inf/direct` column bounces around 1 with no trend (0.4×–1.8×). Per-character in the extension
regime (median over d ∈ {15,20,30}), **3/7** characters have direct more retrievable — the *same*
three as the primary window (Greta, Marek, Maria) — while Nadia, Simon, Bruno lean the other way and
**Elias is again anomalous** (direct ratio 2.05, worse than the no-trait control). Wilcoxon on the
long regime: **W+ = 15, p = 0.9375 — does not clear.** The direct-vs-inferred contrast is essentially
unchanged from the primary window (−0.0022 → −0.0021).

**Two things worth stating plainly:**
- **The null is not a range artifact.** Control ranks sit at ~200–300 at these distances (ample room),
  yet direct and inferred stay statistically indistinguishable. The §7a dynamic-range worry is
  answered and dismissed.
- **The inferred trait still does not collapse at d = 30** (retrievable for 5/7). Under cued retrieval,
  an inferred trait remains recoverable ~30 sentences after the behavioural cue — reinforcing the
  primary headline against v1's one-sentence collapse.

**Method caveat, recorded because it nearly misled us:** the in-notebook preview reported the *mean*
band-rank (direct ≈ 28–35, inferred ≈ 96–104), which looked like a 3× separation. That was outlier
inflation of a right-skewed rank distribution (chiefly Elias). The frozen §3 measure is the
*per-character median ratio*, on which the separation vanishes. Mean-of-ranks is not the registered
statistic, and this is why.

## Interpretation (beyond the pre-registered analysis)

*This section is interpretation, not registered result. It reasons about what the numbers above might
mean and is held to a lower evidential bar than §3's frozen criteria. Read the results first, then
disagree with this freely.*

**v1's "re-read vs re-derive" mechanism is not supported at the retrieval level.** v1 proposed that a
stated trait persists because its literal token can be re-read, while an inferred trait fades because
it must be re-derived from scratch. Under cued retrieval that prediction fails twice: the inferred
trait does not fade (retrievable to d=30), and it is no less retrievable than the stated one. Whatever
asymmetry v1 measured lived in *what the model spontaneously emits at a sentence end*, not in *what it
can retrieve when asked*.

**But the deeper question is untouched, for a structural reason.** "Equally retrievable" is not
"equally held". In this design the behavioural scene stays in context the whole way out — nothing is
evicted — so a trait *re-derived fresh from the still-visible scene on each query* is indistinguishable
from one *held as a standing latent*. We watched; we did not intervene. Separating those two is exactly
what the KV-ablation (Q3) was for, and it is deferred. **So the honest reading is: the collapse story
is wrong, and the held-vs-re-derived question is wide open — not settled in either direction.**

**Retrievability is not representation.** Everything here is read through vocabulary-projection lenses,
which see *disposition to say the trait word*. A trait could be held as a feature while never near the
tip of the tongue, and no lens used here would see it. Expression, retrievability, and representation
are three different questions; v2 measured the middle one. The representation question needs the
direction probe (the natural next run).

**The heterogeneity probably tracks cue strength, not mechanism.** The characters where the stated arm
wins (Greta, Marek, Maria) versus where the inferred wins (Nadia, Simon) do not sort by anything
mechanistic we registered. The parsimonious read is that it reflects how *vivid and stereotyped* the
behavioural scene is against how *strong* the bare adjective is — "climbed under the load twice to pull
him clear" is a louder cue than "Nadia is brave." Elias's "loyal" is weak both ways and reads worse
than its control: a cue-quality failure, not a fact about loyalty. The aggregate null is real, but it
is an average over stimuli of uneven strength, at n=7.

**Q5, modestly.** For at least one clean case (Greta) the J-lens reads a trait that was never written
down while the logit lens has it buried — the instrument doing the thing it claims. That earns the
J-lens some keep on this task, but n=3, mixed, and it is a statement about lens sensitivity, not about
a privileged representation in the model.

**What would actually move this forward:** v1's direction probe — read the trait as a linear direction,
continuously across the filler, the cleanest in-reach test of *held vs re-derived* — and, eventually,
the KV-ablation in a proper lab.

> **Correction (2026-07-21, post-run):** "in a proper lab" was a misjudgement. The KV-ablation (Q3)
> turns out to be runnable on *this* setup — forward pre-hooks on the attention modules, the mechanism
> `prediction.md` §7b already pins. The researcher underestimated the setup; Fable caught it. Q3 is now
> the planned next arm; the held-vs-re-derived question it settles is no longer waiting on someone
> else's lab. See `prediction.md` §9 (2026-07-21, post-run).

## Files

| file | what it is |
|---|---|
| `phase2_reads.csv` | 1134 reads: every (name, arm, distance, cue, measure), both lenses |
| `phase2_per_layer.csv` | per-layer ranks (repeats v1's E4 sub-band check) |
| `phase2_top20.csv` | top-20 J-lens vocabulary at every checkpoint |
| `phase2_reintro.csv` | D3 reintroduction continuations (qualitative) |
| `phase2_logit_posctrl.csv` | per-character logit positive control (3/7 passed) |
| `phase2ext_*.csv` | the §7a extension sweep (d ∈ {15,20,30}); same schema as the primary set |
| `../analyze_phase2.py` | the primary-sweep analysis |
| `../analyze_phase2ext.py` | the combined primary + extension trend analysis |

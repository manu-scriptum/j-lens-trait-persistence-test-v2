# Phase 3, step by step — the KV-ablation (Q3), in plain language

*A companion to `trait_persistence_v2_phase3.ipynb`. No AI or stats background needed. For the exact
rules and numbers, [`prediction.md`](prediction.md) §3 + §7b + the §9 "Q3 implementation pinned" entry
is the pre-registration; [`README`](README.md) has the short technical version.*

> **Written before the run; it has since happened. The answer was "held scene."** Hiding the
> behavioural scene collapsed the trait, hiding an equally sized piece of filler did nothing, and **no
> character showed a held latent.** Two things below are worth reading afterwards with hindsight: the
> "safety checks" section, because one of the checks turned out to be *badly designed* and wrongly
> failed three characters whose blindfold demonstrably worked (it was re-run with a corrected check —
> that is the certified result), and the "four possible outcomes" table, because writing the outcomes
> down in advance is what made the correction a correction rather than a rescue. Results:
> [`phase3b/PHASE3B_RESULTS.md`](phase3b/PHASE3B_RESULTS.md).

---

## The one-sentence question

When the model can still retrieve an **inferred** trait long after the story showed it (Phase 2 proved
it can, out to 30 sentences), is that because it **stored** the trait as a standing fact — or because
it **re-reads the original scene** and works the trait out again, fresh, every time you ask?

## Why Phase 2 couldn't answer it, and Phase 3 can

Phase 2 only *watched*. The behavioural scene ("Maria covered a colleague's rent") stayed on the page
the whole time, so "the model kept the trait in mind" and "the model just glanced back at the scene and
re-derived it" look **identical** from the outside. You cannot tell them apart by watching.

Phase 3 *intervenes*. It **hides the scene from the model's attention** — blindfolds it to those exact
words — and then asks for the trait again:

- If the trait is **still** retrievable with the scene hidden → the model was holding it somewhere
  else. **"Held latent."**
- If the trait **collapses** the moment the scene is hidden → there was nothing stored; it was being
  re-read from the scene each time. **"Held scene."**

Both answers are interesting, and we wrote down the exact rule for each **before running**, so neither
can be talked into afterwards.

## The three versions of each reading

For every character we take the same trait reading three ways:

1. **Baseline** — nothing hidden. (How retrievable is the trait normally?)
2. **Scene hidden** — the behavioural sentence is masked out of attention.
3. **Control: a filler sentence hidden** — instead of the scene, we hide a *plain filler* sentence of
   the same length. This is the fair comparison: hiding *any* chunk of text disturbs the model a little,
   so we only care whether hiding *the scene specifically* does more damage than hiding a same-sized
   irrelevant chunk.

The verdict is a comparison of (2) against (3): scene-hiding barely worse than filler-hiding → held
latent; scene-hiding far worse → held scene.

## The two safety checks (this is the important part)

Hiding text from a model is fiddly, and there is one dangerous failure: **if the blindfold silently
doesn't work, or breaks the model in general, the trait would collapse for a boring technical reason —
and that collapse looks exactly like the interesting "held scene" answer.** So we refuse to trust any
trait number until the blindfold is proven to work, two independent ways:

- **Mechanical check.** We literally measure how much attention lands on the hidden words. With the
  blindfold on it must be ~0. (The notebook asserts this and stops if it isn't.)
- **Meaning check (the registered gate).** We ask the model *"What did NAME do?"* under each condition.
  With the scene hidden it should **no longer be able to say what NAME did**; with only a filler hidden
  it still should. We check this with a small list of scene-specific words per character (e.g. Maria's
  "rent", "colleague") — declared in advance, in the stimuli file.

**If either check fails for a character, that character is reported `not-run` — never as a result.** A
failed blindfold is not allowed to become the exciting answer. This rule is frozen in `prediction.md`
§7b and was the whole reason Q3 was designed carefully rather than just run.

## What's the real answer vs. what's just for context

- **The pinned answer** is read at **one checkpoint**: 10 filler sentences after the scene, at the
  "what kind of person is NAME?" question. One verdict per character.
- We **also** run the same ablation at 0, 1, 2, 4, 7, and 30 sentences of distance — but only as
  context. The distance-30 run is there to check the distance-10 verdict isn't a fluke of that one
  distance. These carry no verdict.
- We **also** run a mirror test on the *stated* arm ("Maria is generous"): hide the literal word
  "generous" and see how much the stated trait's retrievability depends on that one symbol still being
  on the page. Purely descriptive — it's the flip side of the same mechanism.

## The four possible outcomes (all written down in advance)

| verdict | what it means |
|---|---|
| **held latent** | the trait survives the scene being hidden → it was stored, not just re-read |
| **held scene** | the trait collapses when the scene is hidden → recomputed from the scene each time |
| **partial** | in between; reported as such |
| **underpowered** | the trait wasn't retrievable even at baseline for that character → can't test it |
| **not-run** | the blindfold check failed → we say nothing, rather than risk a fake "held scene" |

## The honest size of this

Seven characters, one small open model, one tool. The verdict is per-character and the aggregate can be
dragged by a single character (in Phase 2, "loyal"/Elias was a weak, misbehaving cue — worth watching
here too). "Held latent" and "held scene" are both real, publishable answers; whichever way it lands,
the write-up shows the per-character table, not just a headline count.

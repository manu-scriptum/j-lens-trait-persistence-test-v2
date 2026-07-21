# Phase 2, step by step — what the notebook in Colab is actually doing

*A plain-language companion to the run. No AI, statistics, or interpretability background needed. If
you finish and want the exact rules and numbers, [`prediction.md`](prediction.md) is the
pre-registration and the [`README`](README.md) has the short technical version. For the big-picture
"why does any of this matter", start with the general primer.*

---

## The one-sentence question

If a story **says** "Maria is generous" versus **shows** her quietly covering a colleague's rent, does
the model keep the idea *generous* **retrievable** differently as the story moves on — and when you
later ask "what kind of person is Maria?", which version answers?

## The one thing v2 fixes about v1

v1 mostly *watched* the model at the ends of sentences — it looked at what the model happened to be
about to say anyway. But you can't find out what someone remembers by watching them read; **you have
to ask**. Almost every reading in this run is taken right after a question is put to the model. That
is the whole point of Phase 2: **every checkpoint is a question, not a glance.**

## What this particular run measures — three things

This run deliberately does three things and no more (two harder questions are parked — see the end):

- **Q1 — the main event.** Does a *stated* trait stay retrievable longer than an *inferred* one as
  more and more filler text piles up between the trait and the question? Plain hunch going in: stated
  should last longer, because the word is still sitting there on the page to glance back at, while an
  inferred trait is a conclusion the model would have to rebuild. But we registered **no prediction** —
  every outcome is reportable.
- **Q2 — the honesty check on Q1.** When the *stated* trait lingers, is that because the model is
  holding the **meaning**, or just echoing a **word it saw recently**? To tell those apart we hid a
  neutral, unrelated word (a "tracer" — *lantern*, *kettle*, *bucket*…) in each stated sentence and
  track it the same way. If the meaningless tracer lingers just as long as the trait, then the stated
  arm's staying power is mostly "recently-seen-word echo," not memory of the trait.
- **Q5 — is the fancy tool earning its keep?** We read everything twice: once with the special tool
  (the **Jacobian lens**) and once with a plain, crude readout (the **logit lens**). If the crude tool
  sees the same thing, the finding isn't an artefact of the fancy one. This is a question about the
  *instruments*, not the model.

## How one "reading" works — the three ideas you need

**1. Rank = a word's place in the queue.** The model carries ~262,000 words, and at every instant
they're lined up by how ready it is to say each one next. We report the trait word's **rank** in that
queue. Rank 3 = only two words ahead of it, all but ready to say. Rank 40,000 = buried, idle.
**Lower is stronger.** That single number is the measurement.

**2. The band = which internal layers we read.** The model thinks in ~34 stacked layers. Early ones
are still sorting out raw words; the very last ones have already committed to the next word. The
useful, concept-level thinking sits in the middle. Phase 1 measured exactly where that is on this
model — **layers 13–26** — and Phase 2 reads only there. (You saw the notebook print
`layers 13..26` right at the start — it reads that from Phase 1's file rather than trusting a typed-in
number.)

**3. Always compared against a matched "nothing happened" story.** A common word ranks high just from
being common, so a raw rank means little on its own. Every character also has a **control** version
where no trait was planted. We always report the trait arm **relative to its own control** — same
distance, same question — so we're measuring the effect of the trait, not the background frequency of
the word.

## What you're watching, cell by cell

The notebook runs top to bottom. Here's what each stage is for and how to read what it prints.

1. **Install & sign in.** Fetches the lens tool (pinned to one exact version, so it's identical to v1
   and Phase 1) and logs into Hugging Face to download the model. Housekeeping.

2. **Read the band and roster from Phase 1.** Prints `band … layers 13..26` and the `7 survivors`.
   Crucially it *reads these from Phase 1's saved files*, never retypes them — so the run can't
   silently drift from what Phase 1 actually decided. (Three of the ten characters were dropped in
   Phase 1 for not producing a clean enough signal; we run the 7 that passed, and don't back-fill.)

3. **Load the model and lens.** Downloads `gemma-3-4b-it` and the lens, prints versions, and
   double-checks the saved band actually fits this model before going on.

4. **Wire up and *validate* the crude logit lens.** This is the cell that prints the ` Paris` ladder.
   It's a known-answer test: on "The Eiffel Tower stands in the French capital city of", the word
   ` Paris` *should* climb to the top in the late layers — and it does. This matters because Q5 leans
   entirely on this crude readout, so we prove it's wired correctly (`TOP-8 SETS MATCH: True`) before
   trusting a single number from it. If it were wrong, the cell **stops the whole run** on purpose.

5. **Look up the word IDs.** Turns each trait's word list, each bare adjective, and each tracer into
   the model's internal number for that word — dropping any that aren't a clean single word. Prints one
   line per character.

6. **The "read machinery" cell — prints nothing, and that's correct.** It only *defines* the
   functions that take a reading; it doesn't run them yet. A cell that just defines tools is silent.
   Silent + a number in the `[ ]` on the left = success. (The next cell is where the work happens.)

7. **The sweep — the slow part.** For each of the 7 characters, in 3 versions (say-it / show-it /
   nothing), at 6 distances (0, 1, 2, 4, 7, 10 filler sentences), asked 2 ways (a bare name-mention,
   and the direct "what kind of person is…?" question) — that's **378 separate readings per lens**.
   Each one is a fresh, independent run of the model, so nothing leaks between them. You'll see a
   `swept …` line appear as each character finishes. This is where the minutes go.

8. **The positive-control check.** Prints, per character, whether the *crude* lens could see the
   inferred trait at all at the very start. Only where it can is a later "the crude lens saw nothing"
   meaningful. Expect **3 of 7 to pass** (Nadia, Elias, Greta) — that matches Phase 1. If it doesn't,
   that's a flag to stop and investigate, not to push past.

9. **A first-look table — direction only, *not* the answer.** A quick peek at whether stated is
   trending more retrievable than inferred, just so a gross wiring error would show up now. The real
   verdict — with the proper statistical test — is done later, offline, against the rules we locked in
   *before* seeing any of this. That separation is deliberate: the target can't be moved to fit the
   result.

10. **Save the files.** Five `.csv` files get written for the offline analysis. Download all of them.

## What this run deliberately does *not* do

Two deeper questions are parked, on purpose:

- **Is a recalled inferred trait genuinely *held in mind*, or rebuilt on the spot?** Answering it means
  surgically switching off part of the model and re-checking — an *intervention* that needs tooling and
  safety-checks beyond a read-only setup. Named, specified, and left for a proper lab.
- **Does the model mix up two characters' traits?** A second-character interference test — a separate
  future run.

So this run is the honest, corrected version of v1's core question — done properly this time — and
nothing is dressed up as more than that.

## The honest size of this

Seven characters, one small open model, one tool. Every "most of them" describes what we saw, not a
proof it holds in general. It's a careful pilot, and any result that doesn't clear the bar we set in
advance gets described plainly, not sold as a finding. Getting something wrong and fixing it in the
open — as v1 did once already — is the job, not an embarrassment.

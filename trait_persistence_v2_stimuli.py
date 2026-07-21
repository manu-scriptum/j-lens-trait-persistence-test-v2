"""Canonical v2 stimuli, concept lexicons, tracers, filler, and cues.

Part of the pre-registration (`prediction.md` §5–§7). Committed in the same commit as that
document, before any calibration or screening code was run. This file is the single source of
truth; the notebook imports it rather than restating any string, so doc/code drift is impossible.

Design constraints this file implements (spec §D0, fixing v1's F6):
  * invented town ("Vellin") — no real place-name (v1 used "Lyon");
  * occupations chosen trait-neutral — the role must not itself imply the trait
    (v1 put `brave` on a clinic worker and `patient` next to laying out tools);
  * `control` matched to `inferred` in length AND topic domain — same objects, same setting,
    only the action differs (v1's controls differed in topic as well as in trait content);
  * every `direct` trigger carries a pre-declared tracer word (D4) with no semantic relation
    to trait, character, occupation, or filler.

Ten candidates, 5 positive / 5 negative. The screening gate in `prediction.md` §3 cuts these to a
target of eight. Candidates are declared here in advance precisely so the survivors are not chosen
after seeing data.
"""

TOWN = "Vellin"  # invented; verify it stays invented if the model has opinions about it

# Neutral filler, carried over from v1 unchanged (it was already town-generic and trait-free),
# which also keeps the v1-comparability stream honest.
FILLER_SENTENCES = [
    "The town's main street runs in a straight line from the north gate to the central square.",
    "A row of plane trees stands along the pavement, tall enough to shade the whole street by midsummer.",
    "The central square is paved with grey cobblestones laid in a fan pattern.",
    "A stone fountain in the middle of the square has three tiers and runs from spring until autumn.",
    "The nearest railway station sits at the far end of a long avenue past the clock tower.",
    "Trains to the regional capital leave twice in the morning and once in the early afternoon.",
    "The weather in this region turns from dry summers to grey, rain-heavy winters.",
    "A ridge of low hills marks the eastern edge of the district, covered in scrub and loose rock.",
    "The oldest building still standing is a squat administrative hall with a tiled roof.",
    "A single road bridge crosses the river at the southern edge, wide enough for one lane of traffic.",
    # --- §7a extension filler (added 2026-07-21; see prediction.md §9) --------------------------
    # Twenty more town-generic, trait-neutral sentences so distance can reach d=30. Indices 0-9
    # above are UNCHANGED, so every d<=10 prefix stays byte-identical to the primary Phase 2 run.
    # These 20 continue the same dull physical-description register and contain no trait-lexicon
    # word, no tracer word, and no character name (asserted in the self-check below).
    "The covered hall opens onto the square through a row of iron gates.",
    "Beyond the station the tracks split into a siding used for storing goods wagons.",
    "A narrow stream runs parallel to the eastern road for most of its length.",
    "The water tower on the hill was built from the same grey stone as the hall.",
    "Most of the houses along the avenue have shutters painted a faded green.",
    "The covered hall closes at midday on the first and third days of the week.",
    "A footpath crosses the meadow between the school and the old mill.",
    "The mill by the river has not turned its wheel in many years.",
    "Streetlamps line the avenue at even intervals from the square to the bridge.",
    "The regional bus stops twice a day at a shelter near the north gate.",
    "Rainwater collects in a shallow basin at the low end of the square.",
    "The clock tower chimes on the hour between six in the morning and ten at night.",
    "A stone wall separates the churchyard from the lane behind it.",
    "The bakery on the corner keeps the same opening hours all year.",
    "Two rows of allotments lie between the last houses and the ridge.",
    "The river is shallow enough to wade across at the southern ford in summer.",
    "A weathervane sits atop the administrative hall, though it turns stiffly now.",
    "The library occupies the ground floor of a building that once held offices.",
    "Cobbled side streets branch off the main road at irregular angles.",
    "The fountain is drained and cleaned once at the end of each autumn.",
]

# Distances in filler sentences from the trigger (spec §5).
DISTANCES = [0, 1, 2, 4, 7, 10]
# §7a registered conditional extension distances (prediction.md §9, 2026-07-21). Uses the 20
# extension filler sentences above; runs only if the §7a trigger fired (it did — see §9).
EXT_DISTANCES = [15, 20, 30]

# Concept lexicons (D1 / prediction.md §6). Each entry is checked single-token in its
# LEADING-SPACE form at run time; failures are dropped and logged, never substituted.
# Ordering is not meaningful — the measure is best rank across the surviving set.
TRAIT_LEXICONS = {
    "generous":  ["generous", "generosity", "giving", "charity", "charitable",
                  "kindness", "kind", "donations", "gift", "selfless"],
    "brave":     ["brave", "bravery", "courage", "courageous", "fearless",
                  "heroism", "heroic", "hero", "daring", "bold", "valor"],
    "curious":   ["curious", "curiosity", "inquisitive", "wonder", "interest",
                  "questions", "exploring", "probing"],
    "patient":   ["patient", "patience", "calm", "composed", "tolerant",
                  "unhurried", "steady", "waiting"],
    "loyal":     ["loyal", "loyalty", "faithful", "devoted", "devotion",
                  "allegiance", "steadfast", "dedicated"],
    "greedy":    ["greedy", "greed", "selfish", "avarice", "hoarding",
                  "miserly", "stingy", "grasping", "hoard"],
    "cruel":     ["cruel", "cruelty", "brutal", "brutality", "harsh",
                  "vicious", "callous", "sadistic", "mean"],
    "lazy":      ["lazy", "laziness", "idle", "idleness", "indolent",
                  "sluggish", "slack", "lethargic"],
    "dishonest": ["dishonest", "dishonesty", "lying", "liar", "deceit",
                  "deceitful", "deception", "fraud", "cheating", "lies"],
    "cowardly":  ["cowardly", "coward", "cowardice", "afraid", "fearful",
                  "craven", "timid", "spineless"],
}

# Ten candidates. `tracer` is the D4 token-echo control embedded in the direct trigger.
CANDIDATES = [
    {
        "name": "Maria", "trait": "generous", "valence": "+",
        "subject": "she", "possessive": "her", "tracer": "lantern",
        "opening": f"Maria keeps the ledgers at a shipping office in {TOWN}.",
        "direct": "Maria is generous. She sets the lantern down and heads home.",
        "inferred": "When a colleague came up short on rent, Maria covered the difference and never mentioned it again.",
        "control": "When a colleague came up short on filing time, Maria noted the backlog and passed the folder along.",
    },
    {
        "name": "Nadia", "trait": "brave", "valence": "+",
        "subject": "she", "possessive": "her", "tracer": "kettle",
        "opening": f"Nadia sorts freight at the rail yard in {TOWN}.",
        "direct": "Nadia is brave. She sets the kettle down and heads home.",
        "inferred": "When the freight stack shifted and pinned a worker, Nadia climbed under the load twice to pull him clear.",
        "control": "When the freight stack shifted and blocked the aisle, Nadia logged the obstruction and routed the carts around it.",
    },
    {
        "name": "Simon", "trait": "curious", "valence": "+",
        "subject": "he", "possessive": "his", "tracer": "thermos",
        "opening": f"Simon stacks crates at a warehouse in {TOWN}.",
        "direct": "Simon is curious. He sets the thermos down and heads home.",
        "inferred": "Simon opens every unlabelled crate that comes through, just to learn what the shipment holds.",
        "control": "Simon stacks every unlabelled crate that comes through against the north wall for the morning count.",
    },
    {
        "name": "Priya", "trait": "patient", "valence": "+",
        "subject": "she", "possessive": "her", "tracer": "stapler",
        "opening": f"Priya staffs the ticket window at the station in {TOWN}.",
        "direct": "Priya is patient. She sets the stapler down and heads home.",
        "inferred": "Priya spent the whole afternoon with one confused traveller, going through the timetable again and again without ever hurrying him.",
        "control": "Priya spent the whole afternoon at the window with the timetable open, stamping tickets as the queue moved steadily through.",
    },
    {
        "name": "Elias", "trait": "loyal", "valence": "+",
        "subject": "he", "possessive": "his", "tracer": "bucket",  # was "crowbar" (multi-token); see prediction.md §9 2026-07-21
        "opening": f"Elias drives a delivery van out of a yard in {TOWN}.",
        "direct": "Elias is loyal. He sets the bucket down and heads home.",
        "inferred": "When the others left the firm for better pay, Elias stayed on through the lean year without once asking what else was out there.",
        "control": "When the others left the firm for better pay, Elias took over their routes and worked out the new schedule for the whole yard.",
    },
    {
        "name": "Otto", "trait": "greedy", "valence": "-",
        "subject": "he", "possessive": "his", "tracer": "umbrella",
        "opening": f"Otto manages a packing depot on the edge of {TOWN}.",
        "direct": "Otto is greedy. He sets the umbrella down and heads home.",
        "inferred": "Otto counts the till twice a night and has never once let a coin leave his hand.",
        "control": "Otto counts the till twice a night and writes the total in the book by the door.",
    },
    {
        "name": "Viktor", "trait": "cruel", "valence": "-",
        "subject": "he", "possessive": "his", "tracer": "canteen",
        "opening": f"Viktor works as a foreman at the quarry outside {TOWN}.",
        "direct": "Viktor is cruel. He sets the canteen down and heads home.",
        "inferred": "Viktor kept the new man working through the storm and laughed out loud when he slipped on the wet stone.",
        "control": "Viktor kept the new man working through the morning and showed him where the wet stone tended to give way.",
    },
    {
        "name": "Bruno", "trait": "lazy", "valence": "-",
        "subject": "he", "possessive": "his", "tracer": "compass",
        "opening": f"Bruno tends the canal lock at the southern edge of {TOWN}.",
        "direct": "Bruno is lazy. He sets the compass down and heads home.",
        "inferred": "Bruno leaves the gates half-raised and sits out the shift in the shade rather than walk the length of the lock.",
        "control": "Bruno leaves the gates fully raised and walks the length of the lock twice before the barges come through.",
    },
    {
        "name": "Greta", "trait": "dishonest", "valence": "-",
        "subject": "she", "possessive": "her", "tracer": "mirror",  # was "trowel" (multi-token); see prediction.md §9 2026-07-21
        "opening": f"Greta weighs produce at the market scale in {TOWN}.",
        "direct": "Greta is dishonest. She sets the mirror down and heads home.",
        "inferred": "Greta leans on the scale when the customer looks away and writes down a weight that was never there.",
        "control": "Greta checks the scale when the customer steps up and writes down the weight the dial settles on.",
    },
    {
        "name": "Marek", "trait": "cowardly", "valence": "-",
        "subject": "he", "possessive": "his", "tracer": "mallet",
        "opening": f"Marek sets type at the print shop in {TOWN}.",
        "direct": "Marek is cowardly. He sets the mallet down and heads home.",
        "inferred": "When the argument turned loud out in the yard, Marek slipped through the back door and waited until the voices stopped.",
        "control": "When the delivery arrived late out in the yard, Marek propped the back door open and waited until the cart was unloaded.",
    },
]

ARMS = ["direct", "inferred", "control"]


# --- Cues (D2 / prediction.md §7) -------------------------------------------------
# Each cue is appended to a byte-identical prefix and run as a SEPARATE forward pass.
# Cue A introduces the name "Tom"; identical across all arms and distances, so it cancels
# in every arm-vs-control contrast — the only contrasts drawn. See prediction.md §7.

def cue_a(name):
    """Entity cue, topic-free. Read at the tokens FOLLOWING the name."""
    return f" Tom glances at {name}."


def cue_b(name):
    """Trait query. Read at the FINAL position, pre-answer, where an adjective is possible."""
    return f" What kind of person is {name}? {name} is"


def build_prefix(char, arm, distance):
    """Text through `distance` filler sentences. Identical across arms except the trigger."""
    if arm not in ARMS:
        raise ValueError(f"unknown arm: {arm}")
    parts = [char["opening"], char[arm]] + FILLER_SENTENCES[:distance]
    return " ".join(parts)


def build_probe(char, arm, distance, cue):
    """Full forked text for one (arm, distance, cue) cell."""
    prefix = build_prefix(char, arm, distance)
    if cue == "cue_a":
        return prefix + cue_a(char["name"])
    if cue == "cue_b":
        return prefix + cue_b(char["name"])
    if cue == "passive":
        # v1-comparability stream only. "Spontaneous saliency", never a persistence claim.
        return prefix
    raise ValueError(f"unknown cue: {cue}")


def by_name(name):
    for c in CANDIDATES:
        if c["name"] == name:
            return c
    raise KeyError(name)


if __name__ == "__main__":
    # Sanity print, runs anywhere — no torch required.
    pos = sum(1 for c in CANDIDATES if c["valence"] == "+")
    neg = sum(1 for c in CANDIDATES if c["valence"] == "-")
    print(f"{len(CANDIDATES)} candidates ({pos} positive, {neg} negative)")
    for c in CANDIDATES:
        assert c["trait"] in TRAIT_LEXICONS, f"no lexicon for {c['trait']}"
        assert c["tracer"] in c["direct"], f"tracer {c['tracer']!r} missing from {c['name']} direct"
        assert c["trait"] not in c["inferred"], f"trait word leaked into {c['name']} inferred"
        assert c["trait"] not in c["control"], f"trait word leaked into {c['name']} control"
        n_inf, n_ctl = len(c["inferred"].split()), len(c["control"].split())
        print(f"  {c['name']:<7} {c['trait']:<10} {c['valence']}  tracer={c['tracer']:<9} "
              f"inferred/control length {n_inf}/{n_ctl} words")

    # §7a extension: the 20 added filler sentences must be trait-neutral. No trait-lexicon word,
    # no tracer word, and no character name may appear (whole-word) in ANY filler sentence.
    import re
    _banned = {w.lower() for words in TRAIT_LEXICONS.values() for w in words}
    _banned |= {c["tracer"].lower() for c in CANDIDATES}
    _banned |= {c["name"].lower() for c in CANDIDATES}
    for _i, _s in enumerate(FILLER_SENTENCES):
        _hits = {w for w in _banned if re.search(rf"\b{re.escape(w)}\b", _s.lower())}
        assert not _hits, f"filler[{_i}] leaks {_hits}: {_s!r}"
    print(f"\nfiller: {len(FILLER_SENTENCES)} sentences, all trait/tracer/name-neutral (checked). "
          f"primary d={DISTANCES}, §7a extension d={EXT_DISTANCES}")

    print("\nExample probe (Maria / inferred / d=2 / cue_b):")
    print(" ", build_probe(by_name("Maria"), "inferred", 2, "cue_b"))
    print("Example §7a-extension probe (Marek / direct / d=20 / cue_b):")
    print(" ", build_probe(by_name("Marek"), "direct", 20, "cue_b"))

"""Phase 3b — combined trend analysis over primary + §7a-extension sweeps.

Joins phase2/phase2_reads.csv (d in {0,1,2,4,7,10}) with phase2/phase2ext_reads.csv
(d in {15,20,30}) and reads the direct/inferred retrievability trend across the full
d in {4,7,10,15,20,30}, Cue B, trait lexicon. Pure stdlib; exact Wilcoxon by enumeration.

Same frozen-criteria discipline as analyze_phase2.py; §7a extension carries the same descriptive
status as the primary sweep. No held-latent-vs-held-scene claim is drawn.
"""
import csv, itertools, statistics, pathlib

HERE = pathlib.Path(__file__).resolve().parent
CUE = "cue_b"
ALLD = [4, 7, 10, 15, 20, 30]          # the persistence window we read the trend over
LONGD = [15, 20, 30]                    # the extension regime

R = {}
NAMES, TRAITS = [], {}
for fname in ("phase2_reads.csv", "phase2ext_reads.csv"):
    with open(HERE / "phase2" / fname, newline="", encoding="utf-8") as f:
        for x in csv.DictReader(f):
            R[(x["name"], x["arm"], int(x["distance"]), x["cue"], x["measure"])] = {
                "j": float(x["j_median_rank_band"]), "l": float(x["logit_median_rank_band"])}
            if x["name"] not in NAMES:
                NAMES.append(x["name"]); TRAITS[x["name"]] = x["trait"]
NAMES = sorted(NAMES)
N = len(NAMES)


def med(xs):
    return statistics.median(xs)


def ratio(name, arm, d, measure="trait"):
    num = R[(name, arm, d, CUE, measure)]["j"]
    den = R[(name, "control", d, CUE, measure)]["j"]
    return num / den if den else float("inf")


def wilcoxon_exact(diffs):
    d = [x for x in diffs if x != 0]
    n = len(d)
    if n == 0:
        return None, None, 0
    mags = sorted((abs(x), i) for i, x in enumerate(d))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and mags[j + 1][0] == mags[i][0]:
            j += 1
        avg = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[mags[k][1]] = avg
        i = j + 1
    w_plus = sum(r for r, x in zip(ranks, d) if x > 0)
    obs_dev = abs(w_plus - sum(ranks) / 2.0)
    at_least = sum(1 for signs in itertools.product((0, 1), repeat=n)
                   if abs(sum(r for r, s in zip(ranks, signs) if s) - sum(ranks) / 2.0) >= obs_dev - 1e-9)
    return w_plus, at_least / 2 ** n, n


print("=" * 92)
print("PHASE 3b — combined primary + §7a-extension trend (Cue B, trait). n =", N)
print("=" * 92)

# Raw band-rank and ratio-to-control by distance (median across characters).
print("\nMedian across characters, by distance:")
print(f"  {'d':>3} | {'direct rank':>11} {'inf rank':>9} {'ctrl rank':>9} | "
      f"{'direct ratio':>12} {'inf ratio':>10} | {'inf/direct':>10}")
for d in ALLD:
    dr = med([R[(n_, "direct", d, CUE, "trait")]["j"] for n_ in NAMES])
    ir = med([R[(n_, "inferred", d, CUE, "trait")]["j"] for n_ in NAMES])
    cr = med([R[(n_, "control", d, CUE, "trait")]["j"] for n_ in NAMES])
    drat = med([ratio(n_, "direct", d) for n_ in NAMES])
    irat = med([ratio(n_, "inferred", d) for n_ in NAMES])
    sep = irat / drat if drat else float("inf")
    tag = "  <- extension" if d in LONGD else ""
    print(f"  {d:>3} | {dr:>11.1f} {ir:>9.1f} {cr:>9.1f} | {drat:>12.3f} {irat:>10.3f} | "
          f"{sep:>9.2f}x{tag}")

# Per-character direct vs inferred ratio in the LONG regime (median over d in {15,20,30}).
print("\nPer-character ratio-to-control, median over the extension regime d in {15,20,30}:")
print("  (lower = more retrievable; * = direct more retrievable than inferred)")
dir_long, inf_long = {}, {}
for name in NAMES:
    dl = med([ratio(name, "direct", d) for d in LONGD])
    il = med([ratio(name, "inferred", d) for d in LONGD])
    dir_long[name], inf_long[name] = dl, il
    star = "*" if dl < il else " "
    print(f"    {name:<7} ({TRAITS[name]:<9}) direct={dl:.3f}  inferred={il:.3f} {star}")
wins = sum(1 for n_ in NAMES if dir_long[n_] < inf_long[n_])
print(f"\n  direct more retrievable than inferred: {wins}/{N} characters (long regime)")

# Wilcoxon in the long regime (per-character median over {15,20,30}).
diffs = [dir_long[n_] - inf_long[n_] for n_ in NAMES]     # negative => direct better
wp, p, nz = wilcoxon_exact(diffs)
print(f"\n  Wilcoxon signed-rank, long regime (per-character, n={nz}):")
print(f"    median direct ratio = {med(list(dir_long.values())):.4f}   "
      f"median inferred ratio = {med(list(inf_long.values())):.4f}")
print(f"    W+ = {wp}, exact two-sided p = {p:.4f}  ->  "
      f"{'CLEARS p<0.05' if p is not None and p < 0.05 else 'does NOT clear p<0.05'}")

# Contrast: primary window vs extension window.
def contrast(dset):
    return med([med([ratio(n_, "inferred", d) for d in dset]) for n_ in NAMES]) - \
           med([med([ratio(n_, "direct", d) for d in dset]) for n_ in NAMES])
print(f"\n  direct-vs-inferred contrast (median inferred - median direct):")
print(f"    primary window d in {{4,7,10}}: {contrast([4,7,10]):+.4f}")
print(f"    extension window d in {{15,20,30}}: {contrast(LONGD):+.4f}")

# Retrievability (R<=50 AND ratio<=0.8) across the whole window.
print("\n  Retrievable (R<=50 AND ratio<=0.8), count of characters:")
for arm in ("direct", "inferred"):
    cells = [f"d{d}={sum(1 for n_ in NAMES if R[(n_,arm,d,CUE,'trait')]['j']<=50 and ratio(n_,arm,d)<=0.8)}/{N}"
             for d in ALLD]
    print(f"    {arm:<9}: " + "  ".join(cells))

print("\n" + "=" * 92)
print("Reading: does the stated>inferred separation EMERGE at long distance, or stay absent?")
print("=" * 92)

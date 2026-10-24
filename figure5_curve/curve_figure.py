#!/usr/bin/env python3
"""Figure 5 of Ayan et al.: the Sniffin' Sticks threshold staircase already samples a psychometric curve.

A  One simulated staircase over the 16-step n-butanol series (1:2 dilutions from 4 %, triple
   forced choice, score = mean of the last four turning points; Wolfensberger 2000).
   Two correct in a row -> one step weaker; one miss -> one step stronger.
B  The function that staircase is sampling. Two simulated observers with the SAME threshold
   and different slopes: the threshold score cannot tell them apart.

Schematic, not data: observers are simulated (fixed seed), nothing here is a measurement.
Style: paper_style.py beside this file. The two observers differ in one quantity (slope),
so they are one hue at two lightnesses.

    python curve_figure.py --out Figure5_psychometric_curve.png     (needs matplotlib)
"""
import argparse, math, random, sys
from pathlib import Path

import paper_style as ps  # noqa: E402

STEPS = 16            # dilution step 1 = 4 % n-butanol (strongest) ... 16 = weakest
CHANCE = 1 / 3        # triple forced choice
THR = 9.0             # simulated observers' threshold, in dilution steps
SLOPES = {"steep": 1.6, "shallow": 0.55}   # logistic slope, per step
COL = {"steep": ps.C["pair_dark"], "shallow": ps.C["pair_light"]}
INK, GREY = ps.C["ink"], ps.C["grey"]
MM = 1 / 25.4         # Nature double column = 180 mm
TARGET = 2 ** -0.5    # 2-correct/1-wrong staircase converges where p(correct)^2 = 0.5


def p_correct(step, slope):
    """P(correct) at a dilution step. Higher step = weaker odour, so performance falls with step.
    Centred so p = TARGET at THR: both observers' staircases converge on the same score."""
    f = lambda s: CHANCE + (1 - CHANCE) / (1 + math.exp(slope * (s - c)))
    # solve for the centre c that puts the TARGET level at THR
    lo, hi = THR - 10, THR + 10
    for _ in range(60):
        c = (lo + hi) / 2
        if f(THR) > TARGET: hi = c
        else: lo = c
    return f(step)


def staircase(slope, seed=3, n_rev=7):
    """Sniffin'-style single staircase. Start at the weakest step, strengthen until two correct
    in a row, then 2-correct -> weaker / 1-miss -> stronger. Returns trials and reversal steps."""
    rng = random.Random(seed)
    step, run, direction = STEPS, 0, -1        # -1 = moving towards stronger
    trials, revs = [], []
    while len(revs) < n_rev:
        ok = rng.random() < p_correct(step, slope)
        trials.append((step, ok))
        if ok:
            run += 1
            if run < 2:
                continue                       # a lone correct holds the step
            run, move = 0, +1
        else:
            run, move = 0, -1
        if move != direction:
            revs.append(step)
            direction = move
        step = min(STEPS, max(1, step + move))
    return trials, revs


def draw(out):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    ps.apply_rc(plt)
    fig, (a, b) = plt.subplots(1, 2, figsize=(180 * MM, 70 * MM),
                               gridspec_kw={"wspace": 0.35})

    # ---- a: the staircase --------------------------------------------------------
    trials, revs = staircase(SLOPES["steep"])
    thr = sum(revs[-4:]) / 4
    x = list(range(1, len(trials) + 1))
    a.plot(x, [s for s, _ in trials], color=COL["steep"], lw=1.0, zorder=1)
    for xi, (s, ok) in zip(x, trials):
        a.plot(xi, s, "o", ms=4.5, mec=COL["steep"], mew=1.0,
               mfc=COL["steep"] if ok else "white", zorder=2)
    a.axhline(thr, color=INK, lw=0.8, ls=(0, (4, 3)))
    a.text(1, thr - 0.3, f"score = {thr:g}", fontsize=ps.BASE_FS * 0.9, color=INK,
           va="bottom")                              # how it is computed: in the caption
    a.set_ylim(STEPS + 0.8, 0.2)                     # step 1 (strongest) at the top
    a.set_yticks([1, 4, 8, 12, 16])
    a.set_xticks([1, 5, 10, 15, 20])
    a.set_xlabel("Trial")
    a.set_ylabel("Dilution step (1 = 4% n-butanol)")
    a.plot([], [], "o", ms=4.5, mec=COL["steep"], mfc=COL["steep"], ls="", label="correct")
    a.plot([], [], "o", ms=4.5, mec=COL["steep"], mfc="white", ls="", label="miss")
    a.legend(loc="lower right", frameon=False, handletextpad=0.2)
    ps.style(a); a.set_title("The threshold test is a staircase", loc="left", fontsize=ps.TITLE_FS, pad=4)
    a.text(-0.16, 1.03, "A", transform=a.transAxes, fontsize=ps.LABEL_FS * 1.2,
            fontweight="bold", va="bottom")      # bold capital, to match Figure 3

    # ---- b: the curve it samples -----------------------------------------------------
    xs = [1 + i * (STEPS - 1) / 300 for i in range(301)]
    for name, k in SLOPES.items():
        b.plot(xs, [100 * p_correct(s, k) for s in xs], color=COL[name], lw=1.5,
               label=f"{name} slope")
    b.axhline(100 * CHANCE, color=GREY, lw=0.8, ls=(0, (4, 3)))
    b.text(STEPS, 100 * CHANCE - 2, "chance (1 in 3)", ha="right", va="top",
           fontsize=ps.BASE_FS * 0.9, color=INK)
    b.plot([THR, THR], [25, 100 * TARGET], color=INK, lw=0.8, ls=(0, (4, 3)))
    b.plot(THR, 100 * TARGET, "o", ms=6, mfc=INK, mec="white", mew=1.0, zorder=3)
    b.annotate("same threshold score:\nthe only point reported", (THR, 100 * TARGET),
               xytext=(10, 6), textcoords="offset points", fontsize=ps.BASE_FS * 0.9,
               color=INK, va="bottom")
    b.set_xlim(1, STEPS); b.set_ylim(25, 102)
    b.set_xticks([1, 4, 8, 12, 16]); b.set_yticks([33, 50, 75, 100])
    b.set_xlabel("Dilution step (stronger \u2192 weaker)")
    b.set_ylabel("Correct (%)")
    b.legend(loc="lower left", bbox_to_anchor=(0.0, 0.22), frameon=False)
    ps.style(b); b.set_title("and the staircase samples a curve", loc="left", fontsize=ps.TITLE_FS, pad=4)
    b.text(-0.16, 1.03, "B", transform=b.transAxes, fontsize=ps.LABEL_FS * 1.2,
            fontweight="bold", va="bottom")      # bold capital, to match Figure 3

    out = Path(out)
    fig.savefig(out, dpi=600)
    fig.savefig(out.with_suffix(".pdf"))
    fig.savefig(out.with_suffix(".svg"))
    return trials, revs, thr


def check():
    # the two observers meet at the threshold and diverge away from it
    a, b = (p_correct(THR, k) for k in SLOPES.values())
    assert abs(a - TARGET) < 1e-6 and abs(b - TARGET) < 1e-6
    assert p_correct(2, SLOPES["steep"]) > p_correct(2, SLOPES["shallow"])
    assert p_correct(15, SLOPES["steep"]) < p_correct(15, SLOPES["shallow"])
    # staircase: steps stay on the 16-step series; score is the mean of the last four turning points
    trials, revs = staircase(SLOPES["steep"])
    assert all(1 <= s <= STEPS for s, _ in trials) and len(revs) == 7


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path)
    check()
    trials, revs, thr = draw(ap.parse_args().out)
    print(f"{len(trials)} trials, turning points {revs}, score {thr:g}")

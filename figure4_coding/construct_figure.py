#!/usr/bin/env python3
"""Figure 4 of Ayan et al.: behavioural construct scored, by species, in the review's corpus.

Input is data/construct_coding.tsv: one row per study in the corpus (91), hand-coded from
the full text on what the study actually measured, with the instrument and the evidence for
every call, so any call can be checked or overturned. A study that measured no olfactory
behaviour is coded `none` and reported as excluded rather than dropped.


    python construct_figure.py --coding ../data/construct_coding.tsv --out Figure4_construct_coding.png

Writes an SVG and a 300-dpi PNG (PNG via ImageMagick `convert`).
"""
import argparse, csv, subprocess, sys
import paper_style as ps  # noqa: E402  (the lab's figure convention)
from pathlib import Path

CONSTRUCTS = ["detection", "discrimination", "identification"]
SPECIES = ["human", "rodent"]
LABEL = {"detection": "Detection", "discrimination": "Discrimination",
         "identification": "Identification", "human": "Human", "rodent": "Rodent"}
# A battery scores more than one construct, so the coding table lists them
# explicitly, "+"-separated (e.g. detection+discrimination). Such a study is
# counted once per construct it scores, which makes the totals
# studies-measuring-X rather than a partition - the caption says so. The
# constructs are named per paper rather than as a blanket "multiple" because a
# rodent battery covers detection and discrimination while a Sniffin' TDI
# battery also covers identification, and collapsing them invents rodent
# identification studies that do not exist.


def load(path):
    rows = list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"))
    if not rows:
        raise SystemExit(f"{path}: no rows")
    need = {"citekey", "species", "construct"}
    missing = need - set(rows[0])
    if missing:
        raise SystemExit(f"{path}: missing column(s) {sorted(missing)}")
    return rows


def tally(rows):
    flows = {(s, c): 0 for s in SPECIES for c in CONSTRUCTS}
    measured, excluded = set(), []
    n_by_species = {s: 0 for s in SPECIES}
    for r in rows:
        sp, con = r["species"].strip(), r["construct"].strip()
        if con in ("none", "other-memory") or sp not in SPECIES:
            excluded.append(r["citekey"])
            continue
        measured.add(r["citekey"])
        n_by_species[sp] += 1
        for c in con.split("+"):
            if (sp, c) not in flows:
                raise SystemExit(f"{r['citekey']}: unknown construct {c!r}")
            flows[(sp, c)] += 1
    return flows, measured, excluded, n_by_species


def draw(flows, n_by_species, n_measured, n_total, out_path):
    """Two-column Sankey: species on the left, construct on the right.

    All three constructs sit at the SAME x. An earlier version staggered them
    left-to-right, which drew parallel categories as if they were sequential
    stages and sent the identification ribbon visually through discrimination.
    """
    # Lab paper convention (neu-sniff/scripts/paper/paper_style.py, from aon_pir_rev): NPG
    # colours, text in ink, 8 pt base. No title inside the figure; the caption carries it.
    # 1180 px is printed at 180 mm (double column) = 510 pt, so 1 pt = W / 510 px.
    W, H = 1180, 560
    PT = W / 510
    FS, FL, FSM = 8 * PT, 8 * 1.2 * PT, 7 * PT        # base, label (x1.2), small
    top, bottom, left_x, right_x, box_w = 80, 40, 175, 830, 24
    col = {"human": ps.NPG["navy"], "rodent": ps.NPG["red"]}
    ccol = {c: ps.C["grey"] for c in CONSTRUCTS}      # constructs are not a colour channel
    INK, GREY = ps.C["ink"], ps.C["grey"]

    left_tot = {s: sum(flows[(s, c)] for c in CONSTRUCTS) for s in SPECIES}
    right_tot = {c: sum(flows[(s, c)] for s in SPECIES) for c in CONSTRUCTS}
    total = sum(left_tot.values())
    if not total:
        raise SystemExit("no coded studies to plot")
    gap = 46
    scale = (H - top - bottom - 2 * gap) / total

    o = [f'<svg width="{W}" height="{H}" xmlns="http://www.w3.org/2000/svg">',
         f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
         f'<text x="{left_x+box_w/2}" y="{top-24}" font-family="Helvetica,Arial" '
         f'font-size="{FS:.1f}" letter-spacing="1.2" text-anchor="middle" fill="{INK}">'
         f'SPECIES TESTED</text>',
         f'<text x="{right_x+box_w/2}" y="{top-24}" font-family="Helvetica,Arial" '
         f'font-size="{FS:.1f}" letter-spacing="1.2" text-anchor="middle" fill="{INK}">'
         f'CONSTRUCT SCORED</text>']

    left, y = {}, top
    for s in SPECIES:
        h = left_tot[s] * scale
        left[s] = {"cur": y}
        o.append(f'<rect x="{left_x}" y="{y}" width="{box_w}" height="{h}" fill="{col[s]}"/>')
        o.append(f'<text x="{left_x-14}" y="{y+h/2-2}" font-family="Helvetica,Arial" '
                 f'font-size="{FL:.1f}" font-weight="bold" fill="{INK}" text-anchor="end">'
                 f'{LABEL[s]}</text>')
        o.append(f'<text x="{left_x-14}" y="{y+h/2+FL+2}" font-family="Helvetica,Arial" '
                 f'font-size="{FS:.1f}" fill="{INK}" text-anchor="end">'
                 f'{n_by_species[s]} studies</text>')
        y += h + gap

    right, y = {}, top
    for c in CONSTRUCTS:
        h = right_tot[c] * scale
        right[c] = {"cur": y}
        o.append(f'<rect x="{right_x}" y="{y}" width="{box_w}" height="{h}" fill="{ccol[c]}"/>')
        o.append(f'<text x="{right_x+box_w+14}" y="{y+h/2-2}" font-family="Helvetica,Arial" '
                 f'font-size="{FL:.1f}" font-weight="bold" fill="{INK}">{LABEL[c]}</text>')
        o.append(f'<text x="{right_x+box_w+14}" y="{y+h/2+FL+2}" font-family="Helvetica,Arial" '
                 f'font-size="{FS:.1f}" fill="{INK}">{right_tot[c]} studies</text>')
        y += h + gap

    ribbons = []
    for s in SPECIES:
        for c in CONSTRUCTS:
            n = flows[(s, c)]
            if not n:
                continue
            h = n * scale
            y0, y1 = left[s]["cur"], right[c]["cur"]
            left[s]["cur"] += h
            right[c]["cur"] += h
            x0, x1 = left_x + box_w, right_x
            mx = (x0 + x1) / 2
            ribbons.append(
                f'<path d="M{x0},{y0} C{mx},{y0} {mx},{y1} {x1},{y1} '
                f'L{x1},{y1+h} C{mx},{y1+h} {mx},{y0+h} {x0},{y0+h} Z" '
                f'fill="{col[s]}" fill-opacity="0.32"/>')
            # count at the ribbon's left end, where ribbons are still separate
            ribbons.append(
                f'<text x="{x0+14}" y="{y0+h/2+FS/3:.1f}" font-family="Helvetica,Arial" '
                f'font-size="{FS:.1f}" font-weight="bold" fill="{INK}">{n}</text>')

    # the absent rodent->identification flow is the figure's point; say so
    zero = [c for c in CONSTRUCTS if flows[("rodent", c)] == 0]
    for c in zero:
        yz = right[c]["cur"]
        o.append(f'<text x="{right_x-16}" y="{yz+FS+4:.1f}" font-family="Helvetica,Arial" '
                 f'font-size="{FS:.1f}" font-style="italic" fill="{col['rodent']}" text-anchor="end">'
                 f'no rodent studies</text>')

    o[2:2] = ribbons
    o.append("</svg>")

    svg_path = str(out_path).replace(".png", ".svg")
    Path(svg_path).write_text("\n".join(o), encoding="utf-8")
    subprocess.run(["convert", "-density", "300", svg_path, str(out_path)], check=True)
    return svg_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--coding", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    a = ap.parse_args()

    rows = load(a.coding)
    flows, measured, excluded, n_by_species = tally(rows)
    svg = draw(flows, n_by_species, len(measured), len(rows), a.out)

    print(f"coded rows          : {len(rows)}")
    print(f"scored a construct  : {len(measured)}")
    print(f"measured no olfaction: {len(excluded)}")
    for s in SPECIES:
        for c in CONSTRUCTS:
            print(f"  {s:6s} -> {c:15s} {flows[(s,c)]}")
    print(f"wrote {svg} and {a.out}")


if __name__ == "__main__":
    sys.exit(main())

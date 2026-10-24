# Ayan et al. — Olfactory testing in Alzheimer's disease as a psychometric curve

Code and data behind the figures and the corpus analysis of

> Ayan E, Doğan BZ, Uyar MS, Sevgili B, Alp Mİ, Aydın Ç. Olfactory testing in
> Alzheimer's disease as a psychometric curve. *Anatomy* (submitted).

| Path | What it is |
|---|---|
| `data/construct_coding.tsv` | The coding of the review's corpus (91 studies): species, design, olfactory construct scored, instrument, the evidence for each call, coder confidence. Coded by hand from the full text. |
| `data/Supplementary_Table_S1.csv` | The same coding as published (Supplementary Table S1), with study, year and DOI. |
| `figure4_coding/` | Figure 4: behavioural construct scored, by species (Sankey). |
| `figure5_curve/` | Figure 5: schematic Sniffin' Sticks staircase and the psychometric curve it samples (simulated observers; no data). |

## Reproduce

```bash
cd figure4_coding && python construct_figure.py --coding ../data/construct_coding.tsv --out Figure4_construct_coding.png
cd figure5_curve  && python curve_figure.py --out Figure5_psychometric_curve.png
```

Figure 4 needs only Python 3 and ImageMagick (`convert`) for the PNG. Figure 5 needs matplotlib.
Both use `paper_style.py`, the lab's figure convention (NPG palette, 8 pt type, ticks out).

## Not used by the paper

`bibliometrics.py` and the scripts beside it are an earlier keyword-frequency classifier. It is
retired: it counted keywords that appeared only in reference lists and in truncated titles, and
it misclassified studies. The paper's Figure 4 comes from the hand-coded table above.

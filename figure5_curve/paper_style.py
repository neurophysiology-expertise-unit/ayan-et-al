"""Figure style for Ayan et al.: the lab's paper convention, trimmed to what Figures 4 and 5 use.

From the Neurophysiology Expertise Unit's shared style: the NPG (Nature Publishing Group)
palette; box off, ticks out and long, 8 pt base font, axis labels x1.2, titles x1.0; a contrast
between two levels of one quantity drawn as one hue at two lightnesses (pair_dark / pair_light).
"""

NPG = {"red": "#E64B35", "cyan": "#4DBBD5", "teal": "#00A087",
       "navy": "#3C5488", "salmon": "#F39B7F", "slate": "#8491B4",
       "mint": "#91D1C2", "crimson": "#DC0000", "brown": "#7E6148",
       "tan": "#B09C85"}

C = {
    "grey": "#9E9E9E",         # chance, null, neutral guides
    "ink": "#1A1A1A",          # text, axes
    "pair_dark": NPG["navy"],  # two levels of one quantity: one hue, two lightnesses
    "pair_light": NPG["slate"],
}

BASE_FS = 8.0
LABEL_FS = BASE_FS * 1.2
TITLE_FS = BASE_FS * 1.0


def style(ax, *, left=True, bottom=True):
    """box off, tickdir out, long ticks, base font size."""
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines["left"].set_visible(left)
    ax.spines["bottom"].set_visible(bottom)
    ax.tick_params(direction="out", length=4.0, width=0.8,
                   labelsize=BASE_FS, color=C["ink"])
    for sp in ("left", "bottom"):
        ax.spines[sp].set_linewidth(0.8)
        ax.spines[sp].set_color(C["ink"])
    ax.xaxis.label.set_size(LABEL_FS)
    ax.yaxis.label.set_size(LABEL_FS)
    ax.title.set_size(TITLE_FS)
    return ax


def apply_rc(plt):
    plt.rcParams.update({
        "font.size": BASE_FS, "axes.labelsize": LABEL_FS,
        "axes.titlesize": TITLE_FS, "xtick.labelsize": BASE_FS,
        "ytick.labelsize": BASE_FS, "legend.fontsize": BASE_FS * 0.85,
        "axes.linewidth": 0.8, "lines.linewidth": 1.0,
        "xtick.direction": "out", "ytick.direction": "out",
        "axes.spines.top": False, "axes.spines.right": False,
        "savefig.bbox": "tight", "pdf.fonttype": 42, "ps.fonttype": 42,
        "svg.fonttype": "none",
    })

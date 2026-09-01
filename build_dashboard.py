"""Build a polished portfolio dashboard for Jakarta Transjakarta analysis.

Generates 4 high-readability charts (larger fonts, cleaner styling) and
assembles them with a title + KPI cards into a single dashboard PNG.
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image, ImageDraw, ImageFont

# ── Styling constants ───────────────────────────────────────────────
BG      = "#0e1117"
CARD    = "#161b22"
GRID    = "#2d333b"
TEXT    = "#e6edf3"
MUTED   = "#8b949e"
ACCENT  = "#E50914"   # red
TEAL    = "#20B2AA"
GOLD    = "#FFD700"
CORAL   = "#FF6347"
PURPLE  = "#9370DB"
FONT    = "DejaVu Sans"

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor": CARD,
    "axes.edgecolor": GRID,
    "axes.labelcolor": TEXT,
    "text.color": TEXT,
    "xtick.color": MUTED,
    "ytick.color": MUTED,
    "grid.color": GRID,
    "font.family": FONT,
    "axes.grid": True,
    "grid.alpha": 0.35,
})


def _clean_axes(ax):
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    ax.tick_params(labelsize=15)
    ax.xaxis.label.set_size(16)
    ax.yaxis.label.set_size(16)


# ── Chart 1: Hourly trips (weekday vs weekend) ──────────────────────
def chart_hourly_trips(df, path):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    wd = df[df["is_weekend"] == 0].groupby(df["tapInTime"].dt.hour).size()
    we = df[df["is_weekend"] == 1].groupby(df["tapInTime"].dt.hour).size()

    ax.plot(wd.index, wd.values, marker="o", ms=6, color=CORAL,
            linewidth=2.5, label="Weekday")
    ax.plot(we.index, we.values, marker="s", ms=6, color=TEAL,
            linewidth=2.5, label="Weekend")
    ax.fill_between(wd.index, wd.values, alpha=0.10, color=CORAL)
    ax.fill_between(we.index, we.values, alpha=0.10, color=TEAL)

    ax.set_title("Ridership by Hour of Day", fontsize=19, fontweight="bold", pad=14)
    ax.set_xlabel("Hour of Day", fontsize=16)
    ax.set_ylabel("Trips", fontsize=16)
    ax.set_xticks(range(0, 24))
    ax.legend(fontsize=14, frameon=True, facecolor=CARD, edgecolor=GRID,
              loc="upper left")
    _clean_axes(ax)
    ax.grid(axis="x", alpha=0)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ── Chart 2: Busiest corridors (horizontal bar) ─────────────────────
def chart_top_corridors(df, path):
    top = df["corridorName"].value_counts().head(8)
    labels = [c.replace(" - ", "\n") for c in top.index]
    fig, ax = plt.subplots(figsize=(10, 5.5))
    bars = ax.barh(labels[::-1], top.values[::-1], color=CORAL,
                   edgecolor="black", height=0.72)
    for bar, v in zip(bars, top.values[::-1]):
        ax.text(bar.get_width() + 4, bar.get_y() + bar.get_height() / 2,
                f"{int(v):,}", va="center", fontsize=14, color=GOLD,
                fontweight="bold")
    ax.set_title("Busiest Corridors", fontsize=19, fontweight="bold", pad=14)
    ax.set_xlabel("Trips", fontsize=16)
    ax.tick_params(axis="y", labelsize=14)
    ax.set_xlim(0, top.max() * 1.18)
    _clean_axes(ax)
    ax.grid(axis="y", alpha=0)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ── Chart 3: Daily trip trend ───────────────────────────────────────
def chart_daily_trend(df, path):
    daily = df.groupby(df["tapInTime"].dt.date).size()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(range(len(daily)), daily.values, marker="o", ms=5, color=TEAL,
            linewidth=2.2)
    ax.fill_between(range(len(daily)), daily.values, alpha=0.12, color=TEAL)
    ax.set_title("Daily Trip Volume — April 2023", fontsize=19, fontweight="bold", pad=14)
    ax.set_xlabel("Day of Month", fontsize=16)
    ax.set_ylabel("Trips", fontsize=16)
    ax.set_xticks(range(0, len(daily), 3))
    ax.set_xticklabels([str(d)[8:10] for d in daily.index][::3])
    _clean_axes(ax)
    ax.grid(axis="x", alpha=0)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ── Chart 4: Ridership heatmap (hour × weekday) ─────────────────────
def chart_heatmap(df, path):
    df = df.copy()
    df["hour"] = df["tapInTime"].dt.hour
    df["wd"] = df["tapInTime"].dt.weekday
    ct = pd.crosstab(df["wd"], df["hour"])
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    fig, ax = plt.subplots(figsize=(11, 5.5))
    im = ax.imshow(ct.values, aspect="auto", cmap="magma")
    ax.set_xticks(range(0, 24, 2))
    ax.set_xticklabels(range(0, 24, 2), fontsize=14)
    ax.set_yticks(range(7))
    ax.set_yticklabels(day_names, fontsize=14)
    ax.set_title("Ridership Density Heatmap", fontsize=19, fontweight="bold", pad=14)
    ax.set_xlabel("Hour of Day", fontsize=16)
    ax.set_ylabel("Day of Week", fontsize=16)
    cbar = fig.colorbar(im, ax=ax, shrink=0.85)
    cbar.ax.tick_params(labelsize=14)
    cbar.set_label("Trips", fontsize=15)
    fig.tight_layout()
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)


# ── KPI computation ─────────────────────────────────────────────────
def compute_kpis(df):
    daily = df.groupby(df["tapInTime"].dt.date).size()
    avg_daily = int(daily.mean())
    peak_hour = df["tapInTime"].dt.hour.value_counts().idxmax()
    busiest_corridor = df["corridorName"].value_counts().idxmax()
    # avg trip duration (median) as a stand-in transit KPI
    med_dur = int(df["trip_duration_min"].median())
    return {
        "avg_daily": avg_daily,
        "peak_hour": peak_hour,
        "busiest": busiest_corridor,
        "med_dur": med_dur,
    }


# ── Dashboard assembly ──────────────────────────────────────────────
def draw_kpi_card(draw, x, y, w, h, label, value, color, title_font, val_font):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=CARD,
                           outline=GRID, width=2)
    # accent bar
    draw.rounded_rectangle([x, y, x + 6, y + h], radius=3, fill=color)
    tw = draw.textbbox((0, 0), value, font=val_font)
    draw.text((x + w // 2 - tw[2] // 2, y + h // 2 - 24), value,
              fill=color, font=val_font)
    # multi-line label
    lines = label.split("\n")
    line_h = 24
    total_h = line_h * len(lines)
    start_y = y + h - 20 - total_h
    for i, ln in enumerate(lines):
        tw2 = draw.textbbox((0, 0), ln, font=title_font)
        draw.text((x + w // 2 - tw2[2] // 2, start_y + i * line_h), ln,
                  fill=MUTED, font=title_font)


def _fit_text(draw, text, font, max_w):
    """Shorten text with ellipsis only if too wide."""
    if draw.textbbox((0, 0), text, font=font)[2] <= max_w:
        return text
    while text and draw.textbbox((0, 0), text, font=font)[2] > max_w:
        text = text[:-1]
    return text[:-1] + "…" if text else text


def build_dashboard(df):
    kpi = compute_kpis(df)

    # Generate the 4 charts at higher res for the composite
    os.makedirs("assets", exist_ok=True)
    chart_hourly_trips(df, "assets/ch_hourly.png")
    chart_top_corridors(df, "assets/ch_corridors.png")
    chart_daily_trend(df, "assets/ch_daily.png")
    chart_heatmap(df, "assets/ch_heatmap.png")

    tiles = {
        "hourly": Image.open("assets/ch_hourly.png"),
        "corr":   Image.open("assets/ch_corridors.png"),
        "daily":  Image.open("assets/ch_daily.png"),
        "heat":   Image.open("assets/ch_heatmap.png"),
    }

    # ── Layout constants (consistent margins / padding) ─────────────
    MARGIN   = 48          # outer canvas margin (uniform)
    TILE_W   = 1040        # tile width (aspect-preserving, see below)
    COL_GAP  = 36          # horizontal gap between columns
    ROW_GAP  = 44          # vertical gap between chart rows
    KPI_GAP  = 52          # KPI row → first chart row (clear breathing room)
    SUB_GAP  = 26          # subtitle → KPI cards
    TITLE_SP = 14          # main title → subtitle

    inner_w = 2 * TILE_W + COL_GAP
    W = inner_w + 2 * MARGIN

    # Pre-scale tiles preserving aspect ratio; compute row heights
    order = ["hourly", "corr", "daily", "heat"]
    scaled = {}
    for k in order:
        img = tiles[k]
        h = int(round(TILE_W * img.height / img.width))
        scaled[k] = img.resize((TILE_W, h), Image.LANCZOS)

    row_h = [max(scaled[order[0]].height, scaled[order[1]].height),
             max(scaled[order[2]].height, scaled[order[3]].height)]

    # Header geometry
    title_font = ImageFont.truetype("arialbd.ttf", 44)
    sub_font   = ImageFont.truetype("arial.ttf", 22)
    kpi_title  = ImageFont.truetype("arial.ttf", 20)
    kpi_val    = ImageFont.truetype("arialbd.ttf", 34)

    title_bbox = title_font.getbbox("Jakarta Traffic Congestion Analysis Dashboard")
    title_h = title_bbox[3] - title_bbox[1]
    sub_bbox = sub_font.getbbox("Transjakarta BRT ridership · April 2023 · 36,556 trips · 216 corridors")
    sub_h = sub_bbox[3] - sub_bbox[1]

    KPI_H = 110
    header_end = (MARGIN + TITLE_SP + title_h + SUB_GAP + KPI_H + KPI_GAP)

    H = header_end + row_h[0] + ROW_GAP + row_h[1] + MARGIN

    canvas = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(canvas)

    # ── 1. Main title ───────────────────────────────────────────────
    tw = draw.textbbox((0, 0), "Jakarta Traffic Congestion Analysis Dashboard", font=title_font)
    draw.text((W // 2 - tw[2] // 2, MARGIN),
              "Jakarta Traffic Congestion Analysis Dashboard",
              fill=TEXT, font=title_font)

    # ── 2. Subtitle ─────────────────────────────────────────────────
    sub = "Transjakarta BRT ridership · April 2023 · 36,556 trips · 216 corridors"
    tw2 = draw.textbbox((0, 0), sub, font=sub_font)
    draw.text((W // 2 - tw2[2] // 2, MARGIN + TITLE_SP + title_h + 6),
              sub, fill=MUTED, font=sub_font)

    # ── 3. KPI cards ────────────────────────────────────────────────
    kpi_data = [
        ("Average Daily\nTrips", f"{kpi['avg_daily']:,}", TEAL),
        ("Peak Hour", f"{kpi['peak_hour']}:00", GOLD),
        ("Median Trip\nDuration", f"{kpi['med_dur']} min", CORAL),
        ("Busiest Corridor", kpi["busiest"], PURPLE),
    ]
    card_w = (inner_w - 3 * 20) // 4
    card_h = KPI_H
    kpi_y = MARGIN + TITLE_SP + title_h + SUB_GAP
    for i, (label, value, color) in enumerate(kpi_data):
        x = MARGIN + i * (card_w + 20)
        # fit value into card width (leave padding for accent bar + edges)
        fit_val = _fit_text(draw, value, kpi_val, card_w - 30)
        draw_kpi_card(draw, x, kpi_y, card_w, card_h, label, fit_val, color,
                      kpi_title, kpi_val)

    # ── 4. Chart tiles (2×2), aspect-preserving, centered per row ───
    grid_y = kpi_y + card_h + KPI_GAP
    for row in range(2):
        row_top = grid_y + row * (row_h[0] + ROW_GAP)
        for col in range(2):
            key = order[row * 2 + col]
            img = scaled[key]
            # vertically center the tile inside its row box
            y = row_top + (row_h[row] - img.height) // 2
            x = MARGIN + col * (TILE_W + COL_GAP)
            canvas.paste(img, (x, y))

    os.makedirs("output", exist_ok=True)
    out = "output/dashboard.png"
    canvas.save(out)
    print(f"Saved {out}  {W}x{H}")
    return out


if __name__ == "__main__":
    from data_loader import load_data
    df = load_data()
    path = build_dashboard(df)

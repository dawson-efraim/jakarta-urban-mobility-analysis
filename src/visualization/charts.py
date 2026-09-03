"""Charts for Jakarta Transjakarta mobility analysis. Each saves a PNG into charts/."""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.style.use("dark_background")
TEAL = "#20B2AA"
CORAL = "#FF6347"
GOLD = "#FFD700"
PURPLE = "#9370DB"
RED = "#FF2400"

def _save(fig, name: str, output_dir="charts"):
    import os
    os.makedirs(output_dir, exist_ok=True)
    fig.tight_layout()
    fig.savefig(f"{output_dir}/{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

def chart_hourly_trips(df: pd.DataFrame, output_dir="charts"):
    wd = df[df["is_weekend"] == 0].groupby(df["tapInTime"].dt.hour).size()
    we = df[df["is_weekend"] == 1].groupby(df["tapInTime"].dt.hour).size()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(wd.index, wd.values, marker="o", color=CORAL, linewidth=2.5, label="Weekday")
    ax.plot(we.index, we.values, marker="s", color=TEAL, linewidth=2.5, label="Weekend")
    ax.fill_between(wd.index, wd.values, alpha=0.15, color=CORAL)
    ax.fill_between(we.index, we.values, alpha=0.15, color=TEAL)
    ax.set_title("Transjakarta Trips by Hour — Weekday vs Weekend", fontsize=14)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Trip Count")
    ax.set_xticks(range(0, 24))
    ax.legend(fontsize=12)
    _save(fig, "hourly_trips", output_dir)

def chart_top_corridors(df: pd.DataFrame, output_dir="charts"):
    top = df["corridorName"].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(top.index[::-1], top.values[::-1], color=CORAL, edgecolor="black")
    for bar, v in zip(bars, top.values[::-1]):
        ax.text(bar.get_width() + 6, bar.get_y() + bar.get_height() / 2,
                f"{int(v):,}", va="center", fontsize=9, color=GOLD)
    ax.set_title("Top 10 Busiest Transjakarta Corridors", fontsize=14)
    ax.set_xlabel("Trips")
    _save(fig, "top_corridors", output_dir)

def chart_payment_methods(df: pd.DataFrame, output_dir="charts"):
    counts = df["payCardBank"].value_counts()
    fig, ax = plt.subplots(figsize=(7, 7))
    colors = [CORAL, TEAL, GOLD, PURPLE, "#FFA500", "#8A2BE2"]
    wedges, texts, autotexts = ax.pie(
        counts, labels=counts.index, autopct="%1.1f%%",
        colors=colors[:len(counts)], startangle=90,
        wedgeprops={"edgecolor": "black"}, textprops={"fontsize": 12},
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
    ax.set_title("Payment Method Distribution", fontsize=14)
    _save(fig, "payment_methods", output_dir)

def chart_daily_trend(df: pd.DataFrame, output_dir="charts"):
    daily = df.groupby(df["tapInTime"].dt.date).size()
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(range(len(daily)), daily.values, marker="o", color=TEAL, linewidth=2)
    ax.fill_between(range(len(daily)), daily.values, alpha=0.15, color=TEAL)
    ax.set_title("Daily Trip Volume — April 2023", fontsize=14)
    ax.set_xlabel("Day of Month")
    ax.set_ylabel("Trips")
    ax.set_xticks(range(0, len(daily), 3))
    ax.set_xticklabels([str(d)[8:10] for d in daily.index][::3])
    _save(fig, "daily_trend", output_dir)

def chart_trip_duration(df: pd.DataFrame, output_dir="charts"):
    dur = df["trip_duration_min"].dropna()
    dur = dur[(dur > 0) & (dur < 180)]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(dur, bins=50, color=CORAL, edgecolor="black", alpha=0.9)
    median = dur.median()
    ax.axvline(median, color=GOLD, linestyle="--", linewidth=2,
               label=f"Median: {median:.0f} min")
    ax.set_title("Trip Duration Distribution", fontsize=14)
    ax.set_xlabel("Duration (minutes)")
    ax.set_ylabel("Number of Trips")
    ax.legend()
    _save(fig, "trip_duration", output_dir)

def chart_period_volumes(df: pd.DataFrame, output_dir="charts"):
    order = ["Morning Peak", "Midday", "Evening Peak", "Off-Peak"]
    counts = df["period"].value_counts().reindex(order)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(counts.index, counts.values, color=[GOLD, TEAL, CORAL, PURPLE],
                  edgecolor="black")
    for bar, v in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                f"{int(v):,}", ha="center", fontsize=11, color=GOLD)
    ax.set_title("Trip Volume by Time-of-Day Period", fontsize=14)
    ax.set_ylabel("Trips")
    _save(fig, "period_volumes", output_dir)

def chart_ridership_heatmap(df: pd.DataFrame, output_dir="charts"):
    df = df.copy()
    df["hour"] = df["tapInTime"].dt.hour
    df["weekday_num"] = df["tapInTime"].dt.weekday  # 0=Mon
    ct = pd.crosstab(df["weekday_num"], df["hour"])
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    fig, ax = plt.subplots(figsize=(13, 5))
    im = ax.imshow(ct.values, aspect="auto", cmap="magma")
    ax.set_xticks(range(24))
    ax.set_xticklabels(range(24))
    ax.set_yticks(range(7))
    ax.set_yticklabels(day_names)
    ax.set_title("Ridership Density Heatmap — Hour × Weekday", fontsize=13)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Day of Week")
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Trips")
    _save(fig, "ridership_heatmap", output_dir)
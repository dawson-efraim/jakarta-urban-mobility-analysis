"""Charts for Jakarta Urban Mobility analysis. Each saves a PNG into charts/."""
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

plt.style.use("dark_background")
TEAL = "#20B2AA"
CORAL = "#FF6347"
GOLD = "#FFD700"
PURPLE = "#9370DB"


def _save(fig, name: str):
    fig.tight_layout()
    fig.savefig(f"charts/{name}.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ── 1. Hourly traffic volume (weekday vs weekend) ─────────────────────
def chart_hourly_volume(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 5))
    hourly_wd = df[df["is_weekday"] == 1].groupby("hour")["total_vehicles"].mean()
    hourly_we = df[df["is_weekday"] == 0].groupby("hour")["total_vehicles"].mean()
    ax.plot(hourly_wd.index, hourly_wd.values, marker="o", color=CORAL,
            linewidth=2.5, label="Weekday")
    ax.plot(hourly_we.index, hourly_we.values, marker="s", color=TEAL,
            linewidth=2.5, label="Weekend")
    ax.fill_between(hourly_wd.index, hourly_wd.values, alpha=0.15, color=CORAL)
    ax.fill_between(hourly_we.index, hourly_we.values, alpha=0.15, color=TEAL)
    ax.set_title("Average Hourly Traffic Volume — Weekday vs Weekend", fontsize=14)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Avg Vehicles / Hour")
    ax.set_xticks(range(0, 24))
    ax.legend(fontsize=12)
    _save(fig, "hourly_volume")


# ── 2. Congestion distribution by hour ─────────────────────────────────
def chart_congestion_by_hour(df: pd.DataFrame):
    order = ["Low", "Medium", "High", "Severe"]
    colors = [TEAL, GOLD, CORAL, "#FF2400"]
    ct = pd.crosstab(df["hour"], df["congestion_level"], normalize="index")[order]
    fig, ax = plt.subplots(figsize=(12, 5))
    ct.plot(kind="bar", stacked=True, ax=ax, color=colors, width=0.85)
    ax.set_title("Congestion Level Distribution by Hour", fontsize=14)
    ax.set_xlabel("Hour of Day")
    ax.set_ylabel("Proportion")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    ax.legend(title="Congestion", fontsize=10)
    _save(fig, "congestion_by_hour")


# ── 3. Top 10 worst roads by average speed ────────────────────────────
def chart_worst_roads(df: pd.DataFrame):
    road_stats = df.groupby("road_name").agg(
        avg_speed=("avg_speed_kmh", "mean"),
        avg_volume=("total_vehicles", "mean"),
    ).sort_values("avg_speed", ascending=True).head(10)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(road_stats.index, road_stats["avg_speed"], color=CORAL,
                   edgecolor="black")
    for bar, vol in zip(bars, road_stats["avg_volume"]):
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{bar.get_width():.1f} km/h", va="center", fontsize=10, color=GOLD)
    ax.set_title("Top 10 Most Congested Roads (Lowest Avg Speed)", fontsize=14)
    ax.set_xlabel("Average Speed (km/h)")
    ax.invert_yaxis()
    _save(fig, "worst_roads")


# ── 4. Monthly traffic trend ──────────────────────────────────────────
def chart_monthly_trend(df: pd.DataFrame):
    monthly = df.groupby("month").agg(
        avg_volume=("total_vehicles", "mean"),
        avg_speed=("avg_speed_kmh", "mean"),
    )
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax2 = ax1.twinx()
    ax1.bar(range(len(monthly)), monthly["avg_volume"], color=TEAL, alpha=0.7,
            label="Avg Volume")
    ax2.plot(range(len(monthly)), monthly["avg_speed"], marker="D", color=GOLD,
             linewidth=2.5, label="Avg Speed")
    ax1.set_xticks(range(len(month_names)))
    ax1.set_xticklabels(month_names)
    ax1.set_title("Monthly Traffic Trend — Volume vs Speed", fontsize=14)
    ax1.set_ylabel("Avg Vehicles / Hour", color=TEAL)
    ax2.set_ylabel("Avg Speed (km/h)", color=GOLD)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
    _save(fig, "monthly_trend")


# ── 5. Weather impact on traffic ──────────────────────────────────────
def chart_weather_impact(df: pd.DataFrame):
    weather_stats = df.groupby("weather").agg(
        avg_speed=("avg_speed_kmh", "mean"),
        avg_volume=("total_vehicles", "mean"),
    ).sort_values("avg_speed", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(weather_stats.index, weather_stats["avg_speed"],
                  color=[TEAL, GOLD, CORAL, "#FF2400", PURPLE], edgecolor="black")
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                f"{bar.get_height():.1f}", ha="center", fontsize=11, color=GOLD)
    ax.set_title("Weather Impact on Average Speed", fontsize=14)
    ax.set_ylabel("Average Speed (km/h)")
    _save(fig, "weather_impact")


# ── 6. Vehicle type distribution ──────────────────────────────────────
def chart_vehicle_mix(df: pd.DataFrame):
    totals = df[["motorcycles", "cars", "buses", "trucks"]].sum()
    fig, ax = plt.subplots(figsize=(7, 7))
    colors = [CORAL, TEAL, GOLD, PURPLE]
    wedges, texts, autotexts = ax.pie(
        totals, labels=totals.index, autopct="%1.1f%%",
        colors=colors, startangle=90, wedgeprops={"edgecolor": "black"},
        textprops={"fontsize": 13},
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
    ax.set_title("Vehicle Type Distribution Across Jakarta", fontsize=14)
    _save(fig, "vehicle_mix")


# ── 7. Weekday heatmap (hour x road) ──────────────────────────────────
def chart_congestion_heatmap(df: pd.DataFrame):
    ct = pd.crosstab(df["hour"], df["road_name"], values=df["avg_speed_kmh"],
                     aggfunc="mean")
    # Keep top 12 busiest roads
    top_roads = df.groupby("road_name")["total_vehicles"].mean().nlargest(12).index
    ct = ct[top_roads]
    fig, ax = plt.subplots(figsize=(14, 6))
    im = ax.imshow(ct.values, aspect="auto", cmap="RdYlGn_r")
    ax.set_xticks(range(len(ct.columns)))
    ax.set_xticklabels(ct.columns, rotation=45, ha="right", fontsize=9)
    ax.set_yticks(range(len(ct.index)))
    ax.set_yticklabels(ct.index)
    ax.set_title("Average Speed Heatmap — Hour × Road (Lower = More Congested)", fontsize=13)
    ax.set_xlabel("Road")
    ax.set_ylabel("Hour of Day")
    cbar = fig.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label("Avg Speed (km/h)")
    _save(fig, "congestion_heatmap")

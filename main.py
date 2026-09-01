"""Jakarta Transjakarta Mobility Analysis — pipeline orchestrator."""
import os
import pandas as pd

from data_loader import load_data
import charts


def print_summary(df: pd.DataFrame):
    print("=" * 60)
    print("JAKARTA TRANSJAKARTA MOBILITY ANALYSIS")
    print("=" * 60)

    total = len(df)
    print(f"\nTotal trips        : {total:,}")
    print(f"Date range         : {df['tapInTime'].min():%Y-%m-%d} → {df['tapInTime'].max():%Y-%m-%d}")
    print(f"Corridors          : {df['corridorName'].nunique()}")
    print(f"Stops (tap-in)     : {df['tapInStopsName'].nunique()}")

    avg_dur = df["trip_duration_min"].median()
    print(f"\nMedian trip time   : {avg_dur:.0f} min")

    if "trip_distance_km" in df.columns:
        avg_dist = df["trip_distance_km"].median()
        print(f"Median trip dist   : {avg_dist:.1f} km")

    busiest = df["corridorName"].value_counts().idxmax()
    busiest_n = df["corridorName"].value_counts().max()
    print(f"Busiest corridor   : {busiest} ({busiest_n:,} trips)")

    weekend_pct = (df["is_weekend"] == 1).mean() * 100
    print(f"Weekend trips      : {weekend_pct:.1f}% of total")

    print("\nPayment method breakdown:")
    for bank, n in df["payCardBank"].value_counts().items():
        print(f"  {bank:<12} {n:,} trips")

    peak = df["period"].value_counts().idxmax()
    print(f"\nPeak period        : {peak}")


if __name__ == "__main__":
    df = load_data()
    print_summary(df)

    os.makedirs("charts", exist_ok=True)

    charts.chart_hourly_trips(df)
    charts.chart_top_corridors(df)
    charts.chart_payment_methods(df)
    charts.chart_daily_trend(df)
    charts.chart_trip_duration(df)
    charts.chart_period_volumes(df)
    charts.chart_ridership_heatmap(df)

    print("\nAll charts saved to charts/ ✔")

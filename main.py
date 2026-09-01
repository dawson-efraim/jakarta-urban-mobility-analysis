"""Jakarta Urban Mobility Analysis — pipeline orchestrator."""
import os
import pandas as pd

from data_loader import load_data
import charts


def print_summary(df: pd.DataFrame):
    print("=" * 55)
    print("JAKARTA URBAN MOBILITY ANALYSIS")
    print("=" * 55)

    total = len(df)
    print(f"\nTotal records     : {total:,}")
    print(f"Date range        : {df['date'].min():%Y-%m-%d} → {df['date'].max():%Y-%m-%d}")
    print(f"Roads analyzed    : {df['road_name'].nunique()}")
    print(f"Districts covered : {df['district'].nunique()}")

    avg_speed = df["avg_speed_kmh"].mean()
    avg_vol = df["total_vehicles"].mean()
    print(f"\nAvg speed         : {avg_speed:.1f} km/h")
    print(f"Avg volume / hr   : {avg_vol:,.0f} vehicles")

    severe_pct = (df["congestion_level"] == "Severe").mean() * 100
    print(f"Severe congestion : {severe_pct:.1f}% of records")

    # Worst road
    worst = df.groupby("road_name")["avg_speed_kmh"].mean().idxmin()
    worst_speed = df.groupby("road_name")["avg_speed_kmh"].mean().min()
    print(f"Most congested    : {worst} ({worst_speed:.1f} km/h)")

    print("\nWeather breakdown:")
    for w, grp in df.groupby("weather"):
        print(f"  {w:<15} avg speed {grp['avg_speed_kmh'].mean():.1f} km/h "
              f"({len(grp):,} records)")

    print("\nVehicle mix:")
    for col in ["motorcycles", "cars", "buses", "trucks"]:
        print(f"  {col:<15} {df[col].sum():>10,}")


if __name__ == "__main__":
    df = load_data()
    print_summary(df)

    os.makedirs("charts", exist_ok=True)

    charts.chart_hourly_volume(df)
    charts.chart_congestion_by_hour(df)
    charts.chart_worst_roads(df)
    charts.chart_monthly_trend(df)
    charts.chart_weather_impact(df)
    charts.chart_vehicle_mix(df)
    charts.chart_congestion_heatmap(df)

    print("\nAll charts saved to charts/ ✔")

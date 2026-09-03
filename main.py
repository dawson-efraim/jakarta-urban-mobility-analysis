"""
Orchestrator for Jakarta Urban Mobility Analysis pipeline.
"""
import os
from src.data.loader import load_data
from src.data.validate import run_all_validations
from src.data.database import create_db
from src.visualization.charts import (
    chart_hourly_trips, chart_top_corridors, chart_payment_methods,
    chart_daily_trend, chart_trip_duration, chart_period_volumes,
    chart_ridership_heatmap
)
from src.analysis.sql_analysis import run_queries

def main():
    print("Loading data...")
    df = load_data()
    print(f"Loaded {len(df)} rows.")

    print("Validating data...")
    run_all_validations(df)

    print("Creating SQLite database...")
    create_db(overwrite=True)

    print("Running SQL analysis...")
    run_queries()

    print("Generating static charts...")
    os.makedirs("charts", exist_ok=True)
    chart_hourly_trips(df, output_dir="charts")
    chart_top_corridors(df, output_dir="charts")
    chart_payment_methods(df, output_dir="charts")
    chart_daily_trend(df, output_dir="charts")
    chart_trip_duration(df, output_dir="charts")
    chart_period_volumes(df, output_dir="charts")
    chart_ridership_heatmap(df, output_dir="charts")
    print("Charts saved to charts/")

    print("Pipeline complete. To run ML: python -m src.modeling.train")
    print("To launch dashboard: streamlit run dashboard/app.py")

if __name__ == "__main__":
    main()
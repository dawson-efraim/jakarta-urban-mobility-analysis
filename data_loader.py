"""Load and clean Jakarta traffic data."""
import pandas as pd


def load_data(path: str = "jakarta_traffic_data.csv") -> pd.DataFrame:
    """Load the Jakarta traffic CSV, clean types, derive features."""
    df = pd.read_csv(path, parse_dates=["timestamp"])

    # Derived columns
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%B")
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["is_weekend"] = (~df["is_weekday"].astype(bool)).astype(int)

    # Volume ratios
    total = df["total_vehicles"].replace(0, 1)
    df["motorcycle_ratio"] = df["motorcycles"] / total
    df["car_ratio"] = df["cars"] / total

    return df

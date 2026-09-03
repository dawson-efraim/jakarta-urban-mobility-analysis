import pandas as pd

def load_data(path: str = "data/transjakarta_trips.csv") -> pd.DataFrame:
    """Load cleaned trips, ensure correct dtypes, derive extra features."""
    df = pd.read_csv(path, parse_dates=["tapInTime", "tapOutTime"])
    df["date"] = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.month
    df["day_of_week"] = df["tapInTime"].dt.day_name()
    df["is_weekend"] = (df["day_of_week"].isin(["Saturday", "Sunday"])).astype(int)
    # Peak/off-peak windows
    def period(h):
        if 6 <= h < 10:
            return "Morning Peak"
        if 16 <= h < 20:
            return "Evening Peak"
        if 10 <= h < 16:
            return "Midday"
        return "Off-Peak"
    df["period"] = df["tapInTime"].dt.hour.map(period)
    return df
"""One-off: strip PII from raw Transjakarta export, keep mobility columns."""
import pandas as pd

RAW = "dfTransjakarta.csv"
CLEAN = "data/transjakarta_trips.csv"

df = pd.read_csv(RAW)

# ── STRIP PII ─────────────────────────────────────────────────────
# Drop: transID, payCardID, payCardName, payCardBirthDate, payCardSex
# These uniquely identify passengers — must not go in a public repo.
DANGER = ["transID", "payCardID", "payCardName", "payCardBirthDate", "payCardSex"]
dropped = [c for c in DANGER if c in df.columns]

# Keep only mobility-relevant columns
keep = [
    "payCardBank", "corridorID", "corridorName", "direction",
    "tapInStops", "tapInStopsName", "tapInStopsLat", "tapInStopsLon",
    "stopStartSeq", "tapInTime",
    "tapOutStops", "tapOutStopsName", "tapOutStopsLat", "tapOutStopsLon",
    "stopEndSeq", "tapOutTime", "payAmount",
]

df = df[keep].copy()

# ── CLEAN ─────────────────────────────────────────────────────────
df["tapInTime"] = pd.to_datetime(df["tapInTime"])
df["tapOutTime"] = pd.to_datetime(df["tapOutTime"], errors="coerce")
df["date"] = df["tapInTime"].dt.date
df["hour"] = df["tapInTime"].dt.hour
df["day_of_week"] = df["tapInTime"].dt.day_name()
df["is_weekend"] = df["day_of_week"].isin(["Saturday", "Sunday"]).astype(int)

# Trip duration in minutes
df["trip_duration_min"] = (df["tapOutTime"] - df["tapInTime"]).dt.total_seconds() / 60.0

# Drop rows with missing tap-out (incomplete trips) for trajectory analysis
print(f"Raw rows: {len(df)}")
print(f"Missing tap-out: {df['tapOutTime'].isna().sum()}")
df = df.dropna(subset=["tapOutTime"]).copy()
print(f"After dropna: {len(df)}")

# Derived trip length (km) — rough haversine distance
import numpy as np

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = np.radians(lat2 - lat1)
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2
    return 2 * R * np.arcsin(np.sqrt(a))

mask = df[["tapInStopsLat","tapInStopsLon","tapOutStopsLat","tapOutStopsLon"]].notna().all(axis=1)
df.loc[mask, "trip_distance_km"] = haversine_km(
    df.loc[mask,"tapInStopsLat"], df.loc[mask,"tapInStopsLon"],
    df.loc[mask,"tapOutStopsLat"], df.loc[mask,"tapOutStopsLon"],
)
df["avg_speed_kmh"] = df["trip_distance_km"] / (df["trip_duration_min"] / 60.0)

import os
os.makedirs("data", exist_ok=True)
df.to_csv(CLEAN, index=False)
print(f"\nSaved {len(df)} rows -> {CLEAN}")
print(f"Dropped PII columns: {dropped}")
print(f"Final columns: {list(df.columns)}")

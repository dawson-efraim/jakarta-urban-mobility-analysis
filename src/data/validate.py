import pandas as pd

def validate_columns(df: pd.DataFrame, required: list) -> bool:
    """Check required columns exist."""
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    return True

def validate_timestamps(df: pd.DataFrame) -> bool:
    """Check tapInTime and tapOutTime are datetime."""
    assert pd.api.types.is_datetime64_any_dtype(df["tapInTime"])
    assert pd.api.types.is_datetime64_any_dtype(df["tapOutTime"])
    return True

def validate_duration(df: pd.DataFrame) -> bool:
    """Trip duration > 0 and < 24h."""
    dur = df["trip_duration_min"]
    assert (dur > 0).all() and (dur < 1440).all()
    return True

def validate_no_negative_distances(df: pd.DataFrame) -> bool:
    if "trip_distance_km" in df.columns:
        assert (df["trip_distance_km"] >= 0).all()
    return True

def validate_no_missing_critical(df: pd.DataFrame) -> bool:
    critical = ["tapInTime", "tapOutTime", "corridorName", "payCardBank"]
    for col in critical:
        assert df[col].notna().all()
    return True

def validate_no_duplicates(df: pd.DataFrame) -> bool:
    # Assuming no duplicate rows based on all columns
    assert not df.duplicated().any()
    return True

def run_all_validations(df: pd.DataFrame) -> None:
    required = ["tapInTime", "tapOutTime", "corridorName", "payCardBank", "trip_duration_min"]
    validate_columns(df, required)
    validate_timestamps(df)
    validate_duration(df)
    validate_no_missing_critical(df)
    validate_no_duplicates(df)
    if "trip_distance_km" in df.columns:
        validate_no_negative_distances(df)
    print("All validations passed.")
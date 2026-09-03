import pytest
import pandas as pd
from src.data.loader import load_data
from src.data.validate import run_all_validations

def test_load():
    df = load_data()
    assert len(df) > 0

def test_validate():
    df = load_data()
    run_all_validations(df)

def test_no_negative_duration():
    df = load_data()
    assert (df["trip_duration_min"] >= 0).all()

def test_no_missing_critical():
    df = load_data()
    critical = ["tapInTime", "tapOutTime", "corridorName", "payCardBank"]
    for col in critical:
        assert df[col].notna().all()
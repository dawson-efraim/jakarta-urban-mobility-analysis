import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit, train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import os

from src.data.loader import load_data

def prepare_hourly_data(df):
    """Aggregate trips per hour and create features."""
    df = df.copy()
    df["hour"] = df["tapInTime"].dt.hour
    df["day_of_week"] = df["tapInTime"].dt.dayofweek
    df["month"] = df["tapInTime"].dt.month
    df["is_weekend"] = df["is_weekend"]

    # Group by hour and date
    hourly = df.groupby([df["tapInTime"].dt.date, "hour"]).size().reset_index(name="trips")
    hourly["date"] = pd.to_datetime(hourly["tapInTime"])
    hourly["day_of_week"] = hourly["date"].dt.dayofweek
    hourly["month"] = hourly["date"].dt.month
    hourly["is_weekend"] = (hourly["day_of_week"] >= 5).astype(int)
    # Lag features: previous hour's trips (same date) - not straightforward, we can lag by hour across dates
    # Simpler: use date features, hour, weekend.
    hourly = hourly.sort_values(["date", "hour"])
    # Add lag of 24 hours (same hour previous day)
    hourly["lag_24h"] = hourly.groupby("hour")["trips"].shift(1)
    # Fill missing lag with median
    hourly["lag_24h"] = hourly["lag_24h"].fillna(hourly["trips"].median())
    return hourly

def train_models(hourly_df):
    features = ["hour", "day_of_week", "month", "is_weekend", "lag_24h"]
    X = hourly_df[features]
    y = hourly_df["trips"]

    # Time-based split: first 80% as train, last 20% as test
    split_idx = int(len(hourly_df) * 0.8)
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "Gradient Boosting": GradientBoostingRegressor(n_estimators=100, random_state=42)
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        results[name] = {"MAE": mae, "RMSE": rmse, "R2": r2, "model": model, "pred": y_pred}
        print(f"{name}: MAE={mae:.2f}, RMSE={rmse:.2f}, R2={r2:.2f}")

    # Plot actual vs predicted for best model (by R2)
    best_name = max(results, key=lambda x: results[x]["R2"])
    best = results[best_name]
    plt.figure(figsize=(10, 5))
    plt.plot(y_test.values, label="Actual", alpha=0.7)
    plt.plot(best["pred"], label=f"{best_name} Predicted", alpha=0.7)
    plt.title(f"Actual vs Predicted Hourly Trips (Best: {best_name})")
    plt.xlabel("Test Sample Index")
    plt.ylabel("Trips")
    plt.legend()
    os.makedirs("outputs", exist_ok=True)
    plt.savefig("outputs/actual_vs_predicted.png")
    plt.close()

    # Feature importance for tree-based models
    if hasattr(best["model"], "feature_importances_"):
        fi = best["model"].feature_importances_
        plt.figure(figsize=(8, 4))
        plt.barh(features, fi)
        plt.xlabel("Importance")
        plt.title(f"Feature Importance - {best_name}")
        plt.tight_layout()
        plt.savefig("outputs/feature_importance.png")
        plt.close()

    return results

if __name__ == "__main__":
    df = load_data()
    hourly = prepare_hourly_data(df)
    results = train_models(hourly)
    print("\nModel Comparison:")
    for name, metrics in results.items():
        print(f"{name}: {metrics}")
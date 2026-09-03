import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.data.loader import load_data
from src.visualization.charts import chart_hourly_trips, chart_top_corridors, chart_daily_trend, chart_trip_duration, chart_period_volumes, chart_ridership_heatmap
import os

st.set_page_config(layout="wide")
st.title("Jakarta Urban Mobility Analysis Dashboard")

@st.cache_data
def load_and_cache():
    df = load_data()
    return df

df = load_and_cache()

# Sidebar filters
st.sidebar.header("Filters")
corridors = df["corridorName"].unique()
selected_corridors = st.sidebar.multiselect("Corridor", corridors, default=corridors[:5])
date_range = st.sidebar.date_input("Date Range", [df["date"].min(), df["date"].max()])
hour_range = st.sidebar.slider("Hour Range", 0, 23, (0, 23))

# Filter data
mask = (df["corridorName"].isin(selected_corridors)) & \
       (df["date"] >= pd.to_datetime(date_range[0])) & \
       (df["date"] <= pd.to_datetime(date_range[1])) & \
       (df["tapInTime"].dt.hour >= hour_range[0]) & \
       (df["tapInTime"].dt.hour <= hour_range[1])
filtered = df[mask]

# KPIs
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Trips", f"{len(filtered):,}")
avg_daily = filtered.groupby(filtered["date"].dt.date).size().mean()
col2.metric("Avg Daily Trips", f"{avg_daily:.0f}")
peak_hour = filtered["tapInTime"].dt.hour.value_counts().idxmax()
col3.metric("Peak Hour", f"{peak_hour}:00")
med_dur = filtered["trip_duration_min"].median()
col4.metric("Median Trip Duration (min)", f"{med_dur:.1f}")

# Charts
st.subheader("Hourly Ridership")
fig, ax = plt.subplots(figsize=(10, 5))
wd = filtered[filtered["is_weekend"] == 0].groupby(filtered["tapInTime"].dt.hour).size()
we = filtered[filtered["is_weekend"] == 1].groupby(filtered["tapInTime"].dt.hour).size()
ax.plot(wd.index, wd.values, marker="o", label="Weekday")
ax.plot(we.index, we.values, marker="s", label="Weekend")
ax.set_title("Trips by Hour")
ax.set_xlabel("Hour")
ax.set_ylabel("Trips")
ax.legend()
st.pyplot(fig)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Top Corridors")
    fig2, ax2 = plt.subplots(figsize=(8, 5))
    top = filtered["corridorName"].value_counts().head(10)
    ax2.barh(top.index[::-1], top.values[::-1], color="#FF6347")
    ax2.set_title("Top 10 Corridors")
    st.pyplot(fig2)

with col2:
    st.subheader("Daily Trend")
    daily = filtered.groupby(filtered["tapInTime"].dt.date).size()
    fig3, ax3 = plt.subplots(figsize=(8, 5))
    ax3.plot(daily.index, daily.values, marker="o", color="#20B2AA")
    ax3.set_title("Daily Trips")
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Trips")
    plt.xticks(rotation=45)
    st.pyplot(fig3)

st.subheader("Trip Duration Distribution")
fig4, ax4 = plt.subplots(figsize=(10, 5))
dur = filtered["trip_duration_min"].dropna()
dur = dur[(dur > 0) & (dur < 180)]
ax4.hist(dur, bins=50, color="#FF6347", edgecolor="black")
ax4.axvline(dur.median(), color="gold", linestyle="--", label=f"Median: {dur.median():.0f} min")
ax4.set_title("Trip Duration")
ax4.set_xlabel("Minutes")
ax4.legend()
st.pyplot(fig4)

st.subheader("Ridership Heatmap")
fig5, ax5 = plt.subplots(figsize=(12, 5))
filtered["hour"] = filtered["tapInTime"].dt.hour
filtered["weekday_num"] = filtered["tapInTime"].dt.weekday
ct = pd.crosstab(filtered["weekday_num"], filtered["hour"])
day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
im = ax5.imshow(ct.values, aspect="auto", cmap="magma")
ax5.set_xticks(range(24))
ax5.set_xticklabels(range(24))
ax5.set_yticks(range(7))
ax5.set_yticklabels(day_names)
ax5.set_title("Hour × Weekday")
plt.colorbar(im, ax=ax5)
st.pyplot(fig5)

# ML Section
st.header("Machine Learning: Hourly Ridership Prediction")
if st.button("Run ML Training"):
    with st.spinner("Training models..."):
        from src.modeling.train import prepare_hourly_data, train_models
        hourly = prepare_hourly_data(df)
        results = train_models(hourly)
        st.success("Training complete!")
        st.subheader("Model Performance")
        metrics_df = pd.DataFrame(results).T
        st.dataframe(metrics_df)
        st.image("outputs/actual_vs_predicted.png", caption="Actual vs Predicted")
        if os.path.exists("outputs/feature_importance.png"):
            st.image("outputs/feature_importance.png", caption="Feature Importance")
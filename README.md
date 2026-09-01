<h1 align="center">🚌 Jakarta Public Transit Data Analysis</h1>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas"/>
  <img src="https://img.shields.io/badge/Matplotlib-Visualization-F1502F?style=for-the-badge&logo=matplotlib&logoColor=white" alt="Matplotlib"/>
  <img src="https://img.shields.io/badge/License-CC0-blue?style=for-the-badge" alt="License"/>
</p>

<p align="center">
  End-to-end analysis of <b>36,000+ Transjakarta trips</b> — from raw public-transit transactions to ridership insights and interactive visualizations.
</p>

---

## 📊 Dashboard

<p align="center">
  <img src="output/dashboard.png" alt="Jakarta Transit Dashboard" width="900"/>
</p>

The dashboard above visualizes ridership patterns from **real Transjakarta (Jakarta's BRT) transaction data** (April 2023), with a title header, **4 KPI summary cards**, and 4 analysis panels:

| Panel | Insight |
|-------|---------|
| **KPI Cards** | Average daily trips (1,218), peak hour (6:00), median trip duration (71 min), busiest corridor (Cibubur–Balai Kota) |
| **Hourly Trips** | Weekday ridership spikes at 6–7 AM and 5–6 PM commute peaks; weekends stay flat and low |
| **Top Corridors** | Cibubur–Balai Kota and Ciputat–CSW are the busiest routes |
| **Daily Trend** | Weekdays carry ~90% of trips; weekends drop sharply |
| **Ridership Heatmap** | Commuting hours dominate Mon–Fri; density nearly vanishes on weekends |

---

## 🗂 Project Structure

```
jakarta-urban-mobility-analysis/
├── data/
│   └── transjakarta_trips.csv    # Cleaned, PII-stripped trip data (36,556 rows)
├── data_loader.py                # Load, clean & feature engineering
├── charts.py                     # 7 visualization functions
├── build_dashboard.py            # Portfolio dashboard builder (title + KPI cards + 2×2)
├── main.py                       # Pipeline orchestrator + summary stats
├── prepare_data.py               # (One-off) PII strip + derive features from raw export
├── output/
│   └── dashboard.png             # README showcase dashboard (2×2 grid)
├── charts/                       # Generated PNG charts
│   ├── hourly_trips.png
│   ├── top_corridors.png
│   ├── payment_methods.png
│   ├── daily_trend.png
│   ├── trip_duration.png
│   ├── period_volumes.png
│   └── ridership_heatmap.png
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start

```bash
# Clone
git clone https://github.com/dawson-efraim/jakarta-urban-mobility-analysis.git
cd jakarta-urban-mobility-analysis

# Install
pip install -r requirements.txt

# Run analysis
python main.py
```

Charts are saved to `charts/` as PNGs. Summary statistics print to console.

---

## 🔧 Features

- **Real Kaggle dataset** — 36,556 actual Transjakarta trip transactions (BRT transit)
- **Privacy-first pipeline** — Passenger IDs, names, birth dates, and sex stripped before committing (`prepare_data.py`)
- **7 visualization types** — Line charts, bar charts, pie charts, heatmaps, histograms
- **Dark theme styling** — Coral/teal/gold palette on dark background
- **OOP-ready architecture** — Clean separation: loader → charts → orchestrator

---

## 📈 Questions Answered

| # | Question | Chart |
|---|----------|-------|
| 1 | When do people ride Transjakarta during weekdays vs weekends? | `hourly_trips.png` |
| 2 | Which corridors carry the most passengers? | `top_corridors.png` |
| 3 | How do passengers pay (which card banks)? | `payment_methods.png` |
| 4 | How does ridership fluctuate day to day? | `daily_trend.png` |
| 5 | How long is a typical Transjakarta trip? | `trip_duration.png` |
| 6 | How do peak vs off-peak periods compare? | `period_volumes.png` |
| 7 | What's the ridership density across days and hours? | `ridership_heatmap.png` |

---

## 🛠 Tech Stack

- **Python 3.10+**
- **Pandas** — Data manipulation, groupby, datetime handling
- **Matplotlib** — Visualization with dark theme, heatmaps
- **NumPy** — Haversine distance calculation for trip segments

---

## 📂 Data Source

| Source | Description |
|--------|-------------|
| [Transjakarta Transportation Transaction — Kaggle](https://www.kaggle.com/datasets/dikisahkan/transjakarta-transportation-transaction) | Real April 2023 Transjakarta BRT trip transactions (CC0-1.0 license) |

**Privacy note:** The raw Kaggle export contains passenger identity fields (`transID`, `payCardID`, `payCardName`, `payCardBirthDate`, `payCardSex`). These were **removed** in `prepare_data.py` — the committed `data/transjakarta_trips.csv` contains only mobility features (routes, stops, timestamps, trip durations, distances, payment method). No personal data is published.

---

<p align="center">
  <i>Built as part of a data science learning journey.</i><br>
  <sub>Raw transit transactions → Clean, private analysis → Polished insights</sub>
</p>

"""Fitness tracker: load weight/calorie data, compute TDEE, plot trends."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = Path("Data/raw/weight_calories_raw.csv")
RUNS_PATH = Path("Data/raw/runs_raw.csv")

COLUMN_RENAME = {
    "Date": "date",
    "Total Calories": "total_calories",
    "Carbs (g)": "carbs",
    "Protein (g)": "protein",
    "Fat (g)": "fat",
    "Weight (KG)": "weight_kg",
}

def load_weights(path):
    df = pd.read_csv(path)
    df = df.rename(columns=COLUMN_RENAME)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").asfreq("D")
    return df

def load_runs(path):
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").asfreq("D")
    return df

def weekly_weights(weights):
    """Average weight per calendar week."""
    weekly = weights["weight_kg"].resample("W").mean().to_frame()
    weekly.columns = ["avg_weight_kg"]
    return weekly

def weekly_runs(runs):
    """Total distance per calendar week."""
    weekly = runs["distance_km"].resample("W").sum().to_frame()
    weekly.columns = ["total_km"]
    return weekly

def merge_weekly(weekly_w, weekly_r):
    """Join weekly weights and weekly runs on their week index."""
    combined = pd.merge(
        weekly_w,
        weekly_r,
        left_index=True,
        right_index=True,
        how="outer",
    )
    return combined

def correlate(combined):
    """Compute correlation between weekly avg weight and total km."""
    valid = combined.dropna(subset=["avg_weight_kg", "total_km"])

    if len(valid) < 3:
        print("Not enough complete weeks to compute correlation.")
        return None

    corr = valid["avg_weight_kg"].corr(valid["total_km"])
    print(f"Weeks analyzed: {len(valid)}")
    print(f"Correlation (weight vs. km): {corr:+.2f}")
    return corr

def add_rolling_weight(df, window="7D", min_periods=4):
    df = df.copy()
    df["weight_7d"] = df["weight_kg"].rolling(window, min_periods=min_periods).mean()
    return df


def completeness(df, column="weight_kg"):
    full_range = pd.date_range(df.index.min(), df.index.max(), freq="D")
    present = df[column].reindex(full_range).notna().sum()
    return present / len(full_range)


def estimate_tdee(df, window_days=14, min_weighins=8):
    window = df.tail(window_days)
    weighins = window["weight_kg"].notna().sum()
    if weighins < min_weighins:
        return None, weighins
    first = window["weight_kg"].dropna().iloc[0]
    last = window["weight_kg"].dropna().iloc[-1]
    delta = last - first
    avg_cal = window["total_calories"].mean()
    tdee = avg_cal + (delta * 7700 / window_days)
    return tdee, weighins


def plot_weight(df, out_path="weight_trend.png"):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df.index, df["weight_kg"], "o", alpha=0.4, label="Raw")
    ax.plot(df.index, df["weight_7d"], "-", linewidth=2, label="7-day rolling avg")
    ax.set_ylabel("Weight (kg)")
    ax.set_title("Weight trend")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(out_path, dpi=120)
    plt.close(fig)


def main():
    # --- Weight/TDEE analysis (existing) ---
    weights = load_weights(DATA_PATH)
    weights = add_rolling_weight(weights)

    print(f"Date range: {weights.index.min().date()} -> {weights.index.max().date()}")
    print(f"Days: {len(weights)}")
    print(f"Weigh-in completeness: {completeness(weights):.1%}")
    print()

    tdee, weighins = estimate_tdee(weights, window_days=14)
    print("--- TDEE (last 14 days) ---")
    print(f"Weigh-ins in window: {weighins}")
    if tdee is None:
        print("Insufficient data for a TDEE estimate.")
    else:
        print(f"Estimated TDEE: {tdee:,.0f} cal/day (LOW confidence)")
    print()

    # --- NEW: Running correlation analysis ---
    runs = load_runs(RUNS_PATH)

    weekly_w = weekly_weights(weights)
    weekly_r = weekly_runs(runs)
    combined = merge_weekly(weekly_w, weekly_r)

    print("--- Weekly summary ---")
    print(combined)
    print()

    print("--- Correlation (weight vs. running) ---")
    correlate(combined)

    # --- Chart ---
    plot_weight(weights)
    print("\nSaved weight_trend.png")


if __name__ == "__main__":
    main()
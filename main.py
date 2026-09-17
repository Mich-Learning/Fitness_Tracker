"""Fitness tracker: load weight/calorie data, compute TDEE, plot trends."""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


DATA_PATH = Path("Data/raw/weight_calories_raw.csv")

COLUMN_RENAME = {
    "Date": "date",
    "Total Calories": "total_calories",
    "Carbs (g)": "carbs",
    "Protein (g)": "protein",
    "Fat (g)": "fat",
    "Weight (KG)": "weight_kg",
}

def load_data(path):
    df = pd.read_csv(path)
    df = df.rename(columns=COLUMN_RENAME)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").asfreq("D")
    return df

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
    df = load_data(DATA_PATH)
    df = add_rolling_weight(df)

    print(f"Date range: {df.index.min().date()} -> {df.index.max().date()}")
    print(f"Days: {len(df)}")
    print(f"Weigh-in completeness: {completeness(df):.1%}")
    print()

    tdee, weighins = estimate_tdee(df, window_days=14)
    print("--- TDEE (last 14 days) ---")
    print(f"Weigh-ins in window: {weighins}")
    if tdee is None:
        print("Insufficient data for a TDEE estimate.")
    else:
        print(f"Estimated TDEE: {tdee:,.0f} cal/day (LOW confidence)")

    plot_weight(df)
    print("\nSaved weight_trend.png")


if __name__ == "__main__":
    main()
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]
PERFORMANCE_FILE = BASE_DIR / "data" / "processed" / "07_scheme_performance.csv"

RISK_MAP = {"low":"Low", "moderate":"Moderate", "high":"High"}

def load_funds():
    df = pd.read_csv(PERFORMANCE_FILE)
    df["sharpe_ratio"] = pd.to_numeric(df["sharpe_ratio"], errors="coerce")
    return df.dropna(subset=["sharpe_ratio"])

def recommend(risk_appetite, top_n=3):
    key = str(risk_appetite).strip().lower()
    if key not in RISK_MAP:
        raise ValueError("Risk appetite must be Low, Moderate, or High.")
    return (load_funds()
            .query("risk_grade == @RISK_MAP[key]")
            .sort_values("sharpe_ratio", ascending=False)
            .head(top_n)[["scheme_name","risk_grade","sharpe_ratio"]]
            .reset_index(drop=True))

if __name__ == "__main__":
    appetite = input("Enter risk appetite (Low/Moderate/High): ")
    print("\nTop 3 recommendations:\n")
    print(recommend(appetite).to_string(index=False))

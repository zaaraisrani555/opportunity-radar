"""
main.py — Entry point for the Opportunity Radar pipeline.

Run from the project root:
    python3 src/main.py
"""
import os
import sys

# Ensure imports work when run as `python3 src/main.py` from the project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ingest import load_watchlist, load_tracker, load_sources
from src.signals import attach_signals
from src.score import rank_opportunities
from src.drafts import get_why_now, get_who_to_contact, get_angle, generate_email
from src.report import render_report

OUTPUT_PATH = "outputs/weekly_memo.md"
TOP_N = 5  # number of opportunities to include in the memo


def main():
    print("=" * 50)
    print("  Opportunity Radar — starting pipeline")
    print("=" * 50)

    # 1. Load data
    watchlist = load_watchlist("data/watchlist.csv")
    tracker   = load_tracker("data/outreach_tracker.csv")
    load_sources("data/sources.yaml")   # loaded; available for future filters

    print(f"\n[ingest]  {len(watchlist)} companies loaded from watchlist")
    print(f"[ingest]  {len(tracker)} entries loaded from tracker")

    # 2. Attach signals (merge tracker status + add signal columns)
    df = attach_signals(watchlist, tracker)

    # 3. Score and rank
    top = rank_opportunities(df, top_n=TOP_N)

    print(f"\n[score]   Top {len(top)} opportunities:")
    for _, row in top.iterrows():
        print(
            f"          {row['company']:<25} "
            f"score={int(row['score']):>2}  "
            f"sector={row['sector']:<15}  "
            f"status={row['status']}"
        )

    # 4. Render report
    report = render_report(
        top,
        get_why_now,
        get_who_to_contact,
        get_angle,
        generate_email,
    )

    # 5. Write output
    os.makedirs("outputs", exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        f.write(report)

    print(f"\n[report]  Written → {OUTPUT_PATH}")
    print("\nDone.")


if __name__ == "__main__":
    main()

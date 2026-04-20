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
from src.scraper import scrape_all
from src.signals import attach_signals, attach_scrape_signals
from src.score import rank_opportunities
from src.drafts import get_why_now, get_who_to_contact, get_angle, generate_email
from src.report import render_report, render_html_report

MD_PATH   = "outputs/weekly_memo.md"
HTML_PATH = "outputs/weekly_memo.html"
TOP_N = 5  # number of opportunities to include in the memo


def main():
    print("=" * 50)
    print("  Opportunity Radar — starting pipeline")
    print("=" * 50)

    # 1. Load data
    watchlist = load_watchlist("data/watchlist.csv")
    tracker   = load_tracker("data/outreach_tracker.csv")
    load_sources("data/sources.yaml")

    print(f"\n[ingest]  {len(watchlist)} companies loaded from watchlist")
    print(f"[ingest]  {len(tracker)} entries loaded from tracker")

    # 2. Phase-1 scraping — detect hiring and opportunity signals
    print(f"\n[scrape]  Phase 1 — checking {len(watchlist)} companies...")
    scrape_df = scrape_all(watchlist)

    # Summarise scraping results
    n_reach   = int(scrape_df["website_reachable"].sum())
    n_hiring  = int(scrape_df["hiring_signal_detected"].sum())
    n_opp     = int(scrape_df["opportunity_signal_detected"].sum())
    n_intern  = int(scrape_df["internship_signal_detected"].sum())
    print(
        f"\n[scrape]  Done — {n_reach} reachable  |  "
        f"{n_hiring} hiring  |  {n_intern} internship  |  {n_opp} opportunity signals"
    )

    # 3. Attach base signals + merge scrape signals
    df = attach_signals(watchlist, tracker)
    df = attach_scrape_signals(df, scrape_df)

    # 4. Score and rank (now includes scrape signal bonuses)
    top = rank_opportunities(df, top_n=TOP_N)

    print(f"\n[score]   Top {len(top)} opportunities:")
    for _, row in top.iterrows():
        print(
            f"          {row['company']:<25} "
            f"score={int(row['score']):>2}  "
            f"sector={row['sector']:<15}  "
            f"status={row['status']}"
        )

    os.makedirs("outputs", exist_ok=True)

    # 5a. Markdown report
    md = render_report(top, get_why_now, get_who_to_contact, get_angle, generate_email)
    with open(MD_PATH, "w") as f:
        f.write(md)
    print(f"\n[report]  Written → {MD_PATH}")

    # 5b. HTML report
    html = render_html_report(
        top,
        get_why_now,
        get_who_to_contact,
        get_angle,
        generate_email,
        total_watchlist=len(watchlist),
        total_tracker=len(tracker),
        tracker_df=tracker,
    )
    with open(HTML_PATH, "w") as f:
        f.write(html)
    print(f"[report]  Written → {HTML_PATH}")

    print("\nDone.")


if __name__ == "__main__":
    main()

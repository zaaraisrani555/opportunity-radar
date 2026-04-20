"""
signals.py — Merge watchlist + tracker and attach signal columns to each row.
"""

# All columns produced by the scraper (used to fill missing values with False)
SCRAPE_SIGNAL_COLS = [
    "website_reachable",
    "careers_page_found",
    "hiring_signal_detected",
    "internship_signal_detected",
    "opportunity_signal_detected",
    "high_growth_signal_detected",
    "early_stage_signal_detected",
    "yc_source_checked",
]


def attach_signals(watchlist_df, tracker_df):
    """
    Merge outreach status from tracker into watchlist,
    then add structured signal columns used downstream for scoring.
    """
    # Bring in the latest status for each company from the tracker
    tracker_slim = (
        tracker_df[["company", "status"]]
        .drop_duplicates(subset="company")
    )
    df = watchlist_df.merge(tracker_slim, on="company", how="left")

    # Default status for companies not yet in the tracker
    df["status"] = df["status"].fillna("not_started")

    # Signal columns
    df["on_watchlist"] = True           # always true — every row came from watchlist
    df["target_sector"] = df["sector"]  # alias for readability in report
    df["high_priority"] = df["priority"] == "high"
    df["outreach_stage"] = df["status"] # readable alias

    return df


def attach_scrape_signals(df, scrape_df):
    """
    Merge Phase-1 scrape results into the main DataFrame.

    scrape_df has one row per company with boolean signal columns.
    Companies that weren't scraped (or failed) get False for all signals.
    """
    merge_cols = ["company"] + SCRAPE_SIGNAL_COLS
    df = df.merge(scrape_df[merge_cols], on="company", how="left")

    # Fill any missing rows (scrape errors, YC source entries, etc.) with False
    for col in SCRAPE_SIGNAL_COLS:
        df[col] = df[col].fillna(False).astype(bool)

    return df

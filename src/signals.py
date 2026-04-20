"""
signals.py — Merge watchlist + tracker and attach signal columns to each row.
"""


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

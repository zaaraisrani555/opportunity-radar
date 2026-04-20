"""
score.py — Assign a numeric priority score to each opportunity.

Scoring rules:
  +5  priority = high
  +4  sector is cybersecurity or healthtech
  +3  status = to_research or to_email  (actionable, not yet started)
  +2  category = startup  (more flexible / early hiring)
  +1  category = vc
  -3  already contacted  (waiting, call_booked, emailed)
"""

CONTACTED_STATUSES = {"waiting", "call_booked", "emailed"}
PRIORITY_SECTORS   = {"cybersecurity", "healthtech"}
ACTIONABLE_STATUSES = {"to_research", "to_email"}


def score_opportunity(row):
    """Return an integer score for a single opportunity row (pd.Series)."""
    score = 0

    if str(row.get("priority", "")).lower() == "high":
        score += 5

    if str(row.get("sector", "")).lower() in PRIORITY_SECTORS:
        score += 4

    if str(row.get("status", "")).lower() in ACTIONABLE_STATUSES:
        score += 3

    category = str(row.get("category", "")).lower()
    if category == "startup":
        score += 2
    elif category == "vc":
        score += 1

    # Penalise if we're already mid-conversation (avoid double-outreach)
    if str(row.get("status", "")).lower() in CONTACTED_STATUSES:
        score -= 3

    return score


def rank_opportunities(df, top_n=5):
    """Score every row, sort descending, return the top N."""
    df = df.copy()
    df["score"] = df.apply(score_opportunity, axis=1)
    df = df.sort_values("score", ascending=False).reset_index(drop=True)
    return df.head(top_n)

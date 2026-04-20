"""
report.py — Render the top opportunities into a clean Markdown memo.
"""
from datetime import date


def render_report(top_df, get_why_now_fn, get_who_fn, get_angle_fn, get_email_fn):
    """
    Build the weekly_memo.md string from the top-scored opportunities.

    Parameters
    ----------
    top_df          : scored + filtered DataFrame (already top-N rows)
    get_why_now_fn  : callable(row) -> list[str]
    get_who_fn      : callable(row) -> list[str]
    get_angle_fn    : callable(row) -> str
    get_email_fn    : callable(row) -> str
    """
    today = date.today().strftime("%B %d, %Y")
    lines = [
        "# Opportunity Radar",
        f"**Week of {today}**",
        "",
        "---",
        "",
        "## Top Opportunities",
        "",
    ]

    for rank, (_, row) in enumerate(top_df.iterrows(), start=1):
        lines += [
            f"### {rank}. {row['company']}",
            "",
            f"- **Sector:** {row.get('sector', 'N/A').title()}",
            f"- **Category:** {row.get('category', 'N/A').title()}",
            f"- **Priority Score:** {int(row['score'])}",
            f"- **Outreach Stage:** `{row.get('status', 'N/A')}`",
            "",
        ]

        lines.append("**Why now:**")
        for reason in get_why_now_fn(row):
            lines.append(f"- {reason}")
        lines.append("")

        lines.append("**Who to contact:**")
        for contact in get_who_fn(row):
            lines.append(f"- {contact}")
        lines.append("")

        lines.append("**Suggested angle:**")
        lines.append(get_angle_fn(row))
        lines.append("")

        lines.append("**Draft email:**")
        lines.append("")
        lines.append("```")
        lines.append(get_email_fn(row))
        lines.append("```")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)

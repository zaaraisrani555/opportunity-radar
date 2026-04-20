"""
report.py — Render the top opportunities into Markdown and HTML reports.
"""
import math
from datetime import date
from html import escape


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# HTML report
# ---------------------------------------------------------------------------

def _safe(val):
    """Return display string; em-dash for None / empty / NaN."""
    if val is None:
        return "&#x2014;"
    try:
        if math.isnan(val):
            return "&#x2014;"
    except (TypeError, ValueError):
        pass
    s = str(val).strip()
    return "&#x2014;" if s in ("", "nan", "NaN") else escape(s)


# ── Badge colour maps ──────────────────────────────────────────────────────

_SECTOR_COLORS = {
    "cybersecurity": ("#dce8ff", "#1a3a6c"),
    "healthtech":    ("#d1fae5", "#065f46"),
    "generalist":    ("#ede9fe", "#5b21b6"),
    "enterprise":    ("#fef3c7", "#92400e"),
    "growth":        ("#fce7f3", "#9d174d"),
}
_DEFAULT_BADGE = ("#e2e8f0", "#334155")

_STATUS_COLORS = {
    "to_research":  ("#fef9c3", "#854d0e"),
    "to_email":     ("#dcfce7", "#166534"),
    "emailed":      ("#dbeafe", "#1e40af"),
    "waiting":      ("#dbeafe", "#1e40af"),
    "followup_due": ("#fce7f3", "#9d174d"),
    "responded":    ("#d1fae5", "#065f46"),
    "call_booked":  ("#ede9fe", "#5b21b6"),
    "not_started":  ("#e2e8f0", "#334155"),
}


def _badge(text, bg, fg):
    """Return an inline HTML pill badge."""
    style = (
        f"display:inline-block;padding:3px 11px;border-radius:20px;"
        f"background:{bg};color:{fg};font-size:0.72rem;font-weight:600;"
        f"letter-spacing:0.04em;white-space:nowrap;"
    )
    return f'<span style="{style}">{escape(str(text))}</span>'


def _sector_badge(sector):
    bg, fg = _SECTOR_COLORS.get(str(sector).lower(), _DEFAULT_BADGE)
    return _badge(sector.title(), bg, fg)


def _score_badge(score):
    if score >= 12:
        bg, fg = "#d1fae5", "#065f46"
    elif score >= 8:
        bg, fg = "#fef3c7", "#92400e"
    else:
        bg, fg = "#e2e8f0", "#334155"
    return _badge(f"Score {score}", bg, fg)


def _status_badge(status):
    bg, fg = _STATUS_COLORS.get(str(status).lower(), _DEFAULT_BADGE)
    return _badge(status.replace("_", " ").title(), bg, fg)


def _summary_themes(top_df):
    """One-sentence sector summary derived from the top opportunities."""
    sectors = top_df["sector"].str.lower().value_counts()
    top_sectors = [s.title() for s in sectors.index[:2]]
    if len(top_sectors) == 2:
        return (
            f"This week&#8217;s strongest signals are in "
            f"<strong>{top_sectors[0]}</strong> and "
            f"<strong>{top_sectors[1]}</strong>, with high-priority "
            "startups and VC firms leading the list."
        )
    elif top_sectors:
        return (
            f"This week&#8217;s strongest signals are in "
            f"<strong>{top_sectors[0]}</strong>."
        )
    return "Review the cards below for this week&#8217;s top opportunities."


# ── Opportunity card ───────────────────────────────────────────────────────

# (status_value, button label) pairs for the action strip
_ACTION_BUTTONS = [
    ("to_research",  "To Research"),
    ("to_email",     "To Email"),
    ("emailed",      "Emailed"),
    ("followup_due", "Follow-Up Due"),
    ("responded",    "Responded"),
    ("call_booked",  "Call Booked"),
]


def _opportunity_card(rank, row, get_why_now_fn, get_who_fn, get_angle_fn, get_email_fn):
    """Return the HTML block for one opportunity card."""
    company    = escape(str(row["company"]))
    sector     = str(row.get("sector",   "N/A")).lower()
    category   = str(row.get("category", "N/A"))
    score      = int(row["score"])
    status     = str(row.get("status",   "N/A"))

    why_items  = "".join(f"<li>{escape(r)}</li>" for r in get_why_now_fn(row))
    who_items  = "".join(f"<li>{escape(c)}</li>" for c in get_who_fn(row))
    angle_text = escape(get_angle_fn(row))
    email_text = escape(get_email_fn(row))

    action_btns = "\n          ".join(
        f'<button class="action-btn{" active" if s == status else ""}" '
        f'data-status="{s}" onclick="updateStatus(this)">{label}</button>'
        for s, label in _ACTION_BUTTONS
    )

    return f"""
    <div class="card">
      <div class="card-header">
        <div class="card-rank">#{rank}</div>
        <div class="card-title-group">
          <h2 class="card-company">{company}</h2>
          <div class="card-badges">
            {_sector_badge(sector)}
            {_badge(category.title(), *_DEFAULT_BADGE)}
            {_score_badge(score)}
            <span class="status-badge-wrap">{_status_badge(status)}</span>
          </div>
        </div>
      </div>

      <div class="card-section">
        <h3>Why now</h3>
        <ul>{why_items}</ul>
      </div>

      <div class="card-section">
        <h3>Who to contact</h3>
        <ul>{who_items}</ul>
      </div>

      <div class="card-section">
        <h3>Suggested angle</h3>
        <p>{angle_text}</p>
      </div>

      <div class="card-section">
        <h3>Draft email</h3>
        <pre class="email-draft">{email_text}</pre>
      </div>

      <div class="card-actions">
        <span class="actions-label">Update status</span>
        {action_btns}
      </div>
    </div>"""


# ── Tracker table ──────────────────────────────────────────────────────────

def _tracker_table(tracker_df):
    """Render the outreach tracker as a styled HTML table."""
    rows = []
    for _, row in tracker_df.iterrows():
        company  = _safe(row.get("company"))
        person   = _safe(row.get("person_name"))
        role     = _safe(row.get("role"))

        # Combine person + role; show em-dash if both are empty
        if person == "&#x2014;" and role == "&#x2014;":
            contact = "&#x2014;"
        elif role == "&#x2014;":
            contact = person
        else:
            contact = f"{person} / {role}"

        status_raw  = str(row.get("status", "")).strip().lower()
        status_html = _status_badge(status_raw) if status_raw and status_raw != "nan" else "&#x2014;"

        last_date = _safe(row.get("last_contact_date"))
        followup  = _safe(row.get("followup_due_date"))
        response  = _safe(row.get("response"))
        notes     = _safe(row.get("notes"))
        priority  = _safe(row.get("priority_score"))

        rows.append(f"""        <tr>
          <td class="td-company">{company}</td>
          <td>{contact}</td>
          <td>{status_html}</td>
          <td>{last_date}</td>
          <td>{followup}</td>
          <td>{response}</td>
          <td class="td-notes">{notes}</td>
          <td class="td-center">{priority}</td>
        </tr>""")

    rows_html = "\n".join(rows)
    return f"""<div class="table-wrap">
      <table class="tracker-table">
        <thead>
          <tr>
            <th>Company</th>
            <th>Contact / Role</th>
            <th>Status</th>
            <th>Last Contact</th>
            <th>Follow-Up Due</th>
            <th>Response</th>
            <th>Notes</th>
            <th>Score</th>
          </tr>
        </thead>
        <tbody>
{rows_html}
        </tbody>
      </table>
    </div>"""


# ── Styles ─────────────────────────────────────────────────────────────────

_CSS = """
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --navy:       #0f2544;
    --navy-mid:   #1a3a6c;
    --navy-acc:   #2563eb;
    --bg:         #f0f4f9;
    --surface:    #ffffff;
    --border:     #dde6f0;
    --text:       #1e293b;
    --muted:      #64748b;
    --light:      #94a3b8;
  }

  body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI',
                 system-ui, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.65;
    padding: 0 0 80px;
  }

  /* ── Header ── */
  .site-header {
    background: var(--navy);
    padding: 52px 24px 46px;
    text-align: center;
  }
  .header-inner { max-width: 780px; margin: 0 auto; }
  .header-eyebrow {
    font-size: 0.67rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #7ea8d8;
    margin-bottom: 14px;
  }
  .site-header h1 {
    font-size: 2rem;
    font-weight: 700;
    color: #f1f5fb;
    letter-spacing: -0.025em;
    line-height: 1.2;
  }
  .date-line {
    margin-top: 10px;
    font-size: 0.78rem;
    color: #7ea8d8;
    text-transform: uppercase;
    letter-spacing: 0.11em;
  }
  .subtitle {
    margin-top: 14px;
    font-size: 0.9rem;
    color: #a8c4dc;
    max-width: 460px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.6;
  }

  /* ── Container ── */
  .container { max-width: 780px; margin: 0 auto; padding: 36px 24px 0; }

  /* ── Summary box ── */
  .summary {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 26px 30px;
    margin-bottom: 32px;
    box-shadow: 0 1px 6px rgba(15,37,68,.06);
  }
  .summary-eyebrow {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 18px;
  }
  .summary-stats {
    display: flex;
    gap: 36px;
    flex-wrap: wrap;
    margin-bottom: 18px;
  }
  .stat { display: flex; flex-direction: column; }
  .stat-value {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--navy);
    line-height: 1;
    letter-spacing: -0.02em;
  }
  .stat-label { font-size: 0.74rem; color: var(--muted); margin-top: 5px; }
  .summary-theme {
    font-size: 0.875rem;
    color: var(--muted);
    border-top: 1px solid var(--border);
    padding-top: 14px;
    line-height: 1.55;
  }
  .summary-theme strong { color: var(--navy-mid); font-weight: 600; }

  /* ── Tab nav ── */
  .tab-nav {
    display: flex;
    gap: 4px;
    margin-bottom: 28px;
    border-bottom: 2px solid var(--border);
  }
  .tab-btn {
    font-family: inherit;
    background: none;
    border: none;
    cursor: pointer;
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--muted);
    padding: 10px 20px;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    border-radius: 4px 4px 0 0;
    transition: color 0.15s, border-color 0.15s;
    letter-spacing: 0.01em;
  }
  .tab-btn:hover { color: var(--navy-mid); }
  .tab-btn.active {
    color: var(--navy);
    border-bottom-color: var(--navy);
  }

  /* ── Tab panels ── */
  .tab-panel { display: none; }
  .tab-panel.active { display: block; }

  /* ── Opportunity card ── */
  .card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 28px 30px;
    margin-bottom: 20px;
    box-shadow: 0 2px 10px rgba(15,37,68,.05);
  }
  .card-header {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 22px;
  }
  .card-rank {
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--light);
    padding-top: 5px;
    min-width: 22px;
  }
  .card-title-group { flex: 1; min-width: 0; }
  .card-company {
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--navy);
    margin-bottom: 9px;
    letter-spacing: -0.01em;
  }
  .card-badges { display: flex; flex-wrap: wrap; gap: 6px; }

  /* ── Card sections ── */
  .card-section { margin-bottom: 18px; }
  .card-section:last-child { margin-bottom: 0; }
  .card-section h3 {
    font-size: 0.64rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    color: var(--muted);
    margin-bottom: 8px;
  }
  .card-section ul { padding-left: 16px; }
  .card-section li {
    font-size: 0.875rem;
    color: var(--text);
    margin-bottom: 4px;
  }
  .card-section p { font-size: 0.875rem; color: var(--text); }

  /* ── Email draft ── */
  .email-draft {
    background: #f8fafc;
    border: 1px solid var(--border);
    border-left: 3px solid var(--navy-mid);
    border-radius: 8px;
    padding: 16px 18px;
    font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
    font-size: 0.78rem;
    color: #334155;
    white-space: pre-wrap;
    word-break: break-word;
    line-height: 1.65;
  }

  /* ── Action buttons ── */
  .card-actions {
    margin-top: 22px;
    padding-top: 18px;
    border-top: 1px solid var(--border);
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }
  .actions-label {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--light);
    margin-right: 4px;
  }
  .action-btn {
    font-family: inherit;
    font-size: 0.75rem;
    font-weight: 500;
    padding: 5px 13px;
    border-radius: 20px;
    border: 1px solid var(--border);
    background: var(--bg);
    color: var(--muted);
    cursor: pointer;
    transition: all 0.15s;
    letter-spacing: 0.01em;
  }
  .action-btn:hover {
    border-color: var(--navy-mid);
    color: var(--navy-mid);
    background: #eef3ff;
  }
  .action-btn.active {
    background: var(--navy);
    border-color: var(--navy);
    color: #fff;
    font-weight: 600;
  }

  /* ── Tracker table ── */
  .table-wrap {
    overflow-x: auto;
    border-radius: 14px;
    border: 1px solid var(--border);
    box-shadow: 0 2px 10px rgba(15,37,68,.05);
  }
  .tracker-table {
    width: 100%;
    border-collapse: collapse;
    background: var(--surface);
    font-size: 0.84rem;
  }
  .tracker-table thead tr { background: var(--navy); }
  .tracker-table thead th {
    padding: 13px 16px;
    text-align: left;
    font-size: 0.66rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.11em;
    color: #7ea8d8;
    white-space: nowrap;
    border: none;
  }
  .tracker-table tbody tr {
    border-bottom: 1px solid var(--border);
    transition: background 0.1s;
  }
  .tracker-table tbody tr:last-child { border-bottom: none; }
  .tracker-table tbody tr:hover { background: #f8fafc; }
  .tracker-table td {
    padding: 13px 16px;
    vertical-align: middle;
    color: var(--text);
  }
  .td-company {
    font-weight: 600;
    color: var(--navy);
    white-space: nowrap;
  }
  .td-notes {
    max-width: 200px;
    font-size: 0.8rem;
    color: var(--muted);
  }
  .td-center { text-align: center; }

  /* ── Footer ── */
  .site-footer {
    text-align: center;
    margin-top: 56px;
    font-size: 0.74rem;
    color: var(--light);
    padding: 0 24px;
  }
"""


# ── JavaScript ─────────────────────────────────────────────────────────────

_JS = """
  // Tab switching
  function switchTab(tabName) {
    document.querySelectorAll('.tab-panel').forEach(function(p) {
      p.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(function(b) {
      b.classList.remove('active');
    });
    document.getElementById('tab-' + tabName).classList.add('active');
    document.querySelector('[data-tab="' + tabName + '"]').classList.add('active');
  }

  // Status badge colours (mirrors Python _STATUS_COLORS)
  var STATUS_COLORS = {
    'to_research':  ['#fef9c3', '#854d0e'],
    'to_email':     ['#dcfce7', '#166534'],
    'emailed':      ['#dbeafe', '#1e40af'],
    'waiting':      ['#dbeafe', '#1e40af'],
    'followup_due': ['#fce7f3', '#9d174d'],
    'responded':    ['#d1fae5', '#065f46'],
    'call_booked':  ['#ede9fe', '#5b21b6'],
    'not_started':  ['#e2e8f0', '#334155']
  };

  // Click handler for action buttons
  function updateStatus(btn) {
    var card       = btn.closest('.card');
    var statusWrap = card.querySelector('.status-badge-wrap');
    var newStatus  = btn.dataset.status;

    // Highlight the clicked button, clear others
    card.querySelectorAll('.action-btn').forEach(function(b) {
      b.classList.remove('active');
    });
    btn.classList.add('active');

    // Re-render the status badge with matching colour
    var colors = STATUS_COLORS[newStatus] || ['#e2e8f0', '#334155'];
    var bg = colors[0], fg = colors[1];
    var label = newStatus.replace(/_/g, ' ')
                         .replace(/\\b\\w/g, function(c) { return c.toUpperCase(); });
    statusWrap.innerHTML =
      '<span style="display:inline-block;padding:3px 11px;border-radius:20px;' +
      'background:' + bg + ';color:' + fg + ';font-size:0.72rem;font-weight:600;' +
      'letter-spacing:0.04em;white-space:nowrap;">' + label + '</span>';
  }
"""


# ── Main HTML renderer ─────────────────────────────────────────────────────

def render_html_report(
    top_df,
    get_why_now_fn,
    get_who_fn,
    get_angle_fn,
    get_email_fn,
    total_watchlist,
    total_tracker,
    tracker_df=None,
):
    """
    Build the weekly_memo.html string with Opportunities + Tracker tabs.

    Parameters
    ----------
    top_df           : scored + filtered DataFrame (top-N rows)
    get_why_now_fn   : callable(row) -> list[str]
    get_who_fn       : callable(row) -> list[str]
    get_angle_fn     : callable(row) -> str
    get_email_fn     : callable(row) -> str
    total_watchlist  : int — full watchlist count for summary stats
    total_tracker    : int — tracker row count for summary stats
    tracker_df       : full tracker DataFrame (for the Tracker tab table)
    """
    today      = date.today().strftime("%B %d, %Y")
    top_count  = len(top_df)
    theme_html = _summary_themes(top_df)

    cards_html  = "\n".join(
        _opportunity_card(rank, row, get_why_now_fn, get_who_fn, get_angle_fn, get_email_fn)
        for rank, (_, row) in enumerate(top_df.iterrows(), start=1)
    )
    tracker_html = _tracker_table(tracker_df) if tracker_df is not None else "<p>No tracker data available.</p>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Opportunity Radar for Startup and VC Outreach</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>{_CSS}</style>
</head>
<body>

  <header class="site-header">
    <div class="header-inner">
      <p class="header-eyebrow">Weekly Intelligence Report</p>
      <h1>Opportunity Radar</h1>
      <p class="date-line">Week of {escape(today)}</p>
      <p class="subtitle">
        Automated scan of high-priority startups and VC firms —
        scored, ranked, and paired with outreach drafts.
      </p>
    </div>
  </header>

  <div class="container">

    <section class="summary">
      <p class="summary-eyebrow">This week at a glance</p>
      <div class="summary-stats">
        <div class="stat">
          <span class="stat-value">{total_watchlist}</span>
          <span class="stat-label">Companies on watchlist</span>
        </div>
        <div class="stat">
          <span class="stat-value">{total_tracker}</span>
          <span class="stat-label">Tracker entries</span>
        </div>
        <div class="stat">
          <span class="stat-value">{top_count}</span>
          <span class="stat-label">Top opportunities</span>
        </div>
      </div>
      <p class="summary-theme">{theme_html}</p>
    </section>

    <nav class="tab-nav">
      <button class="tab-btn active" data-tab="opportunities"
              onclick="switchTab('opportunities')">Opportunities</button>
      <button class="tab-btn" data-tab="tracker"
              onclick="switchTab('tracker')">Tracker</button>
    </nav>

    <div id="tab-opportunities" class="tab-panel active">
      {cards_html}
    </div>

    <div id="tab-tracker" class="tab-panel">
      {tracker_html}
    </div>

  </div>

  <footer class="site-footer">
    Generated by Opportunity Radar &mdash; {escape(today)}
  </footer>

  <script>{_JS}</script>
</body>
</html>"""

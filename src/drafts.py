"""
drafts.py — Generate the three narrative blocks + cold email for each opportunity.

All functions accept a single pandas Series (one row from the scored DataFrame)
and return either a list of strings or a plain string.
"""


def get_why_now(row):
    """Return a list of bullet-point reasons this opportunity is timely."""
    reasons = []
    sector   = str(row.get("sector",   "")).lower()
    priority = str(row.get("priority", "")).lower()
    status   = str(row.get("status",   "")).lower()
    category = str(row.get("category", "")).lower()

    if priority == "high":
        reasons.append(
            f"{row['company']} is a high-priority target with strong alignment "
            "to your AI automation and operations background."
        )

    if sector == "cybersecurity":
        reasons.append(
            "Cybersecurity teams are expanding rapidly — AI-native security "
            "companies are actively hiring early-career operators and researchers."
        )
    elif sector == "healthtech":
        reasons.append(
            "Health tech is seeing strong investment and team growth; "
            "mental health infra and clinical AI are two of the hottest sub-sectors."
        )

    if status in ("to_research", "not_started"):
        reasons.append(
            "You haven't reached out yet — the spring semester window "
            "(before summer internships are locked) is closing soon."
        )
    elif status == "to_email":
        reasons.append(
            "Research is done and this is queued to email — act now while "
            "your notes are fresh."
        )

    if category == "vc":
        reasons.append(
            "VC firms hire platform / ops talent in spring and often source "
            "candidates through direct outreach before posting publicly."
        )

    # ── Phase-1 scrape signal reasons ────────────────────────────────────────
    if row.get("internship_signal_detected"):
        reasons.append(
            "Internship or early-career language found on their site — "
            "direct application opportunity confirmed."
        )
    elif row.get("hiring_signal_detected"):
        # Only show hiring if internship wasn't already mentioned (avoid redundancy)
        reasons.append(
            "Active hiring language detected on their careers page — "
            "team is currently expanding."
        )

    if row.get("high_growth_signal_detected"):
        reasons.append(
            "High-growth language detected on site — team is scaling fast "
            "and likely needs execution-focused operators."
        )

    if row.get("early_stage_signal_detected"):
        reasons.append(
            "Early-stage signals detected (seed / YC / accelerator language) — "
            "likely flexible on role scope and open to unconventional hires."
        )

    if row.get("opportunity_signal_detected") and not row.get("hiring_signal_detected"):
        reasons.append(
            "Growth and operations language on their site suggests an opening "
            "for ops, automation, or GTM help even without a posted role."
        )

    if not reasons:
        reasons.append(
            "Strong sector fit and watchlist priority make this a timely opportunity."
        )

    return reasons


def get_who_to_contact(row):
    """Return a list of recommended contact types based on company category."""
    category = str(row.get("category", "")).lower()

    if category == "startup":
        return [
            "Founder or Co-founder (check LinkedIn for NYU / Stern connections)",
            "Head of Operations or Chief of Staff",
            "Head of Growth (if the team has one)",
        ]
    elif category == "vc":
        return [
            "Partner or Principal (look for ones focused on your sectors)",
            "Platform Lead or Community Manager",
            "Talent / Investor Relations team (good cold-email target)",
        ]

    return ["Key decision-maker — search LinkedIn for the company."]


def get_angle(row):
    """Return a 1-2 sentence outreach angle tailored to sector and category."""
    sector   = str(row.get("sector",   "")).lower()
    category = str(row.get("category", "")).lower()
    why      = str(row.get("why_interested", "")).strip()

    if sector == "cybersecurity":
        return (
            f"Lead with your interest in AI-driven security automation and your "
            f"knowledge of the space ({why}). Tie your ops background to their "
            "need for execution-focused early hires."
        )
    elif sector == "healthtech":
        return (
            f"Lead with your understanding of mental health infrastructure and "
            f"clinical AI workflows ({why}). Connect your startup ops experience "
            "to their scaling challenges."
        )
    elif category == "vc":
        return (
            f"Frame yourself as a founder-minded Stern sophomore already building "
            f"tools (Opportunity Radar) and thinking about deals. "
            f"Reference their thesis: {why}."
        )

    return (
        f"Lead with your ops + AI automation background and genuine curiosity "
        f"about their work. Reference why you're interested: {why}."
    )


def generate_email(row):
    """Return a ready-to-personalise cold email draft."""
    company  = row["company"]
    category = str(row.get("category", "")).lower()
    sector   = str(row.get("sector",   "")).lower()
    why      = str(row.get("why_interested", "")).strip().rstrip(".")

    if category == "startup":
        return f"""\
Subject: NYU Stern sophomore interested in ops/growth at {company}

Hi [First Name],

I'm Zaara, a sophomore at NYU Stern studying business with a focus on AI \
automation and startup operations. I've been following {company}'s work in \
{sector} — {why.lower()} — and I'm genuinely excited by what you're building.

I have hands-on experience in growth and operations at an early-stage startup, \
and I've been building my own tooling at the intersection of AI and outreach \
automation. I'd love to explore any ops, growth, or early-career opportunities \
on your team.

Would you be open to a 20-minute call? I'd love to learn more about where \
{company} is headed and how I might contribute.

Best,
Zaara Israni
NYU Stern '27 | AI & Startup Operations
[LinkedIn] | zaara@example.com"""

    else:  # vc
        return f"""\
Subject: Stern sophomore — interested in connecting with {company}

Hi [First Name],

I'm Zaara, a sophomore at NYU Stern focused on early-stage startups and \
venture. I've been following {company}'s portfolio and investment thesis — \
{why.lower()} — and I'd love to connect.

I'm currently building Opportunity Radar, a tool that automates startup and VC \
outreach research, and I have hands-on startup operations experience. I'm \
exploring ways to contribute to a firm like yours — sourcing support, portfolio \
ops, or a platform role.

Would you have 15 minutes for a quick call? I'd genuinely value your \
perspective on the ecosystem.

Best,
Zaara Israni
NYU Stern '27 | Startup & Venture Focus
[LinkedIn] | zaara@example.com"""

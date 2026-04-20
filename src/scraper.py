"""
scraper.py — Phase 1 web scraping for Opportunity Radar.

Scrapes watchlist company websites and careers pages to detect:
  - Explicit hiring signals  (jobs, careers, internship language)
  - Implicit opportunity signals  (growth, early-stage, AI, etc.)

Design principles:
  - Never crashes — every request is wrapped in try/except
  - Prints progress so the user can follow along
  - Returns a clean DataFrame that gets merged into the main pipeline
"""
import math
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup

# ── HTTP config ──────────────────────────────────────────────────────────────

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
TIMEOUT = 6    # seconds per request — keeps the pipeline from hanging
DELAY   = 0.25 # seconds between requests — be polite to servers

# ── Keyword sets ─────────────────────────────────────────────────────────────

HIRING_KEYWORDS = {
    "hiring", "we're hiring", "we are hiring", "join our team",
    "open roles", "open positions", "current openings", "job openings",
    "work with us", "view openings", "see openings", "apply now",
}

INTERNSHIP_KEYWORDS = {
    "internship", "internships", "intern", "interns",
    "co-op", "summer intern", "student program", "early career",
}

# Broad set — signals growth / operational need even without a job posting
OPPORTUNITY_KEYWORDS = {
    "high growth", "fast growing", "fast-growing", "scaling", "scale rapidly",
    "expanding team", "growing team", "early stage", "early-stage",
    "y combinator", "yc", "accelerator", "ycombinator",
    "just launched", "recently launched", "launch", "launched",
    "seed stage", "series a", "series b", "backed by", "venture-backed",
    "growing quickly", "product launch", "momentum", "lean team",
    "small team", "operations", "gtm", "go-to-market",
    "automation", "ai-powered", "ai native", "artificial intelligence",
    "we're building", "mission-driven", "building the future",
}

HIGH_GROWTH_KEYWORDS = {
    "high growth", "fast growing", "fast-growing", "growing quickly",
    "hypergrowth", "scaling fast", "momentum", "rapid growth",
    "scaling", "explosive growth",
}

EARLY_STAGE_KEYWORDS = {
    "early stage", "early-stage", "seed", "series a",
    "y combinator", "yc", "accelerator", "ycombinator",
    "just launched", "recently launched", "pre-launch",
}

# Domains that are YC source pages, not company homepages
YC_DOMAINS = {"ycombinator.com"}


# ── URL helpers ───────────────────────────────────────────────────────────────

def _clean_url(val):
    """Return a normalised URL string or None for empty / NaN values."""
    if val is None:
        return None
    try:
        if math.isnan(float(val)):
            return None
    except (TypeError, ValueError):
        pass
    s = str(val).strip()
    if s in ("", "nan", "NaN"):
        return None
    if not s.startswith("http"):
        s = "https://" + s
    return s


# ── Fetching ──────────────────────────────────────────────────────────────────

def _fetch_text(url):
    """
    GET a URL and return visible page text (scripts/styles stripped).
    Returns None on any error — never raises.
    """
    try:
        resp = requests.get(
            url, headers=HEADERS, timeout=TIMEOUT,
            allow_redirects=True
        )
        if resp.status_code >= 400:
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "noscript", "meta"]):
            tag.decompose()
        return soup.get_text(separator=" ", strip=True)
    except Exception:
        return None


# ── Signal detection ──────────────────────────────────────────────────────────

def _apply_signals(text, signals):
    """Scan page text for all keyword sets; update signals dict in-place."""
    t = text.lower()

    if any(kw in t for kw in HIRING_KEYWORDS):
        signals["hiring_signal_detected"] = True

    if any(kw in t for kw in INTERNSHIP_KEYWORDS):
        signals["internship_signal_detected"] = True

    if any(kw in t for kw in OPPORTUNITY_KEYWORDS):
        signals["opportunity_signal_detected"] = True

    if any(kw in t for kw in HIGH_GROWTH_KEYWORDS):
        signals["high_growth_signal_detected"] = True

    if any(kw in t for kw in EARLY_STAGE_KEYWORDS):
        signals["early_stage_signal_detected"] = True


def _empty_signals(company):
    """Return a zeroed signals dict for a company."""
    return {
        "company":                    company,
        "website_reachable":          False,
        "careers_page_found":         False,
        "hiring_signal_detected":     False,
        "internship_signal_detected": False,
        "opportunity_signal_detected":False,
        "high_growth_signal_detected":False,
        "early_stage_signal_detected":False,
        "yc_source_checked":          False,
    }


# ── Per-company scraper ───────────────────────────────────────────────────────

def scrape_company(row):
    """
    Scrape one watchlist row. Prints progress. Returns a signals dict.
    """
    company  = row["company"]
    website  = _clean_url(row.get("website"))
    careers  = _clean_url(row.get("careers_url"))
    signals  = _empty_signals(company)

    # YC source page — mark as checked, skip actual scraping (JS-rendered)
    if website and any(d in website for d in YC_DOMAINS):
        signals["yc_source_checked"] = True
        print(f"    [yc]      YC source page — marked checked, skipping scrape")
        return signals

    if not website:
        print(f"    [skip]    no website URL")
        return signals

    # ── Main website ─────────────────────────────────────────────────────────
    print(f"    [website] {website}", end="", flush=True)
    text = _fetch_text(website)
    time.sleep(DELAY)

    if text:
        signals["website_reachable"] = True
        _apply_signals(text, signals)
        print("  ✓")
    else:
        print("  ✗ unreachable")

    # ── Careers page ──────────────────────────────────────────────────────────
    if careers:
        print(f"    [careers] {careers}", end="", flush=True)
        ctext = _fetch_text(careers)
        time.sleep(DELAY)

        if ctext:
            signals["careers_page_found"] = True
            _apply_signals(ctext, signals)
            print("  ✓")
        else:
            print("  ✗ not found")

    # ── Print summary of what was found ──────────────────────────────────────
    found = []
    if signals["hiring_signal_detected"]:     found.append("hiring")
    if signals["internship_signal_detected"]: found.append("internship")
    if signals["opportunity_signal_detected"]:found.append("opportunity")
    if signals["high_growth_signal_detected"]:found.append("high-growth")
    if signals["early_stage_signal_detected"]:found.append("early-stage")

    if found:
        print(f"    [signals] {', '.join(found)}")
    elif signals["website_reachable"]:
        print(f"    [signals] none detected")

    return signals


# ── Scrape all ────────────────────────────────────────────────────────────────

def scrape_all(watchlist_df):
    """
    Scrape every company in the watchlist.
    Returns a DataFrame with one row per company containing all signal columns.
    """
    results = []
    total   = len(watchlist_df)

    for i, (_, row) in enumerate(watchlist_df.iterrows(), start=1):
        print(f"\n  [{i:>2}/{total}] {row['company']}")
        result = scrape_company(row)
        results.append(result)

    return pd.DataFrame(results)

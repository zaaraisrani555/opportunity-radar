# Opportunity Radar for Startup and VC Outreach

Opportunity Radar is a lightweight AI-powered sourcing and outreach system designed to help identify startup and venture capital opportunities, prioritize outreach, and manage cold email pipelines.

Instead of manually scanning news, tracking companies, and deciding who to reach out to, this tool automates the process by combining opportunity discovery, signal analysis, prioritization, and outreach drafting into one workflow.

---

## Problem

Students and early-stage candidates trying to break into startups or venture capital often rely on:
- scattered sources (TechCrunch, YC, VC blogs)
- manual tracking of companies
- inconsistent follow-up
- guesswork around who to contact and when

Many of the best opportunities are never posted publicly — they must be identified early through signals and acted on quickly.

---

## Solution

Opportunity Radar acts as an “intelligent assistant” that:

1. Identifies startups and VC firms worth reaching out to  
2. Detects signals that suggest they may need help (even without job postings)  
3. Prioritizes opportunities based on timing, relevance, and likelihood of response  
4. Recommends who to contact  
5. Drafts tailored cold emails  
6. Tracks outreach and follow-ups  

---

## Core Features (MVP)

### 1. Watchlist Tracking
Maintain a curated list of:
- startups
- VC firms
- sectors of interest

---

### 2. Opportunity Ingestion
Pulls in opportunities from:
- curated source list (e.g. YC, startup news, VC sites)
- manually added companies
- sector-specific keywords

---

### 3. Signal Detection

Identifies key signals such as:
- recent funding
- YC batch inclusion
- new product launches
- hiring activity
- small team + high growth
- new VC fund announcements
- portfolio expansion

---

### 4. Opportunity Scoring

Each opportunity is ranked using:
- sector fit (cybersecurity, manufacturing, health tech)
- timing (recent activity, urgency)
- likelihood of needing help
- outreach readiness

---

### 5. Outreach Recommendations

For top opportunities:
- company overview
- “why now” reasoning
- best role/person to contact
- suggested outreach angle

---

### 6. Cold Email Drafting

Generates tailored outreach messages based on:
- company context
- detected signals
- your background

---

### 7. Outreach Tracker

Tracks:
- to research
- to email
- emailed
- follow-up due
- responded
- call booked
- closed

---

### 8. Weekly Action Memo

Outputs:
- top opportunities
- follow-ups
- at-risk threads
- draft emails

---

## Tech Stack

- Python
- pandas
- YAML
- requests / BeautifulSoup (future)
- Markdown / HTML (output)

---

## Project Structure


---

## Example Workflow

1. Load watchlist and tracker
2. Identify opportunities
3. Detect signals
4. Score and rank
5. Recommend outreach
6. Draft emails
7. Output weekly memo
8. Update tracker

---

## Future Improvements

- Live startup + VC scraping
- YC batch parsing
- HTML dashboard UI
- PDF export
- Email enrichment (Hunter)
- Notion / Sheets integration

---

## Author

Zaara Israni  
NYU Stern — Business, Technology & Entrepreneurship  
Interested in startups, VC, AI automation, and growth/operations
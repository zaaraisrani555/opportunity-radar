"""
ingest.py — Load watchlist, tracker, and sources into DataFrames / dicts.
"""
import pandas as pd
import yaml


def load_watchlist(path="data/watchlist.csv"):
    """Load watchlist CSV, skipping comment lines that start with '#'."""
    df = pd.read_csv(path, comment="#")
    df.columns = df.columns.str.strip()
    df["company"] = df["company"].str.strip()
    df["category"] = df["category"].str.strip().str.lower()
    df["sector"] = df["sector"].str.strip().str.lower()
    df["priority"] = df["priority"].str.strip().str.lower()
    return df


def load_tracker(path="data/outreach_tracker.csv"):
    """Load outreach tracker CSV."""
    df = pd.read_csv(path)
    df.columns = df.columns.str.strip()
    df["company"] = df["company"].str.strip()
    df["status"] = df["status"].str.strip().str.lower()
    return df


def load_sources(path="data/sources.yaml"):
    """Load sources YAML into a dict."""
    with open(path) as f:
        return yaml.safe_load(f)

"""Lexical + host-based feature extraction for URLs.

Only uses the URL string itself (no network calls), so it is fast, safe,
and works offline.
"""
import math
import re
from collections import Counter
from urllib.parse import urlparse

SUSPICIOUS_WORDS = [
    "login", "verify", "secure", "account", "update", "bank", "confirm",
    "signin", "password", "wallet", "invoice", "billing", "support", "alert",
]
SUSPICIOUS_TLDS = {"xyz", "top", "tk", "ml", "ga", "cf", "gq", "click", "work", "zip", "info"}
SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd", "cutt.ly"}
IP_RE = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")

FEATURE_NAMES = [
    "url_length", "host_length", "path_length", "num_dots", "num_hyphens",
    "num_digits", "digit_ratio", "num_subdomains", "has_ip_host", "has_at_symbol",
    "uses_https", "num_suspicious_words", "suspicious_tld", "is_shortener",
    "has_punycode", "num_special_chars", "host_entropy", "has_port",
    "num_query_params", "double_slash_in_path",
]


def _entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def extract_features(url: str) -> dict:
    url = url.strip()
    parsed = urlparse(url if "://" in url else "http://" + url)
    host = (parsed.hostname or "").lower()
    path = parsed.path or ""
    parts = host.split(".") if host else []
    tld = parts[-1] if parts else ""
    lowered = url.lower()
    try:
        has_port = int(parsed.port is not None)
    except ValueError:
        has_port = 1

    return {
        "url_length": len(url),
        "host_length": len(host),
        "path_length": len(path),
        "num_dots": url.count("."),
        "num_hyphens": url.count("-"),
        "num_digits": sum(ch.isdigit() for ch in url),
        "digit_ratio": sum(ch.isdigit() for ch in url) / max(len(url), 1),
        "num_subdomains": max(len(parts) - 2, 0),
        "has_ip_host": int(bool(IP_RE.match(host))),
        "has_at_symbol": int("@" in url),
        "uses_https": int(parsed.scheme == "https"),
        "num_suspicious_words": sum(w in lowered for w in SUSPICIOUS_WORDS),
        "suspicious_tld": int(tld in SUSPICIOUS_TLDS),
        "is_shortener": int(host in SHORTENERS),
        "has_punycode": int("xn--" in host),
        "num_special_chars": sum(not ch.isalnum() and ch not in "./:-" for ch in url),
        "host_entropy": _entropy(host),
        "has_port": has_port,
        "num_query_params": len([p for p in parsed.query.split("&") if p]),
        "double_slash_in_path": int("//" in path),
    }

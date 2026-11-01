"""Generate a SYNTHETIC labelled URL dataset (url,label) for demo purposes.

label: 0 = legitimate, 1 = phishing

This lets the project run end-to-end offline. For real results, replace
data/urls.csv with a real dataset (e.g. PhishTank + Tranco top sites, or a
Kaggle phishing-URL dataset) that has the same two columns: url,label.
"""
import random
import string
import pandas as pd

random.seed(42)

LEGIT_DOMAINS = [
    "google.com", "wikipedia.org", "github.com", "stackoverflow.com", "amazon.in",
    "flipkart.com", "linkedin.com", "microsoft.com", "python.org", "kaggle.com",
    "nseindia.com", "zerodha.com", "bbc.com", "nytimes.com", "medium.com",
    "coursera.org", "iisc.ac.in", "mit.edu", "youtube.com", "apple.com",
]
LEGIT_PATHS = ["", "/", "/about", "/docs/intro", "/blog/2025/ml-basics", "/products/12345",
               "/search?q=data+science", "/careers", "/help/contact", "/wiki/Machine_learning"]
BRANDS = ["paypal", "hdfcbank", "sbi", "amazon", "microsoft", "apple", "netflix", "icicibank", "google"]
BAD_TLDS = ["xyz", "top", "tk", "ml", "click", "work", "info", "ga"]
WORDS = ["login", "verify", "secure", "account", "update", "confirm", "signin", "billing", "wallet"]


def rand_str(n):
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def legit_url():
    d = random.choice(LEGIT_DOMAINS)
    sub = random.choice(["", "", "www.", "docs.", "blog."])
    scheme = "https" if random.random() < 0.95 else "http"
    return f"{scheme}://{sub}{d}{random.choice(LEGIT_PATHS)}"


def phishing_url():
    brand = random.choice(BRANDS)
    w1, w2 = random.sample(WORDS, 2)
    kind = random.choice(["brand_sub", "ip", "hyphen", "at", "long", "short_tld"])
    scheme = "http" if random.random() < 0.7 else "https"
    tld = random.choice(BAD_TLDS)
    if kind == "brand_sub":
        return f"{scheme}://{brand}.{w1}.{rand_str(8)}.{tld}/{w2}/index.php?id={rand_str(10)}"
    if kind == "ip":
        ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
        return f"{scheme}://{ip}/{brand}/{w1}-{w2}.html"
    if kind == "hyphen":
        return f"{scheme}://{brand}-{w1}-{w2}.{tld}/{rand_str(6)}"
    if kind == "at":
        return f"{scheme}://{brand}.com@{rand_str(9)}.{tld}/{w1}"
    if kind == "long":
        return f"{scheme}://{w1}.{rand_str(12)}.{tld}/{w2}/{rand_str(20)}/{w1}?session={rand_str(24)}&redirect={brand}"
    return f"{scheme}://{rand_str(7)}.{tld}/{brand}"


def main(n_per_class=2500, out="data/urls.csv"):
    rows = [(legit_url(), 0) for _ in range(n_per_class)]
    rows += [(phishing_url(), 1) for _ in range(n_per_class)]
    random.shuffle(rows)
    pd.DataFrame(rows, columns=["url", "label"]).to_csv(out, index=False)
    print(f"Wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()

# 🛡️ Phishing URL Detector

A machine-learning tool that flags suspicious URLs using only the URL string
(no page visits, no network calls), with a Streamlit app that shows the verdict
and the specific red flags behind it.

## How it works
1. **Feature engineering** (`src/features.py`): 20 lexical/host features, e.g. URL length,
   IP-as-host, `@` symbol, subdomain count, HTTPS use, suspicious keywords/TLDs,
   punycode (look-alike domains), host entropy.
2. **Modelling** (`src/train.py`): Logistic Regression vs Random Forest, compared on
   precision / recall / F1 with a stratified train-test split. Best model saved to `models/`.
3. **App** (`app.py`): paste a URL -> risk score + human-readable red flags.

## Run it
```bash
pip install -r requirements.txt
python src/generate_data.py     # builds a SYNTHETIC demo dataset (see warning)
python src/train.py             # trains, evaluates, saves model + plots in reports/
streamlit run app.py
```

## ⚠️ Important: use a real dataset before putting numbers on your resume
`generate_data.py` creates synthetic URLs so the project runs offline. Because the
patterns are artificially clean, every model scores ~100%. **That number is meaningless.**

To get real results, replace `data/urls.csv` with a real labelled dataset
(columns: `url`, `label` where 0 = legitimate, 1 = phishing). Good sources:
- Kaggle "Phishing Site URLs" / "Malicious URLs" datasets
- PhishTank (phishing) + Tranco top-sites list (legitimate)

Then re-run `python src/train.py` and report the real metrics. On real data, expect
lower scores and a more interesting story (class imbalance, false positives, etc.).

## Ideas to extend
- Handle class imbalance (class weights / SMOTE) and tune the decision threshold
- Add SHAP explanations
- Add WHOIS/domain-age features
- Serve the model through a FastAPI endpoint

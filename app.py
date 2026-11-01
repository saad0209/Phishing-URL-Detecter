"""Streamlit app: paste a URL, get a phishing risk verdict + the reasons."""
import joblib
import pandas as pd
import streamlit as st

from src.features import FEATURE_NAMES, extract_features

st.set_page_config(page_title="Phishing URL Detector", page_icon="🛡️")
st.title("🛡️ Phishing URL Detector")
st.caption("Classifies a URL using lexical features only. No page is visited.")


@st.cache_resource
def load_model():
    return joblib.load("models/model.joblib")


try:
    model = load_model()
except FileNotFoundError:
    st.error("Model not found. Run `python src/generate_data.py` and `python src/train.py` first.")
    st.stop()

url = st.text_input("Enter a URL", placeholder="http://paypal.verify.secure-login.xyz/account")

if st.button("Analyse") and url:
    feats = extract_features(url)
    X = pd.DataFrame([feats])[FEATURE_NAMES]
    prob = float(model.predict_proba(X)[0][1])

    if prob >= 0.5:
        st.error(f"⚠️ Likely PHISHING (risk score {prob:.0%})")
    else:
        st.success(f"✅ Likely legitimate (risk score {prob:.0%})")

    flags = []
    if feats["has_ip_host"]: flags.append("Uses a raw IP address instead of a domain")
    if feats["has_at_symbol"]: flags.append("Contains '@' (can hide the real destination)")
    if not feats["uses_https"]: flags.append("Not using HTTPS")
    if feats["suspicious_tld"]: flags.append("Suspicious top-level domain")
    if feats["num_suspicious_words"]: flags.append(f"{feats['num_suspicious_words']} phishing-style keyword(s)")
    if feats["num_subdomains"] >= 3: flags.append("Unusually many subdomains")
    if feats["is_shortener"]: flags.append("URL shortener hides the destination")
    if feats["has_punycode"]: flags.append("Punycode (possible look-alike characters)")
    st.subheader("Red flags")
    st.write("\n".join(f"- {f}" for f in flags) if flags else "None of the rule-based red flags triggered.")

    with st.expander("Extracted features"):
        st.dataframe(pd.DataFrame([feats]).T.rename(columns={0: "value"}))

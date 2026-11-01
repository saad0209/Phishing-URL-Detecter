"""Train and compare models, save the best one + evaluation plots."""
import json
import os
import sys

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (ConfusionMatrixDisplay, classification_report,
                             f1_score, precision_score, recall_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.features import FEATURE_NAMES, extract_features  # noqa: E402

DATA = "data/urls.csv"


def main():
    df = pd.read_csv(DATA).dropna(subset=["url", "label"])
    X = pd.DataFrame([extract_features(u) for u in df["url"]])[FEATURE_NAMES]
    y = df["label"].astype(int)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

    models = {
        "logistic_regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "random_forest": RandomForestClassifier(n_estimators=200, random_state=42),
    }

    results, best_name, best_f1 = {}, None, -1
    for name, model in models.items():
        model.fit(X_tr, y_tr)
        pred = model.predict(X_te)
        f1 = f1_score(y_te, pred)
        results[name] = {
            "precision": round(precision_score(y_te, pred), 4),
            "recall": round(recall_score(y_te, pred), 4),
            "f1": round(f1, 4),
        }
        print(f"\n=== {name} ===\n{classification_report(y_te, pred, target_names=['legit', 'phishing'])}")
        if f1 > best_f1:
            best_name, best_f1 = name, f1

    best = models[best_name]
    os.makedirs("models", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    joblib.dump(best, "models/model.joblib")
    json.dump({"best_model": best_name, "metrics": results}, open("reports/metrics.json", "w"), indent=2)

    ConfusionMatrixDisplay.from_estimator(best, X_te, y_te, display_labels=["legit", "phishing"])
    plt.title(f"Confusion matrix - {best_name}")
    plt.savefig("reports/confusion_matrix.png", dpi=150, bbox_inches="tight")
    plt.close()

    rf = models["random_forest"]
    imp = pd.Series(rf.feature_importances_, index=FEATURE_NAMES).sort_values()
    imp.plot.barh(figsize=(7, 6), title="Random Forest feature importance")
    plt.savefig("reports/feature_importance.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\nBest model: {best_name} (F1={best_f1:.4f}) saved to models/model.joblib")


if __name__ == "__main__":
    main()

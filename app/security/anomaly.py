"""Intelligent data processing: anomaly detection for Smart-card access logs."""
import base64
import io
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


class AnomalyDetector:
    FEATURES = ["failed_pin_count", "requests_per_min", "hour"]

    def __init__(self, contamination: float = 0.15, random_state: int = 42):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100,
        )
        self.scaler = StandardScaler()

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        if "timestamp" in out.columns:
            out["timestamp"] = pd.to_datetime(out["timestamp"])
            out["hour"] = out["timestamp"].dt.hour
        else:
            out["hour"] = 12
        for col in self.FEATURES:
            if col not in out.columns:
                out[col] = 0
        return out

    def analyze(self, df: pd.DataFrame) -> dict[str, Any]:
        prepared = self.prepare_features(df)
        X = prepared[self.FEATURES].astype(float).values
        X_scaled = self.scaler.fit_transform(X)
        preds = self.model.fit_predict(X_scaled)
        scores = self.model.decision_function(X_scaled)

        prepared["anomaly_score"] = scores
        prepared["is_anomaly"] = preds == -1
        prepared["ml_decision"] = np.where(
            prepared["is_anomaly"], "block_recommended", "allow"
        )

        if "label" in prepared.columns:
            y_true = prepared["label"].astype(str).str.lower() == "attack"
            y_pred = prepared["is_anomaly"]
            accuracy = float((y_true == y_pred).mean()) if len(prepared) else 0.0
        else:
            accuracy = None

        table = prepared.sort_values("anomaly_score").head(20)[
            [
                "session_id",
                "card_id",
                "failed_pin_count",
                "requests_per_min",
                "hour",
                "anomaly_score",
                "ml_decision",
            ]
            + (["label"] if "label" in prepared.columns else [])
        ]

        charts = {
            "histogram": self._chart_histogram(prepared),
            "scatter": self._chart_scatter(prepared),
            "pie": self._chart_pie(prepared),
        }

        summary = {
            "total_records": len(prepared),
            "anomalies_detected": int(prepared["is_anomaly"].sum()),
            "normal_records": int((~prepared["is_anomaly"]).sum()),
            "accuracy_vs_labels": accuracy,
        }

        return {
            "summary": summary,
            "table": table.to_dict(orient="records"),
            "charts": charts,
            "full_predictions": prepared[
                ["session_id", "card_id", "anomaly_score", "ml_decision", "is_anomaly"]
            ].to_dict(orient="records"),
        }

    def _fig_to_base64(self, fig) -> str:
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    def _chart_histogram(self, df: pd.DataFrame) -> str:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.hist(df["anomaly_score"], bins=20, color="#2563eb", edgecolor="white")
        ax.set_title("Распределение anomaly score")
        ax.set_xlabel("Score")
        ax.set_ylabel("Количество сессий")
        return self._fig_to_base64(fig)

    def _chart_scatter(self, df: pd.DataFrame) -> str:
        fig, ax = plt.subplots(figsize=(6, 4))
        colors = np.where(df["is_anomaly"], "#dc2626", "#16a34a")
        ax.scatter(
            df["failed_pin_count"],
            df["requests_per_min"],
            c=colors,
            alpha=0.7,
            edgecolors="white",
        )
        ax.set_title("PIN failures vs request rate")
        ax.set_xlabel("Failed PIN count")
        ax.set_ylabel("Requests per minute")
        return self._fig_to_base64(fig)

    def _chart_pie(self, df: pd.DataFrame) -> str:
        fig, ax = plt.subplots(figsize=(5, 4))
        counts = [
            int((~df["is_anomaly"]).sum()),
            int(df["is_anomaly"].sum()),
        ]
        ax.pie(
            counts,
            labels=["Normal", "Anomaly"],
            autopct="%1.1f%%",
            colors=["#16a34a", "#dc2626"],
        )
        ax.set_title("Классификация сессий ML")
        return self._fig_to_base64(fig)

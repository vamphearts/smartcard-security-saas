import os
from datetime import datetime

import pandas as pd
from flask import Flask, jsonify, render_template, request
from werkzeug.utils import secure_filename

from security import AnomalyDetector, AuditLogger, SecurityContainer

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://app:smartcard_secret@db:5432/smartcard_db",
)

security = SecurityContainer()
audit = AuditLogger(DATABASE_URL)
detector = AnomalyDetector()


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "smartcard-security-web"})


@app.route("/")
def index():
    logs = audit.list_recent(30)
    return render_template("index.html", logs=logs)


@app.route("/api/access", methods=["POST"])
def api_access():
    data = request.get_json(force=True, silent=True) or {}
    card_id = str(data.get("card_id", "")).strip()
    session_id = str(data.get("session_id", "")).strip()
    failed_pin = int(data.get("failed_pin_count", 0))
    rpm = float(data.get("requests_per_min", 0))

    if not card_id or not session_id:
        return jsonify({"error": "card_id and session_id required"}), 400

    decision = security.register_attempt(card_id, session_id, failed_pin, rpm)
    audit.log_event(
        {
            "session_id": session_id,
            "card_id": card_id,
            "failed_pin_count": failed_pin,
            "requests_per_min": rpm,
            "access_granted": 1 if decision["access_granted"] else 0,
            "label": data.get("label", "live"),
            "decision": decision["reason"],
            "details": decision["message"],
        }
    )
    return jsonify(decision)


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    if "file" not in request.files:
        return jsonify({"error": "CSV file required"}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "empty filename"}), 400

    df = pd.read_csv(f.stream)
    required = {"session_id", "card_id", "failed_pin_count", "requests_per_min"}
    if not required.issubset(df.columns):
        return jsonify({"error": f"missing columns: {required - set(df.columns)}"}), 400

    result = detector.analyze(df)

    for row in result["full_predictions"]:
        if row["is_anomaly"]:
            security.block_card(row["card_id"])

    for _, r in df.iterrows():
        ml_row = next(
            (
                p
                for p in result["full_predictions"]
                if p["session_id"] == r["session_id"]
            ),
            None,
        )
        audit.log_event(
            {
                "session_id": r["session_id"],
                "card_id": r["card_id"],
                "timestamp": pd.to_datetime(r.get("timestamp", datetime.utcnow())),
                "failed_pin_count": int(r["failed_pin_count"]),
                "requests_per_min": float(r["requests_per_min"]),
                "access_granted": 0 if ml_row and ml_row["is_anomaly"] else 1,
                "label": str(r.get("label", "import")),
                "anomaly_score": float(ml_row["anomaly_score"]) if ml_row else None,
                "decision": ml_row["ml_decision"] if ml_row else "allow",
                "details": "batch ML analysis",
            }
        )

    return jsonify(result)


@app.route("/api/logs")
def api_logs():
    return jsonify(audit.list_recent(100))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=os.getenv("FLASK_DEBUG", "0") == "1")

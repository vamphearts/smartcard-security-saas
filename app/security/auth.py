"""Security container: session control and access blocking for Smart-card SaaS."""
from datetime import datetime, timedelta
from typing import Optional


class SecurityContainer:
    MAX_FAILED_PIN = 3
    MAX_REQUESTS_PER_MIN = 30
    BLOCK_MINUTES = 15

    def __init__(self):
        self._blocked: dict[str, datetime] = {}
        self._sessions: dict[str, dict] = {}

    def is_blocked(self, card_id: str) -> bool:
        until = self._blocked.get(card_id)
        if not until:
            return False
        if datetime.utcnow() >= until:
            del self._blocked[card_id]
            return False
        return True

    def register_attempt(
        self,
        card_id: str,
        session_id: str,
        failed_pin_count: int,
        requests_per_min: int,
    ) -> dict:
        if self.is_blocked(card_id):
            return {
                "access_granted": False,
                "reason": "card_blocked",
                "message": "Smart-card access temporarily blocked",
            }

        suspicious = (
            failed_pin_count >= self.MAX_FAILED_PIN
            or requests_per_min >= self.MAX_REQUESTS_PER_MIN
        )

        if suspicious:
            self._blocked[card_id] = datetime.utcnow() + timedelta(
                minutes=self.BLOCK_MINUTES
            )
            return {
                "access_granted": False,
                "reason": "anomaly_policy",
                "message": "Blocked by security container policy",
            }

        self._sessions[session_id] = {
            "card_id": card_id,
            "failed_pin_count": failed_pin_count,
            "requests_per_min": requests_per_min,
            "updated_at": datetime.utcnow().isoformat(),
        }
        return {"access_granted": True, "reason": "ok", "message": "Access granted"}

    def get_session(self, session_id: str) -> Optional[dict]:
        return self._sessions.get(session_id)

    def block_card(self, card_id: str, minutes: Optional[int] = None) -> None:
        mins = minutes if minutes is not None else self.BLOCK_MINUTES
        self._blocked[card_id] = datetime.utcnow() + timedelta(minutes=mins)

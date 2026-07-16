from datetime import datetime, timezone


def get_health_response() -> dict:
    return {
        "status": "ok",
        "service": "ms2",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

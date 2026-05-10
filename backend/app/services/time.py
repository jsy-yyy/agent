from datetime import datetime, timezone


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def to_storage_time(value: datetime) -> str:
    return value.isoformat()

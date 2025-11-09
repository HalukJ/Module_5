class DeliveryMarks:
    """Symbols for delivery states (WhatsApp-like stars)."""

    PENDING = "☆"
    DELIVERED = "⭐⭐"
    INCOMPLETE = "☆✗"

    @staticmethod
    def stamp(ts: str, mark: str) -> str:
        return f"{ts} {mark}".strip()


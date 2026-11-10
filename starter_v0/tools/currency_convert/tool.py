from __future__ import annotations

from typing import Any
from tools._shared import err


RATES_TO_USD: dict[str, float] = {
    "USD": 1.0,
    "VND": 0.000039,
    "EUR": 1.08,
    "GBP": 1.29,
    "JPY": 0.0065,
    "CNY": 0.14,
    "AUD": 0.66,
    "CAD": 0.72,
    "SGD": 0.76,
}


def convert_currency(
    amount: float = 1.0,
    from_currency: str = "USD",
    to_currency: str = "VND",
) -> dict[str, Any]:
    """Convert amount between world currencies."""
    try:
        try:
            amt = float(amount)
        except (ValueError, TypeError):
            return {"tool": "currency_convert", "error": "ValueError", "message": f"Invalid amount: {amount}"}

        if amt < 0:
            return {"tool": "currency_convert", "error": "ValueError", "message": "Amount must be non-negative"}

        base_from = (from_currency or "USD").strip().upper()
        base_to = (to_currency or "VND").strip().upper()

        if base_from not in RATES_TO_USD:
            return {"tool": "currency_convert", "error": "ValueError", "message": f"Unsupported currency: {base_from}"}
        if base_to not in RATES_TO_USD:
            return {"tool": "currency_convert", "error": "ValueError", "message": f"Unsupported currency: {base_to}"}

        usd_val = amt * RATES_TO_USD[base_from]
        converted = usd_val / RATES_TO_USD[base_to]
        rate = RATES_TO_USD[base_from] / RATES_TO_USD[base_to]

        return {
            "tool": "currency_convert",
            "amount": amt,
            "from_currency": base_from,
            "to_currency": base_to,
            "converted_amount": round(converted, 4),
            "rate": round(rate, 6),
            "status": "success",
        }
    except Exception as exc:
        return err("currency_convert", exc)


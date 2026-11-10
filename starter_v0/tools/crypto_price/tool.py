from __future__ import annotations

from typing import Any
import requests

from tools._shared import TIMEOUT, err


def get_crypto_price(symbol: str = "", currency: str = "USD") -> dict[str, Any]:
    """Get real-time cryptocurrency price and 24h stats."""
    try:
        clean_symbol = (symbol or "").strip().upper()
        if not clean_symbol:
            return {"tool": "crypto_price", "error": "ValueError", "message": "Symbol cannot be empty"}

        clean_currency = (currency or "USD").strip().upper()
        pair = f"{clean_symbol}{clean_currency}" if clean_currency in ["USDT", "BTC"] else f"{clean_symbol}USDT"
        url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}"

        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()

        return {
            "tool": "crypto_price",
            "symbol": clean_symbol,
            "currency": clean_currency,
            "price": float(data.get("lastPrice", 0.0)),
            "change_24h": float(data.get("priceChangePercent", 0.0)),
            "high_24h": float(data.get("highPrice", 0.0)),
            "low_24h": float(data.get("lowPrice", 0.0)),
            "status": "success",
        }
    except Exception as exc:
        return err("crypto_price", exc)


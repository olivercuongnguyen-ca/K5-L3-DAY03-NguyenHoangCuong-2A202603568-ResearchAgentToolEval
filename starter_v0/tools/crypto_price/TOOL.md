---
name: crypto_price
track: bonus
kind: live_api
provider: Binance Public API
requires_env: []
inputs: [symbol, currency]
outputs: [tool, symbol, currency, price, change_24h, high_24h, low_24h, status]
side_effect: false
---
# crypto_price

Tra cứu giá thời gian thực và biến động 24h của đồng tiền mã hóa (Bitcoin, Ethereum, Solana, v.v.).


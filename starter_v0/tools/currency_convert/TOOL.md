---
name: currency_convert
track: bonus
kind: local_formatter
provider: Exchange Rates
requires_env: []
inputs: [amount, from_currency, to_currency]
outputs: [tool, amount, from_currency, to_currency, converted_amount, rate, status]
side_effect: false
---
# currency_convert

Quy đổi tỷ giá tiền tệ quốc tế giữa các đơn vị phổ biến (USD, VND, EUR, JPY, GBP, CNY).


"""TODO"""
from typing import Dict

import requests


class ForexService:
    """TODO"""
    BASE_URL = "https://api.frankfurter.app/latest"

    def get_quote(self, base: str, target: str, amount: float) -> Dict[str, float]:
        """TODO"""
        params = {"from": base.upper(), "to": target.upper()}
        try:
            resp = requests.get(self.BASE_URL, params=params, timeout=10)
        except requests.RequestException as exc:
            raise RuntimeError(f"Error calling FX API: {exc}") from exc

        if resp.status_code != 200:
            raise RuntimeError(f"FX API error: {resp.status_code} - {resp.text}")

        data = resp.json()
        rates = data.get("rates") or {}
        rate = rates.get(target.upper())
        if rate is None:
            raise RuntimeError("Target currency not supported by FX API")

        converted = float(rate) * float(amount)

        return {
            "rate": float(rate),
            "converted_amount": converted,
        }

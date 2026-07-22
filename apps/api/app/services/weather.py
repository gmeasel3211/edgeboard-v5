from __future__ import annotations

import re
from datetime import datetime
from typing import Any

import httpx


class WeatherClient:
    USER_AGENT = "EdgeBoard/3.0 (support@example.com)"

    async def forecast_for(
        self, latitude: float | None, longitude: float | None, game_time: datetime
    ) -> dict[str, Any]:
        if latitude is None or longitude is None:
            return self.neutral()
        headers = {"User-Agent": self.USER_AGENT, "Accept": "application/geo+json"}
        try:
            async with httpx.AsyncClient(timeout=20, headers=headers) as client:
                point = await client.get(f"https://api.weather.gov/points/{latitude},{longitude}")
                point.raise_for_status()
                hourly_url = point.json()["properties"]["forecastHourly"]
                forecast = await client.get(hourly_url)
                forecast.raise_for_status()
                periods = forecast.json()["properties"]["periods"]
            closest = min(
                periods,
                key=lambda item: abs(
                    datetime.fromisoformat(item["startTime"]).timestamp() - game_time.timestamp()
                ),
            )
            temperature = float(closest.get("temperature", 70))
            wind_speed = self._parse_wind(closest.get("windSpeed", "0 mph"))
            short = str(closest.get("shortForecast", ""))
            rain = closest.get("probabilityOfPrecipitation", {}).get("value") or 0
            temperature_factor = 1 + (temperature - 70) * 0.0022
            wind_factor = 1 + min(wind_speed, 20) * 0.0015
            rain_factor = 0.985 if rain >= 50 else 1.0
            run_factor = min(max(temperature_factor * wind_factor * rain_factor, 0.90), 1.12)
            return {
                "temperature": temperature,
                "wind_speed": wind_speed,
                "rain_probability": rain,
                "summary": short,
                "run_factor": run_factor,
                "quality": 82,
            }
        except Exception:
            return self.neutral()

    @staticmethod
    def _parse_wind(value: str) -> float:
        numbers = [float(item) for item in re.findall(r"\d+(?:\.\d+)?", value)]
        return sum(numbers) / len(numbers) if numbers else 0.0

    @staticmethod
    def neutral() -> dict[str, Any]:
        return {
            "temperature": 70.0,
            "wind_speed": 0.0,
            "rain_probability": 0,
            "summary": "Weather unavailable",
            "run_factor": 1.0,
            "quality": 35,
        }

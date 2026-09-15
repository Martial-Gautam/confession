"""Daily task: refresh the 60-day Instagram token and write it back to .env."""
from pathlib import Path

import requests
from dotenv import dotenv_values, set_key

ENV = Path(__file__).with_name(".env")
token = dotenv_values(ENV)["IG_TOKEN"]
r = requests.get("https://graph.instagram.com/refresh_access_token",
                 params={"grant_type": "ig_refresh_token", "access_token": token}, timeout=30).json()
if "access_token" not in r:
    raise SystemExit(f"refresh failed: {r}")
set_key(ENV, "IG_TOKEN", r["access_token"])
print("token refreshed, expires in", r["expires_in"] // 86400, "days")

import hmac
import hashlib
import time
import requests
import os
from fastapi import FastAPI, Request

app = FastAPI()

API_KEY = os.environ.get("BYBIT_API_KEY")
API_SECRET = os.environ.get("BYBIT_API_SECRET")
VERIFICATION_TOKEN = os.environ.get("VERCEL_AUTH_TOKEN")

BYBIT_URL = "https://api.bybit.com/v5/order/create"

@app.post("/api/bybit_order")
async def place_order(request: Request):
    data = await request.json()
    if data.get("auth") != VERIFICATION_TOKEN:
        return {"error": "Unauthorized"}

    symbol = data.get("symbol")
    side = data.get("side")
    qty = str(data.get("qty"))

    timestamp = str(int(time.time() * 1000))
    recv_window = "5000"

    params = {
        "category": "linear",
        "symbol": symbol,
        "side": side,
        "orderType": "Market",
        "qty": qty,
        "timeInForce": "GTC",
        "timestamp": timestamp,
        "recvWindow": recv_window
    }

    # 建立簽名
    param_str = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    sign = hmac.new(bytes(API_SECRET, "utf-8"), bytes(param_str, "utf-8"), hashlib.sha256).hexdigest()

    headers = {
        "X-BYBIT-API-KEY": API_KEY,
        "X-BYBIT-SIGN": sign,
        "Content-Type": "application/json"
    }

    response = requests.post(BYBIT_URL, headers=headers, json=params)
    return {"status": "done", "bybit_response": response.json()}

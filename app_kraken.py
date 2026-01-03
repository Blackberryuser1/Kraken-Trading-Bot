import os
from flask import Flask, request, abort, jsonify
from dotenv import load_dotenv

from kraken_client import place_kraken_order

load_dotenv()

WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")

app = Flask(__name__)

def validate_payload(payload):
    """
    Basic validation for Kraken webhook payload.
    Expected JSON:
    {
      "side": "buy" or "sell",
      "symbol": "BTC/USD",
      "amount": 0.001
    }
    """
    required = ["side", "symbol", "amount"]

    for field in required:
        if field not in payload:
            return False, f"Missing field: {field}"

    if payload["side"] not in ["buy", "sell"]:
        return False, "Invalid side. Must be 'buy' or 'sell'."

    symbol = payload["symbol"]
    if not isinstance(symbol, str) or not symbol.strip():
        return False, "Symbol must be a non-empty string."

    try:
        amount = float(payload["amount"])
        if amount <= 0:
            return False, "Amount must be greater than zero."
    except Exception:
        return False, "Amount must be a valid number."

    return True, "OK"

@app.route("/kraken-webhook", methods=["POST"])
def kraken_webhook():
    # Simple header secret check
    if WEBHOOK_SECRET and request.headers.get("X-Webhook-Secret") != WEBHOOK_SECRET:
        abort(401)

    payload = request.get_json(silent=True) or {}
    is_valid, message = validate_payload(payload)
    if not is_valid:
        return jsonify({"error": message}), 400

    side = payload["side"]
    symbol = payload["symbol"].upper()
    amount = float(payload["amount"])

    try:
        order = place_kraken_order(side, symbol, amount)
        return jsonify({"status": "ok", "order": order}), 200
    except Exception:
        # In production, log the exception instead of exposing it.
        return jsonify({"error": "Order failed"}), 500

if __name__ == "__main__":
    port = int(os.getenv("KRAKEN_PORT", "5003"))
    app.run(host="0.0.0.0", port=port, debug=False)
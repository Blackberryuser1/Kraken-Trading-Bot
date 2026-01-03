import os
import ccxt
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("KRAKEN_API_KEY")
API_SECRET = os.getenv("KRAKEN_API_SECRET")
TESTNET = os.getenv("KRAKEN_SANDBOX", "true").lower() in ("1", "true", "yes")

exchange = ccxt.kraken({
    "apiKey": API_KEY,
    "secret": API_SECRET,
    "enableRateLimit": True,
})

# Kraken “sandbox” is limited; ccxt may not fully support it,
# but we keep the flag for future handling.
try:
    if TESTNET:
        exchange.set_sandbox_mode(True)
except Exception:
    # If sandbox is not supported, just continue in normal mode
    pass

# Load markets once so we can validate symbols if needed later
exchange.load_markets()

def place_kraken_order(side: str, symbol: str, amount: float):
    """
    Place a crypto market order on Kraken.

    - side: "buy" or "sell"
    - symbol: e.g. "BTC/USD", "ETH/USD", "BTC/EUR"
    - amount: base asset units (e.g., 0.001 BTC)

    Raises:
        ValueError if side is invalid.
        ccxt errors if the order fails.
    """
    if side not in ["buy", "sell"]:
        raise ValueError("Invalid side for Kraken order")

    # Optional: basic symbol check
    if symbol not in exchange.markets:
        raise ValueError(f"Symbol not supported on Kraken: {symbol}")

    order = exchange.create_order(
        symbol=symbol,
        type="market",
        side=side,
        amount=amount
    )
    return order
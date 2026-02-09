"""
SustainAdvisor Elite - SGX Institutional Engine
Flask backend for ESG stock recommendation engine
"""
import json
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "stocks.json")

DEFAULT_STOCKS = [
    {"n": "DBS Group", "c": "D05", "e": 72, "s": 82, "g": 98, "y": 5.2, "vol": "Low", "f": "Voted World's Best Bank 5 times.", "d": "Quarterly dividends; highly reliable.", "gr": "Expansion into digital assets & carbon exchange.", "p": "Top-tier Governance compared to regional banks.", "w": "www.dbs.com/investors", "risk": "Interest rate sensitivity."},
    {"n": "Sembcorp Ind.", "c": "U96", "e": 96, "s": 68, "g": 75, "y": 3.8, "vol": "Med", "f": "SG's largest renewable energy player.", "d": "Steady growth; payouts linked to green profit.", "gr": "Scaling brown-to-green energy transition.", "p": "Leading the utilities sector in ESG metrics.", "w": "www.sembcorp.com", "risk": "Energy transition execution."},
    {"n": "City Develop.", "c": "C09", "e": 94, "s": 88, "g": 90, "y": 2.8, "vol": "Low", "f": "Pioneer in green building since 2000s.", "d": "Conservative but consistent annual payouts.", "gr": "Global expansion of sustainable luxury hotels.", "p": "Ranked #1 most sustainable real estate firm.", "w": "www.cdl.com.sg", "risk": "Property cycle exposure."},
    {"n": "Singtel", "c": "Z74", "e": 82, "s": 92, "g": 88, "y": 5.4, "vol": "Low", "f": "Deep focus on workplace disability inclusion.", "d": "Reliable 'Dividend Aristocrat' in Singapore.", "gr": "Next-gen 5G and green data center growth.", "p": "Superior social score over regional telcos.", "w": "www.singtel.com", "risk": "Competition in regional markets."},
    {"n": "OCBC Bank", "c": "O39", "e": 75, "s": 80, "g": 94, "y": 5.8, "vol": "Low", "f": "Strongest capital ratios in SE Asia.", "d": "High yield; strong payout history.", "gr": "ASEAN-Greater China wealth management hub.", "p": "More value-oriented than DBS with similar G.", "w": "www.ocbc.com", "risk": "Credit cycle exposure."},
    {"n": "CapitaLand Ascas", "c": "A17U", "e": 85, "s": 78, "g": 82, "y": 6.2, "vol": "Med", "f": "Dominant in eco-friendly logistics space.", "d": "High REIT distribution payouts (DPU).", "gr": "High-tech industrial space demand surge.", "p": "Largest industrial REIT in Singapore.", "w": "www.capitaland.com", "risk": "Interest rate sensitivity."},
    {"n": "SIA", "c": "C6L", "e": 68, "s": 85, "g": 82, "y": 4.5, "vol": "High", "f": "Pioneering Sustainable Aviation Fuel (SAF).", "d": "Resumed payouts following profit records.", "gr": "Full travel recovery and fleet modernization.", "p": "Global brand leader in aviation sustainability.", "w": "www.singaporeair.com", "risk": "Oil price and travel demand volatility."},
    {"n": "Keppel Ltd", "c": "BN4", "e": 88, "s": 76, "g": 80, "y": 4.3, "vol": "Med", "f": "Global asset manager for clean infra.", "d": "Competitive semi-annual distributions.", "gr": "Asset-light model boosting return on equity.", "p": "Pivoting faster than traditional conglomerates.", "w": "www.keppel.com", "risk": "Asset recycling execution."},
    {"n": "MapleTree Pan Asia", "c": "N2IU", "e": 78, "s": 82, "g": 80, "y": 6.5, "vol": "Med", "f": "Owns VivoCity, SG's largest mall.", "d": "Top-tier yield for income-seekers.", "gr": "Retail and office rebound in major hubs.", "p": "Exceptional footprint in Asian commercial hubs.", "w": "www.mapletreepanasiacommercialtrust.com", "risk": "Retail sector headwinds."},
    {"n": "ST Engineering", "c": "S63", "e": 74, "s": 86, "g": 85, "y": 3.6, "vol": "Low", "f": "Global leader in aircraft maintenance.", "d": "Recession-resilient dividend history.", "gr": "Smart city and aerospace defense contracts.", "p": "Stability play for conservative portfolios.", "w": "www.stengg.com", "risk": "Defense budget cycles."},
    {"n": "ComfortDelGro", "c": "C52", "e": 90, "s": 82, "g": 78, "y": 5.1, "vol": "Med", "f": "Running EV fleets across 7 countries.", "d": "Consistent payouts supported by cash flow.", "gr": "Public transport electrification globally.", "p": "Transportation sector leader in social metrics.", "w": "www.comfortdelgro.com", "risk": "Government contract renewals."},
    {"n": "Wilmar Intl.", "c": "F34", "e": 66, "s": 74, "g": 80, "y": 4.1, "vol": "High", "f": "World's largest palm oil processor.", "d": "Dividend varies with commodity cycles.", "gr": "Expanding consumer food brands in China/India.", "p": "Critical scale in global food security.", "w": "www.wilmar-international.com", "risk": "Commodity price volatility."},
]


STOCKS_KEY = "sgx_stocks"


def load_stocks():
    """Load stock database from Redis (Vercel) or JSON file (local)."""
    if os.environ.get("UPSTASH_REDIS_REST_URL"):
        try:
            from upstash_redis import Redis
            redis = Redis.from_env()
            data = redis.get(STOCKS_KEY)
            if data:
                return json.loads(data)
        except Exception:
            pass
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return DEFAULT_STOCKS.copy()


def save_stocks(stocks):
    """Save stock database to Redis (Vercel) or JSON file (local)."""
    if os.environ.get("UPSTASH_REDIS_REST_URL"):
        try:
            from upstash_redis import Redis
            redis = Redis.from_env()
            redis.set(STOCKS_KEY, json.dumps(stocks))
            return
        except Exception:
            pass
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(stocks, f, indent=2)


def get_stocks():
    return load_stocks()


def rank_stocks(stocks, u_e: int, u_s: int, u_g: int, u_y: int, top_n: int = 3) -> list:
    """Rank stocks by match score based on user preferences."""
    ranked = []
    for s in stocks:
        diff = (
            abs(s["e"] - u_e)
            + abs(s["s"] - u_s)
            + abs(s["g"] - u_g)
            + abs((s["y"] * 15) - u_y)
        )
        match = max(0, 100 - (diff / 4.5))
        ranked.append({**s, "match": round(match, 1)})
    ranked.sort(key=lambda x: x["match"], reverse=True)
    return ranked[:top_n]


@app.route("/")
def index():
    """Serve main SustainAdvisor Elite interface."""
    return render_template("index.html")


@app.route("/api/analyze", methods=["POST"])
def analyze():
    """API endpoint for stock analysis based on user preferences."""
    data = request.get_json() or {}
    u_e = int(data.get("e", 50))
    u_s = int(data.get("s", 50))
    u_g = int(data.get("g", 50))
    u_y = int(data.get("y", 50))
    top_n = int(data.get("top_n", 3))

    # Validate ranges
    for val, name in [(u_e, "e"), (u_s, "s"), (u_g, "g"), (u_y, "y")]:
        if not 0 <= val <= 100:
            return jsonify({"error": f"Invalid {name} value: {val}"}), 400

    stocks = get_stocks()
    ranked = rank_stocks(stocks, u_e, u_s, u_g, u_y, top_n)
    return jsonify({
        "preferences": {"e": u_e, "s": u_s, "g": u_g, "y": u_y},
        "stocks": ranked,
    })


@app.route("/api/stocks", methods=["GET", "POST"])
def stocks():
    """GET: Return full stock database. POST: Add new company."""
    if request.method == "GET":
        return jsonify({"stocks": get_stocks()})

    # POST: add new stock
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON body"}), 400

    required = ["n", "c", "e", "s", "g", "y", "vol", "f", "d", "gr", "p", "w", "risk"]
    stock = {}
    for key in required:
        val = data.get(key)
        if val is None or val == "":
            return jsonify({"error": f"Missing required field: {key}"}), 400
        stock[key] = val

    # Type coercion for numeric fields
    for k in ["e", "s", "g"]:
        try:
            stock[k] = int(stock[k]) if isinstance(stock[k], str) else int(stock[k])
        except (ValueError, TypeError):
            return jsonify({"error": f"Invalid number for {k}"}), 400
    try:
        stock["y"] = float(stock["y"]) if isinstance(stock["y"], str) else float(stock["y"])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid number for yield"}), 400

    if not 0 <= stock["e"] <= 100 or not 0 <= stock["s"] <= 100 or not 0 <= stock["g"] <= 100:
        return jsonify({"error": "E, S, G must be 0-100"}), 400

    stocks = get_stocks()
    if any(s["c"] == stock["c"] for s in stocks):
        return jsonify({"error": f"Company with ticker {stock['c']} already exists"}), 400

    stocks.append(stock)
    save_stocks(stocks)
    return jsonify({"success": True, "stock": stock})


if __name__ == "__main__":
    app.run(debug=True, port=5001)

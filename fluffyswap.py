from flask import Flask, jsonify, request
import requests
import logging
import time

app = Flask(__name__)

# Setup logging to stdout (Render terminal)
gunicorn_error_logger = logging.getLogger('gunicorn.error')
app.logger.handlers.extend(gunicorn_error_logger.handlers)
app.logger.setLevel(logging.DEBUG)

# Mock data storage
recent_swaps = []
in_coins = {
    "BAN": {"fee": 0, "name": "Banano"},
    "XNO": {"fee": 0, "name": "Nano"}
}

out_coins = {
    "BAN": {"fee": 0, "name": "Banano"},
    "XNO": {"fee": 0, "name": "Nano"}
}

# CoinGecko API base URL
COINGECKO_BASE_URL = 'https://api.coingecko.com/api/v3'

# Function to fetch USD value from CoinGecko
def fetch_usd_value(coin):
    url = f"{COINGECKO_BASE_URL}/simple/price"
    params = {
        'ids': coin,
        'vs_currencies': 'usd'
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        
        # Check if the coin exists in data and 'usd' value is present
        if coin in data and 'usd' in data[coin]:
            return data[coin]['usd']
        else:
            raise ValueError(f"USD value not found for {coin}")
    
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request to CoinGecko API failed: {e}")
        return None
    except ValueError as ve:
        app.logger.error(f"Invalid response from CoinGecko API: {ve}")
        return None

# Function to calculate adjusted exchange rate with fee
def calculate_adjusted_rate(from_coin, to_coin):
    in_usd = fetch_usd_value(from_coin)
    out_usd = fetch_usd_value(to_coin)
    
    if in_usd and out_usd:
        rate = out_usd / in_usd
        fee_adjusted_rate = rate * 1.01  # Adding 1% fee
        return fee_adjusted_rate
    return None

# Endpoint to fetch exchange rate with fee adjustment
@app.route('/rates/<string:from_coin>', methods=['GET'])
def get_exchange_rate(from_coin):
    to_coin = request.args.get('to_coin')
    adjusted_rate = calculate_adjusted_rate(from_coin, to_coin)
    if adjusted_rate:
        return jsonify({"result": adjusted_rate})
    else:
        return jsonify({"error": "Exchange rate not found"}), 404

# Endpoint to fetch recent swaps
@app.route('/recent_swaps', methods=['GET'])
def get_recent_swaps():
    return jsonify({"result": recent_swaps})

# Endpoint to create a new swap
@app.route('/create_swap', methods=['GET'])
def create_swap():
    from_coin = request.args.get('from')
    to_coin = request.args.get('to')
    address = request.args.get('address')
    # Simulate creation of swap
    swap_id = int(time.time())  # Use timestamp as swap ID
    new_swap = {
        "id": swap_id,
        "from_coin": from_coin,
        "to_coin": to_coin,
        "address": address,
        "time": int(time.time())
    }
    recent_swaps.append(new_swap)
    return jsonify({"success": True, "result": {"id": swap_id}})

# Endpoint to check swap status
@app.route('/swap_status', methods=['GET'])
def check_swap_status():
    swap_id = request.args.get('id')
    for swap in recent_swaps:
        if swap['id'] == int(swap_id):
            # Simulate different statuses for demonstration
            if time.time() - swap['time'] < 10:
                status = "wait"
            elif time.time() - swap['time'] < 20:
                status = "sending"
            else:
                status = "finished"
                swap['status'] = status  # Update status in data
                swap['txid'] = "fake_txid_12345"  # Simulated transaction ID
                swap['link'] = f"https://example.com/tx/{swap['txid']}"
            return jsonify({"success": True, "result": swap})
    return jsonify({"error": "Swap not found"}), 404

# Endpoint to fetch available in_coins
@app.route('/in_coins', methods=['GET'])
def get_in_coins():
    return jsonify(in_coins)

# Endpoint to fetch available out_coins
@app.route('/out_coins', methods=['GET'])
def get_out_coins():
    return jsonify(out_coins)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)

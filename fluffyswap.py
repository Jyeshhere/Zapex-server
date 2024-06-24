from flask import Flask, jsonify, request
import requests
import time

COINGECKO_API_KEY = 'CG-Vro2bYPZhJtmf6fBnPGu1uNp'

app = Flask(__name__)

# Mock data storage
in_coins = {
    "BAN": {"fee": 0, "name": "Banano"},
    "XNO": {"fee": 0, "name": "Nano"}
}

out_coins = {
    "BAN": {"fee": 0, "name": "Banano"},
    "XNO": {"fee": 0, "name": "Nano"}
}

# Mapping from tickers to CoinGecko IDs
coin_id_map = {
    "BAN": "banano",
    "XNO": "nano"
}

# CoinGecko API base URL
COINGECKO_BASE_URL = 'https://api.coingecko.com/api/v3'

# Function to fetch USD value from CoinGecko using API key
def fetch_usd_value(coin):
    if coin in coin_id_map:
        coin_id = coin_id_map[coin]
    else:
        return None
    
    url = f"{COINGECKO_BASE_URL}/simple/price"
    params = {
        'ids': coin_id,
        'vs_currencies': 'usd'
    }
    headers = {
        'Authorization': f'Bearer {COINGECKO_API_KEY}'
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        data = response.json()
        
        # Check if the coin ID exists in data and 'usd' value is present
        if coin_id in data and 'usd' in data[coin_id]:
            usd_value = data[coin_id]['usd']
            return usd_value
        else:
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Request to CoinGecko API failed: {e}")
        return None
    except ValueError as e:
        print(f"Error parsing response from CoinGecko API: {e}")
        return None

# Function to calculate adjusted exchange rate with fee
def calculate_adjusted_rate(from_coin, to_coin):
    in_usd = fetch_usd_value(from_coin)
    out_usd = fetch_usd_value(to_coin)
    
    if in_usd and out_usd:
        rate = in_usd / out_usd  
        fee_adjusted_rate = rate * 0.99  # Deducting 1% fee
        return fee_adjusted_rate
    return None

# Endpoint to fetch exchange rate with fee adjustment
@app.route('/rates/<string:from_coin>', methods=['GET'])
def get_exchange_rate(from_coin):
    to_coin = request.args.get('to_coin')
    if to_coin is None:
        return jsonify({"error": "'to_coin' parameter is required"}), 400
    
    adjusted_rate = calculate_adjusted_rate(from_coin, to_coin)
    if adjusted_rate is not None:
        return jsonify({"result": adjusted_rate, "success": True})
    else:
        return jsonify({"result": 0, "success": False})

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
    
    try:
        if not from_coin or not to_coin or not address:
            return jsonify({"error": "Missing required parameters"}), 400
        
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
    
    except Exception as e:
        return jsonify({"error": f"Error creating swap: {str(e)}"}), 500

# Endpoint to check swap status
@app.route('/swap_status', methods=['GET'])
def check_swap_status():
    swap_id = request.args.get('id')
    
    try:
        if not swap_id:
            return jsonify({"error": "'id' parameter is required"}), 400
        
        for swap in recent_swaps:
            if swap['id'] == int(swap_id):
                # Simulate different statuses for demonstration
                if time.time() - swap['time'] < 10:
                    status = "wait"
                elif time.time() - swap['time'] < 20:
                    status = "sending"
                else:
         

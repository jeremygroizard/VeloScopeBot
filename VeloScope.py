import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import threading

# Configuration
token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("CHAT_ID")
headers = {
    'X-CMC_PRO_API_KEY': os.getenv("CMC_API_KEY"),
    'Accepts': 'application/json'
}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"VeloScope Bot is running")

def get_velo_price():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest?symbol=VELO"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        if 'data' in data and 'VELO' in data['data']:
            price = data['data']['VELO']['quote']['USD']['price']
            return price
        else:
            raise ValueError("Invalid response structure")
    except (requests.RequestException, ValueError) as e:
        print(f"Error fetching VELO price: {e}")
        return None

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)

sell_levels = [
    (0.0545, 5000),
    (0.1090, 5000),
    (0.2180, 7500),
    (0.3270, 7500),
    (0.4360, 7500),
    (0.5450, 10000),
    (0.6540, 10000),
    (0.7630, 10000),
    (0.8720, 10000),
    (0.9810, 10000),
    (1.0900, 27691),
    (0.010, None),
    (0.011, None),
    (0.012, None),
]

def check_prices():
    current_price = get_velo_price()
    if current_price is not None:
        for level, tokens in sell_levels:
            if current_price >= level:
                if tokens is None:
                    message = f"[TEST] Le prix a atteint {level} $."
                else:
                    message = f"Le prix a atteint {level} $. Vendez {tokens} tokens."
                send_telegram_alert(message)
                sell_levels.remove((level, tokens))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('', port), Handler)
    print(f"Starting server on port {port}")

    def bot_loop():
        while True:
            check_prices()
            time.sleep(60)

    threading.Thread(target=bot_loop, daemon=True).start()

    server.serve_forever()


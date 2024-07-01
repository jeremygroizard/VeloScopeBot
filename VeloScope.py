import requests
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import os

# Configuration
token = "YOUR_TELEGRAM_BOT_TOKEN"
chat_id = "YOUR_CHAT_ID"
headers = {
    'X-CMC_PRO_API_KEY': 'YOUR_CMC_API_KEY',
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
    response = requests.get(url, headers=headers)
    data = response.json()
    price = data['data']['VELO']['quote']['USD']['price']
    return price

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}
    requests.post(url, data=data)

# Paliers de vente originaux + paliers de test
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
    # Paliers de test
    (0.010, None),  # Palier de test à 0.010 USD
    (0.011, None),  # Palier de test à 0.011 USD
    (0.012, None),  # Palier de test à 0.012 USD
]

def check_prices():
    current_price = get_velo_price()
    for level, tokens in sell_levels:
        if current_price >= level:
            if tokens is None:
                message = f"[TEST] Le prix a atteint {level} $."
            else:
                message = f"Le prix a atteint {level} $. Vendez {tokens} tokens."
            send_telegram_alert(message)
            sell_levels.remove((level, tokens))

if __name__ == "__main__":
    # Démarrer le serveur HTTP pour répondre aux vérifications de l'état
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(('', port), Handler)
    print(f"Starting server on port {port}")
    
    # Lancer une boucle séparée pour le bot
    import threading
    def bot_loop():
        while True:
            check_prices()
            time.sleep(60)  # Vérifie toutes les minutes

    threading.Thread(target=bot_loop, daemon=True).start()
    
    # Exécuter le serveur HTTP
    server.serve_forever()

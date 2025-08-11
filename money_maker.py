from datetime import datetime, timedelta
import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

FINNHUB_API_KEY = "d2ciht1r01qihtcrvj8gd2ciht1r01qihtcrvj90"

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

ALPACA_API_KEY = "PK2JRJ6VZGXNXP9BKTLA"
ALPACA_API_SECRET = "fjjqI4YbHMonpTcd4SfWtbXAwy7KlqnZxvsmQ7UA"

client = TradingClient(ALPACA_API_KEY, ALPACA_API_SECRET, paper=True)

SYMBOLS = [
    "AAPL",
    "MSFT",
    "AMZN",
    "GOOG",
    "GOOGL",
    "META",
    "TSLA",
    "BRK.B",
    "JPM",
    "V",
    "JNJ",
    "WMT",
    "NVDA",
    "DIS",
    "PG",
    "MA",
    "NFLX",
    "UNH",
    "HD",
    "PYPL"
]  

def get_news(symbol, from_date, to_date):
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Błąd pobierania danych:", response.status_code)
        return []

def analyze_sentiment(texts):
    analyzer = SentimentIntensityAnalyzer()
    scores = []
    for text in texts:
        vs = analyzer.polarity_scores(text)
        scores.append(vs['compound'])
    if scores:
        return sum(scores) / len(scores)
    else:
        return 0

def handle_order(sym, sentiment):
    if sentiment > 0.13:
        print(f"kupuje {sym}")
        try:
            order = MarketOrderRequest(
                symbol = sym,
                qty = 4,
                side = OrderSide.BUY,
                time_in_force = TimeInForce.DAY
            )
            client.submit_order(order)
        except Exception as e:
            print(f"Błąd alpaca api dla kupna {sym}: {e}")

    elif sentiment < -0.1:
        print(f"sprzedaje {sym}")
        try:
            order = MarketOrderRequest(
                symbol = sym,
                qty = 4,
                side = OrderSide.SELL,
                time_in_force = TimeInForce.DAY
            )
            client.submit_order(order)
        except Exception as e:
            print(f"Błąd alpaca api dla sprzedazy {sym}: {e}")

    else:
        print(f"trzymam {sym}")

if __name__ == "__main__":
    try:
        client.close_all_positions(cancel_orders=True)
        print("Zamknięto każda aktywną pozycje!")
    except Exception as e:
        print(f"Błąd alpaca api dla zamknięcia każdej pozycji: {e}")

    today = datetime.now().date()
    week_ago = today - timedelta(days=7)  

    print(f"Na bazie wiadomości od {today} do {week_ago}")

    for sym in SYMBOLS:
        news = get_news(sym, week_ago, today)
        headlines = [item['headline'] for item in news[:50]]  # 20 najnowszych wiadomości

        avg_sentiment = analyze_sentiment(headlines)

        #print(headlines)
        print(f"Średni sentyment dla {sym}: {avg_sentiment:.3f}")

        handle_order(sym, avg_sentiment)
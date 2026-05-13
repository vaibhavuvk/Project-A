from SmartApi import SmartConnect
from datetime import datetime
import pandas as pd
import requests
import time

# =========================
# LOGIN DETAILS
# =========================

API_KEY = "MGDISyWm"
CLIENT_ID = "V166639"
PASSWORD = "8600"

# =========================
# TELEGRAM SETTINGS
# =========================

BOT_TOKEN = "8849204178:AAEmbVLc26vBnlLT8Zo2GUk7ieRZIVZzjLI"

CHAT_ID = "109801899"


# =========================
# STOCK LIST
# =========================

stocks = [

    {"symbol": "SBIN-EQ", "token": "3045"},

    {"symbol": "RELIANCE-EQ", "token": "2885"},

    {"symbol": "HDFCBANK-EQ", "token": "1333"},

    {"symbol": "INFY-EQ", "token": "1594"},

    {"symbol": "TCS-EQ", "token": "11536"}

]

# =========================
# LOGIN
# =========================

totp = input("Enter OTP: ")

smartApi = SmartConnect(api_key=API_KEY)

session = smartApi.generateSession(

    CLIENT_ID,

    PASSWORD,

    totp
)

print("Login Success")

# =========================
# TELEGRAM FUNCTION
# =========================

def send_telegram(message):

    try:

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        data = {

            "chat_id": CHAT_ID,

            "text": message
        }

        requests.post(url, data=data)

    except Exception as e:

        print("Telegram Error:", e)

# =========================
# PRICE STORAGE
# =========================

price_history = {}

# =========================
# MAIN LOOP
# =========================

while True:

    try:

        print("\n==============================")

        print("SCAN TIME:", datetime.now())

        print("==============================")

        output = []

        ranking = []

        for stock in stocks:

            symbol = stock["symbol"]

            token = stock["token"]

            # =========================
            # LIVE PRICE
            # =========================

            ltpData = smartApi.ltpData(

                "NSE",

                symbol,

                token
            )

            ltp = ltpData["data"]["ltp"]

            # =========================
            # STORE PRICE
            # =========================

            if symbol not in price_history:

                price_history[symbol] = []

            price_history[symbol].append(ltp)

            # Keep last 50 prices

            if len(price_history[symbol]) > 50:

                price_history[symbol].pop(0)

            prices = price_history[symbol]

            # =========================
            # DATAFRAME
            # =========================

            df = pd.DataFrame(

                prices,

                columns=["close"]
            )

            # =========================
            # EMA
            # =========================

            ema9 = round(

                df["close"].ewm(span=9).mean().iloc[-1],

                2
            )

            ema20 = round(

                df["close"].ewm(span=20).mean().iloc[-1],

                2
            )

            # =========================
            # RSI
            # =========================

            delta = df["close"].diff()

            gain = delta.where(delta > 0, 0)

            loss = -delta.where(delta < 0, 0)

            avg_gain = gain.rolling(14).mean()

            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss

            rsi = 100 - (100 / (1 + rs))

            rsi_value = round(

                rsi.iloc[-1],

                2
            )

            # =========================
            # SIGNAL FILTER
            # =========================

            signal = "WAIT"

            strength = "WEAK"

            # STRONG BUY

            if ema9 > ema20 and rsi_value > 60:

                signal = "BUY"

                strength = "STRONG"

            # NORMAL BUY

            elif ema9 > ema20 and rsi_value > 50:

                signal = "BUY"

                strength = "NORMAL"

            # STRONG SELL

            elif ema20 > ema9 and rsi_value < 40:

                signal = "SELL"

                strength = "STRONG"

            # NORMAL SELL

            elif ema20 > ema9 and rsi_value < 50:

                signal = "SELL"

                strength = "NORMAL"

            # =========================
            # AI SCORE
            # =========================

            score = 0

            if signal == "BUY":

                score += 50

            if strength == "STRONG":

                score += 30

            if rsi_value > 60:

                score += 20

            if rsi_value > 70:

                score += 10

            # =========================
            # PRINT
            # =========================

            print(

                symbol,

                "| LTP:", ltp,

                "| EMA9:", ema9,

                "| EMA20:", ema20,

                "| RSI:", rsi_value,

                "| SIGNAL:", signal,

                "| STRENGTH:", strength,

                "| SCORE:", score
            )

            # =========================
            # TELEGRAM ALERT
            # =========================

            if signal != "WAIT":

                telegram_msg = f"""
{signal} SIGNAL

STOCK: {symbol}

PRICE: {ltp}

EMA9: {ema9}

EMA20: {ema20}

RSI: {rsi_value}

STRENGTH: {strength}

SCORE: {score}

TIME: {datetime.now()}
"""

                send_telegram(telegram_msg)

            # =========================
            # STORE RANKING
            # =========================

            ranking.append({

                "STOCK": symbol,

                "LTP": ltp,

                "EMA9": ema9,

                "EMA20": ema20,

                "RSI": rsi_value,

                "SIGNAL": signal,

                "STRENGTH": strength,

                "SCORE": score
            })

            # =========================
            # SAVE DATA
            # =========================

            output.append({

                "TIME": str(datetime.now()),

                "STOCK": symbol,

                "LTP": ltp,

                "EMA9": ema9,

                "EMA20": ema20,

                "RSI": rsi_value,

                "SIGNAL": signal,

                "STRENGTH": strength,

                "SCORE": score
            })

        # =========================
        # TOP 3 AI RANKING
        # =========================

        ranking_df = pd.DataFrame(ranking)

        ranking_df = ranking_df.sort_values(

            by="SCORE",

            ascending=False
        )

        top3 = ranking_df.head(3)

        print("\n==============================")

        print("TOP 3 STRONGEST STOCKS")

        print("==============================")

        print(top3)

        # =========================
        # TELEGRAM TOP 3
        # =========================

        top_msg = "\nTOP 3 STRONGEST STOCKS\n\n"

        for index, row in top3.iterrows():

            top_msg += f"""
{row['STOCK']}

SIGNAL: {row['SIGNAL']}

STRENGTH: {row['STRENGTH']}

RSI: {row['RSI']}

SCORE: {row['SCORE']}

-------------------
"""

        send_telegram(top_msg)

        # =========================
        # SAVE EXCEL
        # =========================

        excel_df = pd.DataFrame(output)

        excel_df.to_excel(

            "multi_stock_signals.xlsx",

            index=False
        )

        print("\nExcel Updated")

        # =========================
        # WAIT
        # =========================

        time.sleep(10)

    except Exception as e:

        print("ERROR:", e)

        time.sleep(5)
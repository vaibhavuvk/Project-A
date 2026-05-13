from SmartApi import SmartConnect
import pandas as pd
from datetime import datetime
import time
import os

API_KEY = "MGDISyWm"
CLIENT_ID = "V166639"
PASSWORD = "8600"

TOTP = input("Enter OTP: ")

# LOGIN
smartApi = SmartConnect(api_key=API_KEY)

session = smartApi.generateSession(
    CLIENT_ID,
    PASSWORD,
    TOTP
)

print("Login Successful")

excel_file = "ProjectA_Trade_Engine.xlsx"

price_list = []

while True:

    try:

        # ======================
        # LIVE DATA
        # ======================

        nifty = smartApi.ltpData(
            "NSE",
            "NIFTY",
            "99926000"
        )

        data = nifty["data"]

        nifty_ltp = data["ltp"]
        nifty_high = data["high"]
        nifty_low = data["low"]
        nifty_close = data["close"]

        # STORE PRICES
        price_list.append(nifty_ltp)

        price_list = price_list[-100:]

        signal = "WAIT"

        ema9 = 0
        ema20 = 0
        rsi = 0
        vwap = 0

        entry = 0
        stoploss = 0
        target = 0

        # ======================
        # CALCULATIONS
        # ======================

        if len(price_list) >= 20:

            df = pd.DataFrame(price_list, columns=["close"])

            # EMA
            df["EMA9"] = df["close"].ewm(
                span=9,
                adjust=False
            ).mean()

            df["EMA20"] = df["close"].ewm(
                span=20,
                adjust=False
            ).mean()

            ema9 = round(df["EMA9"].iloc[-1], 2)

            ema20 = round(df["EMA20"].iloc[-1], 2)

            # RSI
            delta = df["close"].diff()

            gain = delta.where(delta > 0, 0)

            loss = -delta.where(delta < 0, 0)

            avg_gain = gain.rolling(14).mean()

            avg_loss = loss.rolling(14).mean()

            rs = avg_gain / avg_loss

            df["RSI"] = 100 - (100 / (1 + rs))

            rsi = round(df["RSI"].iloc[-1], 2)

            # VWAP
            typical_price = (
                nifty_high +
                nifty_low +
                nifty_close
            ) / 3

            vwap = round(typical_price, 2)

            # ======================
            # TRADE ENGINE
            # ======================

            # BUY
            if (
                ema9 > ema20 and
                rsi > 50 and
                nifty_ltp > vwap
            ):

                signal = "STRONG BUY"

                entry = nifty_ltp
                stoploss = nifty_ltp - 50
                target = nifty_ltp + 100

            # SELL
            elif (
                ema9 < ema20 and
                rsi < 50 and
                nifty_ltp < vwap
            ):

                signal = "STRONG SELL"

                entry = nifty_ltp
                stoploss = nifty_ltp + 50
                target = nifty_ltp - 100

            else:

                signal = "SIDEWAYS"

        print(
            datetime.now(),
            "NIFTY:", nifty_ltp,
            "EMA9:", ema9,
            "EMA20:", ema20,
            "RSI:", rsi,
            "VWAP:", vwap,
            "SIGNAL:", signal,
            "ENTRY:", entry,
            "SL:", stoploss,
            "TARGET:", target
        )

        # ======================
        # SAVE EXCEL
        # ======================

        new_data = pd.DataFrame([{
            "Time": datetime.now(),
            "NIFTY": nifty_ltp,
            "EMA9": ema9,
            "EMA20": ema20,
            "RSI": rsi,
            "VWAP": vwap,
            "SIGNAL": signal,
            "ENTRY": entry,
            "STOPLOSS": stoploss,
            "TARGET": target
        }])

        if os.path.exists(excel_file):

            old_data = pd.read_excel(excel_file)

            updated_data = pd.concat(
                [old_data, new_data],
                ignore_index=True
            )

        else:
            updated_data = new_data

        updated_data.to_excel(excel_file, index=False)

        print("Excel Updated")

    except Exception as e:

        print("Error:", e)

    time.sleep(5)
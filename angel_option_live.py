from SmartApi import SmartConnect
import pandas as pd
from datetime import datetime
import time
import os

# =========================
# LOGIN DETAILS
# =========================

API_KEY = "MGDISyWm"
CLIENT_ID = "V166639"
PASSWORD = "8600"

TOTP = input("Enter OTP: ")

# =========================
# LOGIN
# =========================

smartApi = SmartConnect(api_key=API_KEY)

session = smartApi.generateSession(
    CLIENT_ID,
    PASSWORD,
    TOTP
)

print("Login Successful")

excel_file = "Live_Option_Chain.xlsx"

while True:

    try:

        # =========================
        # LIVE NIFTY
        # =========================

        nifty = smartApi.ltpData(
            "NSE",
            "NIFTY",
            "99926000"
        )

        nifty_ltp = nifty["data"]["ltp"]

        # =========================
        # ATM STRIKE
        # =========================

        atm = round(nifty_ltp / 50) * 50

        print("\nNIFTY:", nifty_ltp)
        print("ATM STRIKE:", atm)

        # =========================
        # SAMPLE OPTION SYMBOLS
        # =========================

        ce_symbol = f"NIFTY15MAY25{atm}CE"
        pe_symbol = f"NIFTY15MAY25{atm}PE"

        print("CE SYMBOL:", ce_symbol)
        print("PE SYMBOL:", pe_symbol)

        # =========================
        # SAVE EXCEL
        # =========================

        df = pd.DataFrame([{
            "Time": datetime.now(),
            "NIFTY": nifty_ltp,
            "ATM": atm,
            "CE_SYMBOL": ce_symbol,
            "PE_SYMBOL": pe_symbol
        }])

        if os.path.exists(excel_file):

            old = pd.read_excel(excel_file)

            updated = pd.concat(
                [old, df],
                ignore_index=True
            )

        else:

            updated = df

        updated.to_excel(
            excel_file,
            index=False
        )

        print("Excel Updated")

    except Exception as e:

        print("Error:", e)

    time.sleep(5)
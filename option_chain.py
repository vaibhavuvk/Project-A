import requests
import pandas as pd
from datetime import datetime
import time
import os
import json

excel_file = "OptionChain_Data.xlsx"

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "application/json,text/html"
}

session = requests.Session()

# OPEN NSE FIRST
session.get("https://www.nseindia.com", headers=headers)

while True:

    try:

        url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

        response = session.get(url, headers=headers)

        print("STATUS CODE:", response.status_code)

        data = response.json()

        # SHOW TOP KEYS
        print("TOP LEVEL KEYS:", data.keys())

        # CHECK IF RECORDS EXISTS
        if "records" not in data:

            print("FULL RESPONSE:")
            print(json.dumps(data, indent=2))

            time.sleep(10)
            continue

        records = data["records"]["data"]

        nifty_value = data["records"]["underlyingValue"]

        atm = round(nifty_value / 50) * 50

        ce_oi = 0
        pe_oi = 0

        for item in records:

            if item["strikePrice"] == atm:

                if "CE" in item:
                    ce_oi = item["CE"]["openInterest"]

                if "PE" in item:
                    pe_oi = item["PE"]["openInterest"]

        if ce_oi != 0:
            pcr = round(pe_oi / ce_oi, 2)
        else:
            pcr = 0

        signal = "SIDEWAYS"

        if pcr > 1.2:
            signal = "BULLISH"

        elif pcr < 0.8:
            signal = "BEARISH"

        print(
            datetime.now(),
            "NIFTY:", nifty_value,
            "ATM:", atm,
            "PCR:", pcr,
            "SIGNAL:", signal
        )

        new_data = pd.DataFrame([{
            "Time": datetime.now(),
            "NIFTY": nifty_value,
            "ATM": atm,
            "CE_OI": ce_oi,
            "PE_OI": pe_oi,
            "PCR": pcr,
            "SIGNAL": signal
        }])

        if os.path.exists(excel_file):

            old = pd.read_excel(excel_file)

            updated = pd.concat(
                [old, new_data],
                ignore_index=True
            )

        else:
            updated = new_data

        updated.to_excel(excel_file, index=False)

        print("Excel Updated")

    except Exception as e:

        print("Error:", e)

    time.sleep(10)
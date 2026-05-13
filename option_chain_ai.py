import requests
import pandas as pd
from datetime import datetime
import time

session = requests.Session()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "accept-language": "en-US,en;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept": "*/*"
}

# =========================
# GET NSE COOKIES
# =========================

session.get(
    "https://www.nseindia.com",
    headers=headers,
    timeout=10
)

time.sleep(2)

# =========================
# OPTION CHAIN API
# =========================

url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"

response = session.get(
    url,
    headers=headers,
    timeout=10
)

print("STATUS CODE:", response.status_code)

data = response.json()

print("TOP LEVEL KEYS:", data.keys())

# =========================
# SAFETY CHECK
# =========================

if "records" not in data:

    print("\nNSE blocked request temporarily.")
    print("Try again after 10 seconds.")

    exit()

records = data["records"]["data"]

ce_oi = {}
pe_oi = {}

# =========================
# EXTRACT OI
# =========================

for item in records:

    strike = item["strikePrice"]

    if "CE" in item:

        ce_oi[strike] = item["CE"]["openInterest"]

    if "PE" in item:

        pe_oi[strike] = item["PE"]["openInterest"]

# =========================
# SUPPORT / RESISTANCE
# =========================

max_ce_strike = max(
    ce_oi,
    key=ce_oi.get
)

max_pe_strike = max(
    pe_oi,
    key=pe_oi.get
)

max_ce_oi = ce_oi[max_ce_strike]

max_pe_oi = pe_oi[max_pe_strike]

# =========================
# PCR
# =========================

total_ce = sum(ce_oi.values())

total_pe = sum(pe_oi.values())

pcr = round(total_pe / total_ce, 2)

# =========================
# MARKET SIGNAL
# =========================

signal = "SIDEWAYS"

if pcr > 1:
    signal = "BULLISH"

elif pcr < 1:
    signal = "BEARISH"

# =========================
# DISPLAY
# =========================

print("\n========== OPTION CHAIN AI ==========\n")

print("TIME:", datetime.now())

print("\nRESISTANCE:", max_ce_strike)
print("CALL OI:", max_ce_oi)

print("\nSUPPORT:", max_pe_strike)
print("PUT OI:", max_pe_oi)

print("\nPCR:", pcr)

print("\nMARKET VIEW:", signal)

# =========================
# SAVE EXCEL
# =========================

df = pd.DataFrame([{
    "Time": datetime.now(),
    "Resistance": max_ce_strike,
    "Call_OI": max_ce_oi,
    "Support": max_pe_strike,
    "Put_OI": max_pe_oi,
    "PCR": pcr,
    "Signal": signal
}])

df.to_excel(
    "Option_Chain_AI.xlsx",
    index=False
)

print("\nExcel Saved")
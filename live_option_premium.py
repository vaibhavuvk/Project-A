from SmartApi import SmartConnect
from datetime import datetime
import pandas as pd
import requests
import time
import pyotp
import os

# =========================
# SECURE RAILWAY VARIABLES
# =========================

API_KEY = os.getenv("API_KEY")
CLIENT_ID = os.getenv("CLIENT_ID")
PASSWORD = os.getenv("PASSWORD")
TOTP_SECRET = os.getenv("TOTP_SECRET")

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# =========================
# AUTO OTP
# =========================

totp = pyotp.TOTP(TOTP_SECRET).now()

# =========================
# LOGIN
# =========================

try:

    smartApi = SmartConnect(api_key=API_KEY)

    session = smartApi.generateSession(
        CLIENT_ID,
        PASSWORD,
        totp
    )

    print("Login Success")

except Exception as e:

    print("Login Failed:", e)
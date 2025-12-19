import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# ---------------- PAGE ----------------
st.set_page_config(layout="wide")
st.title("📘 SmartTradeX — BTC Live Order Book")

st_autorefresh(interval=1500, key="refresh")

# ---------------- STYLE ----------------
st.markdown("""
<style>
body { background-color:#0e1117; }
table { font-size:13px; }
th, td { text-align:right !important; padding:4px 8px !important; }
.mid-price {
    font-size:22px;
    font-weight:bold;
    text-align:center;
    padding:10px;
}
.sell { color:#f6465d; }
.buy { color:#0ecb81; }
</style>
""", unsafe_allow_html=True)

# ---------------- FETCH DATA (SAFE) ----------------
BINANCE_URL = "https://api.binance.com/api/v3/depth"
PARAMS = {"symbol": "BTCUSDT", "limit": 15}
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

bids, asks = [], []

try:
    r = requests.get(
        BINANCE_URL,
        params=PARAMS,
        headers=HEADERS,
        timeout=5
    )
    r.raise_for_status()
    data = r.json()
    bids = data.get("bids", [])
    asks = data.get("asks", [])
except Exception as e:
    st.error("Binance API not responding. Retrying automatically…")

# ---------------- PREPARE DATA ----------------
def prepare_df(data, reverse=False):
    df = pd.DataFrame(data, columns=["price", "qty"]).astype(float)
    df["total"] = df["price"] * df["qty"]
    if reverse:
        df = df.iloc[::-1]
    return df

# ---------------- UI ----------------
if bids and asks:
    asks_df = prepare_df(asks, reverse=True)   # Sell on top
    bids_df = prepare_df(bids)                 # Buy bottom

    # SELL
    st.markdown("### 🔴 Sell Orders")
    st.markdown(
        asks_df.style
        .format({"price":"{:,.2f}", "qty":"{:.5f}", "total":"{:,.2f}"})
        .background_gradient(subset=["total"], cmap="Reds")
        .to_html(),
        unsafe_allow_html=True
    )

    # MID PRICE
    mid = (float(bids[0][0]) + float(asks[0][0])) / 2
    st.markdown(
        f'<div class="mid-price">{mid:,.2f}</div>',
        unsafe_allow_html=True
    )

    # BUY
    st.markdown("### 🟢 Buy Orders")
    st.markdown(
        bids_df.style
        .format({"price":"{:,.2f}", "qty":"{:.5f}", "total":"{:,.2f}"})
        .background_gradient(subset=["total"], cmap="Greens")
        .to_html(),
        unsafe_allow_html=True
    )

else:
    st.warning("Fetching live order book from Binance… please wait 1–2 seconds")

st.caption("SmartTradeX | Live Binance BTC Order Book (Read-Only)")

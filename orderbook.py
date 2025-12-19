import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SmartTradeX Order Book",
    layout="centered"
)

st.title("📘 SmartTradeX — BTC Live Order Book")

# Auto refresh every 2 seconds
st_autorefresh(interval=2000, key="refresh")

# ---------------- STYLE ----------------
st.markdown("""
<style>
body {
    background-color:#0e1117;
}
table {
    font-size:13px;
    width:100%;
}
th, td {
    text-align:right !important;
    padding:4px 8px !important;
}
.sell {
    color:#f6465d;
}
.buy {
    color:#0ecb81;
}
.mid {
    font-size:22px;
    font-weight:bold;
    text-align:center;
    margin:10px 0;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DATA SOURCE (COINBASE) ----------------
COINBASE_URL = "https://api.exchange.coinbase.com/products/BTC-USDT/book?level=2"
HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

bids, asks = [], []

try:
    r = requests.get(COINBASE_URL, headers=HEADERS, timeout=5)
    r.raise_for_status()
    data = r.json()

    # Coinbase format: [price, size, num-orders]
    bids = data["bids"][:10]
    asks = data["asks"][:10]

except Exception:
    st.error("Live order book source not responding. Please wait…")

# ---------------- DATA PREP ----------------
def prepare_df(data, reverse=False):
    clean = [[row[0], row[1]] for row in data]  # drop 3rd value
    df = pd.DataFrame(clean, columns=["price", "qty"]).astype(float)
    df["total"] = df["price"] * df["qty"]
    if reverse:
        df = df.iloc[::-1]
    return df

# ---------------- UI ----------------
if bids and asks:
    asks_df = prepare_df(asks, reverse=True)
    bids_df = prepare_df(bids)

    # SELL ORDERS (TOP)
    st.markdown("### 🔴 Sell Orders")
    st.markdown(
        asks_df.style
        .format({"price":"{:,.2f}", "qty":"{:.5f}", "total":"{:,.2f}"})
        .set_properties(**{"color": "#f6465d"})
        .to_html(),
        unsafe_allow_html=True
    )

    # MID PRICE
    mid_price = (float(bids[0][0]) + float(asks[0][0])) / 2
    st.markdown(f'<div class="mid">{mid_price:,.2f}</div>', unsafe_allow_html=True)

    # BUY ORDERS (BOTTOM)
    st.markdown("### 🟢 Buy Orders")
    st.markdown(
        bids_df.style
        .format({"price":"{:,.2f}", "qty":"{:.5f}", "total":"{:,.2f}"})
        .set_properties(**{"color": "#0ecb81"})
        .to_html(),
        unsafe_allow_html=True
    )

else:
    st.warning("Fetching live order book… please wait 1–2 seconds")

st.caption("SmartTradeX | Live BTC Order Book (Read-Only)")

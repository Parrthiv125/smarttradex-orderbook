import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# --------------------------------
# PAGE CONFIG
# --------------------------------
st.set_page_config(
    page_title="SmartTradeX Order Book",
    layout="wide"
)

st.title("📘 SmartTradeX — BTC Live Order Book")

# Auto refresh every 1 second
st_autorefresh(interval=1000, key="orderbook_refresh")

# --------------------------------
# DARK THEME + TABLE STYLE
# --------------------------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}
table {
    font-size: 14px;
}
th, td {
    text-align: right !important;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------
# FETCH LIVE ORDER BOOK (BINANCE)
# --------------------------------
BINANCE_URL = "https://api.binance.com/api/v3/depth"
params = {"symbol": "BTCUSDT", "limit": 10}

bids, asks = [], []

try:
    res = requests.get(BINANCE_URL, params=params, timeout=2)
    data = res.json()
    bids = data.get("bids", [])
    asks = data.get("asks", [])
except:
    st.error("Unable to fetch Binance data")

# --------------------------------
# STYLING FUNCTION
# --------------------------------
def style_orderbook(df, side="buy"):
    cmap = "Greens" if side == "buy" else "Reds"

    return (
        df.style
        .format({
            "Price (USDT)": "{:,.2f}",
            "Amount (BTC)": "{:.5f}",
            "Total (USDT)": "{:,.2f}",
            "Sum (USDT)": "{:,.2f}",
        })
        .background_gradient(subset=["Sum (USDT)"], cmap=cmap)
    )

# --------------------------------
# UI — SIDE BY SIDE ORDER BOOK
# --------------------------------
col_buy, col_sell = st.columns(2)

# ============ BUY SIDE ============
with col_buy:
    st.subheader("🟢 Buy Orders")

    if bids:
        buy_df = pd.DataFrame(bids, columns=["Price", "Amount"]).astype(float)
        buy_df["Total"] = buy_df["Price"] * buy_df["Amount"]
        buy_df["Sum"] = buy_df["Total"].cumsum()

        buy_df.columns = [
            "Price (USDT)",
            "Amount (BTC)",
            "Total (USDT)",
            "Sum (USDT)"
        ]

        st.markdown(
            style_orderbook(buy_df, "buy").to_html(),
            unsafe_allow_html=True
        )
    else:
        st.warning("Waiting for buy orders...")

# ============ SELL SIDE ============
with col_sell:
    st.subheader("🔴 Sell Orders")

    if asks:
        sell_df = pd.DataFrame(asks, columns=["Price", "Amount"]).astype(float)
        sell_df["Total"] = sell_df["Price"] * sell_df["Amount"]
        sell_df["Sum"] = sell_df["Total"].cumsum()

        sell_df.columns = [
            "Price (USDT)",
            "Amount (BTC)",
            "Total (USDT)",
            "Sum (USDT)"
        ]

        st.markdown(
            style_orderbook(sell_df, "sell").to_html(),
            unsafe_allow_html=True
        )
    else:
        st.warning("Waiting for sell orders...")

st.caption("SmartTradeX | Live Binance BTC Order Book (Read-Only)")

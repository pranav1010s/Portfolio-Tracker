import streamlit as st
import yfinance as yf
import pandas as pd

st.title("Portfolio Tracker")

# exchange price
USD_TO_GBP = 0.79
EUR_TO_GBP = 0.86

st.subheader("My Holdings")


default_stocks = pd.DataFrame({
    "Ticker": ["AAPL", "MSFT", "SHEL.L"],
    "Shares": [10.0, 5.0, 20.0],
    "Buy Price": [120.0, 210.0, 25.0]
})

if "portfolio" not in st.session_state:
    st.session_state.portfolio = default_stocks

portfolio = st.data_editor(st.session_state.portfolio, num_rows="dynamic")
st.session_state.portfolio = portfolio

st.button("Refresh")  # just triggers rerun

# get all tickers that have data
tickers = [t.strip().upper() for t in portfolio["Ticker"].tolist() if t and str(t).strip()]
tickers = [t for t in tickers if t]  # remove empties

if not tickers:
    st.info("Add some stocks!")
    st.stop()

data = yf.download(tickers, period="1mo", progress=False)

if len(tickers) == 1:
    closes = data["Close"].to_frame(tickers[0])
else:
    closes = data["Close"]

results = []
for _, row in portfolio.iterrows():
    ticker = str(row["Ticker"]).strip().upper()
    if ticker not in closes.columns:
        continue
    
    shares = row["Shares"] or 0
    paid = row["Buy Price"] or 0
    
    price = closes[ticker].dropna().iloc[-1]
    
   
    if ticker.endswith(".L"):
        price = price / 100
    
    # convert usd to gbp
    if not ticker.endswith(".L"):
        price = price * USD_TO_GBP
    
    value = price * shares
    cost = paid * shares
    gain = value - cost
    
    results.append({
        "ticker": ticker,
        "price": price,
        "value": value,
        "cost": cost,
        "gain": gain
    })

if not results:
    st.warning("couldn't get prices")
    st.stop()

df = pd.DataFrame(results)

st.divider()

total_val = df["value"].sum()
total_gain = df["gain"].sum()

col1, col2 = st.columns(2)
col1.metric("Total", f"£{total_val:,.0f}")
col2.metric("P/L", f"£{total_gain:+,.0f}")

st.divider()

# formatting
display = df.copy()
display["price"] = display["price"].apply(lambda x: f"£{x:.2f}")
display["value"] = display["value"].apply(lambda x: f"£{x:,.0f}")
display["cost"] = display["cost"].apply(lambda x: f"£{x:,.0f}")
display["gain"] = display["gain"].apply(lambda x: f"£{x:+,.0f}")
st.dataframe(display, hide_index=True)

# quick chart
st.subheader("Prices")
chart = closes.copy()
for col in chart.columns:
    if col.endswith(".L"):
        chart[col] = chart[col] / 100
    else:
        chart[col] = chart[col] * USD_TO_GBP
st.line_chart(chart)

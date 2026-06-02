import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="US Full Market Scanner", layout="wide")
st.title("🌌 US Market: Broad Market Rejection Scanner")
st.write("Ye scanner S&P 500 aur Nasdaq 100 ke saare stocks ko ek sath scan karta hai bina server crash kiye.")

# --- Step 1: Automatically Fetch S&P 500 & Nasdaq 100 Lists ---
@st.cache_data(ttl=86400)
def get_broad_market_tickers():
    try:
        # S&P 500
        sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        sp500_table = pd.read_html(sp500_url)[0]
        sp500_list = sp500_table['Symbol'].tolist()
        
        # Nasdaq 100
        nasdaq_url = "https://en.wikipedia.org/wiki/Nasdaq-100"
        nasdaq_table = pd.read_html(nasdaq_url)[4]
        nasdaq_list = nasdaq_table['Ticker'].tolist()
        
        # Merge & Clean
        full_list = list(set(sp500_list + nasdaq_list))
        full_list = [t.replace('.', '-') for t in full_list] # For yfinance compatibility
        return sorted(full_list)
    except Exception:
        # Fallback list if internet fails
        return ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AMD", "NFLX", "QCOM"]

all_tickers = get_broad_market_tickers()

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Scanner Settings")
st.sidebar.write(f"📊 **Total Broad Market Stocks Loaded:** {len(all_tickers)}")

timeframe_choice = st.sidebar.selectbox("Select Timeframe", ["Daily", "Weekly", "Monthly"])

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Pattern Sensitivity")
volume_multiplier = st.sidebar.slider("Volume Multiplier (vs 20 MA)", 1.5, 5.0, 2.3, step=0.1)
shadow_multiplier = st.sidebar.slider("Upper Wick vs Body Multiplier", 1.5, 5.0, 2.2, step=0.1)

tf_mapping = {
    "Daily": {"interval": "1d", "period": "2mo"},
    "Weekly": {"interval": "1wk", "period": "6mo"},
    "Monthly": {"interval": "1mo", "period": "2y"}
}
interval = tf_mapping[timeframe_choice]["interval"]
period = tf_mapping[timeframe_choice]["period"]

# --- Step 2: High-Speed Batch Scanner ---
if st.button("🚀 Run Broad Market Scan"):
    st.info(f"Scanning {len(all_tickers)} stocks in batches. Please wait...")
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    table_placeholder = st.empty()
    
    # 40-40 stocks ke batches mein download karenge taaki yfinance crash na ho
    batch_size = 40
    total_tickers = len(all_tickers)
    
    for i in range(0, total_tickers, batch_size):
        current_batch = all_tickers[i:i+batch_size]
        
        # Update progress
        progress_pct = min((i + batch_size) / total_tickers, 1.0)
        progress_bar.progress(progress_pct)
        status_text.text(f"Scanning batch {int(i/batch_size)+1}... (Stocks {i} to {min(i+batch_size, total_tickers)})")
        
        try:
            # Bulk download (Sabse fast tarika)
            data = yf.download(current_batch, period=period, interval=interval, group_by='ticker', progress=False)
            
            for ticker in current_batch:
                try:
                    # Single ticker extraction from multi-index dataframe
                    df = data[ticker] if len(current_batch) > 1 else data
                    df = df.dropna(subset=['Close']) # Drop empty rows
                    
                    if len(df) < 21:
                        continue
                        
                    # Latest candle math
                    open_p = float(df['Open'].iloc[-1])
                    high_p = float(df['High'].iloc[-1])
                    low_p = float(df['Low'].iloc[-1])
                    close_p = float(df['Close'].iloc[-1])
                    volume = float(df['Volume'].iloc[-1])
                    
                    # 20 Volume MA
                    vol_ma = df['Volume'].iloc[-21:-1].mean()
                    if vol_ma == 0: continue
                    
                    body = abs(close_p - open_p)
                    if body == 0: body = 0.001
                    
                    high_of_body = max(open_p, close_p)
                    low_of_body = min(open_p, close_p)
                    
                    upper_wick = high_p - high_of_body
                    total_range = high_p - low_p
                    if total_range == 0: continue
                    
                    # Strict filters matching your images
                    is_high_volume = volume > (vol_ma * volume_multiplier)
                    is_long_upper_wick = upper_wick > (body * shadow_multiplier)
                    is_price_rejected = (close_p < (low_p + (total_range * 0.45))) # Closed in bottom 45%
                    
                    if is_high_volume and is_long_upper_wick and is_price_rejected:
                        vol_increase_pct = ((volume - vol_ma) / vol_ma) * 100
                        wick_ratio = (upper_wick / total_range) * 100
                        
                        results.append({
                            "Ticker": ticker,
                            "Close Price": f"${close_p:.2f}",
                            "Wick % of Candle": f"{wick_ratio:.1f}%",
                            "Vol Surge %": f"+{vol_increase_pct:.1f}%",
                            "Volume": f"{int(volume):,}",
                            "Date": df.index[-1].strftime('%Y-%m-%d')
                        })
                        
                        # Live Update UI
                        live_df = pd.DataFrame(results)
                        table_placeholder.dataframe(live_df.set_index("Ticker"), use_container_width=True)
                except:
                    continue
        except:
            continue
            
        time.sleep(0.5) # Chhota sa anti-block pause
        
    status_text.success(f"Scan complete! Found {len(results)} stocks matching your pattern.")
    if not results:
        st.warning("Is waqt market mein is strict setting par koi stock nahi mila. Sliders ko thoda kam karke check karein.")

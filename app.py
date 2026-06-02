import streamlit as st
import yfinance as yf
import pandas as pd
import time

# Page configuration
st.set_page_config(page_title="Nasdaq Entire Market Scanner", layout="wide")
st.title("🌌 Nasdaq Entire Market (4000+ Stocks) Scanner")
st.write("Ye scanner pure NASDAQ market ke hazaron stocks ko batches mein scan karta hai bina crash kiye ya block hue.")

# --- Step 1: Fetch ENTIRE Nasdaq Ticker List Safely ---
@st.cache_data(ttl=86400) # Cache list for 24 hours
def get_all_nasdaq_tickers():
    try:
        # FTP server se live nasdaq listed stocks ki fresh text file fetch karna
        url = "https://raw.githubusercontent.com/rreichel3/US-Stock-Symbols/main/nasdaq/nasdaq_tickers.txt"
        tickers_df = pd.read_csv(url, header=None, names=['Ticker'])
        ticker_list = tickers_df['Ticker'].dropna().unique().tolist()
        # Clean clean symbols (remove warrants, test tickers, etc.)
        ticker_list = [str(t).strip().upper() for t in ticker_list if len(str(t).strip()) <= 4]
        return sorted(ticker_list)
    except Exception:
        # Fallback list agar internet issue ho
        return ["AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "TSLA", "AMD", "NFLX", "QCOM", "INTC", "CSCO"]

all_nasdaq_stocks = get_all_nasdaq_tickers()

# --- Sidebar Controls ---
st.sidebar.header("1. Scanner Controls")
st.sidebar.write(f"📊 **Total NASDAQ Tickers Found:** {len(all_nasdaq_stocks)}")

# Timeframe selection
timeframe_choice = st.sidebar.selectbox(
    "Select Timeframe",
    ["Daily", "Weekly", "Monthly"]
)

# Batch size controls to prevent crashes
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Stability Settings (Anti-Crash)")
batch_size = st.sidebar.slider("Batch Size (Per Request)", 20, 100, 50, help="Ek baar me kitne stocks ka data download hoga.")
pause_time = st.sidebar.slider("Rest Time between Batches (Seconds)", 1.0, 5.0, 2.0, help="Har batch ke baad script kitna break legi.")

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Pattern Sensitivity")
volume_multiplier = st.sidebar.slider("Volume Multiplier (vs 20 MA)", 1.5, 5.0, 2.5, step=0.1)
shadow_multiplier = st.sidebar.slider("Upper Wick vs Body Multiplier", 2.0, 6.0, 2.5, step=0.1)

# Timeframe configurations
tf_mapping = {
    "Daily": {"interval": "1d", "period": "3mo"},
    "Weekly": {"interval": "1wk", "period": "1y"},
    "Monthly": {"interval": "1mo", "period": "3y"}
}
interval = tf_mapping[timeframe_choice]["interval"]
period = tf_mapping[timeframe_choice]["period"]

# --- Step 2: Core Analysis Logic ---
def analyze_data(df, ticker, vol_mult, shadow_mult):
    try:
        if df.empty or len(df) < 21:
            return None
        
        # Latest Candle details
        open_p = float(df['Open'].iloc[-1])
        high_p = float(df['High'].iloc[-1])
        low_p = float(df['Low'].iloc[-1])
        close_p = float(df['Close'].iloc[-1])
        volume = float(df['Volume'].iloc[-1])
        
        # 20 Moving Average of Volume
        vol_ma = df['Volume'].iloc[-21:-1].mean()
        if vol_ma == 0: return None
        
        body = abs(close_p - open_p)
        if body == 0: body = 0.001
            
        high_of_body = max(open_p, close_p)
        low_of_body = min(open_p, close_p)
        
        upper_wick = high_p - high_of_body
        total_range = high_p - low_p
        if total_range == 0: return None
        
        # Pattern conditions logic
        is_high_volume = volume > (vol_ma * vol_mult)
        is_long_upper_wick = upper_wick > (body * shadow_mult)
        is_price_rejected = (close_p < (low_p + (total_range * 0.4))) # Close inside lower 40%
        
        if is_high_volume and is_long_upper_wick and is_price_rejected:
            vol_increase_pct = ((volume - vol_ma) / vol_ma) * 100
            wick_ratio = (upper_wick / total_range) * 100
            
            return {
                "Ticker": ticker,
                "Close Price": f"${close_p:.2f}",
                "Wick % of Candle": f"{wick_ratio:.1f}%",
                "Vol Surge %": f"+{vol_increase_pct:.1f}%",
                "Current Volume": f"{int(volume):,}",
                "Date Found": df.index[-1].strftime('%Y-%m-%d')
            }
    except:
        return None
    return None

# --- Step 3: Streamlit UI Trigger ---
if st.button("🚀 Start Nasdaq Entire Market Scan"):
    st.warning(f"⚠️ Heavy Scan Initialized! Hazaron stocks ko {batch_size}-{batch_size} ke groups me check kiya ja raha hai taaki script crash na ho. Isme thoda time lagega...")
    
    results = []
    
    # Progress UI Components
    progress_bar = st.progress(0)
    status_box = st.empty()
    table_placeholder = st.empty()
    
    # Chunks or Batches banana
    total_stocks = len(all_nasdaq_stocks)
    
    for i in range(0, total_stocks, batch_size):
        batch = all_nasdaq_stocks[i:i + batch_size]
        
        # Update Status
        current_progress = min((i + batch_size) / total_stocks, 1.0)
        progress_bar.progress(current_progress)
        status_box.info(f"Processing Batch {int(i/batch_size)+1}: Scanning stocks {i} to {min(i+batch_size, total_stocks)} of {total_stocks}...")
        
        # Batch download directly from yfinance (Group Download is much faster)
        try:
            # group_by='ticker' se saare stocks ek sath fast download hote hain
            data = yf.download(batch, period=period, interval=interval, group_by='ticker', progress=False)
            
            for ticker in batch:
                # Check matrix type single stock or multi-index
                try:
                    if len(batch) > 1:
                        ticker_df = data[ticker]
                    else:
                        ticker_df = data
                        
                    res = analyze_data(ticker_df, ticker, volume_multiplier, shadow_multiplier)
                    if res:
                        results.append(res)
                        # Live dashboard update: jaise hi koi mile turant screen par show karo
                        live_df = pd.DataFrame(results)
                        table_placeholder.dataframe(live_df.set_index("Ticker"), use_container_width=True)
                except:
                    continue # Koi ek stock error de toh baaki na rukein
                    
        except Exception as batch_error:
            # Agar poora batch fail ho jaye, toh script crash nahi hogi, agle batch par chali jayegi
            continue
            
        # ☕ Anti-crash cooling break (Sleep interval)
        time.sleep(pause_time)
        
    status_box.success(f"🎯 Scan Complete! Pure Nasdaq me total {len(results)} stocks mile hain.")
    
    if not results:
        st.error("Is waqt pure Nasdaq market me is specific criteria ka koi stock nahi mila. Try adjusting the sliders.")

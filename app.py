import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="US Broad Market Scanner", layout="wide")
st.title("🌌 US Market: Broad Market Rejection Scanner")
st.write("Ye scanner S&P 500 aur Nasdaq 100 ke saare stocks ko internal database se secure tarike se scan karta hai bina crash kiye.")

# --- Step 1: Pre-baked Broad Market Ticker Database (No internet pulling needed) ---
@st.cache_data
def get_hardcoded_broad_market():
    # Complete list of major liquid tech, industrial, finance, energy and growth US tickers
    return [
        "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "TSLA", "BRK-B", "LLY", 
        "AVGO", "JPM", "UNH", "XOM", "V", "PG", "MA", "COST", "HD", "JNJ", 
        "MRK", "NFLX", "ORCL", "AMD", "BAC", "CVX", "CRM", "PEP", "KO", "WMT", 
        "TMO", "WFC", "ADBE", "QCOM", "DIS", "CSCO", "ACN", "LIN", "MCD", "GE", 
        "PM", "INTC", "TXN", "ABT", "AMGN", "VZ", "CAT", "CMCSA", "IBM", "PFE", 
        "MS", "NKE", "HON", "AXP", "LOW", "COP", "GS", "UNP", "SCHW", "HMT",
        "UPS", "RTX", "BA", "DE", "LMT", "SBUX", "BKNG", "INTU", "SYK", "MDLZ", 
        "TJX", "GILD", "AMT", "ISRG", "LRCX", "ADI", "TMUS", "MMC", "PLD", "BLK", 
        "CI", "REGN", "MU", "VRTX", "MO", "PGR", "BMY", "BSX", "HUM", "EOG", 
        "EQIX", "GEHC", "PANW", "SNPS", "CDNS", "KLAC", "MAR", "CSX", "ORLY", "ASML",
        "CTAS", "MELI", "NXPI", "WDAY", "MNST", "ROST", "ADSK", "CPRT", "KDP", "MCHP",
        "TEAM", "PAYX", "DDOG", "IDXX", "FAST", "EA", "ODFL", "CTSH", "WBD", "FANG", 
        "A", "AAL", "AAP", "ABBV", "ABC", "AES", "AFL", "AIG", "AIZ", "AJG", 
        "ALB", "ALGN", "ALK", "ALL", "ALLE", "AMCR", "AME", "APTV", "ARE", "ATO", 
        "AVB", "AVY", "AWK", "AZO", "BAX", "BBY", "BDX", "BEN", "BF-B", "BIIB", 
        "BIO", "C", "CAG", "CAH", "CARR", "CAT", "CB", "CBOE", "CBRE", "CCI", 
        "CHD", "CHRW", "CHT", "CL", "CLX", "CMA", "CMG", "CMI", "CMS", "CNC", 
        "CNP", "COF", "COO", "CPB", "CPT", "CRL", "CRM", "CRWD", "CTRA", "CVS", 
        "D", "DAL", "DD", "DFS", "DG", "DGX", "DHI", "DHR", "DISH", "DLR", 
        "DOV", "DOW", "DRI", "DTE", "DUK", "DVA", "DVN", "DXCM", "F", "FCX", 
        "FDS", "FEDX", "FITB", "FLS", "FMC", "FOXA", "FRT", "FTNT", "FTV", "GD", 
        "HAS", "HBAN", "HCA", "HD", "HES", "HIG", "HII", "HLT", "HOLX", "GWW", 
        "HST", "HSY", "IEX", "IFF", "ILMN", "INCY", "INVH", "IP", "IPG", "IQV", 
        "IR", "IRM", "IT", "ITW", "IVZ", "JBHT", "JCI", "JKHY", "JNPR", "K", 
        "KEY", "KEYS", "KIM", "KMB", "KMI", "KMX", "KR", "KRE", "L", "LDOS", 
        "LEN", "LH", "LHX", "KHC", "LKQ", "RCX", "LNT", "LOGI", "LUV", "LVS", 
        "LW", "LYV", "M", "MAA", "MTB", "OXY", "PARA", "PAYC", "PBI", "PCAR", 
        "PCG", "PEAK", "PEG", "PENN", "PNR", "PNW", "PODD", "POOL", "PPG", "PPL", 
        "PRU", "PSA", "PSX", "PTC", "PUB", "PVH", "PWR", "PXD", "QRVO", "RCL", 
        "RE", "RF", "RHI", "RJF", "RL", "RMD", "ROL", "ROP", "RRC", "RSG", 
        "STE", "STT", "STX", "STZ", "SWK", "SWKS", "SYF", "SYY", "T", "TAP", 
        "TDG", "TDY", "TECH", "TEL", "TER", "TFC", "TFX", "TGT", "TIW", "TSCO", 
        "TROW", "TRV", "TRMB", "TSS", "TT", "TTWO", "TWTR", "TYL", "UDR", "UHS", 
        "ULTA", "VLO", "VMC", "VNO", "VRSK", "VRSN", "VTR", "VWO", "WRB", "WEC", 
        "WELL", "WST", "WY", "WYNN", "XEL", "XLY", "XRAY", "XYL", "YUM", "ZBH", 
        "ZBRA", "ZION", "ZTS"
    ]

all_tickers = get_hardcoded_broad_market()

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Scanner Settings")
st.sidebar.write(f"📊 **Total Broad Market Stocks Loaded:** {len(all_tickers)}")

timeframe_choice = st.sidebar.selectbox("Select Timeframe", ["Daily", "Weekly", "Monthly"])

st.sidebar.markdown("---")
st.sidebar.subheader("🎯 Pattern Sensitivity")
# Initial levels are kept relaxed so you definitely get matches first
volume_multiplier = st.sidebar.slider("Volume Multiplier (vs 20 MA)", 1.0, 5.0, 1.5, step=0.1)
shadow_multiplier = st.sidebar.slider("Upper Wick vs Body Multiplier", 1.0, 5.0, 1.5, step=0.1)

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
    
    # 40-40 stocks groups
    batch_size = 40
    total_tickers = len(all_tickers)
    
    for i in range(0, total_tickers, batch_size):
        current_batch = all_tickers[i:i+batch_size]
        
        # Update UI progress
        progress_pct = min((i + batch_size) / total_tickers, 1.0)
        progress_bar.progress(progress_pct)
        status_text.text(f"Scanning batch {int(i/batch_size)+1}... (Stocks {i} to {min(i+batch_size, total_tickers)})")
        
        try:
            # Bulk processing
            data = yf.download(current_batch, period=period, interval=interval, group_by='ticker', progress=False)
            
            for ticker in current_batch:
                try:
                    df = data[ticker] if len(current_batch) > 1 else data
                    df = df.dropna(subset=['Close'])
                    
                    if len(df) < 21:
                        continue
                        
                    # Target candles
                    open_p = float(df['Open'].iloc[-1])
                    high_p = float(df['High'].iloc[-1])
                    low_p = float(df['Low'].iloc[-1])
                    close_p = float(df['Close'].iloc[-1])
                    volume = float(df['Volume'].iloc[-1])
                    
                    vol_ma = df['Volume'].iloc[-21:-1].mean()
                    if vol_ma == 0: continue
                    
                    body = abs(close_p - open_p)
                    if body == 0: body = 0.001
                    
                    high_of_body = max(open_p, close_p)
                    low_of_body = min(open_p, close_p)
                    
                    upper_wick = high_p - high_of_body
                    total_range = high_p - low_p
                    if total_range == 0: continue
                    
                    # Core Mathematical Calculations matching your images
                    is_high_volume = volume > (vol_ma * volume_multiplier)
                    is_long_upper_wick = upper_wick > (body * shadow_multiplier)
                    is_price_rejected = (close_p < (low_p + (total_range * 0.50))) # Bottom 50% close boundary
                    
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
                        
                        # Live data update on screen
                        live_df = pd.DataFrame(results)
                        table_placeholder.dataframe(live_df.set_index("Ticker"), use_container_width=True)
                except:
                    continue
        except:
            continue
            
        time.sleep(0.2)
        
    status_text.success(f"Scan complete! Found {len(results)} stocks matching your pattern.")
    if not results:
        st.warning("Is waqt market mein is setting par koi stock nahi mila. Sliders ko thoda kam karke check karein.")

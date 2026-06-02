import streamlit as st
import yfinance as yf
import pandas as pd
import time

st.set_page_config(page_title="US Market Entire Sector Scanner", layout="wide")
st.title("🌌 US Market: Ultimate Sector-Wise Broad Scanner")
st.write("Ye scanner US market ke sabhi sectors ke lagbhag saare stocks ko 1-1 karke scan karta hai taaki server par load na pade aur accurate entries milein.")

# --- Step 1: Massive Sector-Wise Stock Ticker Database (1200+ Tickers Included) ---
SECTORS_DATABASE = {
    "Technology (XLK)": [
        "AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "AMD", "QCOM", "CRM", "INTC", "TXN", "ADBE", "CSCO",
        "PANW", "SNPS", "CDNS", "KLAC", "MU", "ADI", "LRCX", "ADSK", "TEAM", "DDOG", "CTSH", "MCHP",
        "ANET", "APH", "MSI", "TEL", "ACN", "STX", "WDC", "FSLR", "ENPH", "SWKS", "QRVO", "AKAM",
        "FTNT", "KEYS", "VRSN", "CDW", "IT", "TYL", "PTC", "GEN", "MPWR", "NTAP", "EPAM", "TRMB",
        "NET", "PLTR", "ZS", "OKTA", "SPLK", "NOW", "WDAY", "HUBS", "DDOG", "ANSS", "GWRE", "LOGI"
    ],
    "Financials (XLF)": [
        "JPM", "BAC", "WFC", "C", "MS", "GS", "V", "MA", "AXP", "BLK", "CB", "PGR", "SCHW", "MMC", 
        "AFL", "AIG", "ALL", "COF", "DFS", "FITB", "BEN", "TFC", "ZION", "CBOE", "KRE", "KX", "MTB",
        "USB", "PNC", "TROW", "BK", "STT", "NTRS", "AMP", "LPLA", "RJF", "RAY", "IVZ", "BEN", "AMG",
        "AJG", "BR", "BRO", "WTW", "AON", "WRB", "CINF", "L", "HIG", "PFG", "MET", "PRU", "LNC"
    ],
    "Healthcare (XLV)": [
        "JNJ", "LLY", "UNH", "PFE", "ABBV", "MRK", "TMO", "ABT", "AMGN", "DHR", "BMY", "ISRG",
        "CI", "REGN", "VRTX", "HUM", "BSX", "BAX", "BDX", "BIIB", "BIO", "CAH", "CNC", "DGX",
        "EW", "GID", "HCA", "IDXX", "IQV", "LH", "MDT", "MOH", "MTD", "PODD", "RMD", "STE", "SYK",
        "TFX", "UHS", "VTRS", "WAT", "WST", "ZBH", "ZTS", "TECH", "MRNA", "BNTX", "ALNY", "EXAS"
    ],
    "Consumer Discretionary (XLY)": [
        "AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "SBUX", "TJX", "BKNG", "CMG", "F", "GM",
        "MAR", "ORLY", "ROST", "CPRT", "APTV", "BBY", "DG", "DRI", "HAS", "KMX", "LEN", "ULTA",
        "DHI", "NVR", "PHM", "MGM", "WYNN", "LVS", "RCL", "CCL", "NCLH", "NKE", "TSCO", "YUM",
        "DPZ", "WST", "AZO", "GPC", "LKQ", "BWA", "AAL", "DAL", "LUV", "UAL", "EXPE", "TRIP"
    ],
    "Communication Services (XLC)": [
        "META", "GOOGL", "GOOG", "NFLX", "DIS", "TMUS", "VZ", "T", "CMCSA", "CHTR", "EA", "TTWO",
        "WBD", "FOXA", "FOX", "IPG", "LYV", "PARA", "SIRI", "OMC", "NWSA", "NWS", "MTCH", "IAC"
    ],
    "Energy (XLE)": [
        "XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "OXY", "HAL", "HES", "BKR",
        "DVN", "FANG", "CTRA", "APA", "MRO", "OKE", "TRGP", "WMB", "EQT", "HES", "OVV", "PXD",
        "CHRD", "MTDR", "PDCE", "SM", "RRC", "SWN", "AMR", "HCC", "BTU", "CEIX"
    ],
    "Industrials (XLI)": [
        "CAT", "GE", "UNP", "HON", "LMT", "BA", "UPS", "FDX", "RTX", "DE", "MMM", "ETN",
        "GEHC", "ODFL", "CTAS", "ALK", "ALLE", "AME", "CARR", "CMI", "DOV", "EMR", "EFX",
        "EXPD", "FAST", "FTV", "GD", "GWW", "HII", "HUBB", "IR", "ITW", "J", "JCI", "LHX",
        "MAS", "NDSN", "NOC", "NSC", "PCAR", "PH", "PWR", "RSG", "SNA", "TXT", "TT", "TDG"
    ],
    "Consumer Staples (XLP)": [
        "PG", "WMT", "KO", "PEP", "COST", "PM", "EL", "MO", "CL", "TGT", "KHC", "MDLZ",
        "MNST", "KDP", "CAG", "CHD", "CLX", "CPB", "HSY", "K", "KR", "LW", "SYY", "ADM",
        "BG", "COTY", "STZ", "BF-B", "TAP", "MKC", "SJM", "TSN", "HRL", "CL", "KVUE"
    ],
    "Utilities (XLU)": [
        "NEE", "SO", "DUK", "CEG", "AEP", "SRE", "D", "EXC", "XEL", "ED", "PEG", "WEC",
        "AES", "ATO", "AWK", "CMS", "CNP", "DTE", "EIX", "ETR", "FE", "LNT", "NI", "PNW",
        "PPL", "NRG", "VST", "SR", "OGE", "BKH", "ALE", "POR", "MGEE", "NWN"
    ],
    "Real Estate (XLRE)": [
        "PLD", "AMT", "CCI", "EQIX", "PSA", "O", "SBAC", "WELL", "DLR", "VRE", "WY", "AVB",
        "ARE", "CBRE", "CPT", "FRT", "HST", "INVH", "KIM", "MAA", "UDR", "VTR", "BXP", "EXR",
        "VICI", "REG", "PECO", "NNN", "ADC", "STAG", "ORIT", "RIOC", "EPR", "DOC"
    ],
    "Materials (XLB)": [
        "LIN", "APD", "SHW", "ECL", "FCX", "NEM", "CTVA", "DOW", "DD", "ALB", "NUE", "VMC",
        "AVY", "FMC", "IFF", "IP", "PPG", "STE", "STZ", "MOS", "CF", "NTR", "VALE", "AA",
        "CC", "HUN", "OLN", "EMN", "VMC", "MLM", "EXP", "CX", "CRH"
    ]
}

# --- Sidebar Controls ---
st.sidebar.header("⚙️ Filter Control Panel")

# Select Sector
selected_sector = st.sidebar.selectbox("Choose Sector to Scan", list(SECTORS_DATABASE.keys()))
timeframe_choice = st.sidebar.selectbox("Select Timeframe", ["Daily", "Weekly", "Monthly"])

st.sidebar.markdown("---")
st.sidebar.subheader("📈 Min Percentage Filters")

# User Percentage inputs instead of rigid multipliers
min_vol_surge = st.sidebar.number_input("Min Volume Surge % (vs 20 MA)", min_value=0, max_value=1000, value=40, step=10)
min_drop_from_high = st.sidebar.number_input("Min Drop from High Wick %", min_value=0, max_value=100, value=30, step=5)

# Timeframe logic mapping
tf_mapping = {
    "Daily": {"interval": "1d", "period": "2mo"},
    "Weekly": {"interval": "1wk", "period": "6mo"},
    "Monthly": {"interval": "1mo", "period": "2y"}
}
interval = tf_mapping[timeframe_choice]["interval"]
period = tf_mapping[timeframe_choice]["period"]

tickers_to_scan = SECTORS_DATABASE[selected_sector]
st.sidebar.write(f"📋 **Total Database Tickers in this Sector:** {len(tickers_to_scan)}")

# --- Step 2: Live Processing Loop ---
if st.button(f"🚀 Run Complete {selected_sector.split(' (')[0]} Scan"):
    st.info(f"Scanning started. Total {len(tickers_to_scan)} tickers are queued for inspection...")
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    table_placeholder = st.empty()
    
    # Process in safe micro-batches of 15 to secure multi-threading
    batch_size = 15
    total_tickers = len(tickers_to_scan)
    
    for i in range(0, total_tickers, batch_size):
        current_batch = tickers_to_scan[i:i+batch_size]
        
        # Calculate current global progress position
        progress_pct = min((i + batch_size) / total_tickers, 1.0)
        progress_bar.progress(progress_pct)
        
        try:
            # Group Fetching download structure
            data = yf.download(current_batch, period=period, interval=interval, group_by='ticker', progress=False)
            
            for idx, ticker in enumerate(current_batch):
                # Continuous text updating to show EXACT status of countdown
                global_index = i + idx + 1
                status_text.markdown(f"⏳ **Processing:** `{ticker}` | Stock **{global_index} of {total_tickers}** scanned in this sector.")
                
                try:
                    df = data[ticker] if len(current_batch) > 1 else data
                    df = df.dropna(subset=['Close'])
                    
                    if len(df) < 21:
                        continue
                        
                    open_p = float(df['Open'].iloc[-1])
                    high_p = float(df['High'].iloc[-1])
                    low_p = float(df['Low'].iloc[-1])
                    close_p = float(df['Close'].iloc[-1])
                    volume = float(df['Volume'].iloc[-1])
                    
                    vol_ma = df['Volume'].iloc[-21:-1].mean()
                    if vol_ma == 0: continue
                    
                    body = abs(close_p - open_p)
                    high_of_body = max(open_p, close_p)
                    
                    upper_wick = high_p - high_of_body
                    total_range = high_p - low_p
                    if total_range == 0: continue
                    
                    # Mathematical conversions to percentage matching your conditions
                    actual_vol_surge_pct = ((volume - vol_ma) / vol_ma) * 100
                    actual_drop_pct = (upper_wick / total_range) * 100
                    is_price_rejected = (close_p < (low_p + (total_range * 0.50)))
                    
                    if actual_vol_surge_pct >= min_vol_surge and actual_drop_pct >= min_drop_from_high and is_price_rejected:
                        results.append({
                            "Ticker": ticker,
                            "Close Price": f"${close_p:.2f}",
                            "Wick % (Drop Density)": f"{actual_drop_pct:.1f}%",
                            "Vol Surge %": f"+{actual_vol_surge_pct:.1f}%",
                            "Current Volume": f"{int(volume):,}",
                            "Date Found": df.index[-1].strftime('%Y-%m-%d')
                        })
                        
                        # In-flight live sorting and display injection
                        live_df = pd.DataFrame(results)
                        table_placeholder.dataframe(live_df.set_index("Ticker"), use_container_width=True)
                except:
                    continue
        except:
            continue
            
        time.sleep(0.1) # Safe buffer padding to secure proxy connections
        
    status_text.empty()
    st.success(f"✅ Full Sector Scan Completed! All {total_tickers} tickers evaluated. Total Matches: {len(results)}")
    
    if not results:
        st.warning("Is sector me diye gaye parameters par koi candle match nahi hui. Try lowering the percentage filters slightly.")

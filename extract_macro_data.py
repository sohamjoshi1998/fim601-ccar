import pandas as pd
import pandas_datareader.data as web
import datetime

def download_fred_data():
    """
    Downloads historical macroeconomic data from FRED (Federal Reserve Economic Data)
    for CCAR stress testing modeling.
    
    Time range: 
    - Download Start: 1999 (Buffer year for growth calculations)
    - Output Start:   2000 (Clean data start)
    - End:            2025
    
    Frequency: Converted to Quarterly (averages)
    """
    
    # 1. Define the time range
    # We start from 2000 to capture the 2008 Financial Crisis for model training
    start_date = datetime.datetime(1999, 1, 1)
    end_date = datetime.datetime(2025, 12, 31)

    # 2. Define the data mapping (FRED Series ID -> Readable Variable Name)
    # These variables are selected based on the Fed's Supervisory Stress Test Methodology
    indicators = {
        'UNRATE': 'Unemployment_Rate',       # Monthly: Civilian Unemployment Rate for Credit Cards
        'GDPC1': 'Real_GDP',                 # Quarterly: Real Gross Domestic Product for C&I
        'BAMLC0A4CBBB': 'BBB_Spread',        # Daily: ICE BofA BBB US Corp Index Option-Adjusted Spread. If this spread goes up, it means it's super expensive for companies to borrow money, so they might fail.
        'VIXCLS': 'VIX_Volatility_Index',    # Daily: CBOE Volatility Index
        'DGS10': '10Y_Treasury_Yield',       # Daily: 10-Year Treasury Constant Maturity Rate for PPNR
        'TB3MS': '3M_Treasury_Rate',         # Monthly: 3-Month Treasury Bill Secondary Market Rate for PPNR
        'DPRIME': 'Prime_Rate',              # Daily: Bank Prime Loan Rate (Benchmark for Credit Card Pricing, affecting income) for PPNR 
        'CPIAUCSL': 'CPI_Inflation',         # Monthly: Consumer Price Index for All Urban Consumers
        'DSPIC96': 'Real_Disposable_Income', # Monthly: Real Disposable Personal Income (Key driver for Retail Credit)
        'GDP': 'Nominal_GDP',                # Quarterly: Nominal Gross Domestic Product
        'CP': 'Corporate_Profits',           # Quarterly: Corporate Profits After Tax (with IVA and CCAdj)
        'CSUSHPINSA': 'House_Price_Index',   # Monthly: S&P/Case-Shiller U.S. National Home Price Index (Real Estate proxy, starts 1987)
        'NASDAQCOM': 'Stock_Market_Index',    # Daily: NASDAQ Composite Index (Proxy for US Equity market; avoids S&P 500 10-year FRED data limit)
        'NFCI': 'NFCI_Financial_Conditions',      # Weekly: Chicago Fed National Financial Conditions Index.
        'STLFSI4': 'STLFSI_Financial_Stress',     # Weekly: St. Louis Fed Financial Stress Index (version 4).
        'BAMLH0A0HYM2': 'HY_Spread',              # Daily: ICE BofA US High Yield OAS, in %.
        'BAMLC0A1CAAA': 'AAA_Spread',             # Daily: ICE BofA AAA US Corporate OAS, in %.
        'BAMLC0A2CAA': 'AA_Spread',               # Daily: ICE BofA AA US Corporate OAS, in %.
        'INDPRO': 'Industrial_Production',        # Monthly: Industrial Production Index.--Manufacturing/industrial activity; downturn implies weaker corporate revenues and stress.
        'TCU': 'Capacity_Utilization'           # Monthly: Capacity Utilization rate (%).--How “tight” industrial capacity is; falls in recessions.
    }

    print(f"Fetching indicators: {list(indicators.keys())}")

    try:
        # 3. Fetch data from FRED
        df_raw = web.DataReader(list(indicators.keys()), 'fred', start_date, end_date)
        
        # 4. Data Processing & Frequency Standardization
        # Resample all data to Quarterly End frequency and calculate the mean
        df_quarterly = df_raw.resample('QE').mean()
        
        # 5. Rename columns for better readability
        df_quarterly.rename(columns=indicators, inplace=True)
        
        # 6. Transform non-stationary variables into growth rates/returns
        df_quarterly['Real_GDP_Growth'] = df_quarterly['Real_GDP'].pct_change(1, fill_method=None) * 4 # Annualized Quarter-over-Quarter, QoQ Annualized
        df_quarterly['Nominal_GDP_Growth'] = df_quarterly['Nominal_GDP'].pct_change(1, fill_method=None) * 4 
        df_quarterly['Corp_Profits_YoY'] = df_quarterly['Corporate_Profits'].pct_change(4, fill_method=None) # Year-over-Year Growth, YoY
        df_quarterly['HPI_YoY'] = df_quarterly['House_Price_Index'].pct_change(4, fill_method=None)
        df_quarterly['Stock_Market_Return'] = df_quarterly['Stock_Market_Index'].pct_change(1, fill_method=None) # Simple QoQ Return
        df_quarterly['CPI_YoY'] = df_quarterly['CPI_Inflation'].pct_change(4, fill_method=None)
        df_quarterly['INDPRO_YoY'] = df_quarterly['Industrial_Production'].pct_change(4, fill_method=None)
        df_quarterly['INDPRO_Growth'] = df_quarterly['Industrial_Production'].pct_change(1, fill_method=None) * 4
        df_quarterly['TCU_Change'] = df_quarterly['Capacity_Utilization'].diff(1)
        df_quarterly['Term_Spread_10Y_3M'] = df_quarterly['10Y_Treasury_Yield'] - df_quarterly['3M_Treasury_Rate'] # Yield curve slope
        df_quarterly['RDI_YoY'] = df_quarterly['Real_Disposable_Income'].pct_change(4, fill_method=None)
        df_quarterly['RDI_Growth'] = df_quarterly['Real_Disposable_Income'].pct_change(1, fill_method=None) * 4
        df_quarterly['10Y_Change'] = df_quarterly['10Y_Treasury_Yield'].diff(1)
        df_quarterly['3M_Change']  = df_quarterly['3M_Treasury_Rate'].diff(1)
        df_quarterly['Prime_Change'] = df_quarterly['Prime_Rate'].diff(1)
        df_quarterly['BBB_Change'] = df_quarterly['BBB_Spread'].diff(1)
        df_quarterly['HY_Change']  = df_quarterly['HY_Spread'].diff(1)

        # 7. *** The Trimming Step ***
        # Remove the 1999 buffer data. Keep only data from 2000-01-01 onwards.
        df_final = df_quarterly.loc['2000-01-01':].copy()

        # 8. Final Check
        df_final.dropna(how='all', inplace=True)

        # 8. Success Message & Preview
        print("-" * 40)
        print("Download and Processing Successful!")
        print(f"Time Range: {df_final.index[0].date()} to {df_final.index[-1].date()}")
        print(f"Shape: {df_final.shape}")
        print("-" * 40)
        print("First 5 rows of the final dataset (2000+):")
        print(df_final.head())

        # 9. Save to CSV
        OUTPUT_PATH = "./output/ccar_macro_data_quarterly.csv"
        df_final.to_csv(OUTPUT_PATH)
        print(f"\nData saved to: {OUTPUT_PATH}")

    except Exception as e:
        print(f"\n[Error] {e}")

if __name__ == "__main__":
    download_fred_data()


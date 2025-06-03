import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt

def option_chains(ticker):
    print('start function')
    asset = yf.Ticker(ticker)
    print(f'Fetching options for {ticker}')
    expirations = asset.options
    print(f"Available expirations: {expirations}")

    chains = pd.DataFrame()

    for expiration in expirations:
        # tupple of two dataframes
        opt =asset.option_chain(expiration)
        calls = opt.calls
        calls["optionType"] = "call"

        put = opt.puts
        put["optionType"] = "put"
        
        chain = pd.concat([calls, put])
        chain["expiration"] = (
            pd.to_datetime(expiration) +
            pd.DateOffset(hours = 23, minutes = 59, seconds = 59)
        )

        chains = pd.concat([chains, chain])
        print(f"Fetched {len(chain)} options for expiration {expiration}")
        print(chains.head())
    
    chains["daysToExpiration"] = (chains.expiration
        - dt.datetime.today()).dt.days + 1

    return chains

if __name__ == "__main__":
    import sys
    
    # Allow ticker to be passed as command line argument
    ticker = sys.argv[1] if len(sys.argv) > 1 else "ERJ"
    print(f"Analyzing options for ticker: {ticker}")

    try:
        option_chains_data = option_chains(ticker)
        calls = option_chains_data[option_chains_data['optionType'] == 'call']

        print(f"Total calls found: {len(calls)}")
        
        if len(calls) == 0:
            print(f"No call options found for ticker {ticker}. Please check if it's a valid ticker with options.")
            sys.exit(1)
            
        print(f"Available expirations in calls: {calls['expiration'].unique()}")

        # Check if the specific expiration exists
        target_expiration = '2025-05-02 23:59:59'
        calls_at_expiry = calls[calls['expiration'] == target_expiration]
        
        print(f"Calls found for {target_expiration}: {len(calls_at_expiry)}")
        
        if len(calls_at_expiry) == 0:
            print("No calls found for the specified expiration date.")
            # Use the first available expiration instead
            if len(calls) > 0:
                first_expiration = calls['expiration'].iloc[0]
                print(f"Using first available expiration: {first_expiration}")
                calls_at_expiry = calls[calls['expiration'] == first_expiration]
            else:
                print("No calls data available at all!")
                sys.exit(1)
                
    except Exception as e:
        print(f"Error fetching options data for {ticker}: {e}")
        print("This could be due to:")
        print("1. Invalid ticker symbol")
        print("2. No options available for this ticker")
        print("3. Network connectivity issues")
        sys.exit(1)# filter out low vols
    filtered_calls_at_expiry = calls_at_expiry[calls_at_expiry['impliedVolatility'] > 0.001]
    
    print(f"Calls after filtering low volatility: {len(filtered_calls_at_expiry)}")
    
    if len(filtered_calls_at_expiry) == 0:
        print("Still no data after relaxing filter. Showing all calls for this expiration:")
        filtered_calls_at_expiry = calls_at_expiry
        
    if len(filtered_calls_at_expiry) > 0:
        try:
            expiration_str = filtered_calls_at_expiry['expiration'].iloc[0].strftime('%Y-%m-%d')
            print(f"Plotting volatility data for {len(filtered_calls_at_expiry)} options")
            
            # Check if we have the required columns
            if 'strike' in filtered_calls_at_expiry.columns and 'impliedVolatility' in filtered_calls_at_expiry.columns:
                plot_data = filtered_calls_at_expiry[["strike", "impliedVolatility"]].copy()
                
                # Remove any NaN values
                plot_data = plot_data.dropna()
                
                if len(plot_data) > 0:
                    plot_data.set_index("strike").plot(
                        title=f"IV for {ticker} at {expiration_str}",
                        ylabel="Implied Volatility",
                        xlabel="Strike",
                        figsize=(10, 6),
                        grid=True,
                        style='o-',
                        legend=False
                    )
                    plt.show()
                else:
                    print("No valid data points to plot after removing NaN values!")
            else:
                print("Required columns (strike, impliedVolatility) not found in data")
                print(f"Available columns: {filtered_calls_at_expiry.columns.tolist()}")
                
        except Exception as e:
            print(f"Error while plotting: {e}")
            print("Available data:")
            if len(filtered_calls_at_expiry) > 0:
                print(filtered_calls_at_expiry.head())
            else:
                print("DataFrame is empty")
    else:
        print("No data to plot!")
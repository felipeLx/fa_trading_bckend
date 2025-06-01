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
    ticker = "ERJ"

    option_chains = option_chains(ticker)
    calls = option_chains[option_chains['optionType'] == 'call']

    # select expiration to plot
    calls_at_expiry = calls[calls['expiration'] == '2025-05-02 23:59:59']

    # filter out low vols
    filtered_calls_at_expiry = calls_at_expiry[calls_at_expiry['impliedVolatility'] > 0.001]

    filtered_calls_at_expiry[["strike", "impliedVolatility"]].set_index("strike").plot(title=f"IV for {ticker} at {calls_at_expiry['expiration'].iloc[0]}",
        ylabel="Implied Volatility",
        xlabel="Strike",
        figsize=(10, 6),
        grid=True,
        style='o-',
        legend=False
    )
    plt.show()
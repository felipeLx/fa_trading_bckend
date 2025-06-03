import numpy as np
import pandas as pd
import datetime as dt
import yfinance as yf
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import sys
import os

# Set matplotlib to use a non-interactive backend
plt.switch_backend('Agg')

def fetch_option_chains(ticker):
    """
    Fetch all option chains for a given ticker
    
    Args:
        ticker (str): Stock ticker symbol
        
    Returns:
        pd.DataFrame: Complete option chains data
    """
    print(f'Fetching options for {ticker}')
    asset = yf.Ticker(ticker)
    expirations = asset.options
    print(f"Available expirations: {expirations}")

    if not expirations:
        raise ValueError(f"No options available for ticker {ticker}")

    chains = pd.DataFrame()

    for expiration in expirations:
        try:
            opt = asset.option_chain(expiration)
            calls = opt.calls.copy()
            calls["optionType"] = "call"

            puts = opt.puts.copy()
            puts["optionType"] = "put"
            
            chain = pd.concat([calls, puts], ignore_index=True)
            chain["expiration"] = (
                pd.to_datetime(expiration) +
                pd.DateOffset(hours=23, minutes=59, seconds=59)
            )

            chains = pd.concat([chains, chain], ignore_index=True)
            print(f"Fetched {len(chain)} options for expiration {expiration}")
            
        except Exception as e:
            print(f"Error fetching options for expiration {expiration}: {e}")
            continue
    
    if len(chains) == 0:
        raise ValueError(f"No option data could be fetched for {ticker}")
        
    # Calculate days to expiration
    chains["daysToExpiration"] = (
        chains.expiration - dt.datetime.today()
    ).dt.days + 1

    return chains

def filter_options_data(options_df, option_type='call', min_volatility=0.001):
    """
    Filter options data by type and minimum volatility
    
    Args:
        options_df (pd.DataFrame): Options data
        option_type (str): 'call' or 'put'
        min_volatility (float): Minimum implied volatility threshold
        
    Returns:
        pd.DataFrame: Filtered options data
    """
    # Filter by option type
    filtered = options_df[options_df['optionType'] == option_type].copy()
    print(f"Total {option_type}s found: {len(filtered)}")
    
    if len(filtered) == 0:
        return filtered
    
    # Filter by volatility
    filtered = filtered[filtered['impliedVolatility'] > min_volatility]
    print(f"{option_type.title()}s after filtering volatility > {min_volatility}: {len(filtered)}")
    
    # If no data after filtering, try with lower threshold
    if len(filtered) == 0:
        print(f"No data after filtering. Trying with lower threshold...")
        original_filtered = options_df[options_df['optionType'] == option_type].copy()
        filtered = original_filtered[original_filtered['impliedVolatility'] > min_volatility/10]
        print(f"Data with lower threshold: {len(filtered)}")
    
    return filtered

def plot_volatility_smile(options_df, ticker, expiration_date=None, save_path=None):
    """
    Plot implied volatility smile for a specific expiration
    
    Args:
        options_df (pd.DataFrame): Filtered options data
        ticker (str): Stock ticker
        expiration_date (str or None): Specific expiration to plot
        save_path (str): Path to save the plot (optional)
    """
    if len(options_df) == 0:
        print("No data available for volatility smile plot")
        return
    
    # If no specific expiration, use the first available
    if expiration_date is None:
        expiration_date = options_df['expiration'].iloc[0]
        print(f"Using expiration: {expiration_date}")
    
    # Filter for specific expiration
    exp_data = options_df[options_df['expiration'] == expiration_date]
    
    if len(exp_data) == 0:
        print(f"No data found for expiration {expiration_date}")
        return
    
    # Clean data for plotting
    plot_data = exp_data[["strike", "impliedVolatility"]].dropna()
    
    if len(plot_data) == 0:
        print("No valid data points after cleaning")
        return
    
    # Create the plot
    plt.figure(figsize=(12, 6))
    plt.plot(plot_data["strike"], plot_data["impliedVolatility"], 'o-', linewidth=2, markersize=6)
    
    expiration_str = pd.to_datetime(expiration_date).strftime('%Y-%m-%d')
    plt.title(f"Implied Volatility Smile for {ticker} - Expiration: {expiration_str}")
    plt.xlabel("Strike Price")
    plt.ylabel("Implied Volatility")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
      # Save or show the plot
    if save_path is None:
        expiration_str = pd.to_datetime(expiration_date).strftime('%Y-%m-%d')
        save_path = f"{ticker}_volatility_smile_{expiration_str}.png"
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Volatility smile plot saved as: {save_path}")
    plt.close()  # Close the figure to free memory

def create_volatility_surface(options_df, ticker, save_path=None):
    """
    Create and plot 3D volatility surface
    
    Args:
        options_df (pd.DataFrame): Options data
        ticker (str): Stock ticker
        save_path (str): Path to save the plot (optional)
    """
    if len(options_df) == 0:
        print("No data available for volatility surface")
        return None
    
    print("Creating volatility surface...")
    
    # Create pivot table for the surface
    surface_data = options_df[['daysToExpiration', 'strike', 'impliedVolatility']].pivot_table(
        values='impliedVolatility', 
        index='strike', 
        columns='daysToExpiration'
    ).dropna()
    
    if surface_data.empty:
        print("Insufficient data for volatility surface")
        return None
    
    print(f"Surface dimensions: {surface_data.shape}")
    
    # Create 3D surface plot
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_subplot(111, projection='3d')
    
    # Prepare data for 3D plot
    X, Y = np.meshgrid(surface_data.columns, surface_data.index)
    Z = surface_data.values
    
    # Create surface plot
    surf = ax.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
    
    ax.set_xlabel('Days to Expiration')
    ax.set_ylabel('Strike Price')
    ax.set_zlabel('Implied Volatility')
    ax.set_title(f'Implied Volatility Surface for {ticker}')
    
    # Add color bar
    fig.colorbar(surf, shrink=0.5, aspect=20)
    
    plt.tight_layout()
    
    # Save the plot
    if save_path is None:
        save_path = f"{ticker}_volatility_surface_3d.png"
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"3D volatility surface saved as: {save_path}")
    plt.close()  # Close the figure to free memory
    
    return surface_data

def plot_volatility_heatmap(surface_data, ticker, save_path=None):
    """
    Plot volatility surface as a heatmap
    
    Args:
        surface_data (pd.DataFrame): Pivot table of volatility surface
        ticker (str): Stock ticker
        save_path (str): Path to save the plot (optional)
    """
    if surface_data is None or surface_data.empty:
        print("No surface data available for heatmap")
        return
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(surface_data, cmap='viridis', annot=False, fmt='.3f', cbar_kws={'label': 'Implied Volatility'})
    plt.title(f'Implied Volatility Heatmap for {ticker}')
    plt.xlabel('Days to Expiration')
    plt.ylabel('Strike Price')
    plt.tight_layout()
    
    # Save the plot
    if save_path is None:
        save_path = f"{ticker}_volatility_heatmap.png"
    
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Volatility heatmap saved as: {save_path}")
    plt.close()  # Close the figure to free memory

def analyze_volatility_statistics(options_df, ticker):
    """
    Print statistical analysis of volatility data
    
    Args:
        options_df (pd.DataFrame): Options data
        ticker (str): Stock ticker
    """
    if len(options_df) == 0:
        print("No data available for statistics")
        return
    
    print(f"\n=== Volatility Statistics for {ticker} ===")
    vol_stats = options_df['impliedVolatility'].describe()
    print(vol_stats)
    
    # Additional statistics
    print(f"\nAdditional Statistics:")
    print(f"Volatility Range: {options_df['impliedVolatility'].min():.4f} - {options_df['impliedVolatility'].max():.4f}")
    print(f"Volatility Spread: {options_df['impliedVolatility'].max() - options_df['impliedVolatility'].min():.4f}")
    
    # Group by expiration
    print(f"\nVolatility by Expiration:")
    exp_stats = options_df.groupby('expiration')['impliedVolatility'].agg(['mean', 'std', 'count'])
    print(exp_stats)

def create_charts_directory():
    """Create a directory to store chart images"""
    charts_dir = "volatility_charts"
    if not os.path.exists(charts_dir):
        os.makedirs(charts_dir)
        print(f"Created charts directory: {charts_dir}")
    return charts_dir

def main(ticker="ERJ", option_type="call", min_volatility=0.001):
    """
    Main analysis function
    
    Args:
        ticker (str): Stock ticker to analyze
        option_type (str): 'call' or 'put'
        min_volatility (float): Minimum volatility threshold
    """
    print(f"=== Options Volatility Analysis for {ticker} ===\n")
    
    # Create charts directory
    charts_dir = create_charts_directory()
    
    try:
        # Fetch option chains
        print("1. Fetching option chains...")
        option_chains_data = fetch_option_chains(ticker)
        print(f"Total options fetched: {len(option_chains_data)}")
        
        # Filter options data
        print(f"\n2. Filtering {option_type} options...")
        filtered_options = filter_options_data(option_chains_data, option_type, min_volatility)
        
        if len(filtered_options) == 0:
            print(f"No {option_type} options found after filtering")
            return
        
        # Statistical analysis
        print(f"\n3. Statistical Analysis...")
        analyze_volatility_statistics(filtered_options, ticker)
        
        # Plot volatility smile
        print(f"\n4. Creating volatility smile plot...")
        smile_path = os.path.join(charts_dir, f"{ticker}_volatility_smile.png")
        plot_volatility_smile(filtered_options, ticker, save_path=smile_path)
        
        # Create volatility surface
        print(f"\n5. Creating volatility surface...")
        surface_path = os.path.join(charts_dir, f"{ticker}_volatility_surface_3d.png")
        surface_data = create_volatility_surface(filtered_options, ticker, save_path=surface_path)
        
        # Plot heatmap
        if surface_data is not None and not surface_data.empty:
            print(f"\n6. Creating volatility heatmap...")
            heatmap_path = os.path.join(charts_dir, f"{ticker}_volatility_heatmap.png")
            plot_volatility_heatmap(surface_data, ticker, save_path=heatmap_path)
        
        print(f"\n=== Analysis Complete for {ticker} ===")
        print(f"Charts saved in directory: {charts_dir}")
        
        return {
            'raw_data': option_chains_data,
            'filtered_data': filtered_options,
            'surface_data': surface_data,
            'charts_directory': charts_dir
        }
        
    except Exception as e:
        print(f"Error in volatility analysis for {ticker}: {e}")
        print("This could be due to:")
        print("1. Invalid ticker symbol")
        print("2. No options available for this ticker")
        print("3. Network connectivity issues")
        return None

if __name__ == "__main__":
    # Parse command line arguments
    ticker = sys.argv[1] if len(sys.argv) > 1 else "ERJ"
    option_type = sys.argv[2] if len(sys.argv) > 2 else "call"
    min_volatility = float(sys.argv[3]) if len(sys.argv) > 3 else 0.001
    
    # Run main analysis
    results = main(ticker, option_type, min_volatility)
    
    if results:
        print(f"\nAnalysis completed successfully!")
        print(f"Raw data shape: {results['raw_data'].shape}")
        print(f"Filtered data shape: {results['filtered_data'].shape}")
        if results['surface_data'] is not None:
            print(f"Surface data shape: {results['surface_data'].shape}")

#!/usr/bin/env python3
"""
Dynamic Balance Management System for Trading Robot
Critical security module to prevent financial exposure from hardcoded balances.

This module provides:
1. Real-time account balance calculation from trade history
2. CedroTech API portfolio synchronization
3. Centralized balance tracking with database integration
4. Risk management based on current available balance
5. Trade impact calculation and P&L tracking
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils.database import fetch_trade_asset, supabase
import logging

load_dotenv()

class BalanceManager:
    """
    Centralized balance management system for dynamic balance tracking.
    
    Features:
    - Real-time balance calculation from trade history
    - API portfolio synchronization
    - Database-driven balance persistence
    - Risk management integration
    """
    def __init__(self, api=None, initial_balance=None):
        """
        Initialize Balance Manager with API integration.
          Args:
            api: CedroTech API instance for portfolio data
            initial_balance: Starting balance (only used if no trade history exists)
        """
        self.api = api
        self.initial_balance = initial_balance or float(os.getenv('INITIAL_BALANCE', 500.0))
        self.user_id = os.getenv('USER_ID')
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.logger.info(f"🏦 Balance Manager initialized with initial balance: R${self.initial_balance:,.2f}")
    
    def get_current_balance(self, from_source='auto'):
        """
        Get current account balance from the most reliable source.
        
        Args:
            from_source (str): 'auto', 'api', 'database', 'calculation'
        
        Returns:
            dict: {
                'balance': float,
                'source': str,
                'last_updated': str,
                'confidence': str,
                'details': dict
            }
        """
        balance_result = {
            'balance': self.initial_balance,
            'source': 'initial',
            'last_updated': datetime.now().isoformat(),
            'confidence': 'low',
            'details': {}
        }
        
        try:
            if from_source in ['auto', 'api'] and self.api:
                # Try to get balance from CedroTech API first (highest priority)
                api_balance = self._get_api_balance()
                if api_balance['success']:
                    balance_result.update({
                        'balance': api_balance['balance'],
                        'source': 'api',
                        'confidence': 'high',
                        'details': api_balance
                    })
                    self.logger.info(f"✅ API Balance: R${api_balance['balance']:,.2f}")
                    return balance_result
            
            if from_source in ['auto', 'calculation']:
                # Calculate balance from trade history (medium priority)
                calc_balance = self._calculate_balance_from_trades()
                if calc_balance['success']:
                    balance_result.update({
                        'balance': calc_balance['balance'],
                        'source': 'calculation',
                        'confidence': 'medium',
                        'details': calc_balance
                    })
                    self.logger.info(f"📊 Calculated Balance: R${calc_balance['balance']:,.2f}")
                    return balance_result
            
            if from_source in ['auto', 'database']:
                # Get balance from database records (low priority)
                db_balance = self._get_database_balance()
                if db_balance['success']:
                    balance_result.update({
                        'balance': db_balance['balance'],
                        'source': 'database',
                        'confidence': 'medium',
                        'details': db_balance
                    })
                    self.logger.info(f"💾 Database Balance: R${db_balance['balance']:,.2f}")
                    return balance_result
            
        except Exception as e:
            self.logger.error(f"❌ Error getting balance: {e}")
            balance_result['details']['error'] = str(e)
        
        # Fallback to initial balance
        self.logger.warning(f"⚠️ Using fallback balance: R${self.initial_balance:,.2f}")
        return balance_result
    
    def _get_api_balance(self):
        """Get balance from CedroTech API portfolio data."""
        try:
            if not self.api:
                return {'success': False, 'error': 'No API instance available'}
            
            if self.api.paper_trading:
                # In paper trading, simulate portfolio with current calculated balance
                calc_result = self._calculate_balance_from_trades()
                simulated_balance = calc_result.get('balance', self.initial_balance)
                return {
                    'success': True,
                    'balance': simulated_balance,
                    'cash_available': simulated_balance,
                    'positions_value': 0.0,
                    'source': 'api_simulated'
                }
            
            # Get real portfolio data from CedroTech API
            portfolio = self.api.get_portfolio_positions()
            
            if 'error' in portfolio:
                return {'success': False, 'error': portfolio['error']}
            
            # Extract cash balance from portfolio
            cash_balance = portfolio.get('cash', 0.0)
            positions_value = 0.0
            
            # Calculate total position value
            if 'positions' in portfolio:
                for position in portfolio['positions']:
                    quantity = position.get('quantity', 0)
                    current_price = position.get('current_price', 0)
                    positions_value += quantity * current_price
            
            total_balance = cash_balance + positions_value
            
            return {
                'success': True,
                'balance': total_balance,
                'cash_available': cash_balance,
                'positions_value': positions_value,
                'positions': portfolio.get('positions', []),
                'source': 'api_live'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _calculate_balance_from_trades(self):
        """Calculate current balance based on trade history and P&L."""
        try:
            # Get all trades from today and calculate running balance
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Fetch all trades for the user
            result = supabase.table("trade_asset").select(
                "ticker, type, price, volume, created_at"
            ).eq("user_id", self.user_id).order("created_at", desc=False).execute()
            
            if not result.data:
                # No trades found, return initial balance
                return {
                    'success': True,
                    'balance': self.initial_balance,
                    'total_trades': 0,
                    'daily_pnl': 0.0,
                    'source': 'calculation_no_trades'
                }
            
            # Calculate balance from trade history
            running_balance = self.initial_balance
            total_invested = 0.0
            total_realized = 0.0
            daily_pnl = 0.0
            trade_count = 0
            
            # Group trades by ticker to calculate P&L
            position_tracking = {}
            
            for trade in result.data:
                ticker = trade['ticker']
                trade_type = trade['type']
                price = float(trade['price'])
                volume = float(trade['volume'])
                trade_date = trade['created_at'][:10]  # Extract date
                
                trade_count += 1
                
                if ticker not in position_tracking:
                    position_tracking[ticker] = {
                        'shares': 0,
                        'total_cost': 0.0,
                        'realized_pnl': 0.0
                    }
                
                if trade_type in ['buy']:
                    # Buy order - subtract cost from balance
                    cost = price * volume
                    running_balance -= cost
                    total_invested += cost
                    
                    # Update position
                    position_tracking[ticker]['shares'] += volume
                    position_tracking[ticker]['total_cost'] += cost
                    
                elif trade_type in ['sell', 'force_close']:
                    # Sell order - add proceeds to balance
                    proceeds = price * volume
                    running_balance += proceeds
                    total_realized += proceeds
                    
                    # Calculate realized P&L
                    if position_tracking[ticker]['shares'] > 0:
                        avg_cost = position_tracking[ticker]['total_cost'] / position_tracking[ticker]['shares']
                        realized_pnl = (price - avg_cost) * min(volume, position_tracking[ticker]['shares'])
                        position_tracking[ticker]['realized_pnl'] += realized_pnl
                        
                        # Update position
                        shares_sold = min(volume, position_tracking[ticker]['shares'])
                        position_tracking[ticker]['shares'] -= shares_sold
                        position_tracking[ticker]['total_cost'] -= avg_cost * shares_sold
                        
                        # Add to daily P&L if trade is from today
                        if trade_date == today:
                            daily_pnl += realized_pnl
            
            return {
                'success': True,
                'balance': running_balance,
                'total_trades': trade_count,
                'total_invested': total_invested,
                'total_realized': total_realized,
                'daily_pnl': daily_pnl,
                'positions': position_tracking,
                'source': 'calculation_trade_history'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _get_database_balance(self):
        """Get balance from database balance tracking table."""
        try:
            # Try to get the most recent balance record
            result = supabase.table("account_balance").select(
                "balance, updated_at, source"
            ).eq("user_id", self.user_id).order("updated_at", desc=True).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                balance_record = result.data[0]
                return {
                    'success': True,
                    'balance': float(balance_record['balance']),
                    'last_updated': balance_record['updated_at'],
                    'source': f"database_{balance_record['source']}"
                }
            else:
                return {'success': False, 'error': 'No balance records found in database'}
                
        except Exception as e:
            # Table might not exist, that's ok
            return {'success': False, 'error': str(e)}
    
    def update_balance_after_trade(self, trade_type, ticker, price, volume):
        """
        Update balance after a trade is executed.
        
        Args:
            trade_type (str): 'buy', 'sell', 'force_close'
            ticker (str): Stock ticker
            price (float): Execution price
            volume (float): Number of shares
        
        Returns:
            dict: Updated balance information
        """
        try:
            # Get current balance
            current_balance_info = self.get_current_balance()
            current_balance = current_balance_info['balance']
            
            # Calculate impact of trade
            trade_value = price * volume
            
            if trade_type in ['buy']:
                new_balance = current_balance - trade_value
                impact = -trade_value
            elif trade_type in ['sell', 'force_close']:
                new_balance = current_balance + trade_value
                impact = trade_value
            else:
                # Unknown trade type, no balance change
                new_balance = current_balance
                impact = 0.0
            
            # Save updated balance to database
            self._save_balance_to_database(new_balance, f"trade_{trade_type}")
            
            self.logger.info(f"💰 Balance updated after {trade_type}: R${current_balance:,.2f} → R${new_balance:,.2f} (Impact: R${impact:,.2f})")
            
            return {
                'success': True,
                'previous_balance': current_balance,
                'new_balance': new_balance,
                'trade_impact': impact,
                'trade_details': {
                    'type': trade_type,
                    'ticker': ticker,
                    'price': price,
                    'volume': volume,
                    'value': trade_value
                }
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error updating balance after trade: {e}")
            return {'success': False, 'error': str(e)}
    
    def _save_balance_to_database(self, balance, source):
        """Save balance to database for tracking."""
        try:
            # Insert balance record
            supabase.table("account_balance").insert({
                "user_id": self.user_id,
                "balance": balance,
                "source": source,
                "updated_at": datetime.now().isoformat()
            }).execute()
            
            self.logger.info(f"💾 Balance saved to database: R${balance:,.2f} (source: {source})")
            
        except Exception as e:
            # If table doesn't exist, create it
            try:
                self._create_balance_table()
                # Retry insert
                supabase.table("account_balance").insert({
                    "user_id": self.user_id,
                    "balance": balance,
                    "source": source,
                    "updated_at": datetime.now().isoformat()
                }).execute()
                
                self.logger.info(f"💾 Balance saved to database (after table creation): R${balance:,.2f}")
                
            except Exception as e2:
                self.logger.warning(f"⚠️ Could not save balance to database: {e2}")
    
    def _create_balance_table(self):
        """Create account_balance table if it doesn't exist."""
        # This would typically be done through database migrations
        # For now, we'll just log that the table should be created
        self.logger.warning("📋 Account balance table should be created in database schema")
    
    def get_available_cash(self):
        """Get available cash for trading (excludes money tied up in positions)."""
        balance_info = self.get_current_balance()
        
        if balance_info['source'] == 'api' and 'cash_available' in balance_info['details']:
            return balance_info['details']['cash_available']
        else:
            # For calculated balances, assume all balance is available cash
            # In a real system, you'd subtract the value of open positions
            return balance_info['balance']
    
    def calculate_position_size_with_current_balance(self, risk_per_trade, stop_loss_distance):
        """
        Calculate position size using current dynamic balance.
        
        Args:
            risk_per_trade (float): Risk percentage (0.02 = 2%)
            stop_loss_distance (float): Distance to stop loss in currency
        
        Returns:
            dict: Position size calculation results
        """
        try:
            available_cash = self.get_available_cash()
            risk_amount = available_cash * risk_per_trade
            
            if stop_loss_distance <= 0:
                return {
                    'success': False,
                    'error': 'Stop loss distance must be positive',
                    'available_cash': available_cash
                }
            
            position_size = risk_amount / stop_loss_distance
            max_position_value = available_cash * 0.95  # Use max 95% of available cash
            max_position_size = max_position_value / stop_loss_distance
            
            # Use the smaller of calculated position size or maximum allowed
            final_position_size = min(position_size, max_position_size)
            
            return {
                'success': True,
                'position_size': final_position_size,
                'available_cash': available_cash,
                'risk_amount': risk_amount,
                'risk_percentage': risk_per_trade * 100,
                'stop_loss_distance': stop_loss_distance,
                'max_position_value': max_position_value,
                'position_limited_by': 'risk' if position_size <= max_position_size else 'cash_available'
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def validate_trade_affordability(self, ticker, quantity, price):
        """
        Validate if a trade can be afforded with current balance.
        
        Args:
            ticker (str): Stock ticker
            quantity (float): Number of shares
            price (float): Price per share
        
        Returns:
            dict: Validation results
        """
        try:
            available_cash = self.get_available_cash()
            trade_value = quantity * price
            
            if trade_value > available_cash:
                return {
                    'success': False,
                    'affordable': False,
                    'available_cash': available_cash,
                    'required_cash': trade_value,
                    'shortage': trade_value - available_cash,
                    'message': f"Insufficient funds: Need R${trade_value:,.2f}, Available R${available_cash:,.2f}"
                }
            
            return {
                'success': True,
                'affordable': True,
                'available_cash': available_cash,
                'required_cash': trade_value,
                'remaining_cash': available_cash - trade_value,
                'cash_utilization': (trade_value / available_cash) * 100
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_balance_summary(self):
        """Get comprehensive balance and portfolio summary."""
        balance_info = self.get_current_balance()
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'current_balance': balance_info['balance'],
            'balance_source': balance_info['source'],
            'balance_confidence': balance_info['confidence'],
            'available_cash': self.get_available_cash(),
            'initial_balance': self.initial_balance
        }
        
        # Add calculated metrics if available
        if balance_info['source'] == 'calculation' and 'details' in balance_info:
            details = balance_info['details']
            summary.update({
                'total_trades': details.get('total_trades', 0),
                'daily_pnl': details.get('daily_pnl', 0.0),
                'total_invested': details.get('total_invested', 0.0),
                'total_realized': details.get('total_realized', 0.0),
                'net_pnl': details.get('total_realized', 0.0) - details.get('total_invested', 0.0),
                'return_percentage': ((balance_info['balance'] - self.initial_balance) / self.initial_balance) * 100
            })
        
        return summary

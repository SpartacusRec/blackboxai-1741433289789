import ccxt
import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExchangeInterface:
    def __init__(self, exchange_id='binance', api_key=None, api_secret=None):
        """Initialize exchange interface"""
        self.exchange_id = exchange_id
        self.exchange_class = getattr(ccxt, exchange_id)
        self.exchange = self.exchange_class({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot'
            }
        })
        
    def fetch_historical_data(self, symbol='DOGE/IDR', timeframe='1h', limit=1000):
        """Fetch historical OHLCV data"""
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            return df
        except Exception as e:
            logger.error(f"Error fetching historical data: {str(e)}")
            raise
    
    def get_current_price(self, symbol='DOGE/IDR'):
        """Get current price for a symbol"""
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error fetching current price: {str(e)}")
            raise
    
    def get_balance(self, currency='DOGE'):
        """Get balance for a specific currency"""
        try:
            balance = self.exchange.fetch_balance()
            return balance[currency] if currency in balance else None
        except Exception as e:
            logger.error(f"Error fetching balance: {str(e)}")
            raise
    
    def create_order(self, symbol='DOGE/IDR', order_type='limit', side='buy', amount=None, price=None):
        """Create a new order"""
        try:
            if not amount:
                raise ValueError("Amount must be specified")
            
            if order_type == 'limit' and not price:
                raise ValueError("Price must be specified for limit orders")
            
            order = self.exchange.create_order(
                symbol=symbol,
                type=order_type,
                side=side,
                amount=amount,
                price=price
            )
            logger.info(f"Order created: {order}")
            return order
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise
    
    def cancel_order(self, order_id, symbol='DOGE/IDR'):
        """Cancel an existing order"""
        try:
            return self.exchange.cancel_order(order_id, symbol)
        except Exception as e:
            logger.error(f"Error canceling order: {str(e)}")
            raise
    
    def get_open_orders(self, symbol='DOGE/IDR'):
        """Get all open orders for a symbol"""
        try:
            return self.exchange.fetch_open_orders(symbol)
        except Exception as e:
            logger.error(f"Error fetching open orders: {str(e)}")
            raise
    
    def get_order_status(self, order_id, symbol='DOGE/IDR'):
        """Get the status of a specific order"""
        try:
            return self.exchange.fetch_order(order_id, symbol)
        except Exception as e:
            logger.error(f"Error fetching order status: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    exchange = ExchangeInterface()
    try:
        # Fetch historical data
        historical_data = exchange.fetch_historical_data()
        print("Historical data shape:", historical_data.shape)
        
        # Get current price
        current_price = exchange.get_current_price()
        print("Current DOGE/IDR price:", current_price)
        
    except Exception as e:
        logger.error(f"Error in example usage: {str(e)}")

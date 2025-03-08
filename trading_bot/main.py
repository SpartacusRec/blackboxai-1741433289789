import os
import logging
from datetime import datetime
import time
from threading import Thread

from database import DatabaseManager
from exchange_integration import ExchangeInterface
from lstm_model import LSTMPricePredictor
from trading_strategy import TradingStrategy
from dashboard import TradingDashboard

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        """Initialize the trading bot with all components"""
        # Load environment variables
        self.db_connection = os.getenv('DB_CONNECTION_STRING')
        self.api_key = os.getenv('EXCHANGE_API_KEY')
        self.api_secret = os.getenv('EXCHANGE_API_SECRET')
        self.symbol = os.getenv('TRADING_SYMBOL', 'DOGE/IDR')
        
        # Initialize components
        self.db = DatabaseManager(self.db_connection)
        self.exchange = ExchangeInterface(
            api_key=self.api_key,
            api_secret=self.api_secret
        )
        self.model = LSTMPricePredictor()
        self.strategy = TradingStrategy(symbol=self.symbol)
        self.dashboard = TradingDashboard(self.db, self.exchange)
        
        # Trading parameters
        self.running = False
        self.update_interval = 300  # 5 minutes
        
    def train_model(self):
        """Train the LSTM model with historical data"""
        try:
            # Fetch historical data
            historical_data = self.exchange.fetch_historical_data(
                symbol=self.symbol,
                timeframe='1h',
                limit=1000
            )
            
            # Prepare data for training
            X, y, scaler = self.model.prepare_data(historical_data)
            
            # Train the model
            self.model.train(X, y, epochs=50)
            
            logger.info("Model training completed")
            return scaler
            
        except Exception as e:
            logger.error(f"Error training model: {str(e)}")
            raise
    
    def make_prediction(self, scaler):
        """Make price predictions using the trained model"""
        try:
            # Get recent data for prediction
            recent_data = self.exchange.fetch_historical_data(
                symbol=self.symbol,
                timeframe='1h',
                limit=60  # Last 60 hours
            )
            
            # Prepare data
            X, _, _ = self.model.prepare_data(recent_data)
            
            # Make prediction
            prediction = self.model.predict(X[-1:])
            predicted_price = scaler.inverse_transform(prediction)[0][0]
            
            # Store prediction
            self.db.store_prediction({
                'symbol': self.symbol,
                'predicted_price': predicted_price,
                'actual_price': None,
                'prediction_horizon': 1
            })
            
            return predicted_price
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            raise
    
    def execute_trades(self, predicted_price):
        """Execute trades based on predictions and strategy"""
        try:
            current_price = self.exchange.get_current_price(self.symbol)
            balance = self.exchange.get_balance('DOGE')
            
            # Check if we should open a new position
            should_trade, side, amount = self.strategy.should_open_position(
                predicted_price,
                current_price,
                balance['free'] if balance else 0
            )
            
            if should_trade:
                # Create the order
                order = self.exchange.create_order(
                    symbol=self.symbol,
                    order_type='limit',
                    side=side,
                    amount=amount,
                    price=current_price
                )
                
                # Record the trade
                self.db.store_trade({
                    'symbol': self.symbol,
                    'order_id': order['id'],
                    'order_type': 'limit',
                    'side': side,
                    'amount': amount,
                    'price': current_price,
                    'status': 'open'
                })
                
                # Track the position
                self.strategy.open_position(
                    order['id'],
                    side,
                    amount,
                    current_price
                )
            
            # Update existing positions
            self.strategy.update_position_tracking(current_price)
            
        except Exception as e:
            logger.error(f"Error executing trades: {str(e)}")
            raise
    
    def trading_loop(self):
        """Main trading loop"""
        try:
            # Initial model training
            scaler = self.train_model()
            
            while self.running:
                # Make prediction
                predicted_price = self.make_prediction(scaler)
                
                # Execute trades based on prediction
                self.execute_trades(predicted_price)
                
                # Store historical data
                historical_data = self.exchange.fetch_historical_data(
                    symbol=self.symbol,
                    timeframe='1h',
                    limit=1
                )
                self.db.store_historical_data(historical_data, self.symbol)
                
                # Wait for next update
                time.sleep(self.update_interval)
                
        except Exception as e:
            logger.error(f"Error in trading loop: {str(e)}")
            self.running = False
    
    def start(self):
        """Start the trading bot"""
        try:
            self.running = True
            
            # Start trading loop in a separate thread
            trading_thread = Thread(target=self.trading_loop)
            trading_thread.start()
            
            # Start dashboard
            self.dashboard.run_server()
            
        except Exception as e:
            logger.error(f"Error starting trading bot: {str(e)}")
            self.running = False
    
    def stop(self):
        """Stop the trading bot"""
        self.running = False

if __name__ == "__main__":
    # Create and start the trading bot
    bot = TradingBot()
    bot.start()

import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, Float, String, DateTime, MetaData
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, connection_string):
        """Initialize database connection
        
        Args:
            connection_string (str): SQL Server connection string
            Example: 'mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server'
        """
        self.engine = create_engine(connection_string)
        self.metadata = MetaData()
        self.Session = sessionmaker(bind=self.engine)
        
        # Define tables
        self.historical_prices = Table(
            'historical_prices', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('timestamp', DateTime),
            Column('symbol', String(20)),
            Column('open', Float),
            Column('high', Float),
            Column('low', Float),
            Column('close', Float),
            Column('volume', Float)
        )
        
        self.trades = Table(
            'trades', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('timestamp', DateTime),
            Column('symbol', String(20)),
            Column('order_id', String(50)),
            Column('order_type', String(20)),
            Column('side', String(10)),
            Column('amount', Float),
            Column('price', Float),
            Column('status', String(20))
        )
        
        self.predictions = Table(
            'predictions', self.metadata,
            Column('id', Integer, primary_key=True),
            Column('timestamp', DateTime),
            Column('symbol', String(20)),
            Column('predicted_price', Float),
            Column('actual_price', Float),
            Column('prediction_horizon', Integer)
        )
        
        # Create tables if they don't exist
        self.metadata.create_all(self.engine)
    
    def store_historical_data(self, df, symbol):
        """Store historical price data"""
        try:
            df = df.reset_index()
            df['symbol'] = symbol
            df.to_sql('historical_prices', self.engine, if_exists='append', index=False)
            logger.info(f"Stored historical data for {symbol}")
        except Exception as e:
            logger.error(f"Error storing historical data: {str(e)}")
            raise
    
    def store_trade(self, trade_data):
        """Store trade information"""
        try:
            session = self.Session()
            session.execute(
                self.trades.insert(),
                [{
                    'timestamp': datetime.now(),
                    'symbol': trade_data['symbol'],
                    'order_id': trade_data['order_id'],
                    'order_type': trade_data['order_type'],
                    'side': trade_data['side'],
                    'amount': trade_data['amount'],
                    'price': trade_data['price'],
                    'status': trade_data['status']
                }]
            )
            session.commit()
            logger.info(f"Stored trade data for order {trade_data['order_id']}")
        except Exception as e:
            logger.error(f"Error storing trade data: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()
    
    def store_prediction(self, prediction_data):
        """Store price prediction"""
        try:
            session = self.Session()
            session.execute(
                self.predictions.insert(),
                [{
                    'timestamp': datetime.now(),
                    'symbol': prediction_data['symbol'],
                    'predicted_price': prediction_data['predicted_price'],
                    'actual_price': prediction_data.get('actual_price', None),
                    'prediction_horizon': prediction_data['prediction_horizon']
                }]
            )
            session.commit()
            logger.info(f"Stored prediction data for {prediction_data['symbol']}")
        except Exception as e:
            logger.error(f"Error storing prediction data: {str(e)}")
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_historical_data(self, symbol, start_date=None, end_date=None):
        """Retrieve historical price data"""
        try:
            query = f"SELECT * FROM historical_prices WHERE symbol = '{symbol}'"
            if start_date:
                query += f" AND timestamp >= '{start_date}'"
            if end_date:
                query += f" AND timestamp <= '{end_date}'"
            query += " ORDER BY timestamp"
            
            df = pd.read_sql(query, self.engine)
            return df
        except Exception as e:
            logger.error(f"Error retrieving historical data: {str(e)}")
            raise
    
    def get_recent_trades(self, symbol, limit=100):
        """Retrieve recent trades"""
        try:
            query = f"""
                SELECT * FROM trades 
                WHERE symbol = '{symbol}'
                ORDER BY timestamp DESC 
                LIMIT {limit}
            """
            df = pd.read_sql(query, self.engine)
            return df
        except Exception as e:
            logger.error(f"Error retrieving recent trades: {str(e)}")
            raise
    
    def get_prediction_accuracy(self, symbol, days=30):
        """Calculate prediction accuracy for the last N days"""
        try:
            query = f"""
                SELECT 
                    AVG(ABS(predicted_price - actual_price) / actual_price) * 100 as avg_error
                FROM predictions
                WHERE symbol = '{symbol}'
                    AND timestamp >= DATEADD(day, -{days}, GETDATE())
                    AND actual_price IS NOT NULL
            """
            result = pd.read_sql(query, self.engine)
            return result['avg_error'].iloc[0] if not result.empty else None
        except Exception as e:
            logger.error(f"Error calculating prediction accuracy: {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    connection_string = 'mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server'
    db = DatabaseManager(connection_string)
    
    # Example: Store trade data
    trade_data = {
        'symbol': 'DOGE/IDR',
        'order_id': '12345',
        'order_type': 'limit',
        'side': 'buy',
        'amount': 1000,
        'price': 2000,
        'status': 'completed'
    }
    
    try:
        db.store_trade(trade_data)
        print("Trade data stored successfully")
    except Exception as e:
        print(f"Error: {str(e)}")

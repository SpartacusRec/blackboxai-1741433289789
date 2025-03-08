import numpy as np
from datetime import datetime
import logging
from typing import Dict, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingStrategy:
    def __init__(self, 
                 symbol: str = 'DOGE/IDR',
                 prediction_threshold: float = 0.02,  # 2% price movement threshold
                 position_size: float = 0.1,  # 10% of available balance
                 stop_loss: float = 0.05,  # 5% stop loss
                 take_profit: float = 0.1,  # 10% take profit
                 max_positions: int = 3):  # Maximum number of open positions
        """
        Initialize trading strategy parameters
        
        Args:
            symbol: Trading pair symbol
            prediction_threshold: Minimum predicted price movement to trigger trade
            position_size: Percentage of available balance to use per trade
            stop_loss: Stop loss percentage
            take_profit: Take profit percentage
            max_positions: Maximum number of concurrent open positions
        """
        self.symbol = symbol
        self.prediction_threshold = prediction_threshold
        self.position_size = position_size
        self.stop_loss = stop_loss
        self.take_profit = take_profit
        self.max_positions = max_positions
        self.open_positions: Dict = {}
    
    def calculate_position_size(self, available_balance: float, current_price: float) -> float:
        """Calculate the position size based on available balance"""
        return (available_balance * self.position_size) / current_price
    
    def should_open_position(self, 
                           predicted_price: float, 
                           current_price: float, 
                           available_balance: float) -> Tuple[bool, str, Optional[float]]:
        """
        Determine if a new position should be opened
        
        Returns:
            Tuple of (should_trade, trade_side, trade_amount)
        """
        try:
            # Check if we can open new positions
            if len(self.open_positions) >= self.max_positions:
                return False, "", None
            
            # Calculate price movement percentage
            price_movement = (predicted_price - current_price) / current_price
            
            # If predicted movement is significant enough
            if abs(price_movement) >= self.prediction_threshold:
                # Calculate position size
                position_size = self.calculate_position_size(available_balance, current_price)
                
                if price_movement > 0:
                    return True, "buy", position_size
                else:
                    return True, "sell", position_size
                    
            return False, "", None
            
        except Exception as e:
            logger.error(f"Error in should_open_position: {str(e)}")
            return False, "", None
    
    def should_close_position(self, 
                            position_id: str, 
                            entry_price: float, 
                            current_price: float) -> bool:
        """Determine if a position should be closed based on stop loss or take profit"""
        try:
            if position_id not in self.open_positions:
                return False
            
            position = self.open_positions[position_id]
            price_change = (current_price - entry_price) / entry_price
            
            # Check stop loss
            if position['side'] == 'buy' and price_change <= -self.stop_loss:
                logger.info(f"Stop loss triggered for position {position_id}")
                return True
                
            if position['side'] == 'sell' and price_change >= self.stop_loss:
                logger.info(f"Stop loss triggered for position {position_id}")
                return True
            
            # Check take profit
            if position['side'] == 'buy' and price_change >= self.take_profit:
                logger.info(f"Take profit triggered for position {position_id}")
                return True
                
            if position['side'] == 'sell' and price_change <= -self.take_profit:
                logger.info(f"Take profit triggered for position {position_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in should_close_position: {str(e)}")
            return False
    
    def open_position(self, 
                     order_id: str, 
                     side: str, 
                     amount: float, 
                     price: float) -> None:
        """Record a new open position"""
        try:
            self.open_positions[order_id] = {
                'side': side,
                'amount': amount,
                'entry_price': price,
                'entry_time': datetime.now()
            }
            logger.info(f"Opened new {side} position: {order_id}")
        except Exception as e:
            logger.error(f"Error opening position: {str(e)}")
    
    def close_position(self, order_id: str) -> None:
        """Close an open position"""
        try:
            if order_id in self.open_positions:
                position = self.open_positions.pop(order_id)
                logger.info(f"Closed position: {order_id}")
                return position
            return None
        except Exception as e:
            logger.error(f"Error closing position: {str(e)}")
            return None
    
    def get_position_status(self, order_id: str) -> Dict:
        """Get the current status of a position"""
        return self.open_positions.get(order_id, None)
    
    def calculate_pnl(self, 
                     entry_price: float, 
                     exit_price: float, 
                     amount: float, 
                     side: str) -> float:
        """Calculate profit/loss for a position"""
        try:
            if side == 'buy':
                return (exit_price - entry_price) * amount
            else:  # sell
                return (entry_price - exit_price) * amount
        except Exception as e:
            logger.error(f"Error calculating PnL: {str(e)}")
            return 0.0

    def update_position_tracking(self, current_price: float) -> None:
        """Update tracking of all open positions"""
        try:
            positions_to_close = []
            
            for order_id, position in self.open_positions.items():
                if self.should_close_position(order_id, position['entry_price'], current_price):
                    positions_to_close.append(order_id)
            
            # Close positions that hit stop loss or take profit
            for order_id in positions_to_close:
                self.close_position(order_id)
                
        except Exception as e:
            logger.error(f"Error updating position tracking: {str(e)}")

if __name__ == "__main__":
    # Example usage
    strategy = TradingStrategy()
    
    # Test strategy logic
    predicted_price = 2100  # IDR
    current_price = 2000    # IDR
    available_balance = 1000000  # IDR
    
    should_trade, side, amount = strategy.should_open_position(
        predicted_price, current_price, available_balance
    )
    
    if should_trade:
        print(f"Opening {side} position with amount: {amount}")
        strategy.open_position("test_order", side, amount, current_price)

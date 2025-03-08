# DOGE/IDR Trading Bot

An AI-powered cryptocurrency trading bot specifically designed for the DOGE/IDR trading pair. The bot uses LSTM (Long Short-Term Memory) neural networks for price prediction and implements automated trading strategies.

## Features

- **AI Price Prediction**: Uses LSTM neural networks to predict future price movements
- **Exchange Integration**: Connects to cryptocurrency exchanges using CCXT library
- **Database Storage**: Stores historical data and transactions in MSSQL
- **Automated Trading**: Implements trading strategies based on AI predictions
- **Real-time Monitoring**: Provides a web-based dashboard using Dash
- **Docker Support**: Easy deployment using Docker containers

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- MSSQL Server
- Exchange API credentials
- ODBC Driver 17 for SQL Server

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd trading_bot
```

2. Create and configure the environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Build and run using Docker:
```bash
docker-compose up --build
```

## Project Structure

- `lstm_model.py`: LSTM model implementation for price prediction
- `exchange_integration.py`: CCXT-based exchange interface
- `database.py`: MSSQL database management
- `trading_strategy.py`: Trading logic and position management
- `dashboard.py`: Real-time monitoring dashboard
- `main.py`: Main application entry point

## Configuration

Configure the following in your `.env` file:

### Database Configuration
- `DB_USER`: Database username
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host address
- `DB_NAME`: Database name

### Exchange Configuration
- `EXCHANGE_API_KEY`: Your exchange API key
- `EXCHANGE_API_SECRET`: Your exchange API secret

### Trading Configuration
- `TRADING_SYMBOL`: Trading pair (default: DOGE/IDR)
- `UPDATE_INTERVAL`: Bot update interval in seconds
- `PREDICTION_THRESHOLD`: Minimum price movement threshold
- `POSITION_SIZE`: Position size as fraction of balance
- `STOP_LOSS`: Stop loss percentage
- `TAKE_PROFIT`: Take profit percentage
- `MAX_POSITIONS`: Maximum number of open positions

## Dashboard

The trading dashboard is accessible at `http://localhost:8050` and provides:

- Real-time price monitoring
- Trading performance metrics
- Open positions overview
- Historical trade data
- Price predictions visualization

## Trading Strategy

The bot implements a trading strategy based on:

1. LSTM price predictions
2. Configurable entry/exit thresholds
3. Position size management
4. Stop-loss and take-profit orders
5. Maximum position limits

## Database Schema

The MSSQL database includes tables for:

- Historical price data
- Trading transactions
- Price predictions
- Performance metrics

## Safety Features

- Stop-loss orders for risk management
- Position size limits
- Maximum open positions limit
- Error handling and logging
- Automatic error recovery

## Monitoring and Logging

- Real-time dashboard monitoring
- Detailed logging system
- Performance metrics tracking
- Error reporting

## Development

To run the bot in development mode:

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the bot:
```bash
python main.py
```

## Production Deployment

For production deployment:

1. Configure environment variables in `.env`
2. Build and run using Docker Compose:
```bash
docker-compose up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This trading bot is for educational purposes only. Cryptocurrency trading carries significant risks. Use at your own risk.

import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingDashboard:
    def __init__(self, db_manager, exchange_interface):
        """Initialize the dashboard with database and exchange connections"""
        self.db = db_manager
        self.exchange = exchange_interface
        self.app = dash.Dash(__name__)
        self.setup_layout()
        self.setup_callbacks()
    
    def setup_layout(self):
        """Set up the dashboard layout"""
        self.app.layout = html.Div([
            # Header
            html.Div([
                html.H1('DOGE/IDR Trading Bot Dashboard',
                       style={'textAlign': 'center', 'color': '#2c3e50', 'margin': '20px'}),
                html.Hr()
            ]),
            
            # Current Price and Stats
            html.Div([
                html.Div([
                    html.H3('Current Price'),
                    html.H2(id='current-price', children='Loading...')
                ], className='stats-card'),
                
                html.Div([
                    html.H3('24h Change'),
                    html.H2(id='price-change', children='Loading...')
                ], className='stats-card'),
                
                html.Div([
                    html.H3('Prediction Accuracy'),
                    html.H2(id='prediction-accuracy', children='Loading...')
                ], className='stats-card')
            ], style={'display': 'flex', 'justifyContent': 'space-around', 'margin': '20px'}),
            
            # Price Chart
            html.Div([
                html.H3('Price History and Predictions'),
                dcc.Graph(id='price-chart'),
                dcc.Interval(
                    id='price-update',
                    interval=60*1000,  # Update every minute
                    n_intervals=0
                )
            ], style={'margin': '20px'}),
            
            # Trading History
            html.Div([
                html.H3('Recent Trades'),
                html.Div(id='trades-table')
            ], style={'margin': '20px'}),
            
            # Open Positions
            html.Div([
                html.H3('Open Positions'),
                html.Div(id='positions-table')
            ], style={'margin': '20px'}),
            
            # Performance Metrics
            html.Div([
                html.H3('Performance Metrics'),
                dcc.Graph(id='performance-chart')
            ], style={'margin': '20px'})
        ])
        
        # Add custom CSS
        self.app.index_string = '''
        <!DOCTYPE html>
        <html>
            <head>
                {%metas%}
                <title>Trading Bot Dashboard</title>
                {%css%}
                <style>
                    .stats-card {
                        background-color: white;
                        border-radius: 10px;
                        padding: 20px;
                        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                        text-align: center;
                        flex: 1;
                        margin: 0 10px;
                    }
                    body {
                        background-color: #f5f6fa;
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    }
                </style>
            </head>
            <body>
                {%app_entry%}
                <footer>
                    {%config%}
                    {%scripts%}
                    {%renderer%}
                </footer>
            </body>
        </html>
        '''
    
    def setup_callbacks(self):
        """Set up dashboard callbacks"""
        @self.app.callback(
            [Output('current-price', 'children'),
             Output('price-change', 'children'),
             Output('price-change', 'style')],
            [Input('price-update', 'n_intervals')]
        )
        def update_price(n):
            try:
                current = self.exchange.get_current_price()
                # Get 24h old price from database
                old_price = self.db.get_historical_data(
                    'DOGE/IDR',
                    start_date=(datetime.now() - timedelta(days=1))
                ).iloc[0]['close']
                
                change = ((current - old_price) / old_price) * 100
                color = 'green' if change >= 0 else 'red'
                
                return (
                    f"IDR {current:,.2f}",
                    f"{change:+.2f}%",
                    {'color': color}
                )
            except Exception as e:
                logger.error(f"Error updating price: {str(e)}")
                return "Error", "Error", {'color': 'red'}
        
        @self.app.callback(
            Output('price-chart', 'figure'),
            [Input('price-update', 'n_intervals')]
        )
        def update_price_chart(n):
            try:
                # Get historical data
                df = self.db.get_historical_data(
                    'DOGE/IDR',
                    start_date=(datetime.now() - timedelta(days=7))
                )
                
                # Get predictions
                predictions = self.db.get_prediction_accuracy('DOGE/IDR')
                
                # Create the chart
                fig = go.Figure()
                
                # Add price line
                fig.add_trace(go.Scatter(
                    x=df['timestamp'],
                    y=df['close'],
                    name='Actual Price',
                    line=dict(color='#2ecc71')
                ))
                
                # Add predictions if available
                if predictions is not None:
                    fig.add_trace(go.Scatter(
                        x=predictions['timestamp'],
                        y=predictions['predicted_price'],
                        name='Predicted Price',
                        line=dict(color='#3498db', dash='dash')
                    ))
                
                fig.update_layout(
                    title='DOGE/IDR Price History',
                    xaxis_title='Date',
                    yaxis_title='Price (IDR)',
                    template='plotly_white'
                )
                
                return fig
            except Exception as e:
                logger.error(f"Error updating price chart: {str(e)}")
                return go.Figure()
        
        @self.app.callback(
            Output('trades-table', 'children'),
            [Input('price-update', 'n_intervals')]
        )
        def update_trades_table(n):
            try:
                trades = self.db.get_recent_trades('DOGE/IDR', limit=10)
                
                if trades.empty:
                    return html.P("No recent trades")
                
                return html.Table(
                    # Header
                    [html.Tr([html.Th(col) for col in trades.columns])] +
                    # Body
                    [html.Tr([html.Td(trades.iloc[i][col]) for col in trades.columns])
                     for i in range(len(trades))]
                )
            except Exception as e:
                logger.error(f"Error updating trades table: {str(e)}")
                return html.P("Error loading trades")
    
    def run_server(self, debug=True, port=8050):
        """Run the dashboard server"""
        self.app.run_server(debug=debug, port=port)

if __name__ == '__main__':
    # Example usage
    from database import DatabaseManager
    from exchange_integration import ExchangeInterface
    
    # Initialize components
    db = DatabaseManager('your_connection_string')
    exchange = ExchangeInterface()
    
    # Create and run dashboard
    dashboard = TradingDashboard(db, exchange)
    dashboard.run_server()

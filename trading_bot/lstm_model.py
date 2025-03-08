import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

class LSTMPricePredictor:
    def __init__(self, sequence_length=60):
        self.sequence_length = sequence_length
        self.model = None
        
    def create_model(self, input_shape):
        """Create and compile the LSTM model"""
        model = Sequential([
            LSTM(50, return_sequences=True, input_shape=input_shape),
            Dropout(0.2),
            LSTM(50, return_sequences=False),
            Dropout(0.2),
            Dense(25),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        self.model = model
        return model
    
    def prepare_data(self, data, target_column='close'):
        """Prepare data for LSTM model"""
        dataset = data[target_column].values
        dataset = dataset.reshape(-1, 1)
        
        # Normalize the data
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler(feature_range=(0, 1))
        dataset = scaler.fit_transform(dataset)
        
        # Create sequences
        X, y = [], []
        for i in range(len(dataset) - self.sequence_length):
            X.append(dataset[i:(i + self.sequence_length), 0])
            y.append(dataset[i + self.sequence_length, 0])
        
        X = np.array(X)
        y = np.array(y)
        
        # Reshape X to be [samples, time steps, features]
        X = np.reshape(X, (X.shape[0], X.shape[1], 1))
        
        return X, y, scaler
    
    def train(self, X, y, epochs=50, batch_size=32, validation_split=0.1):
        """Train the model"""
        if self.model is None:
            self.create_model((X.shape[1], 1))
        
        history = self.model.fit(
            X, y,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            verbose=1
        )
        return history
    
    def predict(self, X):
        """Make predictions"""
        return self.model.predict(X)
    
    def save_model(self, filepath):
        """Save the model"""
        self.model.save(filepath)
    
    def load_model(self, filepath):
        """Load a saved model"""
        from tensorflow.keras.models import load_model
        self.model = load_model(filepath)

#!/usr/bin/env python3
"""
Battery Health Analysis Starter Script
Uses PyTorch for voltage-based State of Health (SOH) prediction

Expected data format:
- CSV with columns: cycle_number, timestamp, voltage, current, temperature, capacity (optional label)
- Or: NPY file with shape (n_cycles, timesteps, features)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION - Modify these for your setup
# =============================================================================

class Config:
    """Configuration for battery analysis"""
    # Data paths
    DATA_PATH = "battery_data.csv"  # or "battery_data.npy"
    OUTPUT_DIR = "battery_analysis_output"
    
    # Data parameters
    WINDOW_SIZE = 100  # Timesteps per sequence
    STRIDE = 10        # Overlap between sequences
    FEATURE_COLS = ['voltage', 'current', 'temperature']  # Input features
    TARGET_COL = 'capacity'  # What we're predicting (SOH proxy)
    CYCLE_COL = 'cycle_number'
    
    # Model parameters
    MODEL_TYPE = 'lstm'  # Options: 'lstm', 'cnn', 'autoencoder'
    HIDDEN_SIZE = 64
    NUM_LAYERS = 2
    DROPOUT = 0.2
    
    # Training parameters
    BATCH_SIZE = 32
    EPOCHS = 100
    LEARNING_RATE = 1e-3
    EARLY_STOPPING_PATIENCE = 15
    
    # Device
    DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

print(f"Using device: {Config.DEVICE}")

# =============================================================================
# DATA LOADING AND PREPROCESSING
# =============================================================================

class BatteryDataset(Dataset):
    """PyTorch Dataset for battery voltage sequences"""
    
    def __init__(self, sequences, targets=None):
        self.sequences = torch.FloatTensor(sequences)
        self.targets = torch.FloatTensor(targets) if targets is not None else None
    
    def __len__(self):
        return len(self.sequences)
    
    def __getitem__(self, idx):
        if self.targets is not None:
            return self.sequences[idx], self.targets[idx]
        return self.sequences[idx]


def load_battery_data(filepath):
    """
    Load battery data from CSV or NPY
    
    Returns:
        df: DataFrame with columns [cycle_number, voltage, current, temperature, capacity]
    """
    filepath = Path(filepath)
    
    if filepath.suffix == '.csv':
        df = pd.read_csv(filepath)
    elif filepath.suffix == '.npy':
        data = np.load(filepath)
        # Assuming shape: (n_cycles, timesteps, features)
        # You'll need to adapt this to your specific format
        print(f"Loaded NPY with shape: {data.shape}")
        df = None  # Convert to DataFrame based on your structure
    else:
        raise ValueError(f"Unsupported file format: {filepath.suffix}")
    
    print(f"Data loaded: {len(df)} rows" if df is not None else "NPY loaded")
    return df


def create_sequences(df, config):
    """
    Create sliding window sequences from battery cycles
    
    Args:
        df: DataFrame with battery measurements
        config: Config object
    
    Returns:
        X: Array of shape (n_sequences, window_size, n_features)
        y: Array of shape (n_sequences,) - capacity/SOH labels
        cycle_ids: Array indicating which cycle each sequence belongs to
    """
    sequences = []
    targets = []
    cycle_ids = []
    
    # Group by cycle
    for cycle_num, cycle_df in df.groupby(config.CYCLE_COL):
        if len(cycle_df) < config.WINDOW_SIZE:
            continue
        
        features = cycle_df[config.FEATURE_COLS].values
        target = cycle_df[config.TARGET_COL].iloc[-1]  # Final capacity of cycle
        
        # Create sliding windows
        for i in range(0, len(features) - config.WINDOW_SIZE + 1, config.STRIDE):
            seq = features[i:i + config.WINDOW_SIZE]
            sequences.append(seq)
            targets.append(target)
            cycle_ids.append(cycle_num)
    
    return np.array(sequences), np.array(targets), np.array(cycle_ids)


def engineer_features(sequences):
    """
    Add engineered features to sequences
    
    Adds:
    - dV/dt (voltage change rate)
    - Cumulative discharge/charge
    - Voltage statistics
    """
    enhanced = []
    
    for seq in sequences:
        # Original features: [voltage, current, temperature]
        voltage = seq[:, 0]
        current = seq[:, 1]
        temperature = seq[:, 2]
        
        # Feature engineering
        dv_dt = np.gradient(voltage)  # Voltage change rate
        cumsum_current = np.cumsum(current)  # Accumulated charge
        voltage_mean = np.full_like(voltage, np.mean(voltage))
        voltage_std = np.full_like(voltage, np.std(voltage))
        
        # Stack all features
        enhanced_seq = np.column_stack([
            seq,           # Original: voltage, current, temp
            dv_dt,         # Rate of change
            cumsum_current, # Accumulated charge
            voltage_mean,  # Statistical features
            voltage_std
        ])
        enhanced.append(enhanced_seq)
    
    return np.array(enhanced)


# =============================================================================
# MODEL ARCHITECTURES
# =============================================================================

class BatteryLSTM(nn.Module):
    """LSTM for SOH prediction from voltage sequences"""
    
    def __init__(self, input_size, hidden_size=64, num_layers=2, dropout=0.2):
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_size // 2, 1)  # Predict SOH/capacity
        )
    
    def forward(self, x):
        # x shape: (batch, seq_len, features)
        lstm_out, (hidden, cell) = self.lstm(x)
        # Take last timestep output
        last_output = lstm_out[:, -1, :]
        return self.fc(last_output).squeeze(-1)


class BatteryCNN(nn.Module):
    """1D CNN for voltage curve analysis"""
    
    def __init__(self, input_size, seq_len, dropout=0.2):
        super().__init__()
        
        self.conv_layers = nn.Sequential(
            nn.Conv1d(input_size, 32, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(32, 64, kernel_size=5, padding=2),
            nn.ReLU(),
            nn.MaxPool1d(2),
            nn.Conv1d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.AdaptiveAvgPool1d(1)  # Global average pooling
        )
        
        self.fc = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1)
        )
    
    def forward(self, x):
        # x shape: (batch, seq_len, features) -> (batch, features, seq_len)
        x = x.permute(0, 2, 1)
        conv_out = self.conv_layers(x)
        conv_out = conv_out.squeeze(-1)  # (batch, 128)
        return self.fc(conv_out).squeeze(-1)


class BatteryAutoencoder(nn.Module):
    """Autoencoder for anomaly detection in voltage profiles"""
    
    def __init__(self, input_size, seq_len, latent_dim=16):
        super().__init__()
        
        # Encoder
        self.encoder = nn.Sequential(
            nn.Linear(input_size * seq_len, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, latent_dim)
        )
        
        # Decoder
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 128),
            nn.ReLU(),
            nn.Linear(128, input_size * seq_len)
        )
        
        self.input_size = input_size
        self.seq_len = seq_len
    
    def forward(self, x):
        batch_size = x.size(0)
        x_flat = x.view(batch_size, -1)
        
        encoded = self.encoder(x_flat)
        decoded = self.decoder(encoded)
        
        return decoded.view(batch_size, self.seq_len, self.input_size)
    
    def get_reconstruction_error(self, x):
        """Get MSE reconstruction error for anomaly detection"""
        reconstructed = self.forward(x)
        error = torch.mean((x - reconstructed) ** 2, dim=(1, 2))
        return error


# =============================================================================
# TRAINING AND EVALUATION
# =============================================================================

class EarlyStopping:
    """Early stopping to prevent overfitting"""
    
    def __init__(self, patience=10, min_delta=1e-4):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
    
    def __call__(self, val_loss):
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0


def train_model(model, train_loader, val_loader, config):
    """Train the model with early stopping"""
    
    model = model.to(config.DEVICE)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=config.LEARNING_RATE)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
    early_stopping = EarlyStopping(patience=config.EARLY_STOPPING_PATIENCE)
    
    train_losses = []
    val_losses = []
    
    print(f"\nTraining {config.MODEL_TYPE.upper()} model...")
    print(f"Epochs: {config.EPOCHS}, Batch size: {config.BATCH_SIZE}")
    
    for epoch in range(config.EPOCHS):
        # Training
        model.train()
        train_loss = 0
        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(config.DEVICE)
            batch_y = batch_y.to(config.DEVICE)
            
            optimizer.zero_grad()
            
            if config.MODEL_TYPE == 'autoencoder':
                # Unsupervised: reconstruct input
                output = model(batch_x)
                loss = criterion(output, batch_x)
            else:
                # Supervised: predict target
                output = model(batch_x)
                loss = criterion(output, batch_y)
            
            loss.backward()
            optimizer.step()
            train_loss += loss.item()
        
        train_loss /= len(train_loader)
        train_losses.append(train_loss)
        
        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(config.DEVICE)
                batch_y = batch_y.to(config.DEVICE)
                
                if config.MODEL_TYPE == 'autoencoder':
                    output = model(batch_x)
                    loss = criterion(output, batch_x)
                else:
                    output = model(batch_x)
                    loss = criterion(output, batch_y)
                
                val_loss += loss.item()
        
        val_loss /= len(val_loader)
        val_losses.append(val_loss)
        
        scheduler.step(val_loss)
        early_stopping(val_loss)
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{config.EPOCHS} - Train Loss: {train_loss:.6f}, Val Loss: {val_loss:.6f}")
        
        if early_stopping.early_stop:
            print(f"Early stopping at epoch {epoch+1}")
            break
    
    return model, train_losses, val_losses


def evaluate_model(model, test_loader, config):
    """Evaluate model and return predictions"""
    
    model.eval()
    predictions = []
    actuals = []
    
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            batch_x = batch_x.to(config.DEVICE)
            output = model(batch_x)
            
            if config.MODEL_TYPE == 'autoencoder':
                # Return reconstruction error as health metric
                errors = model.get_reconstruction_error(batch_x)
                predictions.extend(errors.cpu().numpy())
            else:
                predictions.extend(output.cpu().numpy())
            
            actuals.extend(batch_y.numpy())
    
    return np.array(predictions), np.array(actuals)


# =============================================================================
# VISUALIZATION
# =============================================================================

def plot_training_history(train_losses, val_losses, output_dir):
    """Plot training curves"""
    plt.figure(figsize=(10, 5))
    plt.plot(train_losses, label='Train Loss')
    plt.plot(val_losses, label='Validation Loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.title('Training History')
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{output_dir}/training_history.png", dpi=150)
    plt.close()


def plot_predictions(y_true, y_pred, output_dir):
    """Plot predicted vs actual capacity/SOH"""
    plt.figure(figsize=(10, 5))
    
    # Scatter plot
    plt.subplot(1, 2, 1)
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--')
    plt.xlabel('Actual Capacity')
    plt.ylabel('Predicted Capacity')
    plt.title('Prediction Accuracy')
    plt.grid(True)
    
    # Time series
    plt.subplot(1, 2, 2)
    sort_idx = np.argsort(y_true)
    plt.plot(y_true[sort_idx], label='Actual', alpha=0.7)
    plt.plot(y_pred[sort_idx], label='Predicted', alpha=0.7)
    plt.xlabel('Sample (sorted by actual)')
    plt.ylabel('Capacity')
    plt.title('Capacity Degradation Prediction')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/predictions.png", dpi=150)
    plt.close()


def plot_voltage_profiles(df, output_dir, n_samples=5):
    """Plot sample voltage discharge curves"""
    plt.figure(figsize=(12, 6))
    
    cycles = df[Config.CYCLE_COL].unique()[:n_samples]
    for cycle in cycles:
        cycle_data = df[df[Config.CYCLE_COL] == cycle]
        plt.plot(cycle_data.index, cycle_data['voltage'], label=f'Cycle {cycle}')
    
    plt.xlabel('Time/Step')
    plt.ylabel('Voltage (V)')
    plt.title('Sample Voltage Profiles')
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{output_dir}/voltage_profiles.png", dpi=150)
    plt.close()


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def main():
    """Main execution pipeline"""
    
    # Create output directory
    Path(Config.OUTPUT_DIR).mkdir(exist_ok=True)
    
    print("=" * 60)
    print("BATTERY HEALTH ANALYSIS PIPELINE")
    print("=" * 60)
    
    # -------------------------------------------------------------------------
    # STEP 1: Load Data
    # -------------------------------------------------------------------------
    print("\n[1/6] Loading data...")
    try:
        df = load_battery_data(Config.DATA_PATH)
        print(f"   Data columns: {list(df.columns)}")
        print(f"   Cycles: {df[Config.CYCLE_COL].nunique()}")
        print(f"   Samples: {len(df)}")
    except Exception as e:
        print(f"   ERROR: Could not load data - {e}")
        print("   Please check DATA_PATH in Config class")
        return
    
    # -------------------------------------------------------------------------
    # STEP 2: Create Sequences
    # -------------------------------------------------------------------------
    print("\n[2/6] Creating sequences...")
    X, y, cycles = create_sequences(df, Config)
    print(f"   Sequences created: {len(X)}")
    print(f"   Sequence shape: {X.shape}")
    print(f"   Target shape: {y.shape}")
    
    # -------------------------------------------------------------------------
    # STEP 3: Feature Engineering
    # -------------------------------------------------------------------------
    print("\n[3/6] Engineering features...")
    X = engineer_features(X)
    print(f"   Enhanced shape: {X.shape}")
    print(f"   Features: voltage, current, temp, dV/dt, cumsum_current, v_mean, v_std")
    
    # -------------------------------------------------------------------------
    # STEP 4: Preprocessing
    # -------------------------------------------------------------------------
    print("\n[4/6] Preprocessing...")
    
    # Normalize features per feature dimension
    n_samples, seq_len, n_features = X.shape
    X_reshaped = X.reshape(-1, n_features)
    
    scaler_X = StandardScaler()
    X_scaled = scaler_X.fit_transform(X_reshaped).reshape(n_samples, seq_len, n_features)
    
    # Normalize targets
    scaler_y = MinMaxScaler()
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y_scaled, test_size=0.2, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42
    )
    
    print(f"   Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    # Create dataloaders
    train_dataset = BatteryDataset(X_train, y_train)
    val_dataset = BatteryDataset(X_val, y_val)
    test_dataset = BatteryDataset(X_test, y_test)
    
    train_loader = DataLoader(train_dataset, batch_size=Config.BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=Config.BATCH_SIZE)
    test_loader = DataLoader(test_dataset, batch_size=Config.BATCH_SIZE)
    
    # -------------------------------------------------------------------------
    # STEP 5: Model Training
    # -------------------------------------------------------------------------
    print("\n[5/6] Training model...")
    
    input_size = X.shape[2]  # Number of features
    seq_len = X.shape[1]
    
    if Config.MODEL_TYPE == 'lstm':
        model = BatteryLSTM(input_size, Config.HIDDEN_SIZE, Config.NUM_LAYERS, Config.DROPOUT)
    elif Config.MODEL_TYPE == 'cnn':
        model = BatteryCNN(input_size, seq_len, Config.DROPOUT)
    elif Config.MODEL_TYPE == 'autoencoder':
        model = BatteryAutoencoder(input_size, seq_len)
    else:
        raise ValueError(f"Unknown model type: {Config.MODEL_TYPE}")
    
    print(f"   Model parameters: {sum(p.numel() for p in model.parameters()):,}")
    
    model, train_losses, val_losses = train_model(model, train_loader, val_loader, Config)
    
    # -------------------------------------------------------------------------
    # STEP 6: Evaluation and Visualization
    # -------------------------------------------------------------------------
    print("\n[6/6] Evaluating and saving results...")
    
    y_pred, y_true = evaluate_model(model, test_loader, Config)
    
    # Inverse transform predictions
    y_true_orig = scaler_y.inverse_transform(y_true.reshape(-1, 1)).flatten()
    
    if Config.MODEL_TYPE != 'autoencoder':
        y_pred_orig = scaler_y.inverse_transform(y_pred.reshape(-1, 1)).flatten()
        mae = np.mean(np.abs(y_true_orig - y_pred_orig))
        rmse = np.sqrt(np.mean((y_true_orig - y_pred_orig) ** 2))
        
        print(f"   MAE: {mae:.4f}")
        print(f"   RMSE: {rmse:.4f}")
        
        plot_predictions(y_true_orig, y_pred_orig, Config.OUTPUT_DIR)
    else:
        print(f"   Mean reconstruction error: {np.mean(y_pred):.6f}")
        # For autoencoder, higher error = more anomalous (worse health)
    
    # Save visualizations
    plot_training_history(train_losses, val_losses, Config.OUTPUT_DIR)
    plot_voltage_profiles(df, Config.OUTPUT_DIR)
    
    # Save model
    torch.save({
        'model_state_dict': model.state_dict(),
        'config': vars(Config),
        'scaler_X': scaler_X,
        'scaler_y': scaler_y
    }, f"{Config.OUTPUT_DIR}/model.pt")
    
    print(f"\n✓ Results saved to: {Config.OUTPUT_DIR}/")
    print(f"  - model.pt (trained model)")
    print(f"  - training_history.png")
    print(f"  - predictions.png")
    print(f"  - voltage_profiles.png")
    
    # Save config for reference
    with open(f"{Config.OUTPUT_DIR}/config.json", 'w') as f:
        config_dict = {k: str(v) if isinstance(v, torch.device) else v 
                      for k, v in vars(Config).items()}
        json.dump(config_dict, f, indent=2)
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)


# =============================================================================
# INFERENCE FUNCTION (for later use)
# =============================================================================

def predict_soh(model_path, new_data_path):
    """
    Load trained model and predict SOH for new battery data
    
    Usage:
        predictions = predict_soh('battery_analysis_output/model.pt', 'new_data.csv')
    """
    checkpoint = torch.load(model_path, map_location='cpu')
    scaler_X = checkpoint['scaler_X']
    scaler_y = checkpoint['scaler_y']
    
    # Load and preprocess new data
    df = load_battery_data(new_data_path)
    X, _, _ = create_sequences(df, Config)
    X = engineer_features(X)
    
    # Scale
    n_samples, seq_len, n_features = X.shape
    X_scaled = scaler_X.transform(X.reshape(-1, n_features)).reshape(n_samples, seq_len, n_features)
    
    # Load model (you'll need to reconstruct based on saved config)
    # ... model reconstruction code ...
    
    # Predict
    model.eval()
    with torch.no_grad():
        predictions = model(torch.FloatTensor(X_scaled))
    
    # Inverse transform
    predictions_orig = scaler_y.inverse_transform(predictions.numpy().reshape(-1, 1))
    
    return predictions_orig


if __name__ == "__main__":
    # Check if data exists before running
    if not Path(Config.DATA_PATH).exists():
        print(f"\n⚠ DATA FILE NOT FOUND: {Config.DATA_PATH}")
        print("\nTo use this script:")
        print("1. Place your battery data in the workspace directory")
        print("2. Update Config.DATA_PATH to point to your file")
        print("3. Adjust Config.FEATURE_COLS to match your column names")
        print("4. Run: python battery_analysis.py")
        print("\nExpected data format (CSV):")
        print("  cycle_number, timestamp, voltage, current, temperature, capacity")
        print("  1, 0.0, 4.2, 0.0, 25.0, 2.0")
        print("  1, 10.0, 4.1, -1.0, 25.5, 2.0")
        print("  ...")
    else:
        main()

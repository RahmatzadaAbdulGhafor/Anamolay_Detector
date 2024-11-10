# data_stream.py
import numpy as np

def generate_data_stream():
    """Simulates a continuous data stream with regular patterns, random noise, and anomalies."""
    t = 0
    while True:
        # Regular pattern (sinusoidal)
        base = np.sin(t / 10.0)
        # Seasonal variation (sinusoidal with a different frequency)
        seasonal = 0.5 * np.sin(t / 100.0)
        # Random noise
        noise = np.random.normal(0, 0.2)
        # Randomly add an anomaly (spike)
        anomaly = np.random.choice([0, np.random.normal(5, 2)], p=[0.99, 0.01])
        yield base + seasonal + noise + anomaly
        t += 1

import numpy as np
import logging
from sklearn.ensemble import IsolationForest

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AnomalyDetector:
    def __init__(self, initial_window_size=1, growth_interval=100):
        self.initial_window_size = initial_window_size
        self.window_size = initial_window_size
        self.growth_interval = growth_interval
        self.model = self._build_model()
        self.trained = False

    def _build_model(self):
        # Build the Isolation Forest model
        model = IsolationForest(n_estimators=100, max_samples='auto', contamination=0.1, random_state=42)
        return model

    def train(self, data):
        """Train the model using normal data."""

        if len(data) < 2:
            # Ensure there is enough data for training
            raise ValueError("Insufficient data for training. Provide more data points.")

        # Reshape the data for training
        X_train = np.array(data).reshape(-1, 1)
        self.model = self._build_model()
        self.model.fit(X_train)
        self.trained = True
        logging.info("Model training completed.")

    def adjust_window_size(self, current_time_step):

        self.window_size += 1
        # """Increase window size periodically."""
        # if current_time_step % self.growth_interval == 0:
        #     self.window_size += self.growth_interval
            # No need to retrain here; training happens on full windows in this approach

    def detect(self, data_point):
        """Detect anomalies using Isolation Forest."""

        if not self.trained:
            logging.error("Model has not been trained yet.")
            return False

        try:

            # Reshape the data point for prediction
            data_point = np.array(data_point).reshape(1, -1)
            prediction = self.model.predict(data_point)
            is_anomaly = prediction[0] == -1
            if is_anomaly:
                logging.info("Anomaly detected.")
            return is_anomaly
        except Exception as e:
            logging.error(f"Error detecting anomaly: {e}")
            return False

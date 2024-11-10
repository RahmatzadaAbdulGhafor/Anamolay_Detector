# Real-Time Anomaly Detector 
This project is a real-time data stream visualisation tool which detects anomalies using Dash, Plotly, and an Isolation Forest model (for the detection algorithm). The app allows you to start, stop, and reset the data streaming, with detected anomalies highlighted on the graph.


![image](/assets/homePage.png)
## Features
- [x] Real-time data visualisation (or user input) 
  - Continuously plots incoming data on a live graph where the user can interrupt and enter their own value
  - (recommended to use small floats)

- [x] Anomaly detection using Isolation Forest 
  - Identifies outliers in the data stream, enhancing data analysis and decision-making

- [x] Start, stop, and reset controls for the data stream
  - Control the flow of data for better testing and observation of anomalies by entering your own number

- [x] Interactive graph showing data stream, with anomalies and recovered anomalies
  - allowing the user to experience a very easy-to-use interface
- [x] CSV file output
  - Allow the user to download a CSV output **[x, y, is_anomaly]**

- [] Recovered points 
  - (points that in the short term is an anomaly but becomes *normal* as data grows)

## Requirements
- Docker
- Python 3.10 (if running locally without Docker)
- Dependencies specified in `requirements.txt`
## Getting Started

### Run with Docker

1. **Build the Docker image:**

   ```bash
   docker build -t anomaly-detection-app .

2. **Run the Docker container:**

    ```bash
    docker run -p 8050:8050 anomaly-detection-app

2. **Open the local instance:**
    ```bash
    Go to http://localhost:8050

### Running Locally (without Docker)
1. **install requirements.txt:**
    ```bash
    pip install -r requirements.txt

2. **Run the app:**
    ```bash
    python app.py

3. **Open the local instance:**
    ```bash
    Go to http://localhost:8050
   
## Chosen Algorithm (Isolation Forest)

### Isolation Forest Overview Logic

This is a specific ensemble learning method for anomaly detection. A certain number of decision trees are constructed to isolate the observations. Anomalies get isolated much quicker compared to normal data because of their unique feature patterns.
### Strengths
Effective in high-dimensional data, and it works well on large datasets.
It is robust to many irrelevant features; hence, it is applicable to diverse types of data.
### Model Parameters
User is allowed to specify an expected proportion of anomalies, enhancing flexibility for different datasets.

Parameters like:
- contamination - Proportion of anomalies in the dataset
- n_estimators - Number of base estimators/trees in the forest
- random_state - Controls randomness of the estimator for reproducibility
### Real-Time Adaptation

It is retrained with the addition of the new, incoming data, thereby making it effective in dynamic environments. 
It is very accurate with low false positives.
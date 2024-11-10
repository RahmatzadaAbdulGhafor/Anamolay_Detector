import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Output, Input, State
import plotly.graph_objs as go
from dataStream import generate_data_stream
from anomalyDetection import AnomalyDetector
import webbrowser
import pandas as pd
import io
import base64


# Function to retrain the anomaly detector
def retrain_detector():
    # Generate the initial small set of data to retrain the model
    initial_data = [next(generate_data_stream()) for _ in range(100)]
    initial_data = np.array(initial_data).reshape(-1, 1)
    detector.train(initial_data)





# Initialize the Dash app
app = dash.Dash(__name__)
# simple html layout
app.layout = html.Div([

    dcc.Graph(id='live-update-graph'),
    dcc.Interval(id='interval-component', interval=400, n_intervals=0, disabled=True),# Update every 400 milliseconds
    html.Div([
        dcc.Input(id='user-input', type='number', placeholder='Enter your own anomaly'),
        html.Button('Submit', id='submit-button'),
    ], style={'display': 'flex', 'justify-content': 'center', 'align-items': 'center', 'margin-top': '20px'}),
    html.Div(
        [
            html.Button(
                'Start',
                id='start-button',
                n_clicks=0,
                style={
                    'padding': '10px 20px',
                    'margin': '10px',
                    'backgroundColor': '#4CAF50',  # Green background
                    'color': 'white',  # White text
                    'border': 'none',  # No border
                    'borderRadius': '5px',  # Rounded corners
                    'cursor': 'pointer',  # Pointer cursor on hover
                    'fontSize': '16px',
                    'transition': 'background-color 0.3s ease',  # Smooth transition for hover
                }
            ),
            html.Button(
                'Stop',
                id='stop-button',
                n_clicks=0,
                style={
                    'padding': '10px 20px',
                    'margin': '10px',
                    'backgroundColor': '#f44336',  # Red background
                    'color': 'white',  # White text
                    'border': 'none',  # No border
                    'borderRadius': '5px',  # Rounded corners
                    'cursor': 'pointer',  # Pointer cursor on hover
                    'fontSize': '16px',
                    'transition': 'background-color 0.3s ease',  # Smooth transition for hover
                }
            ),
            html.Button(
                'reset',
                id='reset-button',
                n_clicks=0,
                style={
                    'padding': '10px 20px',
                    'margin': '10px',
                    'backgroundColor': '#f44336',  # Red background
                    'color': 'white',  # White text
                    'border': 'none',  # No border
                    'borderRadius': '5px',  # Rounded corners
                    'cursor': 'pointer',  # Pointer cursor on hover
                    'fontSize': '16px',
                    'transition': 'background-color 0.3s ease',  # Smooth transition for hover
                }
            ),
            html.Button(
                'Download CSV', id='download-button', n_clicks=0,
                style={
                    'padding': '10px 20px',
                    'margin': '10px',
                    'backgroundColor': '#2196F3',  # Blue background
                    'color': 'white',
                    'border': 'none',
                    'borderRadius': '5px',
                    'cursor': 'pointer',
                    'fontSize': '16px',
                    'transition': 'background-color 0.3s ease',
                }
            ),
            dcc.Download(id='download-dataframe-csv')
        ],
        style={'textAlign': 'center'}  # Align buttons to center
    ),

    html.Div(
        [
            html.H6("\n Recovered Points -->//DOESNT WORK PROPERLY (yet)//<--", style={'textAlign': 'center', 'fontSize': '18px'}),
        ],
        style={'margin': '5px 0'}
    )
])

#allowing users random number
user_data_buffer = None
waiting_for_user_data = False
#tracking of data
x_data = []
y_data = []
anomaly_x = []
anomaly_y = []
# Use additional deques to store recovering data points
recovering_x = []
recovering_y = []
# Store recent anomalies for recovery (key: time step, value: data point
recent_anomalies = {}
# help with reset graph
interval_counter = 0

# Callback to enable/disable the Interval component based on button clicks
@app.callback(
    Output('interval-component', 'disabled'),
    [Input('start-button', 'n_clicks'), Input('stop-button', 'n_clicks'), Input('reset-button', 'n_clicks')],
    prevent_initial_call=True
)
def control_streaming(start_clicks, stop_clicks, reset_clicks):
    ctx = dash.callback_context
    if not ctx.triggered:
        return True  # Disable by default if no button clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Enable streaming if "Start" is clicked; otherwise, disable
    if button_id == 'start-button':
        return False  # Enable streaming
    elif button_id in ['stop-button', 'reset-button']:
        return True  # Disable streaming



# Callback function to update the graph
@app.callback(Output('live-update-graph', 'figure'),
              [Input('interval-component', 'n_intervals'),
               Input('reset-button', 'n_clicks'),
               Input('submit-button', 'n_clicks')],
              [State('user-input', 'value')],
              prevent_initial_call=True)
def update_graph_live(n, reset_clicks, submit_clicks, user_value):
    global x_data, y_data, anomaly_x, anomaly_y, recovering_x, recovering_y, recent_anomalies, interval_counter, user_data_buffer, waiting_for_user_data,detector

    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'reset-button':
        # Clear all global variables to reset the graph
        x_data.clear()
        y_data.clear()
        anomaly_x.clear()
        anomaly_y.clear()
        recovering_x.clear()
        recovering_y.clear()
        recent_anomalies.clear()
        interval_counter = 0

        # Reinitialise and retrain the anomaly detector (beacuse it wont well with those small numbers at the beginning)
        detector = AnomalyDetector(initial_window_size=0)
        retrain_detector()

        # Return an empty figure to reset the graph
        return {
            'data': [],
            'layout': {
                'title': 'Anomaly Detection with Real-Time Data Stream',
                'xaxis': {'title': 'Time Steps'},
                'yaxis': {'title': 'Value'}
            }
        }

    if button_id == 'submit-button' and user_value is not None and not waiting_for_user_data:
        # Set the user input as the next data point
        user_data_buffer = float(user_value)
        waiting_for_user_data = True  # Set flag to wait for user data
        return dash.no_update  # Skip graph update until the user data is processed

    # Generate the next data point
    if waiting_for_user_data and user_data_buffer is not None:
        # Use the user input as the next data point
        data_point = user_data_buffer
        user_data_buffer = None  # Clear buffer
        waiting_for_user_data = False
    else:
        # Generate a random data point as usual
        data_point = next(generate_data_stream())
    x_data.append(interval_counter)
    y_data.append(data_point)



    detector.adjust_window_size(interval_counter)

    # Check for anomaly if we have enough data points for the sliding window
    if len(y_data) >= detector.window_size:  # Ensure we have enough data points for detection

        # # Append the data point to a temporary buffer for sliding window
        # training_buffer = y_data[:]  # Keep only the most recent 100 points

        # Periodically retrain the model (e.g., every 50 data points)
        if interval_counter % 50 == 0 and len(y_data)>50:  # Change interval if needed
            detector.train(y_data)  # Retrain on recent addition data
            print("Model retrained with sliding window.")



            # Check all historical points for recovery
            all_anomalies = list(recent_anomalies.items())  # Create a list to avoid dictionary size change during iteration
            for timestamp, value in all_anomalies:
                if not detector.detect([value]):  # If no longer an anomaly
                    recovering_x.append(timestamp)
                    recovering_y.append(value)
                    # Remove from anomaly lists
                    recent_anomalies.pop(timestamp)
                    if timestamp in anomaly_x:
                        idx = anomaly_x.index(timestamp)
                        anomaly_x.pop(idx)
                        anomaly_y.pop(idx)


        # checking if current point is anomaly or not (Data point is the last point in the data stream)
        try:
            is_anomaly = detector.detect([data_point])
            if is_anomaly:
                # If an anomaly is detected, add to the anomaly lists
                anomaly_x.append(interval_counter)
                anomaly_y.append(data_point)
                recent_anomalies[interval_counter] = float(data_point)
            # else:
            #    # If no longer an anomaly, add to the recovering lists (changed logic of this)
            #     if (n, data_point) in recent_anomalies:
            #         recovering_x.append(n)
            #         recovering_y.append(data_point)
            #         recent_anomalies.pop(n)
        except Exception as e:
            # Log the error for debugging but continue processing
            print(f"Error detecting anomaly: {e}")

    # Create the plot
    fig = go.Figure()

    # Plot the entire data stream as a blue line
    fig.add_trace(go.Scatter(
        x=list(x_data),
        y=list(y_data),
        mode='lines',
        name='Data Stream',
        line=dict(color='blue')
    ))

    # Plot anomalies as red circles
    fig.add_trace(go.Scatter(
        x=list(anomaly_x),
        y=list(anomaly_y),
        mode='markers',
        marker=dict(color='red', size=10, symbol='circle'),
        name='Anomalies'
    ))

    fig.add_trace(go.Scatter(
        x=list(recovering_x),
        y=list(recovering_y),
        mode='markers',
        marker=dict(color='orange', size=8, symbol='circle'),
        name='Recovered Points (No anomaly- based on whole data)'
    ))

    # Set initial window size to 20 points or the current data length, whichever is smaller
    window_size = min(60, len(x_data))

    # Calculate the range for x and y axes
    x_min = x_data[0]
    x_max = x_data[-1]

    # If we have more than 20 points, create a moving window
    if len(x_data) > 60:
        x_min = x_data[-60]

    # Get visible y values for range calculation
    visible_y = list(y_data)[-window_size:]
    if anomaly_y:  # Add any anomaly points in the visible range
        visible_anomalies = [y for x, y in zip(anomaly_x, anomaly_y) if x >= x_min]
        visible_y.extend(visible_anomalies)

    y_min = min(visible_y) if visible_y else 0
    y_max = max(visible_y) if visible_y else 1
    y_margin = (y_max - y_min) * 0.1  # Add 10% margin

    # Update layout for better visualisation (fixed range, title but shifts along)
    fig.update_layout(
        title='Anomaly Detection with Real-Time Data Stream',
        xaxis_title='Time Steps',
        yaxis_title='Value',
        showlegend=True,
        xaxis=dict(
            range=[x_min, x_max],
            fixedrange=True,  # Prevents zoom on x-axis
            rangeslider=dict(
                visible=True,
                thickness=0.1  # Adjust the thickness if needed
            )
        ),
        yaxis=dict(
            range=[y_min - y_margin, y_max + y_margin],
            fixedrange=True  # Prevents zoom on y-axis
        )
    )
    # fig.update_layout(
    #     title='Real-Time Data Stream with Anomaly Detection',
    #     xaxis_title='Time Steps',
    #     yaxis_title='Value',
    #     showlegend=True
    # )

    interval_counter += 1
    return fig


# output CSV file of data
@app.callback(
    Output('download-dataframe-csv', 'data'),
    [Input('download-button', 'n_clicks')],
    prevent_initial_call=True
)
def download_csv(n_clicks):
    # Prepare data for the CSV
    is_anomaly = [int(x in anomaly_x) for x in x_data]  # 1 if anomaly, 0 otherwise
    df = pd.DataFrame({
        'x': x_data,
        'y': y_data,
        'is_anomaly': is_anomaly
    })

    # Convert DataFrame to CSV
    csv_string = df.to_csv(index=False)

    # Return the CSV data for download
    return dict(
        content=csv_string,
        filename='data_stream.csv',
        type='text/csv',  # Corrected from 'mime_type' to 'type'
        base64=False
    )



if __name__ == '__main__':
    global detector
    detector = AnomalyDetector(initial_window_size=0)
    retrain_detector()
    app.run_server(debug=True,host='0.0.0.0', port=8050)
    webbrowser.open("http://localhost:8050")
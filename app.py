from dash.dependencies import Output, Input
from influxdb_client import InfluxDBClient, Point, Dialect

import csv
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import os
import plotly.express as px
import plotly.graph_objects as go
import plotly.express as px

# Dash App
app = dash.Dash(__name__, title='Ribbit Network')
server = app.server

# Connect to InfluxDB
client = InfluxDBClient.from_config_file("influx_config.ini")
query_api = client.query_api()

def get_influxdb_data(duration):
    ## Query data as pandas dataframe
    df = query_api.query_data_frame('from(bucket:"co2")'
                                    f'|> range(start: -{duration})'
                                    '|> filter(fn: (r) => r.host == "6cb1b8e43a19bdb3950a118a36af3452")'
                                    '|> aggregateWindow(every: 1m, fn: mean, createEmpty: false)'
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                    '|> keep(columns: ["co2", "temperature", "humidity", "lat", "lon", "alt", "_time", "baro_pressure"])')
    return df.drop(['result', 'table'], axis=1)

def serve_layout():
    return html.Div([
        html.Div(id='onload', hidden=True),

        html.Div([
            html.Img(src='assets/frog.svg'),
            html.H1('Ribbit Network'),
            html.A(html.H3('Learn More'), href='https://ribbitnetwork.org/', style={'margin-left': 'auto', 'text-decoration': 'none', 'color': 'black'}),
        ], id='nav'),

        dcc.Dropdown(id='duration', clearable=False, searchable=False, value='24h', options=[
            {'label': '10 minutes', 'value': '10m'},
            {'label': '30 minutes', 'value': '30m'},
            {'label': '1 hour',     'value': '1h'},
            {'label': '1 day',      'value': '24h'},
            {'label': '7 days',      'value': '7d'},
            {'label': '30 days',      'value': '30d'},
        ]),

        dcc.Graph(id='map', figure=map_fig),

        html.Div([
            dcc.Graph(id='co2_graph'),
            dcc.Graph(id='temp_graph'),
            dcc.Graph(id='baro_graph'),
            dcc.Graph(id='humidity_graph'),
            dcc.Interval(id='interval', interval=60*1000, n_intervals=0),
            html.Div(id='timezone', hidden=True),
            html.Div([html.Button('Export as CSV', id='export'), dcc.Download(id='download')]),
        ]),
    ])

# Only get the latest point for displaying on the map
map_df = query_api.query_data_frame('from(bucket:"co2") '
                                    '|> range(start:-15m) '
                                    '|> limit(n:1) '
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") '
                                    '|> keep(columns: ["co2","lat", "lon"])')


map_fig = go.Figure(data=go.Scattermapbox(
    lon=map_df['lon'],
    lat=map_df['lat'],
    text='CO₂: '+map_df['co2'].round(decimals=2).astype('str'),
    mode='markers',
    marker=dict(color=map_df['co2'], size=18, showscale = True, cmin=300, cmax = 600)
))
map_fig.update_layout(mapbox_style="carto-positron")
map_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

app.layout = serve_layout

# Get browser timezone
app.clientside_callback(
    '''
    function(n_intervals) {
        return Intl.DateTimeFormat().resolvedOptions().timeZone
    }
    ''',
    Output('timezone', 'children'),
    Input('onload', 'children'),
)

# Update CO2 graph
@app.callback(
    Output('co2_graph', 'figure'),
    Output('temp_graph', 'figure'),
    Output('baro_graph', 'figure'),
    Output('humidity_graph', 'figure'),
    [
        Input('timezone', 'children'),
        Input('duration', 'value'),
        Input('interval', 'n_intervals'),
    ],
)
def update_graphs(timezone, duration, n_intervals):
    df = get_influxdb_data(duration)
    df.rename(columns = {'_time':'Time', 'co2':'CO₂ (PPM)', 'humidity':'Humidity (%)', 'lat':'Latitude', 
                         'lon':'Longitude','alt':'Altitude (m)','temperature':'Temperature (C)', 'baro_pressure':'Barometric Pressure (mBar)'}, inplace = True)
    df['Time'] = df['Time'].dt.tz_convert(timezone)
    co2_line = px.line(df, x='Time', y='CO₂ (PPM)', color_discrete_sequence=['black'],
                       template='plotly_white', render_mode='svg', hover_data = {'CO₂ (PPM)':':.2f'})
    temp_line = px.line(df, x='Time', y='Temperature (C)', color_discrete_sequence=['black'], 
                        template='plotly_white', render_mode='svg', hover_data = {'Temperature (C)':':.2f'})
    baro_line = px.line(df, x='Time', y='Barometric Pressure (mBar)', color_discrete_sequence=['black'],
                        template='plotly_white', render_mode='svg', hover_data = {'Barometric Pressure (mBar)':':.2f'})
    humidity_line = px.line(df, x='Time', y='Humidity (%)', color_discrete_sequence=['black'],
                            template='plotly_white', render_mode='svg', hover_data = {'Humidity (%)':':.2f'})
    return co2_line, temp_line, baro_line, humidity_line

# Export data as CSV
@app.callback(Output('download', 'data'), [Input('export', 'n_clicks'), Input('duration', 'value')])
def export_data(n_clicks, duration):
    if n_clicks == None:
        return
    df = get_influxdb_data(duration)
    df.columns = ['Timestamp', 'Altitude', 'CO2', 'Humidity', 'Latitude', 'Longitude', 'Temperature']
    return dcc.send_data_frame(df.to_csv, index=False, filename='data.csv')

if __name__ == '__main__':
    app.run_server(debug=True)

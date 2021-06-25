import os

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px

from influxdb_client import InfluxDBClient, Point, Dialect

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Dash App
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Connect to InfluxDB
client = InfluxDBClient.from_config_file("influx_config.ini")
query_api = client.query_api()

## Query data as pandas dataframe
data_frame = query_api.query_data_frame('from(bucket:"co2") '
                                        '|> range(start: -10m) '
                                        '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value") '
                                        '|> keep(columns: ["co2", "temperature", "humidity", "lat", "lon", "alt", "_time"])')


fig = px.line(data_frame, x="_time", y="co2", title="Co2 PPM")


app.layout = html.Div([
    dcc.Graph(
        id='life-exp-vs-gdp',
        figure=fig
    ),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in data_frame.columns],
        data=data_frame.to_dict('records')
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)

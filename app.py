import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_leaflet as dl
import dash_leaflet.express as dlx
import db
import numpy as np
import pandas as pd
import plotly.graph_objects as go

from dash.dependencies import Output, Input
from dash_extensions.javascript import assign
from plotly.subplots import make_subplots

TITLE = 'Ribbit Network'
REFRESH_MS = 60 * 1000

chroma = 'https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js'
colorscale = ['lightgreen', 'green', 'darkgreen', 'black']

# Dash App
app = dash.Dash(__name__, title=TITLE, update_title=None, external_scripts=[chroma])
server = app.server

sensor_data = pd.DataFrame(columns=['Time', 'CO2 (PPM)', 'Temperature (degC)', 'Barometric Pressure (mBar)', 'Humidity (%)'])


def serve_layout():
    df = db.get_map_data()

    return html.Div([
        html.Div(id='onload', hidden=True),
        dcc.Interval(id='interval', interval=REFRESH_MS, n_intervals=0),

        html.Div([
            html.Img(src='assets/frog.svg'),
            html.H1(TITLE),
            html.A(html.H3('Learn'), href='https://ribbitnetwork.org/',
                   style={'margin-left': 'auto', 'text-decoration': 'underline', 'color': 'black'}),
            html.A(html.H3('Build'),
                   href='https://github.com/Ribbit-Network/ribbit-network-frog-sensor#build-a-frog',
                   style={'margin-left': '2em', 'text-decoration': 'underline', 'color': 'black'}),
            html.A(html.H3('Order'),
                   href='https://ribbitnetwork.org/#buy',
                   style={'margin-left': '2em', 'text-decoration': 'underline', 'color': 'black'}),
            html.A(html.H3('Support'), href='https://ko-fi.com/keenanjohnson',
                   style={'margin-left': '2em', 'text-decoration': 'underline', 'color': 'black'}),
        ], id='nav'),

        html.Div([
            dl.Map(
                [
                    dl.TileLayer(url='https://cartodb-basemaps-{s}.global.ssl.fastly.net/light_all/{z}/{x}/{y}.png',
                                 attribution='Map tiles by Carto, under CC BY 3.0. Data by OpenStreetMap, under ODbL.'),
                    dl.LocateControl(startDirectly=True, options=dict(keepCurrentZoomLevel=True, drawCircle=False, drawMarker=False)),
                    dl.GeoJSON(id='geojson'),
                    dl.Colorbar(colorscale=colorscale, width=20, height=200, min=300, max=600, unit='PPM'),
                    dl.GestureHandling(),
                ],
                id='map',
                zoom=3,
                minZoom=3,
                maxBounds=[[-75, -180],[75, 200]],
            ),
        ], id='map-container'),
        html.Div([
			html.Label(['Duration'], id='durationLabel'),
            dcc.Dropdown(id='duration', clearable=False, searchable=False, value='7d', options=[
                {'label': '10 minutes', 'value': '10m'},
                {'label': '30 minutes', 'value': '30m'},
                {'label': '1 hour', 'value': '1h'},
                {'label': '1 day', 'value': '24h'},
                {'label': '7 days', 'value': '7d'},
                {'label': '30 days', 'value': '30d'},
            ]),
			html.Label(['Sampling'], id='frequencyLabel'),
			dcc.Dropdown(id='frequency', clearable=False, searchable=False, value='1h', options=[
                {'label': '1 minute sample', 'value': '1min'},
                {'label': '5 minute average', 'value': '5min'},
				{'label': '15 minute  average', 'value': '15min'},
				{'label': '30 minute average', 'value': '30min'},
                {'label': '1 hour average', 'value': '1h'},
            ]),
            html.Div([
                html.Button(html.Div([
                    html.Img(src='assets/download.svg'),
                    'Export as CSV',
                ]), id='export'),
                dcc.Download(id='download'),
            ]),
        ], id='controls'),

        html.Div([
            dcc.Graph(id='timeseries'),
            html.Div(id='timezone', hidden=True),
        ], id='graphs'),
    ])

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

point_to_layer = assign('''function(feature, latlng, context) {
    const {min, max, colorscale, circleOptions, colorProp} = context.props.hideout;
    const csc = chroma.scale(colorscale).domain([min, max]);
    circleOptions.fillColor = csc(feature.properties[colorProp]);
    return L.circleMarker(latlng, circleOptions);
}''')

cluster_to_layer = assign('''function(feature, latlng, index, context) {
    const {min, max, colorscale, circleOptions, colorProp} = context.props.hideout;
    const csc = chroma.scale(colorscale).domain([min, max]);
    // Set color based on mean value of leaves.
    const leaves = index.getLeaves(feature.properties.cluster_id);
    let valueSum = 0;
    for (let i = 0; i < leaves.length; ++i) {
        valueSum += leaves[i].properties[colorProp]
    }
    const valueMean = valueSum / leaves.length;
    // Render a circle with the number of leaves written in the center.
    const icon = L.divIcon.scatter({
        html: '<div style="background-color:white;"><span>' + feature.properties.point_count_abbreviated + '</span></div>',
        className: "marker-cluster",
        iconSize: L.point(40, 40),
        color: csc(valueMean)
    });
    return L.marker(latlng, {icon : icon})
}''')


# Update the Map
@app.callback(
    Output('geojson', 'children'),
    [
        Input('onload', 'children'),
        Input('interval', 'n_intervals'),
    ],
)
def update_map(_children, _n_intervals):
    df = db.get_map_data()
    df['tooltip'] = df['co2'].round(decimals=2).astype(str) + ' PPM'

    return dl.GeoJSON(
        id='geojson',
        data=dlx.dicts_to_geojson(df.to_dict('records')),
        options=dict(pointToLayer=point_to_layer),
        cluster=True,
        clusterToLayer=cluster_to_layer,
        zoomToBoundsOnClick=True,
        superClusterOptions=dict(radius=100),
        hideout=dict(colorProp='co2', circleOptions=dict(fillOpacity=1, stroke=False, radius=12), min=300, max=600,
                     colorscale=colorscale),
    )


# Update Data Plots
@app.callback(
    Output('timeseries', 'figure'),
    [
        Input('timezone', 'children'),
        Input('duration', 'value'),
		Input('frequency', 'value'),
        Input('geojson', 'click_feature'),
        Input('interval', 'n_intervals'),
    ],
)
def update_graphs(timezone, duration, frequency, click_feature, _n_intervals):
    global sensor_data

    if click_feature is not None:
        sensor = click_feature.get('properties', {}).get('host', None)
        if sensor is not None:
            sensor_data = db.get_sensor_data(sensor, duration, frequency)
            sensor_data.rename(
                columns={'_time': 'Time', 'co2': 'CO2 (PPM)', 'humidity': 'Humidity (%)', 'lat': 'Latitude', 'lon': 'Longitude',
                         'alt': 'Altitude (m)', 'temperature': 'Temperature (degC)',
                         'baro_pressure': 'Barometric Pressure (mBar)'}, inplace=True)
            sensor_data['Time'] = sensor_data['Time'].dt.tz_convert(timezone)

    columns_to_plot = ['CO2 (PPM)', 'Temperature (degC)', 'Barometric Pressure (mBar)', 'Humidity (%)']
    fig = make_subplots(rows=4, cols=1, shared_xaxes=True)
    for ind, col in enumerate(columns_to_plot):
        fig.add_scatter(x=sensor_data["Time"], 
						y=sensor_data[col], 
						mode="lines", 
						line=go.scatter.Line(color="black"), 
						showlegend=False, 
						row=ind+1, 
						col=1, 
						hovertemplate="Time: %{x}<br>%{text}: %{y:.2f}<extra></extra>", 
						text=[col]*len(sensor_data[col]))
        fig.update_yaxes(title_text=col, row=ind+1, col=1)
    fig.update_layout(template="plotly_white", height=1200)
    return fig


# Export data as CSV
@app.callback(
    Output('download', 'data'),
    Input('export', 'n_clicks'),
)
def export_data(n_clicks):
    if n_clicks is None or sensor_data.empty:
        return

    return dcc.send_data_frame(sensor_data.to_csv, index=False, filename='data.csv')


if __name__ == '__main__':
    app.run_server(debug=True)

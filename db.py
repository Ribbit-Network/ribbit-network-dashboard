import pandas as pd

from influxdb_client import InfluxDBClient

client = InfluxDBClient.from_config_file('influx_config.ini')
query_api = client.query_api()


def get_map_data():
    df = query_api.query_data_frame('from(bucket:"co2")'
                                    '|> range(start:-15m)'
                                    '|> limit(n:1)'
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                    '|> keep(columns: ["host", "lat", "lon", "co2"])')
    return pd.concat(df)


def get_sensor_data(host, duration):
    query = 'from(bucket:"co2")'
    query += f'|> range(start: -{duration})'

    if host is not None:
        query += f'|> filter(fn: (r) => r.host == "{host}")'

    query += '|> aggregateWindow(every: 1m, fn: mean, createEmpty: false)'
    query += '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
    query += '|> keep(columns: ["co2", "temperature", "humidity", "lat", "lon", "alt", "_time", "baro_pressure"])'

    df = query_api.query_data_frame(query)
    return df.drop(['result', 'table'], axis=1)

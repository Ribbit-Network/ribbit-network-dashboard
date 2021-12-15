import pandas as pd

from influxdb_client import InfluxDBClient

client = InfluxDBClient.from_config_file('influx_config.ini')
query_api = client.query_api()


def get_map_data():
    df = query_api.query_data_frame('from(bucket:"co2")'
                                    '|> range(start:-15m)'
                                    '|> limit(n:1)'
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                    '|> filter(fn: (r) => r.lat != 0 and r.lon != 0)'
                                    '|> keep(columns: ["host", "lat", "lon", "co2"])')
    return pd.concat(df)


def get_sensor_data(host, duration):
    df = query_api.query_data_frame('from(bucket:"co2")'
                                    f'|> range(start: -{duration})'
                                    f'|> filter(fn: (r) => r.host == "{host}")'
                                    '|> aggregateWindow(every: 1m, fn: mean, createEmpty: false)'
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                    '|> keep(columns: ["co2", "temperature", "humidity", "lat", "lon", "alt", "_time", "baro_pressure"])')
    return df.drop(['result', 'table'], axis=1)

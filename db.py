import pandas as pd
from cachetools import cached, TTLCache

from influxdb_client import InfluxDBClient

client = InfluxDBClient.from_config_file('influx_config.ini')
query_api = client.query_api()


@cached(cache=TTLCache(maxsize=1, ttl=60))
def get_map_data() -> pd.DataFrame:
    df = query_api.query_data_frame('from(bucket:"lab-testing")'
                                    '|> range(start:-30d)'
                                    '|> filter(fn: (r) => r._field == "co2" or r._field == "lat" or r._field == "lon")'
                                    '|> last()'
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                    '|> filter(fn: (r) => r.lat != 0 and r.lon != 0)'
                                    '|> keep(columns: ["_time", "host", "co2"])')
    if type(df) is list:
        return pd.concat(df)
    if type(df) is pd.DataFrame:
        return df


# `100` chosen arbitrarily, tweak with extreme prejudice
@cached(cache=TTLCache(maxsize=100, ttl=60))
def get_sensor_data(host: str, duration: str, frequency: str) -> pd.DataFrame:
    df = query_api.query_data_frame('from(bucket:"lab-testing")'
                                    f'|> range(start: -{duration})'
                                    f'|> filter(fn: (r) => r.host == "{host}")'
                                    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")'
                                    '|> keep(columns: ["co2", "temperature", "humidity", "_time", "baro_pressure"])')
    if df.empty:
        return df
    df.drop(['result', 'table'], axis=1, inplace=True)
    if frequency in ['5min', '10min', '15min', '30min', '1h']:
        df.set_index('_time', inplace=True)
        df = df.resample(frequency).mean().reset_index()
    return df

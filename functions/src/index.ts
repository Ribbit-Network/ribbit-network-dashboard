import * as functions from "firebase-functions";
import core, { SensorData } from "./core";

export const getSensorData = functions.https.onRequest((request, response) => {
  response.set("Access-Control-Allow-Origin", "*");

  const mapQuery =
    'from(bucket:"co2")' +
    "|> range(start:-30d)" +
    '|> filter(fn: (r) => r._field == "co2" or r._field == "lat" or r._field == "lon")' +
    "|> last()" +
    '|> pivot(rowKey:["_time"], columnKey: ["_field"], valueColumn: "_value")' +
    "|> filter(fn: (r) => r.lat != 0 and r.lon != 0)" +
    '|> keep(columns: ["_time", "host", "lat", "lon", "co2"])';

  const data: SensorData[] = [];

  core.influxDB.queryRows(mapQuery, {
    next: (raw: any, tableMeta: any) => {
      const row: SensorData = tableMeta.toObject(raw);

      data.push(row);
    },
    error: (e: Error) => {
      functions.logger.error(e, { structuredData: true });

      response.send("something went wrong!");
    },
    complete: () => {
      response.json(data);
    },
  });
});

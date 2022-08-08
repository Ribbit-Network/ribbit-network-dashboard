import { makeAutoObservable } from "mobx";
import { InfluxDB } from "@influxdata/influxdb-client";

export interface SensorData {
  co2: number;
  host: string;
  lat: number;
  lon: number;
  result: string;
  table: number;
  _time: string;
}

class Core {
  influxDB: any;

  constructor() {
    this.influxDB = new InfluxDB({
      url: "https://us-west-2-1.aws.cloud2.influxdata.com",
      token: process.env.INFLUX_DB_TOKEN,
    }).getQueryApi(process.env.INFLUX_DB_ORG);

    makeAutoObservable(this);
  }
}

export default new Core();

import { makeAutoObservable } from "mobx";
import { InfluxDB } from "@influxdata/influxdb-client";

class Core {
  influxDB: any;

  constructor() {
    this.influxDB = new InfluxDB({
      url: "https://us-west-2-1.aws.cloud2.influxdata.com",
      token:
        "wQdQ6Xeh0jvjy_oCHnqYtux9qNaoEdt57B4mQiFz6gV-itMn2WnuLnolwAVfFuE6c6dR27m6bUxdqSxb9f5Rog==",
    }).getQueryApi("keenan.johnson@gmail.com");

    makeAutoObservable(this);
  }
}

export default new Core();

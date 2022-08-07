import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { makeAutoObservable } from "mobx";
import { InfluxDB } from "@influxdata/influxdb-client-browser";

const firebaseConfig = {
  apiKey: "AIzaSyD35dn4IMvA7-Tul_OPeBGerHPHJfqypSk",
  authDomain: "ribbit-network.firebaseapp.com",
  projectId: "ribbit-network",
  storageBucket: "ribbit-network.appspot.com",
  messagingSenderId: "56492711430",
  appId: "1:56492711430:web:6a5d17592974fa06492d87",
  measurementId: "G-METWMB8750",
};

class Core {
  app: any;
  analytics: any;

  influxDB: any;

  constructor() {
    this.app = initializeApp(firebaseConfig);
    this.analytics = getAnalytics(this.app);

    this.influxDB = new InfluxDB({
      url: "https://us-west-2-1.aws.cloud2.influxdata.com",
      token:
        "wQdQ6Xeh0jvjy_oCHnqYtux9qNaoEdt57B4mQiFz6gV-itMn2WnuLnolwAVfFuE6c6dR27m6bUxdqSxb9f5Rog==",
    }).getQueryApi("keenan.johnson@gmail.com");

    makeAutoObservable(this);

    console.log("firebase initialized");
  }
}

export default new Core();

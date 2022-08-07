import * as functions from "firebase-functions";

// // Start writing Firebase Functions
// // https://firebase.google.com/docs/functions/typescript

export const heartbeat = functions.https.onRequest((request, response) => {
  response.send("Hello from ribbit frog!");
});

export const getSensorData = functions.https.onRequest((request, response) => {
  functions.logger.info("Hello logs!", { structuredData: true });
  response.send("Hello from Firebase!");
});

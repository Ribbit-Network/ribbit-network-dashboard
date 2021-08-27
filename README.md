# Ribbit Network Sensor
[This project will create the world's largest Greenhouse Gas Emissions dataset that will empower anyone to join in the work on climate and provide informed data for climate action.](https://ribbitnetwork.org/)

The Greenhouse Gas Sensor Cloud is a large network of open-source, low-cost, Greenhouse Gas (CO2 and possibly methane) Detection Sensors. These sensor units will be sold by the Ribbit Network and will upload their data to the cloud, creating the world's most complete Greenhouse Gas dataset.

[See more about the Frog Sensors here.](https://github.com/Ribbit-Network/ribbit-network-frog-sensor)

## Dashboard
The Ribbit Network saves the sensor data and makes it accessible for scientists everywhere to analyze and pinpoint emissions. Using this data we can identify and track emissions, allowing us to verify our assumptions about climate and hold ourselves accountable through corporate, government, and individual action.

This repository contains the dashboard for that public information

![image](https://user-images.githubusercontent.com/2559382/128451521-2e97bbf5-b5f7-4663-b070-af488d3d1f65.png)

## Current Status
This dashboard is in it's very earliest version and needs a lot of work.!

The first prototype sensors are up and running in Seattle. [Here is some real data from that sensor](https://ribbit-network.herokuapp.com/) (Note this dashboard is still experimental and may be down occasionally).

## Technical Details
The application is built as a [Dash app](https://plotly.com/dash/).

It is currently automatically deployed on [Heroku](https://dashboard.heroku.com/) from this repository.

You can run the website locally on your development machine using the following instructions after cloning this repo:

```
python3 -m venv env
source env/bin/activate
python3 -m pip install -r requirements.txt
python3 app.py
```

Once the server is up and running you can visit it locally by going to http://127.0.0.1:8050/

## Contributing
See the [Issues](https://github.com/Ribbit-Network/ribbit-network-dashboard/issues) section of this project for the work that I've currently scoped out to be done. Reach out to me if you are interested in helping out!

[You can also join our developer discord here.](https://discord.gg/vq8PkDb2TC)

## Background Information
[See the Wiki for background research.](https://github.com/Ribbit-Network/ribbit-network-sensor/wiki/Background-Research) This project is inspired by some awesome research by incedible scientists in academia.

## Developer
Hi, I'm [Keenan](https://www.keenanjohnson.com/) and I work on this project! Reach out if you are interested or just want to chat.

Consider sponsoring me on [Ko-fi](https://ko-fi.com/W7W14VTU8) or through [Github Sponsors](https://github.com/sponsors/keenanjohnson) to help cover the research and development costs.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/W7W14VTU8)

# Ribbit Network Dashboard
<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->
[![All Contributors](https://img.shields.io/badge/all_contributors-1-orange.svg?style=flat-square)](#contributors-)
<!-- ALL-CONTRIBUTORS-BADGE:END -->
[This project will create the world's largest Greenhouse Gas Emissions dataset that will empower anyone to join in the work on climate and provide informed data for climate action.](https://ribbitnetwork.org/)

Ribbit Network is a large network of open-source, low-cost, Greenhouse Gas (CO2 and possibly methane) Detection Sensors. These sensor units will be sold by the Ribbit Network and will upload their data to the cloud, creating the world's most complete Greenhouse Gas dataset.

[See more about the Frog Sensors here.](https://github.com/Ribbit-Network/ribbit-network-frog-sensor)

## Dashboard
The Ribbit Network saves the sensor data and makes it accessible for scientists everywhere to analyze and pinpoint emissions. Using this data we can identify and track emissions, allowing us to verify our assumptions about climate and hold ourselves accountable through corporate, government, and individual action.

This repository contains the dashboard for that public information

![image](https://user-images.githubusercontent.com/2559382/128451521-2e97bbf5-b5f7-4663-b070-af488d3d1f65.png)

## Current Status
This dashboard is in it's very earliest version and needs a lot of work.

The first prototype sensors are up and running in Seattle. [Here is the deployed version of this repo which shows the current live sensor data](https://ribbit-network.herokuapp.com/) (Note this dashboard is still experimental and may be down occasionally).

## Technical Details

![Block Diagram](block_diagram.drawio.svg)

The application is built as a [Dash app](https://plotly.com/dash/).

It is currently automatically deployed on [Heroku](https://dashboard.heroku.com/) from this repository.

You can run the website locally on your development machine using the following instructions after cloning this repo:

On mac/linux
```
python3 -m venv env
source env/bin/activate
python3 -m pip install -r requirements.txt
python3 app.py
```

On Windows (If using Git Bash)
```
python3 -m venv env
env/Scripts/activate
python3 -m pip install -r requirements.txt
python3 app.py
```

On Windows (If using Command Prompt)
```
python3 -m venv env
env\Scripts\activate
python3 -m pip install -r requirements.txt
python3 app.py
```

Once the server is up and running you can visit it locally by going to http://127.0.0.1:8050/

## Contributing
See the [Issues](https://github.com/Ribbit-Network/ribbit-network-dashboard/issues) section of this project for the work that I've currently scoped out to be done. Reach out to me if you are interested in helping out!

The [contributing guide](CONTRIBUTING.md) outlines the process for helping out!

[You can also join our developer discord here.](https://discord.gg/vq8PkDb2TC)

## Questions?
[Check out the Frequently Asked Questions section.](https://github.com/Ribbit-Network/ribbit-network-faq) If you don't see your question, let us know either in a Github Discussion or via Discord.

## Background Information
[See the Wiki for background research.](https://github.com/Ribbit-Network/ribbit-network-sensor/wiki/Background-Research) This project is inspired by some awesome research by incedible scientists in academia.

## Spoort
Hi, I'm [Keenan](https://www.keenanjohnson.com/) and I moderate on this project! Reach out if you are interested or just want to chat.

Consider sponsoring me on [Ko-fi](https://ko-fi.com/W7W14VTU8) or through [Github Sponsors](https://github.com/sponsors/keenanjohnson) to help cover the research and development costs.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/W7W14VTU8)

## Contributors ✨

Thanks goes to these wonderful people ([emoji key](https://allcontributors.org/docs/en/emoji-key)):

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://brianstrauch.com"><img src="https://avatars.githubusercontent.com/u/7474900?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Brian Strauch</b></sub></a><br /><a href="https://github.com/Ribbit-Network/ribbit-network-dashboard/commits?author=brianstrauch" title="Code">💻</a> <a href="#design-brianstrauch" title="Design">🎨</a> <a href="#ideas-brianstrauch" title="Ideas, Planning, & Feedback">🤔</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!

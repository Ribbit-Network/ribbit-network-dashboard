import dash


def test_dash001_smoke(dash_duo):
    app = dash.Dash(__name__)

    dash_duo.start_server(app)

    dash_duo.wait_for_element("h1")
    assert dash_duo.find_element("h1").text == "Ribbit Network"
from app import app


def test_dash001_smoke(dash_duo):
    dash_duo.start_server(app)

    dash_duo.wait_for_element("h1")
    assert dash_duo.find_element("h1").text == "Ribbit Network"

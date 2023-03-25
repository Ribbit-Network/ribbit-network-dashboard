from src.app import app


def test_dash001_smoke(dash_duo):
    dash_duo.start_server(app)

    dash_duo.wait_for_element("h1")

    # Dismiss "User denied Geolocation" alert
    driver = dash_duo.driver
    alert = driver.switch_to.alert
    assert alert.text == "Geolocation error: User denied Geolocation."
    alert.accept()

    # Simple verification that the page loaded (beyond the geolocation alert)
    assert dash_duo.find_element("h1").text == "Ribbit Network"

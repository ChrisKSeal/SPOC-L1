import pytest

from src.specularpoint import FlightProcessor

test_flight_lat_lon_alt = (-39.6594543457031, 176.729477592137, 19725)
known_altitude_in_metres = 6012.19202438405
known_ecef_x_y_z_coords = (-4913538.73980396, 280776.609248639, -4052785.53858799)


@pytest.mark.dependency()
def test_convert_altitude_from_feet_to_metres():
    assert FlightProcessor.convert_altitude_from_feet_to_metres(
        test_flight_lat_lon_alt[2]
    ) == pytest.approx(known_altitude_in_metres, 0.001)


@pytest.mark.dependency(depends=["test_convert_altitude_from_feet_to_metres"])
def test_convert_lat_lon_alt_to_ecef():
    altitude_in_metres = FlightProcessor.convert_altitude_from_feet_to_metres(
        test_flight_lat_lon_alt[2]
    )
    assert FlightProcessor.convert_lat_lon_alt_to_ecef(
        test_flight_lat_lon_alt[0], test_flight_lat_lon_alt[1], altitude_in_metres
    ) == pytest.approx(known_ecef_x_y_z_coords)

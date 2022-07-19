from datetime import datetime

import pytest
import pytz

from src.specularpoint import SatellitePredictor

satellite_code = "GPS BIIR-5  (PRN 28)"
tle_line1 = "1 26407U 00040A   20099.47757926 -.00000027  00000-0  00000-0 0 "
tle_line2 = "2 26407  56.0474 304.9288 0187106 279.1817 266.4558  2.00564596144607"

timestamp = 1546306405
known_satellite_ecef = (-22193369.0555635, -12834880.1130687, 7512217.55615829)
known_satellite_lat_lon_alt = (16.3562393108991, -149.958325258204, 20338964.8670521)


sp = SatellitePredictor()
# Define satellite model since TLEs are updated periodically
sp.define_satellite_by_two_line_entry(satellite_code, tle_line1, tle_line2)
time = sp.convert_timestamp_to_time_object(timestamp)


@pytest.mark.xfail()
def test_get_satellite_position_ecef():
    print(sp.get_satellite_position(satellite_code, time))
    print(time.utc_iso())
    time.julian_calendar_cutoff = 2459680
    print(time.tt)
    dt_timestamp = datetime.fromtimestamp(timestamp, tz=pytz.utc)
    print(dt_timestamp)
    assert sp.get_satellite_position(satellite_code, time) == pytest.approx(
        known_satellite_ecef
    )


@pytest.mark.xfail()
def test_get_satellite_position_lat_lon_alt():
    print(sp.get_satellite_position(satellite_code, time, ecef=False))
    assert sp.get_satellite_position(satellite_code, time, ecef=False) == pytest.approx(
        known_satellite_lat_lon_alt
    )

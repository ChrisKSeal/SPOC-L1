"""Functions to predict the position of satellites in ECEF frame of reference"""

import logging
from datetime import datetime

import pytz
from skyfield.api import EarthSatellite, Time, load, wgs84

# from pathlib import Path


logger = logging.getLogger(__name__)

EXPIRES_IN = 7  # days for timedelta i.e. 1 week


class SatellitePredictor:
    def __init__(self):
        """Initialise the SatellitePredictor using TLEs downloaded from
        celestrak.com.
        Attributes:
            self.satellites: a dictionary of EarthSatellite objects
            self.ts: a timescale object for converting between GPS time and
                POSIX timestamps"""
        TLE_URL = "https://celestrak.com/NORAD/elements/gnss.txt"
        satellites = load.tle_file(TLE_URL)
        self.satellites = {sat.name: sat for sat in satellites}
        self.ts = load.timescale(
            builtin=True
        )  # change this to false when maintanence complete
        logger.debug(self.satellites)

    def get_satellite_position(
        self, satellite_code: str, time: Time, ecef: bool = True
    ) -> tuple:
        try:
            satellite = self.satellites[satellite_code]
        except KeyError:
            return (0, 0, 0)
        geocentric = satellite.at(time)
        position = wgs84.geographic_position_of(geocentric)
        if ecef:
            return tuple(position.itrs_xyz.m)
        return (
            position.latitude.degrees,
            position.longitude.degrees,
            position.elevation.m,
        )

    def define_satellite_by_two_line_entry(
        self, satellite_code: str, tle_line1: str, tle_line2: str
    ):
        self.satellites[satellite_code] = EarthSatellite(
            tle_line1, tle_line2, satellite_code, self.ts
        )

    def convert_timestamp_to_time_object(self, timestamp):
        dt_timestamp = datetime.fromtimestamp(timestamp, tz=pytz.utc)
        return self.ts.from_datetime(dt_timestamp)

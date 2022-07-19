"""Functions to process flight data into lat/log/altitude and ECEF frames of reference"""

from pathlib import Path

import pandas as pd
from pint import UnitRegistry
from skyfield.api import wgs84


class FlightProcessor:
    """Class to handle the conversion between data as generated by the NGRx and ECEF for
    calculating the specular points"""

    def __init__(self):
        # Placeholder for initialisation
        pass

    @staticmethod
    def convert_lat_lon_alt_to_ecef(
        latitude: float, longitude: float, altitude: float
    ) -> tuple:
        """Using the WGS84 Geoid convert from latitude longitude and altitude co-ordinates
        into ECEF x, y, z, coordinates"""
        position = wgs84.latlon(latitude, longitude, elevation_m=altitude)
        x, y, z = position.itrs_xyz.m
        return (x, y, z)

    @staticmethod
    def convert_altitude_from_feet_to_metres(altitude: float) -> float:
        """Helper function to convert between altitude in feet and altitude in metres"""
        ureg = UnitRegistry()
        altitude = altitude * ureg.foot
        altitude.ito(ureg.m)
        return altitude.magnitude
""" cooridinate.py

A helper class to hold different cooridinate systems and to convert between ECEF and 
Lat/Long/Altitude frames of reference on a WGS84 geodetic"""

from astropy import units as unit
from astropy.coordinates import EarthLocation


class Coordinates:
    def __init__(self):
        self.location = None

    @classmethod
    def from_ecef(cls, x: float, y: float, z: float):
        """Class instantiating using ECEF coordinates"""
        cls.location = EarthLocation().from_geocentric(x, y, z, unit.m)

    def from_lat_long_alt(cls, latitude: float, longitude: float, altitude: float):
        """Class instantiating using Lat/Long/Altitude coordinates"""
        cls.location = EarthLocation().from_geodetic(
            latitude, longitude, height=altitude, ellipsoid="WSG84"
        )

import logging

import numpy as np
from pymap3d.ecef import ecef2geodetic
from skyfield.api import wgs84

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
filehandler = logging.FileHandler("debug.log")
filehandler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)


class SpecularPointSolver:
    """Class to collect the specular point solver functions"""

    def __init__(self):
        """Initialise the class instance with Fibonacci sequence for iteration"""
        self.receiver_position = np.array([0, 0, 0])
        self.transmitter_position = np.array([0, 0, 0])
        self.fibonacci = np.array(SpecularPointSolver.fibonacci(60))
        self.number_of_iterations = 0

    def set_input_data(
        self, receiver_position: np.array, transmitter_position: np.array
    ) -> None:
        """Set the input data for an iterative solution"""
        self.receiver_position = receiver_position
        self.transmitter_position = transmitter_position
        self.number_of_iterations = self.determine_number_of_iterations(
            SpecularPointSolver.calculate_direct_path_length(
                receiver_position, transmitter_position
            )
        )

    @staticmethod
    def fibonacci(number_of_values: int) -> int:
        """Calculate a set number of the Fibonacci numbers"""
        if number_of_values < 2:
            return number_of_values
        fibs = [0, 1]
        for _ in range(2, number_of_values + 1):
            fibs.append(fibs[-1] + fibs[-2])
        return fibs[1:]

    @staticmethod
    def calculate_direct_path_length(
        receiver_position: np.array, transmitter_position: np.array
    ) -> float:
        """Calculate the magnitude of the vector describing the direct path
        between the transmitter and reciever"""
        logger.debug("calculate_direct_path_length")
        logger.debug("Input")
        logger.debug(receiver_position, transmitter_position)
        logger.debug("Output")
        logger.debug(np.linalg.norm(receiver_position - transmitter_position))
        return np.linalg.norm(receiver_position - transmitter_position)

    def determine_number_of_iterations(self, direct_path_length):
        """Determine the number of iterations using the Fibonacci sequence
        and direct path length"""
        return np.searchsorted(self.fibonacci, direct_path_length)

    @staticmethod
    def calculate_nadir(position: np.array) -> np.array:
        """Calculate the nadir (position on the earth) of a point using the
        WGS84 Geoid"""
        theta_rads = np.arcsin(position[2] / np.linalg.norm(position))
        cos_theta = np.cos(theta_rads)
        cos_theta_squared = cos_theta ** 2
        latitude_dependant_earth_radius = wgs84.radius.m * np.sqrt(
            (1 - wgs84._e2) / (1 - (wgs84._e2 * cos_theta_squared))
        )
        logger.debug("calculate_nadir")
        logger.debug("Input")
        logger.debug(position)
        logger.debug("Output")
        logger.debug(
            latitude_dependant_earth_radius * (position / np.linalg.norm(position))
        )
        return latitude_dependant_earth_radius * (position / np.linalg.norm(position))

    @staticmethod
    def calculate_propagation_distance(
        transmitter_position: np.array,
        reciever_position: np.array,
        specular_point: np.array,
    ) -> float:
        """Calculate the distance from the transmitter to the specular
        point and then onto the receiver."""
        logger.debug("calculate_propagation_distance")
        logger.debug("Input")
        logger.debug(transmitter_position, reciever_position, specular_point)
        logger.debug("Output")
        logger.debug(
            np.linalg.norm(specular_point - transmitter_position)
            + np.linalg.norm(reciever_position - specular_point),
        )
        return np.linalg.norm(specular_point - transmitter_position) + np.linalg.norm(
            reciever_position - specular_point
        )

    def _do_iteration(
        self,
        modified_receiver_position: np.array,
        modified_transmitter_position: np.array,
        iteration_number: int,
    ) -> tuple:
        """Run a single iteration of the specular point solver"""
        term_1 = (
            self.fibonacci[self.number_of_iterations - iteration_number - 2]
            / self.fibonacci[self.number_of_iterations - iteration_number]
        )
        term_2 = (
            self.fibonacci[self.number_of_iterations - iteration_number - 1]
            / self.fibonacci[self.number_of_iterations - iteration_number]
        )
        m_lambda = modified_receiver_position + term_1 * (
            modified_transmitter_position - modified_receiver_position
        )
        m_mu = modified_receiver_position + term_2 * (
            modified_transmitter_position - modified_receiver_position
        )
        s_lambda = SpecularPointSolver.calculate_nadir(m_lambda)
        s_mu = SpecularPointSolver.calculate_nadir(m_mu)
        f_lambda = SpecularPointSolver.calculate_propagation_distance(
            self.transmitter_position, self.receiver_position, s_lambda
        )
        f_mu = SpecularPointSolver.calculate_propagation_distance(
            self.transmitter_position, self.receiver_position, s_mu
        )
        logger.debug("_do_iteration")
        logger.debug("Inputs")
        logger.debug(
            modified_receiver_position, modified_transmitter_position, iteration_number
        )
        logger.debug("Output")
        logger.debug(
            term_1,
            term_2,
            m_lambda,
            m_mu,
            s_lambda,
            s_mu,
            f_lambda,
            f_mu,
        )
        if f_lambda > f_mu:
            return (m_lambda, modified_transmitter_position, m_lambda)
        return (modified_receiver_position, m_mu, m_lambda)

    def _iterate_specular_point(
        self, modified_receiver_position, modified_transmitter_position
    ):
        """Run the iteration to determine the output from the model"""
        m_lambda = self.receiver_position
        for iteration in range(self.number_of_iterations - 2):
            (
                modified_receiver_position,
                modified_transmitter_position,
                m_lambda,
            ) = self._do_iteration(
                modified_receiver_position,
                modified_transmitter_position,
                (iteration + 1),
            )
        return m_lambda

    def determine_coarse_specular_point_position(self):
        """Iterate and determine the specular point solution on the
        WGS84 Geoid"""
        logger.debug("determine_coarse_specular_point_position")
        logger.debug("Input")
        logger.debug(self.receiver_position, self.transmitter_position)
        logger.debug("Iterations begin")
        m_lambda = self._iterate_specular_point(
            self.receiver_position, self.transmitter_position
        )
        logger.debug("Iterations end")
        logger.debug("Output")
        logger.debug(SpecularPointSolver.calculate_nadir(m_lambda))
        position = SpecularPointSolver.calculate_nadir(m_lambda)
        logger.debug(ecef2geodetic(position[0], position[1], position[2]))
        return SpecularPointSolver.calculate_nadir(m_lambda)

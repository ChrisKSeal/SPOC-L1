import numpy as np
import pytest

from src.specularpoint import SpecularPointSolver


@pytest.mark.dependency()
def test_calculate_nadir():
    position = np.array([-4932792.52691575, 265773.534792175, -4039772.70569845])
    assert SpecularPointSolver.calculate_nadir(position) == pytest.approx(
        np.array([-4923590.92159792, 265277.762233784, -4032236.93487315]),
        abs=1.0,  # tolerance of 1 metre
    )


def test_calculate_propagation_distance():
    transmitter_position = np.array(
        [-22052644.76142904, -13074480.840453148, 7530822.467494242]
    )
    receiver_position = np.array(
        [-4913538.73980396, 280776.609248639, -4052785.53858799]
    )
    specular_point = np.array([-4923590.92159792, 265277.762233784, -4032236.93487315])
    assert SpecularPointSolver.calculate_propagation_distance(
        transmitter_position, receiver_position, specular_point
    ) == pytest.approx(
        24625558.1007588, abs=1.0
    )  # tolerance of 1 metre


@pytest.mark.dependency(depends=["test_calculate_nadir"])
def test_determine_coarse_specular_point_position():
    transmitter_position = np.array(
        [-22052644.76142904, -13074480.840453148, 7530822.467494242]
    )
    receiver_position = np.array(
        [-4913538.73980396, 280776.609248639, -4052785.53858799]
    )
    known_specular_point = np.array(
        [-4923590.92159792, 265277.762233784, -4032236.93487316]
    )
    sp = SpecularPointSolver()
    sp.set_input_data(receiver_position, transmitter_position)
    assert sp.determine_coarse_specular_point_position() == pytest.approx(
        known_specular_point, abs=1.0  # tolerance of 1 metre
    )

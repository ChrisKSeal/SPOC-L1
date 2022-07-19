import json
from copy import deepcopy
from pathlib import Path

import mat73
import numpy as np
import pandas as pd


def read_json(json_file: Path) -> dict:
    """Reads and parses a JSON formatted file

    Args:
        json_file: The file path to the JSON formatted file

    Returns:
        A python dictionary containing the parsed file
    """

    try:
        with open(json_file, "r", encoding="utf8") as in_file:
            json_dict = json.load(in_file)
    except Exception as err:
        raise err
    return json_dict


def write_json(json_dict: dict, json_file: Path) -> None:
    """Writes a JSON formatted file from a python dictionary

    Args:
        json_dict: The python dictionary to be serialised
        json_file: The file path to the JSON formatted file

    Returns:
        None
    """

    try:
        with open(json_file, "w", encoding="utf8") as out_file:
            json.dump(json_dict, out_file, indent=4)
    except Exception as err:
        raise err


def extract_mat(mat_file: Path) -> dict:
    """Reads a .mat file and returns a Python dictionary of stored data"""

    return_dict = mat73.loadmat(mat_file)
    return return_dict


def recursively_change_np_arrays_to_lists(input_dict: dict) -> dict:
    cleaned_dict = {}
    for key in input_dict.keys():
        item = input_dict[key]
        if isinstance(item, dict):
            cleaned_dict[key] = recursively_change_np_arrays_to_lists(input_dict[key])
        elif isinstance(item, np.ndarray):
            cleaned_dict[key] = input_dict[key].tolist()
        else:
            cleaned_dict[key] = input_dict[key]
    return cleaned_dict


def process_sat_mat(mat_file: Path) -> None:
    data_dict = extract_mat(mat_file)
    print(data_dict["SatPos"]["SatPos_00000"]["GNSS_4"])
    print(data_dict["SatPos"]["SatPos_00000"]["ECEF_4"])
    print(data_dict["SatPos"]["SatPos_00000"]["LLA_4"])
    print(data_dict.keys())
    print(data_dict["SatPos"].keys())
    for key in data_dict["SatPos"].keys():
        # print(data_dict["SatPos"]["FID_00000"])
        if key.startswith("FID"):
            print(data_dict["SatPos"][key])
    # for key in data_dict["SatPos"]["SatPos_00000"].keys():
    #    if key.startswith("GNSS"):
    #        print(key, data_dict["SatPos"]["SatPos_00000"][key])
    for key in data_dict["SatPos"].keys():
        if key.startswith("SatPos"):
            ecef_df = pd.DataFrame(data_dict["SatPos"][key]["ECEF_4"])
            lla_df = pd.DataFrame(data_dict["SatPos"][key]["LLA_4"])
            ecef_file = key + "_ECEF.csv"
            lla_file = key + "_LLA.csv"
            ecef_df.to_csv(ecef_file)
            lla_df.to_csv(lla_file)


def process_flight_ecef_mat(mat_file: Path) -> None:
    data_dict = extract_mat(mat_file)
    print(data_dict["flight_ecef"].keys())
    print(data_dict["flight_ecef"]["ID_00001"])
    print(data_dict["flight_ecef"]["stamp_00001"])
    print(data_dict["flight_ecef"]["ECEF_00001"])
    flight_df = pd.DataFrame(data_dict["flight_ecef"]["ECEF_00001"])
    flight_df["timestamp"] = data_dict["flight_ecef"]["stamp_00001"]
    flight_df.to_csv("/home/chris/GitRepos/rongowai-L1/tests/XL_flight_ecef.csv")


def process_flight_lla_mat(mat_file: Path):
    data_dict = extract_mat(mat_file)
    print(data_dict["flight_lla"].keys())
    print(data_dict["flight_lla"]["ID_00001"])
    print(data_dict["flight_lla"]["stamp_00001"])
    print(data_dict["flight_lla"]["LLA_00001"])
    flight_df = pd.DataFrame(data_dict["flight_lla"]["LLA_00001"])
    flight_df["timestamp"] = data_dict["flight_lla"]["stamp_00001"]
    flight_df.to_csv("/home/chris/GitRepos/rongowai-L1/tests/XL_flight_lla.csv")


root_dir = Path("/home/chris/Projects/SP-Rongowai/SP sovler - Rongowai/int/")
for filename in root_dir.glob("SatPos.mat"):
    process_sat_mat(filename)
"""flight_ecef = Path(
    "/home/chris/Projects/SP-Rongowai/SP sovler - Rongowai/int/flight_ecef.mat"
)
flight_lla = Path(
    "/home/chris/Projects/SP-Rongowai/SP sovler - Rongowai/int/flight_lla.mat"
)
process_flight_ecef_mat(flight_ecef)
process_flight_lla_mat(flight_lla)"""

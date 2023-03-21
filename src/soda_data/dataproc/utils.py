import os
import json
from numpy.random import choice
from typing import Dict, List, Optional
from soda_data import XML_FOLDER, JSON_FOLDER

SPLIT_FILE = os.path.join(JSON_FOLDER, "split.json")


def create_split(
        probs: Optional[List[float]] = [0.1, 0.1, 0.8],
        split_file: str = SPLIT_FILE,
        xml_data_dir: str = XML_FOLDER) -> Dict[str, str]:
    """
    AI is creating summary for assign_split
    Args:
        probs (`list(float)`, optional): List of probabilities for each split
    Returns:
        dict: Dictionary with keys as filenames and split as values
    """
    # Check first if a split file exists
    if not os.path.exists(xml_data_dir):
        raise FileNotFoundError(f"XML data folder {xml_data_dir} does not exist")

    if os.path.exists(split_file):
        with open(split_file, "r") as fp:
            split_dict = json.load(fp)
    else:
        split_dict = {}

    for filename in os.listdir(xml_data_dir):
        if filename.split(".xml")[0] not in list(split_dict.keys()):
            split = choice(["test", "validation", "train"], p=probs)
            split_dict[filename.split(".xml")[0]] = split

    with open(split_file, "w") as fp:
        json.dump(split_dict, fp)

    return split_dict

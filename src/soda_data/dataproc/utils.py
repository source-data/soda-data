import os
import json
from numpy.random import choice
from typing import Dict, List, Optional

SPLIT_FILE = "/app/data/json/split_dict.json"
XML_DATA_DIR = "/app/data/xml"


def create_split(probs: Optional[List[float]] = [0.1, 0.1, 0.8]) -> Dict[str, str]:
    """
    AI is creating summary for assign_split
    Args:
        probs (`list(float)`, optional): List of probabilities for each split
    Returns:
        dict: Dictionary with keys as filenames and split as values
    """
    # Check first if a split file exists
    if os.path.exists(SPLIT_FILE):
        with open(SPLIT_FILE, "r") as fp:
            split_dict = json.load(fp)
    else:
        split_dict = {}

    for filename in os.listdir(XML_DATA_DIR):
        if filename.split(".xml")[0] not in list(split_dict.keys()):
            split = choice(["test", "validation", "train"], p=probs)
            split_dict[filename.split(".xml")[0]] = split

    with open(SPLIT_FILE, "w") as fp:
        json.dump(split_dict, fp)

    return split_dict

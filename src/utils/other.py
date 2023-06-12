import random
from os import getenv
from typing import List


def get_environment_vars(*variables: str) -> List[str]:
    out = []
    for variable_name in variables:
        variable = getenv(variable_name)
        if variable is None:
            raise ValueError(f"Missing {variable_name} in environment")
        out.append(variable)
    return out


def pick_random_from_list(_list):
    return random.choice(_list)

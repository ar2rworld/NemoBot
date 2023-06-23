import random
from os import getenv


def get_environment_vars(*variables: str) -> list[str]:
    out = []
    for variable_name in variables:
        variable = getenv(variable_name)
        if variable is None:
            msg = f"Missing {variable_name} in environment"
            raise ValueError(msg)
        out.append(variable)
    return out


def pick_random_from_list(_list: list[dict]) -> dict:
    return random.choice(_list)

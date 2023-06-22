import random
from os import getenv


def get_environment_vars(*variables: str) -> list[str]:
    out = []
    p = {}
    with open(".envTestRemote") as f:
        lines = f.readlines()
        for line in lines:
            a, b = line.split("=")
            p[a] = b.replace("\n", "")
    for variable_name in variables:
        variable = getenv(variable_name)
        variable = p[variable_name]
        print(variable_name, variable)
        if variable is None:
            msg = f"Missing {variable_name} in environment"
            raise ValueError(msg)
        out.append(variable)
    return out


def pick_random_from_list(_list: list[dict]) -> dict:
    return random.choice(_list)

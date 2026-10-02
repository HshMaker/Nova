from dataclasses import dataclass


@dataclass
class Variable:
    type_name: str
    value: object

from dataclasses import dataclass
from nova.ast_nodes import Parameter


@dataclass
class Function:
    name: str
    parameters: list[Parameter]
    return_type: str | None
    body: list
    closure: dict

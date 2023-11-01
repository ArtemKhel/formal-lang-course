from pathlib import Path
from typing import Self

from pyformlang.cfg import Variable, Terminal
from pyformlang.regular_expression import Regex

from project.utils.rsm import RSM


class ECFG:
    def __init__(
        self,
        variables: AbstractSet[Variable] = None,
        terminals: AbstractSet[Terminal] = None,
        productions: dict[Variable, Regex] = None,
        start_symbol: Variable = None,
    ):
        self._variables = variables
        self._terminals = terminals
        self._productions = productions
        self._start_symbol = start_symbol

    @property
    def variables(self) -> AbstractSet[Variable]:
        return self._variables

    @property
    def productions(self) -> dict[Variable, Regex]:
        return self._productions

    @property
    def start_symbol(self) -> Variable:
        return self._start_symbol

    @classmethod
    def from_text(cls, text: str, start_symbol=Variable('S')) -> Self:
        variables = set()
        productions = dict()
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue

            head, body = line.split('->')
            head = Variable(head.strip())
            variables.add(head)
            productions[head] = Regex(body.strip())
        return cls(variables=variables, start_symbol=start_symbol, productions=productions)

    @classmethod
    def from_file(cls, file: Path, start_symbol=Variable('S')) -> Self:
        with open(file) as f:
            return cls.from_text(f.read(), start_symbol)


def ecfg_to_rsm(ecfg: ECFG) -> RSM:
    transitions = {}
    for var in ecfg.variables:
        transitions[var] = ecfg.productions[var].to_epsilon_nfa()
    return RSM(ecfg.start_symbol, transitions)

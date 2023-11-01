from pyformlang.cfg import Variable
from pyformlang.finite_automaton import DeterministicFiniteAutomaton


class RSM:
    def __init__(self, start_symbol: Variable, transitions: dict[Variable, DeterministicFiniteAutomaton]):
        self._start_symbol = start_symbol
        self._transitions = transitions

    def minimize(self):
        self._transitions = {v: tr.minimize() for v, tr in self._transitions.items()}

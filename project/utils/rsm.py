from typing import Self, Iterable

from pyformlang.cfg import Variable
from pyformlang.finite_automaton import DeterministicFiniteAutomaton


class RSMBox:
    def __init__(self, start_symbol: Variable, dfa: DeterministicFiniteAutomaton):
        self._start_symbol = start_symbol
        self._dfa = dfa

    @property
    def start_symbol(self) -> Variable:
        return self._start_symbol

    @property
    def dfa(self) -> DeterministicFiniteAutomaton:
        return self._dfa

    def minimize(self):
        self._dfa = self._dfa.minimize()


class RSM:
    def __init__(self, start_symbol: Variable, boxes: Iterable[RSMBox]):
        self._start_symbol = start_symbol
        self._boxes = boxes

    @property
    def boxes(self) -> Iterable[RSMBox]:
        return self._boxes

    @property
    def start_symbol(self) -> Variable:
        return self._start_symbol

    def minimize(self) -> Self:
        for b in self._boxes:
            b.minimize()
        return self

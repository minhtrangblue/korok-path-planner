from core.optimiser import Optimiser
from typing import Tuple

class Solver:
    def __init__(self, optimiser: Optimiser) -> None:
        self._optimiser = optimiser

    @property
    def optimiser(self) -> Optimiser:
        return self._optimiser

    @optimiser.setter
    def optimiser(self, optimiser: Optimiser) -> None:
        self._optimiser = optimiser

    def solve(self) -> Tuple[list, float]:
        return self._optimiser.optimise()



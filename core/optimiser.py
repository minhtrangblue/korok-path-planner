from abc import ABC, abstractmethod
from typing import Tuple, Optional
import random
import math as m
from itertools import permutations


class Optimiser(ABC):

    @abstractmethod
    def get_nodes(self) -> list:
        ...

    @abstractmethod
    def set_nodes(self, val: list) -> None:
        ...

    nodes = property(get_nodes, set_nodes)

    @abstractmethod
    def optimise(self) -> Tuple[list, float]:
        ...


class ExactOptimiser(Optimiser):
    def __init__(self, nodes: list):
        self._nodes = nodes
        self._cost = [[None for _ in range(len(nodes[0]))] for _ in range(len(nodes[0]))]

    def get_nodes(self) -> list:
        return self._nodes

    def set_nodes(self, val: list) -> None:
        self._nodes = val

    nodes = property(get_nodes, set_nodes)

    def cal_route_cost(self, nodes_idx: list) -> float:
        route_cost = 0
        for i in range(1, len(nodes_idx)):
            start_node = nodes_idx[i - 1]
            end_node = nodes_idx[i]
            # calculate distance value if not yet calculated
            if not self._cost[start_node][end_node]:
                self._cost[start_node][end_node] = ((self.nodes[0][end_node] - self.nodes[0][start_node]) / 4) ** 2 + (
                        (self.nodes[1][end_node] - self.nodes[1][start_node]) / 4) ** 2
            # add to total sum
            route_cost = route_cost + self._cost[start_node][end_node]
        return route_cost

    def optimise(self) -> Tuple[list, float]:
        nodes_idx = list(range(len(self.nodes[0])))
        energy_best = self.cal_route_cost(nodes_idx)
        route_best = nodes_idx
        for _, route in enumerate(permutations(nodes_idx)):
            energy_curr = self.cal_route_cost(route)
            if energy_curr < energy_best:
                route_best = route
                energy_best = energy_curr
        route_coord = [[row[col] for col in route_best] for row in self.nodes]
        return route_coord, energy_best


class SimulatedAnnealing(Optimiser):
    def __init__(self, nodes: list, batch_size=1000, shuffle: Optional[bool] = False):
        self._nodes = nodes
        self._batch_size = batch_size
        self._shuffle = shuffle
        self._cost = [[None for _ in range(len(nodes[0]))] for _ in range(len(nodes[0]))]

    def get_nodes(self) -> list:
        return self._nodes

    def set_nodes(self, val: list) -> None:
        self._nodes = val

    nodes = property(get_nodes, set_nodes)

    @property
    def shuffle(self):
        return self._shuffle

    @shuffle.setter
    def shuffle(self, val: bool):
        self._shuffle = val

    def cal_route_cost(self, nodes_idx: list) -> float:
        route_cost = 0
        for i in range(1, len(nodes_idx)):
            start_node = nodes_idx[i - 1]
            end_node = nodes_idx[i]
            # calculate distance value if not yet calculated
            if not self._cost[start_node][end_node]:
                self._cost[start_node][end_node] = ((self.nodes[0][end_node] - self.nodes[0][start_node]) / 10) ** 2 + (
                        (self.nodes[1][end_node] - self.nodes[1][start_node]) / 10) ** 2
            # add to total sum
            route_cost = route_cost + self._cost[start_node][end_node]
        return route_cost

    def optimise(self) -> Tuple[list, float]:
        # init route
        nodes_idx = list(range(len(self.nodes[0])))
        # if shuffle is True, shuffle input before running simulated annealing
        if self._shuffle:
            random.shuffle(nodes_idx)
        # run simulated annealing
        energy_curr = self.cal_route_cost(nodes_idx)
        route_best = nodes_idx.copy()
        energy_best = energy_curr
        for i in range(len(self.nodes[0])):
            temperature = 1 / (1 + i)
            for j in range(self._batch_size):
                # swapping 2 nodes as next state and calculate cost
                id1 = random.randrange(1, len(self.nodes[0]) - 1)
                id2 = random.randrange(1, len(self.nodes[0]) - 1)
                route_next = nodes_idx.copy()
                route_next[min(id1, id2):max(id1, id2)] = route_next[max(id1, id2)-1:min(id1, id2)-1:-1]
                energy_next = self.cal_route_cost(route_next)
                # evaluate next state
                energy_delta = energy_next - energy_curr
                if energy_delta <= 0:
                    # if cost is lower accept state
                    nodes_idx = route_next.copy()
                    energy_curr = energy_next
                    route_best = route_next.copy()
                    energy_best = energy_next
                else:
                    if temperature > 0 and m.exp(-1 * energy_delta / temperature) >= random.uniform(0, 1):
                        # if cost is higher accept state with certain probability
                        nodes_idx = route_next.copy()
                        energy_curr = energy_next
        route_coord = [[row[col] for col in route_best] for row in self.nodes]
        return route_coord, energy_best



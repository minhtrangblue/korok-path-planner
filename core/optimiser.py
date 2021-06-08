from abc import ABC, abstractmethod
from typing import Tuple
import random
import math as m
from itertools import permutations


class Optimiser(ABC):

    @abstractmethod
    def optimise(self) -> Tuple[list, float]:
        ...


class SimulatedAnnealing(Optimiser):
    def __init__(self, nodes: list,batch_size=1000):
        self._nodes = nodes
        self.batch_size = batch_size
        self.cost = [[None for _ in range(len(nodes[0]))] for _ in range(len(nodes[0]))]

    @property
    def nodes(self) -> list:
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: list) -> None:
        self._nodes = nodes

    def cal_route_cost(self, nodes_idx: list) -> float:
        route_cost = 0
        for i in range(1, len(nodes_idx)):
            start_node = nodes_idx[i - 1]
            end_node = nodes_idx[i]
            # calculate distance value if not yet calculated
            if not self.cost[start_node][end_node]:
                self.cost[start_node][end_node] = ((self.nodes[0][end_node] - self.nodes[0][start_node]) / 4) ** 2 + (
                        (self.nodes[1][end_node] - self.nodes[1][start_node]) / 4) ** 2
            # add to total sum
            route_cost = route_cost + self.cost[start_node][end_node]
        return route_cost

    def cal_exact_path(self) -> Tuple[list, float]:
        nodes_idx = list(range(len(self.nodes[0])))
        energy_best = self.cal_route_cost(nodes_idx)
        route_best = nodes_idx
        for _, route in enumerate(permutations(nodes_idx)):
            energy_curr = self.cal_route_cost(route)
            if energy_curr < energy_best:
                route_best = route
                energy_best = energy_curr
        route_coord = [[row[col] for col in route_best] for row in self.nodes]
        route_coord = list(map(list, zip(*route_coord[::-1])))
        return route_coord, energy_best

    def cal_estimated_path(self) -> Tuple[list, float]:
        # init route
        nodes_idx = list(range(len(self.nodes[0])))
        random.shuffle(nodes_idx)
        # run simulated annealing
        # history = [0 for _ in range(self.nodes.shape[1]*self.batch_size)]
        energy_curr = self.cal_route_cost(nodes_idx)
        route_best = nodes_idx.copy()
        energy_best = energy_curr
        # temperature = 1
        for i in range(len(self.nodes[0])):
            temperature = 1 / (1 + 100 * i / len(self.nodes[0]))
            for j in range(self.batch_size):
                # swapping 2 nodes as next state and calculate cost
                id1 = random.randrange(1, len(self.nodes[0]) - 1)
                id2 = random.randrange(1, len(self.nodes[0]) - 1)
                route_next = nodes_idx.copy()
                route_next[id1], route_next[id2] = route_next[id2], route_next[id1]
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
                    if temperature > 0 and m.exp((-1 * energy_delta / energy_curr) / temperature) >= random.uniform(0,
                                                                                                                    1):
                        # if cost is higher accept state with certain probability
                        nodes_idx = route_next.copy()
                        energy_curr = energy_next
            # history[i] = E_curr
        route_coord = [[row[col] for col in route_best] for row in self.nodes]
        route_coord = list(map(list, zip(*route_coord[::-1])))
        return route_coord, energy_best

    def optimise(self) -> Tuple[list, float]:
        if len(self.nodes[0]) <= 8:
            # if fewer than 8 nodes run exact algorithm
            route_coord, energy_best = self.cal_exact_path()
        else:
            # if more than 8 nodes run estimation
            route_coord, energy_best = self.cal_estimated_path()

        return route_coord, energy_best

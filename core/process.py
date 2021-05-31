import random
import math as m
from itertools import permutations


class simulatedAnnealling:
    def __init__(self, nodes, batch_size=1000):
        self.batch_size = batch_size
        self.nodes = nodes
        self.cost = [[None for _ in range(nodes.shape[1])] for _ in range(nodes.shape[1])]

    def calRouteCost(self, nodes_idx):
        routeCost = 0
        for i in range(1, len(nodes_idx)):
            try:
                start_node = nodes_idx[i - 1]
                end_node = nodes_idx[i]
                # calculate distance value if not yet calculated
                if not self.cost[start_node][end_node]:
                    self.cost[start_node][end_node] = (self.nodes[0, end_node] - self.nodes[0, start_node]) ** 2 + (
                                self.nodes[1, end_node] - self.nodes[1, start_node]) ** 2
                # add to total sum
                routeCost = routeCost + self.cost[start_node][end_node]
            except Exception as e:
                print(e)
        return routeCost

    def calExactPath(self):
        nodes_idx = list(range(0, self.nodes.shape[1]))
        energy_best = self.calRouteCost(nodes_idx)
        route_best = nodes_idx
        for _, route in enumerate(permutations(nodes_idx)):
            energy_curr = self.calRouteCost(route)
            if energy_curr < energy_best:
                route_best = route
                energy_best = energy_curr
        return self.nodes[:, route_best], energy_best
        
    def optimise(self):
        # init route
        nodes_idx = list(range(0, self.nodes.shape[1]))
        random.shuffle(nodes_idx)
        # run simulated annealling
        # history = [0 for _ in range(self.nodes.shape[1]*self.batch_size)]
        energy_curr = self.calRouteCost(nodes_idx)
        route_best = nodes_idx.copy()
        energy_best = energy_curr
        T = 1
        for i in range(self.nodes.shape[1]*self.batch_size):
            # T = 1 - (i / (self.nodes.shape[1]*self.batch_size))
            T = T / (100 * ((i+1) / (self.nodes.shape[1] * self.batch_size)))
            # swapping 2 nodes as next state and calculate cost
            id1 = random.randrange(1, self.nodes.shape[1] - 1)
            id2 = random.randrange(1, self.nodes.shape[1] - 1)
            route_next = nodes_idx.copy()
            route_next[id1], route_next[id2] = route_next[id2], route_next[id1]
            energy_next = self.calRouteCost(route_next)
            # evaluate next state
            energy_delta = energy_next - energy_curr
            if energy_delta <= 0:
                # if cost is lower accept state
                nodes_idx = route_next.copy()
                energy_curr = energy_next
                route_best = route_next.copy()
                energy_best = energy_next
            else:
                if T > 0 and m.exp((-1) / (T)) >= random.uniform(0, 1):
                # if cost is higher accept state with certain probability
                    nodes_idx = route_next.copy()
                    energy_curr = energy_next
            # history[i] = E_curr
        return self.nodes[:, route_best], energy_best
import random
import math as m


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

    def optimise(self):
        # init route
        nodes_idx = list(range(0, self.nodes.shape[1]))
        random.shuffle(nodes_idx)
        # run simulated annealling
        # history = [0 for _ in range(self.nodes.shape[1]*self.batch_size)]
        E_curr = self.calRouteCost(nodes_idx)
        s_best = nodes_idx.copy()
        E_best = E_curr
        for i in range(self.nodes.shape[1]*self.batch_size):
            T = 1 - (i / (self.nodes.shape[1]*self.batch_size))
            # swapping 2 nodes as next state and calculate cost
            id1 = random.randrange(1, self.nodes.shape[1] - 1)
            id2 = random.randrange(1, self.nodes.shape[1] - 1)
            s_next = nodes_idx.copy()
            s_next[id1], s_next[id2] = s_next[id2], s_next[id1]
            E_next = self.calRouteCost(s_next)
            # evaluate next state
            E_delta = E_next - E_curr
            if E_delta <= 0:
                # if cost is lower accept state
                nodes_idx = s_next.copy()
                E_curr = E_next
                s_best = s_next.copy()
                E_best = E_next
            elif m.exp((-1) / (T)) >= random.uniform(0, 1):
                # if cost is higher accept state with certain probability
                nodes_idx = s_next.copy()
                E_curr = E_next
            # history[i] = E_curr
        return self.nodes[:, s_best], E_best
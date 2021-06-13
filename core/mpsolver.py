import multiprocessing
from core.optimiser import Optimiser
from typing import Tuple, Optional


class MPSolver:

    def __init__(self, optimiser: Optimiser, num_proc: Optional[int] = 4):
        self._optimiser = optimiser
        self._num_proc = min(multiprocessing.cpu_count(), num_proc)
        # self._exit_event = multiprocessing.Manager().Event()
        # self._output_queue = multiprocessing.Manager().Queue(maxsize=self._num_proc)

    @property
    def optimiser(self) -> Optimiser:
        return self._optimiser

    @optimiser.setter
    def optimiser(self, optimiser: Optimiser) -> None:
        self._optimiser = optimiser

    @property
    def num_proc(self) -> int:
        return self._num_proc

    def worker_solve(self, worker_id: int) -> Tuple[list, float]:
        # print('Worker ' + str(worker_id) + ' starts ')
        route_coord, energy_best = self._optimiser.optimise()
        # self._output_queue.put_nowait((route_coord, energy_best))
        # self._exit_event.set()
        return route_coord, energy_best

    def solve(self) -> Tuple[list, float]:
        # start pool
        pool = multiprocessing.Pool(self.num_proc)
        args = list(range(self.num_proc))
        # solve in parallel
        intermediate_result = pool.map_async(self.worker_solve, args)
        intermediate_result.wait()
        pool.close()
        pool.join()
        # pool terminated
        # return best route from all processes
        routes = []
        energies = []
        for (route_coord, energy_best) in intermediate_result.get():
            routes.append(route_coord)
            energies.append(energy_best)
        index_min = min(range(len(energies)), key=energies.__getitem__)
        # use best route found to initialise the optimiser one more time
        self._optimiser.set_nodes(routes[index_min])
        route_coord, energy_best = self._optimiser.optimise()
        # return the best route found
        if energy_best < energies[index_min]:
            pass
        else:
            route_coord = routes[index_min]
            energy_best = energies[index_min]
        return route_coord, energy_best

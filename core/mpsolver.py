import multiprocessing
from core.optimiser import Optimiser
from typing import Tuple
import os


class MPSolver:

    def __init__(self, optimiser: Optimiser, num_proc: int):
        self._optimiser = optimiser
        self._num_proc = num_proc
        self.exit_event = multiprocessing.Manager().Event()
        self.input_stream = multiprocessing.Manager().list(nodes)
        self.output_queue = multiprocessing.Manager().Queue(maxsize=1)

    @property
    def optimiser(self) -> Optimiser:
        return self._optimiser

    @optimiser.setter
    def optimiser(self, optimiser: Optimiser) -> None:
        self._optimiser = optimiser

    @property
    def num_proc(self) -> int:
        return self._num_proc

    def solve(self) -> Tuple[list, float]:
        return self._optimiser.optimise()

    def func(self, no, target):
        x = no ** 2
        print('Process: ' + str(os.getpid()) + ' returns ' + str(x))
        if x == target:
            print('Found')
            self.output_queue.put([x, x*x])
            self.exit_event.set()

    def run(self, target):
        args = [(no, target) for no in self.input_stream]
        print("start pool")
        pool = multiprocessing.Pool(self.num_proc)
        result = pool.starmap_async(self.func, args)
        # result.wait()
        # pool.close()
        self.exit_event.wait()
        print(self.output_queue.get())
        pool.terminate()
        # pool.join()
        print('pool terminated')



if __name__ == '__main__':
    ncpu = 2
    # l = [6, 2, 7, 1, 4, 5, 1, 8, 7]
    nodes = [[1375.5, 1229., 1264.,  1175.,  1244.5, 1172.5, 1207.5, 1178.5, 1302.5],
             [945.5,  941.,   896.,   881.5,  826.,   811.5,  793.5,  790.5,  767.]]

    target = 36
    # e = Event()
    s = MPSolver(ncpu)
    s.run(target)

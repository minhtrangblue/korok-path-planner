from multiprocessing import Process, Event
# from core.solver import SimulatedAnnealing
import random


class MPSolver:

    def __init__(self, num_proc=4):
        self.num_proc = num_proc

    def func(self, x, event):
        print("Worker "+str(x))
        while True:
            x = random.randint(0, 10)
            if x == 5:
                event.set()
                break
        return x

    def run(self):
        event = Event()
        pool = [Process(target=self.func, args=(i, event)) for i in range(self.num_proc)]
        for p in pool:
            p.start()
        event.wait()
        print('Terminating processes')
        for p in pool:
            p.terminate()
        for p in pool:
            p.join()


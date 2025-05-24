import threading
from typing import List

class Locking:
    def __init__(self, total_resources: List[int], max_claim: List[List[int]]):

        self._lock = threading.RLock()
        self.available = total_resources[:]                  # r 
        self.max_claim = [row[:] for row in max_claim]      # p x r
        self.num_processe = len(max_claim)
        self.num_resources = len(total_resources)
        # initially zero allocated
        self.allocated = [[0]*self.num_resources for _ in range(self.num_processe)]

    def request(self, pid: int, req: List[int]) -> bool:
        
        #try to allocate req to process pid.
        #return True if granted.
        
        with self._lock:
            if any(r > self.max_claim[pid][i] - self.allocated[pid][i]
                   for i, r in enumerate(req)):
                return False

            if any(r > self.available[i] for i, r in enumerate(req)):
                return False

            new_available = [a - r for a, r in zip(self.available, req)]
            new_allocated = [row[:] for row in self.allocated]
            for i in range(self.num_resources):
                new_allocated[pid][i] += req[i]

            if not self._is_safe(new_available, new_allocated):
                return False

            self.available = new_available
            self.allocated = new_allocated
            return True

    def release(self, pid: int, rel: List[int]) -> None:
        #Release resources from process pid.
        with self._lock:
            for i, r in enumerate(rel):
                to_release = min(r, self.allocated[pid][i])
                self.available[i] += to_release
                self.allocated[pid][i] -= to_release

    def _is_safe(self, work: List[int], allocated: List[List[int]]) -> bool:
        #Banker's safety algorithm.

        # compute need = max_claim – alloc
        need = [
            [self.max_claim[p][i] - allocated[p][i]
             for i in range(self.num_resources)]
            for p in range(self.num_processe)
        ]
        finish = [False]*self.num_processe

        while True:
            progressed = False
            for p in range(self.num_processe):
                if not finish[p] and all(need[p][i] <= work[i]
                                         for i in range(self.num_resources)):
                    # pretend this process completes
                    for i in range(self.num_resources):
                        work[i] += allocated[p][i]
                    finish[p] = True
                    progressed = True
            if not progressed:
                break

        return all(finish)

import threading 
from typing import List 
class LockWrapper:
    
    def __init__(self, name: str, rank: int, timeout: float):
        if not name or not isinstance(name, str):
            raise ValueError("Lock name must be a non-empty string.")
        if not isinstance(rank, int):
            raise ValueError("Lock rank must be an integer.")
        if not isinstance(timeout, (int, float)) or timeout <= 0:
            raise ValueError("Lock timeout must be a positive number.")

        self.name = name
        self.rank = rank
        self.timeout = timeout
        self._lock = threading.RLock() # reentrant lock, allowing the same thread to acquire it multiple times.

    def acquire(self, blocking: bool = True, timeout_override: float = -1) -> bool:
        if timeout_override >= 0:
            self.timeout = timeout_override # verride the timeout specified

        if not blocking: # blocking is False -> try to acquire the lock without waiting.
            return self._lock.acquire(blocking=False) 
        # get the lock; wait up to 'self.timeout'. True if acquired, False if timeout.
        acquired = self._lock.acquire(timeout=self.timeout) 
        if not acquired:
            print(f"Timeout: Lock '{self.name}' (rank {self.rank}) "
                  f"could not be acquired within {self.timeout}s.")
        return acquired

    def release(self): # release the lock so allow other threads to acquire it.
        try:
            self._lock.release() 

        except RuntimeError: #  if a thread tries to release a lock it doesn't currently hold.
            print(f"Error: Lock '{self.name}' (rank {self.rank}) release failed (not held).")

    def __enter__(self): # Part of pythons context manager protocol (used with 'with' statements)
        if not self.acquire(): # Automatically tries to acquire the lock when entering a 'with' block.
            raise threading.ThreadError( # An error specific to threading problems.
                f"Timeout acquiring lock '{self.name}' (rank {self.rank})."
            )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb): # Part of Python's "context manager" protocol
        self.release() # automatically releases the lock when exiting the block.
        return False 

    @classmethod #this method belongs to the class.
    def ordered_acquire(cls, locks: List["LockWrapper"]): # cls is the class itself.
        # sort locks by their rank to prevent deadlocks.
        locks_sorted = sorted(locks, key=lambda lock: lock.rank) 
        acquired_locks: List["LockWrapper"] = [] # track of locks
        try:
            for lock in locks_sorted:
                if not lock.acquire(): # try to acquire each lock in the sorted order.
                    raise threading.ThreadError(
                        f"Timeout in ordered acquire for lock '{lock.name}' (rank {lock.rank})."
                    )
                acquired_locks.append(lock)
        except Exception:
            # any of them fails, and release all locks already acquired in reverse order.
            for lock in reversed(acquired_locks): 
                lock.release()
            raise

    @classmethod
    def ordered_release(cls, locks: List["LockWrapper"]):
        # release them in the reverse order they were acquired
        for lock in sorted(locks, key=lambda lock: lock.rank, reverse=True): 
            lock.release()

    def __repr__(self): # thats just representation magic method upon called
        return f"<LockWrapper name={self.name!r} rank={self.rank} timeout={self.timeout}>" 
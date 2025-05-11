import random
import numpy as np
from sortedcontainers import SortedList


class SumTree:
    """Sum tree data structure used for prioritized experience replay

    if N: number of leaf nodes(=items) in the tree,

    Priority update, adding new item, and sampling are done in O(log n) time
    Also stores the priorities in a sorted list to keep track of the max priority and also ranks in order to support rank-based sampling
    """

    def __init__(self, capacity):
        self.capacity = capacity
        self.tree = np.zeros(2 * capacity - 1)
        self.data = np.zeros(capacity, dtype=object)
        self.priorities = SortedList()
        self.max_p = 1
        self.n_entries = 0
        self.write = 0
        self.data_size = 0

    def get_max_priority(self):
        if self.priorities:
            return self.priorities[-1]
        else:
            return 1

    def update(self, idx, priority):
        change = priority - self.tree[idx]

        prev_value = self.tree[idx]
        self.tree[idx] = priority

        assert priority > 0, f"priority: {priority} is not greater than 0"
        self.priorities.discard(prev_value)
        self.priorities.add(priority)

        while idx != 0:
            idx = (idx - 1) // 2
            self.tree[idx] += change

    def add(self, priority, data):
        idx = self.write + self.capacity - 1

        self.data[self.write] = data

        self.update(idx, priority)

        self.write = (self.write + 1) % self.capacity
        self.data_size = min(self.data_size + 1, self.capacity)

        if self.n_entries < self.capacity:
            self.n_entries += 1

    def get(self, v):
        idx = 0

        while True:
            left = 2 * idx + 1
            right = left + 1

            if left >= len(self.tree):
                break

            if v <= self.tree[left]:
                idx = left
            else:
                v -= self.tree[left]
                idx = right

        data_idx = idx - self.capacity + 1

        return idx, self.tree[idx], self.data[data_idx]

    def sample(self):
        return self.get(random.uniform(0, self.tree[0]))

    def __len__(self):
        return self.data_size

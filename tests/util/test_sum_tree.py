import unittest
from util.sum_tree import SumTree
from collections import defaultdict 

class SumTreeTest(unittest.TestCase):
    SAMPLE_ERROR_BOUND = 0.02

    def test_sum_tree_basic(self):
        tree = SumTree(4)
        tree.add(40, 1)
        tree.add(30, 2)
        tree.add(20, 3)
        tree.add(10, 4)

        indices = [tree.get(1)[0], tree.get(41)[0], tree.get(71)[0], tree.get(91)[0]]

        # sum of all the priorities = 40 + 30 + 20 + 10 = 100
        assert tree.tree[0] == 100, f"tree.tree[0] should be 100, but it is {tree.tree[0]}"

        # updating first priority makes the total sum = 100 + 30 + 20 + 10 = 160
        tree.update(indices[0], 100)
        assert tree.tree[0] == 160, f"tree.tree[0] should be 160, but it is {tree.tree[0]}"

        # updating second priority makes the total sum = 100 + 100 + 20 + 10 = 230
        tree.update(indices[1], 100)
        assert tree.tree[0] == 230, f"tree.tree[0] should be 230, but it is {tree.tree[0]}"

        # updating third priority makes the total sum = 100 + 100 + 100 + 10 = 310
        tree.update(indices[2], 100)
        assert tree.tree[0] == 310, f"tree.tree[0] should be 310, but it is {tree.tree[0]}"

        # updating fourth priority makes the total sum = 100 + 100 + 100 + 100 = 400
        tree.update(indices[3], 100)
        assert tree.tree[0] == 400, f"tree.tree[0] should be 400, but it is {tree.tree[0]}"

    def test_sum_tree_sample(self):
        tree = SumTree(5)

        priorities = [40, 20, 10, 30, 5]
        for i, priority in enumerate(priorities):
            tree.add(priority, i)

        # the probability of each item being selected is 40/105, 20/105, 10/105, 30/105, 5/105
        probabilities = [priority / tree.tree[0] for priority in priorities]

        SAMPLE_COUNT = 10000

        sample_count_for_each_item = defaultdict(int)

        # If we sample the tree 10000 times, the number of times each item is selected should each be close to the probability of each item being selected
        for _ in range(SAMPLE_COUNT):
            index = tree.sample()[2]
            sample_count_for_each_item[index] += 1

        for i, priority in enumerate(priorities):
            sample_ratio = sample_count_for_each_item[i] / SAMPLE_COUNT
            assert probabilities[i] - self.SAMPLE_ERROR_BOUND <= sample_ratio <= probabilities[i] + self.SAMPLE_ERROR_BOUND, f"sample_ratio for item {i} should be {probabilities[i]}, but it is {sample_ratio}"

if __name__ == '__main__':
    unittest.main()



import random

from tests.BasicTest import BasicTest

"""
测试乱序情况
"""

class RandomShuffleTest(BasicTest):
    def handle_packet(self):
        if random.choice([True, False]):
            return
        random.shuffle(self.forwarder.in_queue)
        for p in self.forwarder.in_queue:
            self.forwarder.out_queue.append(p)

        # empty out the in_queue
        self.forwarder.in_queue = []
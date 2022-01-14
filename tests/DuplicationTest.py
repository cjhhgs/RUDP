import random

from tests.BasicTest import BasicTest

"""
测试重复
"""

class DuplicationTest(BasicTest):
    def handle_packet(self):        
        for p in self.forwarder.in_queue:
            self.forwarder.out_queue.append(p)
            while random.choice([True, False]):
                self.forwarder.out_queue.append(p)

        # empty out the in_queue
        self.forwarder.in_queue = []
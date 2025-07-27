from typing import Dict, Any, List
import graph

def memory_test():
    test_memory = graph.Memory()
    test_data = ("this is a piece of text for testing purposes.")
    print(test_memory.importance_evaluator(data=test_data))


def testing_suite():
    # starting off with a memory test to check if the class if functional
    memory_test()


if __name__ == "__main__":
    testing_suite()
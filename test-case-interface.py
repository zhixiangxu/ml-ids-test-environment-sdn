from abc import ABCMeta

class TestCaseInterface:
    __metaclass__ = ABCMeta

    def run_test(self): raise NotImplementedError
    
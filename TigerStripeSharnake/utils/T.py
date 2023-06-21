import random
import time


class T:

    @staticmethod
    def prob(x):
        assert x > 0 and x < 1, '概率错误'
        return random.uniform(0, 1) < x
    
    @staticmethod
    def ksm(x: float, p: int):
        a, b = 1, x
        while p > 0:
            if p & 1: a *= b
            b *= b
            p >>= 1
        return a
    

class G:
    TIME = 0
    TIME___ = 0

    @classmethod
    def record(cls):
        cls.TIME = time.time()
        
    @classmethod
    def record_(cls):
        cls.TIME___ = time.time()
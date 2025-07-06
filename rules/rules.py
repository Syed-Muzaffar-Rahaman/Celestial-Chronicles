import math

def CalculateModifier(Stats: int):
    from main.config import LogarithmicBase
    if Stats == 0:
        return int('-inf')
    return round(math.log(Stats, base=LogarithmicBase))


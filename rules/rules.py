import math

def CalculateModifier(Stats: int):
    if Stats == 0:
        return int('-inf')
    return round(math.log(Stats, base=1.25))


import random
import time
from typing import Optional, Callable, List

class Dice:
	registry = {}

	def __init__(self, sides: int, weights: Optional[List[float]] = None, seed: Optional[int] = None):
		if sides < 2:
			raise ValueError("Dice must have at least 2 sides.")

		self.sides = sides
		self.faces = list(range(1, sides + 1))

		if weights is not None:
			if min(weights) == max(weights):
				weights = None
			else:
				if len(weights) != sides:
					raise ValueError("Number of weights must match number of sides.")
				if any(w < 0 for w in weights):
					raise ValueError("Weights must be non-negative.")
				if sum(weights) <= 0:
					raise ValueError("Sum of weights must be greater than zero.")
		self.weights = weights

		self.seed = seed if seed is not None else int(time.time_ns())
		self.rng = random.Random(self.seed)


	def Roll(self) -> int:
		return self.rng.choices(self.faces, weights=self.weights)[0]

	def RollMany(self, k: int) -> List[int]:
		if k < 1:
			raise ValueError("Must roll at least once.")
		return [self.Roll() for _ in range(k)]

	def RerollUntil(self, condition: Callable[[List[int]], bool]) -> List[int]:
		results = []
		while True:
			result = self.Roll()
			results.append(result)
			if not condition(results):
				break
		return results
	
	def RerollOnMin(self) -> List[int]:
		return self.RerollUntil(lambda rolls: rolls[-1] == 1)
	
	def RerollOnMax(self) -> List[int]:
		return self.RerollUntil(lambda rolls: rolls[-1] == self.sides)

	def GetSeed(self) -> int:
		return self.seed

	def Reseed(self, new_seed: Optional[int] = None):
		self.seed = new_seed if new_seed is not None else int(time.time_ns())
		self.rng.seed(self.seed)

	def __repr__(self):
		if self.weights is not None:
			return f'Weighted D{self.sides} with Weights{self.weights} Seeded with {self.seed}'
		else:
			return f'Unbiased D{self.sides} Seeded with {self.seed}'
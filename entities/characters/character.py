from __future__ import annotations

from rules.rules import CalculateModifier
from entities.entity import GameData, YamlEntity, YamlSchema

from pathlib import Path


class Character(YamlEntity):
	files = GameData / Path('Characters')

	def Attack(self, target: Character):
		target.HP -= CalculateModifier(self.Str) - CalculateModifier(target.Dur)

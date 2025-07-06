from __future__ import annotations

from pathlib import Path

from rules.rules import CalculateModifier

from entities.entity import YamlEntity
from entities.validator import YamlEntityValidator

from main.config import GameData

class Character(YamlEntity):
	files = GameData / Path('Entities') / Path('Characters')

	def Attack(self, target: Character):
		target.HP -= CalculateModifier(self.Str) - CalculateModifier(target.Dur)

class CharacterSchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Characters')



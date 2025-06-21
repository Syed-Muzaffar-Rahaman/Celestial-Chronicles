from __future__ import annotations

from pathlib import Path

from rules.rules import CalculateModifier

from entities.entity import GameData, YamlEntity
from entities.validator import YamlEntityValidator


class Character(YamlEntity):
	files = GameData / Path('Entities') / Path('Characters')

	def Attack(self, target: Character):
		target.HP -= CalculateModifier(self.Str) - CalculateModifier(target.Dur)

class CharacterSchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Characters')

CharacterSchema.LoadAll()
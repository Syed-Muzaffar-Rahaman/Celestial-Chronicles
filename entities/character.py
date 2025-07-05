from __future__ import annotations

from pathlib import Path

from rules.rules import CalculateModifier

from entities.entity import GameData, YamlEntity
from entities.validator import YamlEntityValidator

from utils.fields import Dict
class Character(YamlEntity):
	files = GameData / Path('Entities') / Path('Characters')

	def Attack(self, target: Character):
		target.HP -= CalculateModifier(self.Str) - CalculateModifier(target.Dur)

class CharacterSchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Characters')

CharacterSchema.LoadAll()

print(CharacterSchema.registry)
print(CharacterSchema.registry['core'])

Character.Load('Xiao Xue')
print(Character.registry)
print(Character.registry['Xiao Xue'])

print(CharacterSchema.Validate(Character.registry['Xiao Xue']))



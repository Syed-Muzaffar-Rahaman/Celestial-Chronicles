from __future__ import annotations

from pathlib import Path

from entities.entity import YamlEntity
from entities.validator import YamlEntityValidator

from main.config import GameData

from utils.fields import GetField

class Ability(YamlEntity):
	files = GameData / Path('Entities') / Path('Abilities')

	def Interpret(self):
		return GetField(self, 'Damage'), GetField(self, 'DamageType')

class AbilitySchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Abilities')

AbilitySchema.LoadAll()
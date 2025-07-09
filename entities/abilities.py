from __future__ import annotations

from pathlib import Path
from typing import List

from entities.entity import YamlEntity
from entities.validator import YamlEntityValidator

from main.config import GameData

from utils.fields import GetField, SetField

class Ability(YamlEntity):
	files = GameData / Path('Entities') / Path('Abilities')

	def Interpret(self, AppliedTraits: List[str]):
		Cost = 0
		Cost += GetField(self, 'Cost[*].Value')[0]
		Damages = []
		Damages.extend(GetField(self, 'Damage[*]'))
		variants = GetField(self, 'Variants')
		for trait in variants:
			name = GetField(trait, 'Name')
			if name in AppliedTraits:
				Cost += GetField(trait, 'Cost[*].Value')[0]
				Damages.extend(GetField(trait, 'Damage[*]'))
		return Cost, Damages




class AbilitySchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Abilities')

AbilitySchema.LoadAll()
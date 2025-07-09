from __future__ import annotations

from pathlib import Path

from rules.rules import CalculateModifier

from entities.entity import YamlEntity
from entities.validator import YamlEntityValidator

from main.config import GameData

from utils.fields import GetField, SetField

class Character(YamlEntity):
	files = GameData / Path('Entities') / Path('Characters')

	def Attack(self, target: Character, ability: str):
		from entities.abilities import Ability
		Ability.Load(ability)
		AttackDamage, AttackDamageType = Ability.registry[ability].Interpret()

		target.TakeDamage({AttackDamageType: AttackDamage})

	def TakeDamage(self, DamageList: dict):
		Resistances = GetField(self, 'Resistances')
		Weaknesses = GetField(self, 'Weaknesses')

		for damagetype in DamageList.keys():
			DamageModifier = 1
			if damagetype in Resistances.keys():
				DamageModifier /= 1 + (Resistances[damagetype] / 100)
			if damagetype in Weaknesses.keys():
				DamageModifier *= 1 + (Weaknesses[damagetype] / 100)
			SetField(self, 'Resource.HP.Current', DamageList[damagetype] * DamageModifier, mode='-')

class CharacterSchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Characters')
from __future__ import annotations

from pathlib import Path

from rules.rules import CalculateModifier

from entities.entity import YamlEntity
from entities.validator import YamlEntityValidator

from main.config import GameData

from utils.fields import GetField, SetField

class Character(YamlEntity):
	files = GameData / Path('Entities') / Path('Characters')

	def Attack(self, target: Character):
		damage = CalculateModifier(GetField(self, 'Stats.Strength'))
		SetField(target, 'Resource.HP.Current', damage, mode='-')

class CharacterSchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Characters')
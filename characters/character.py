from __future__ import annotations

from rules.rules import CalculateModifier
from entities.entity import YamlEntity

from pathlib import Path
GameData = Path('../.GameData')
CharacterFiles = GameData / Path('')
CharacterFiles.mkdir(exist_ok=True)
CharacterSchemas = GameData / Path('CharacterSchemas')
CharacterSchemas.mkdir(exist_ok=True)

class Character(YamlEntity):
	def get_file_path(self, name: str):
		return CharacterFiles / Path(name.replace(' ', '_') + '.yaml')

	def Attack(self, target: Character):
		target.HP -= CalculateModifier(self.Str) - CalculateModifier(target.Dur)

class CharacterSchema(YamlEntity):
	def get_file_path(self, name: str):
		return CharacterSchemas / Path(name.replace(' ', '_') + '.yaml')

	@classmethod
	def loadAll(cls):
		for file in CharacterSchemas.glob('*.yaml'):
			name = file.stem
			if name not in cls.registry:
				cls(name)
from __future__ import annotations

from pathlib import Path

from entities.entity import GameData, YamlEntity
from entities.validator import YamlEntityValidator


class Ability(YamlEntity):
	files = GameData / Path('Entities') / Path('Abilities')

class AbilitySchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Abilities')

AbilitySchema.LoadAll()
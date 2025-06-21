from __future__ import annotations

from pathlib import Path

from entities.entity import GameData, YamlEntity
from entities.validator import YamlEntityValidator


class Skill(YamlEntity):
	files = GameData / Path('Entities') / Path('Skills')

class SkillSchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Skills')

SkillSchema.LoadAll()
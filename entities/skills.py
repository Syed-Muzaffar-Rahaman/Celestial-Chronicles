from __future__ import annotations

from pathlib import Path

from entities.entity import YamlEntity
from entities.validator import YamlEntityValidator

from main.config import GameData

class Skill(YamlEntity):
	files = GameData / Path('Entities') / Path('Skills')

class SkillSchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Skills')

SkillSchema.LoadAll()
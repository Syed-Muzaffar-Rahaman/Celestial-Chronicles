from __future__ import annotations

from pathlib import Path

from entities.entity import YamlEntity
from entities.validator import YamlEntityValidator

from main.config import GameData

class Location(YamlEntity):
	files = GameData / Path('Entities') / Path('Locations')

class LocationSchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Locations')

LocationSchema.LoadAll()
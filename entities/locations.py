from __future__ import annotations

from pathlib import Path

from entities.entity import GameData, YamlEntity
from entities.validator import YamlEntityValidator


class Location(YamlEntity):
	files = GameData / Path('Entities') / Path('Locations')

class LocationSchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Locations')

LocationSchema.LoadAll()
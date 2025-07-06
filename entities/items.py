from __future__ import annotations

from pathlib import Path

from entities.entity import YamlEntity
from entities.validator import YamlEntityValidator

from main.config import GameData

class Item(YamlEntity):
	files = GameData / Path('Entities') / Path('Items')

class ItemSchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Items')

ItemSchema.LoadAll()
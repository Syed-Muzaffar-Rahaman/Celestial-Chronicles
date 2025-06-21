from __future__ import annotations

from pathlib import Path

from entities.entity import GameData, YamlEntity
from entities.validator import YamlEntityValidator


class Item(YamlEntity):
	files = GameData / Path('Entities') / Path('Items')

class ItemSchema(YamlEntityValidator):
	files = GameData / Path('Schemas') / Path('Items')

ItemSchema.LoadAll()
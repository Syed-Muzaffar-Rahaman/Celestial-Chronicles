from pathlib import Path
import yaml
from utils.fields import to_dict

GameData = Path('../.GameData')

from enum import IntEnum
class SchemaValidationCode(IntEnum):
	SchemaImplemented = 0
	SchemaNotImplemented = 1
class EntityValidationCode(IntEnum):
	Valid = 0
	Invalid = 1


class YamlEntity:
	registry = {}

	files: Path

	def __init__(self, name: str):
		self.Name = name
		self._file_path = self.get_file_path(name)

	@classmethod
	def get_file_path(cls, name: str) -> Path:
		if cls.files is None:
			raise NotImplementedError("Subclasses must define files: Path")
		else:
			cls.files.mkdir(exist_ok=True)
			return cls.files / Path(name.replace(' ', '_') + '.yaml')

	@classmethod
	def create(cls, name: str, **data):
		obj = cls(name)
		for k, v in data.items():
			setattr(obj, k, v)
		cls.registry[obj.Name] = obj
		return obj

	@classmethod
	def load(cls, name: str):
		obj = cls(name)
		data = {}
		if obj._file_path.is_file():
			with obj._file_path.open('r') as file:
				data = yaml.safe_load(file) or {}
		for k, v in data.items():
			setattr(obj, k, v)
		cls.registry[obj.Name] = obj
		return obj

	def save(self):
		with self._file_path.open('w') as file:
			yaml.dump(to_dict(self), file, allow_unicode=True)

class YamlSchema(YamlEntity):
	@classmethod
	def loadAll(cls):
		for file in cls.files.glob('*.yaml'):
			name = file.stem
			if name not in cls.registry:
				cls(name)
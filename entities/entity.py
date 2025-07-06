import yaml

from pathlib import Path
from enum import IntEnum

from utils.fields import Dict

from main.config import GameData

class ValidationCode(IntEnum):
	Valid = 0
	Invalid = 1

class YamlEntity:
	def __init_subclass__(cls, **kwargs):
		super().__init_subclass__(**kwargs)
		cls.registry = {}

	files: Path

	def __str__(self):
		return str(Dict(self))

	def __repr__(self):
		return self.__str__()

	def __init__(self, name: str):
		self.Name = name
		self._file_path = self.GetFilePath(name)

	@classmethod
	def GetFilePath(cls, name: str) -> Path:
		if cls.files is None:
			raise NotImplementedError("Subclasses must define files: Path")
		else:
			cls.files.mkdir(exist_ok=True)
			return cls.files / Path(name.replace(' ', '_') + '.yaml')

	@classmethod
	def Create(cls, name: str, **data):
		obj = cls(name)
		for k, v in data.items():
			setattr(obj, k, v)
		cls.registry[obj.Name] = obj
		return obj

	@classmethod
	def Load(cls, name: str):
		obj = cls(name)
		data = {}
		if obj._file_path.is_file():
			with obj._file_path.open('r') as file:
				data = yaml.safe_load(file) or {}
		for k, v in data.items():
			setattr(obj, k, v)
		cls.registry[obj.Name] = obj
		return obj

	def Save(self):
		with self._file_path.open('w') as file:
			yaml.dump(Dict(self), file, allow_unicode=True)
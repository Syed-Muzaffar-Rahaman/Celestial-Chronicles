from pathlib import Path
import yaml
from utils.Field_utils import to_dict


class YamlEntity:
	registry = {}

	def __init__(self, name: str):
		self.Name = name
		self._file_path = self.get_file_path(name)

	def get_file_path(self, name: str) -> Path:
		raise NotImplementedError("Subclasses must define get_file_path")

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
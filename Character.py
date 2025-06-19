from __future__ import annotations

from pathlib import Path
import yaml


from graph_utils import toposort, build_reverse_graph, get_all_descendants
from Field_utits import HasField, flatten_fields

from Rules import CalculateModifier

from Entity import YamlEntity


GameData = Path('.GameData')

CharacterFiles = GameData / Path('Characters')
CharacterFiles.mkdir(exist_ok=True)

CharacterSchemas = GameData / Path('CharacterSchemas')
CharacterSchemas.mkdir(exist_ok=True)

from enum import IntEnum

class Character(YamlEntity):
	def get_file_path(self, name: str) -> Path:
		return CharacterFiles / Path(name.replace(' ', '_') + '.yaml')

	def Attack(self, target: Character):
		target.HP -= CalculateModifier(self.Str) - CalculateModifier(target.Dur)

class CharacterSchema:
	registry = {}

	def __init__(self, name: str):
		self._file_path = CharacterSchemas / Path(name + '.yaml')

		self.Name = name
		with self._file_path.open('r') as file:
			data = yaml.safe_load(file) or {}
			
			self.Extends = data.pop('Extends', [])
			self.Mandatory = data.pop('Mandatory', [])
			self.Optional = data.pop('Optional', [])
			self.AnyOf = data.pop('AnyOf', [])

		type(self).registry[self.Name] = self

	@classmethod
	def loadAll(cls):
		for file in CharacterSchemas.glob('*.yaml'):
			name = file.stem
			if name not in cls.registry:
				cls(name)


CharacterSchema.loadAll()

SchemasGraph = {name: schema.Extends for name, schema in CharacterSchema.registry.items()}
SchemasReverseGraph = build_reverse_graph(SchemasGraph)
Schemas = toposort(SchemasGraph)

class SchemaValidationCode(IntEnum):
	UNACCEPTABLE = 0
	INVALID = 1
	VALID = 2

class CharacterValidator:

	@staticmethod
	def ValidateSchema(char : Character, schema: CharacterSchema) -> tuple[SchemaValidationCode, set]:
		ValidatedFields = set()
		MissingFields = set()
		IsCoreSchema = False if not schema.Extends else True

		for field in schema.Mandatory:
			if HasField(char, field):
				ValidatedFields.add(field)
			else:
				MissingFields.add(field)

		for field in schema.Optional:
			if HasField(char, field): ValidatedFields.add(field)

		if not any(HasField(char, field) for field in schema.AnyOf):
			MissingFields.update(schema.AnyOf)
		else:
			for field in schema.AnyOf:
				if HasField(char, field): ValidatedFields.add(field)

		if len(MissingFields) == 0:
			ValidationCode = SchemaValidationCode.VALID
		elif IsCoreSchema or len(ValidatedFields) != 0:
			ValidationCode = SchemaValidationCode.UNACCEPTABLE
		elif len(ValidatedFields) == 0:
			ValidationCode = SchemaValidationCode.INVALID
		else:
			raise AssertionError("unreachable")

		return ValidationCode, ValidatedFields

	@staticmethod
	def ValidatePresenceOfFields(char : Character):
		DroppedSchemas = set()
		ValidFields = set()

		ValidationSuccess = True

		for schema in Schemas:
			if schema in DroppedSchemas:
				continue

			Status, ValidatedFields = char.ValidateSchema(CharacterSchema.registry[schema])

			if Status == SchemaValidationCode.VALID:
				ValidFields |= ValidatedFields
			elif Status == SchemaValidationCode.INVALID:
				DroppedSchemas |= get_all_descendants(schema, SchemasReverseGraph)
			elif Status == SchemaValidationCode.UNACCEPTABLE:
				ValidationSuccess = False

		return ValidationSuccess, ValidFields

	@staticmethod
	def ValidateExtraneousFields(char : Character, ValidFields: set) -> set:
		from Field_utits import to_dict

		CharacterFields = flatten_fields(to_dict(char))
		UndefinedFields = CharacterFields - ValidFields
		return UndefinedFields
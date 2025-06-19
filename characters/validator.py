from __future__ import annotations

from utils.graph_utils import toposort, build_reverse_graph, get_all_descendants
from utils.Field_utils import HasField, flatten_fields

from character import Character, CharacterSchema

CharacterSchema.loadAll()

SchemasGraph = {name: schema.Extends for name, schema in CharacterSchema.registry.items()}
SchemasReverseGraph = build_reverse_graph(SchemasGraph)
Schemas = toposort(SchemasGraph)


from enum import IntEnum
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
		from utils.Field_utils import to_dict

		CharacterFields = flatten_fields(to_dict(char))
		UndefinedFields = CharacterFields - ValidFields
		return UndefinedFields
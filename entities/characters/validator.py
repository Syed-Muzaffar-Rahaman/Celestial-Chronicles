from __future__ import annotations

from enum import IntEnum

from character import Character, CharacterSchema
from utils.graphs import toposort, build_reverse_graph

CharacterSchema.loadAll()
SchemasGraph = {name: schema.Extends for name, schema in CharacterSchema.registry.items()}
Schemas = toposort(SchemasGraph)
SchemasReverseGraph = build_reverse_graph(SchemasGraph)


class SchemaValidationCode(IntEnum):
    UNACCEPTABLE = 0
    INVALID = 1
    VALID = 2


class CharacterValidator:
    @staticmethod
    def ValidateSchema(char: Character, schema: CharacterSchema) -> tuple[SchemaValidationCode, set]:
        ValidatedFields = set()
        MissingFields = set()
        IsCoreSchema = False if not schema.Extends else True

        from utils.fields import HasField

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
    def ValidatePresenceOfFields(char: Character):
        from utils.graphs import get_all_descendants

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
    def ValidateExtraneousFields(char: Character, ValidFields: set) -> set:
        from utils.fields import to_dict, flatten_fields

        CharacterFields = flatten_fields(to_dict(char))
        UndefinedFields = CharacterFields - ValidFields
        return UndefinedFields

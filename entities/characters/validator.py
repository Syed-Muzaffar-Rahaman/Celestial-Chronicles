from __future__ import annotations

from character import Character
from utils.graphs import toposort, build_reverse_graph
from entities.entity import GameData, YamlSchema, SchemaValidationCode, EntityValidationCode

from pathlib import Path
from utils.fields import HasField
from utils.graphs import get_all_descendants

from utils.fields import to_dict, flatten_fields


class CharacterSchema(YamlSchema):
    files = GameData / Path('Schemas') / Path('Characters')

    def ValidateMandatoryFields(self, char: Character):
        ValidatedFields = set()
        for field in self.Mandatory:
            if HasField(char, field):
                ValidatedFields.add(field)
            else:
                return None
        return ValidatedFields

    def ValidateOptionalFields(self, char: Character):
        ValidatedFields = set()
        for field in self.Optional:
            if HasField(char, field):
                ValidatedFields.add(field)
        return ValidatedFields

    def ValidateAnyOfFields(self, char: Character):
        ValidatedFields = set()
        for field in self.AnyOf:
            if HasField(char, field):
                ValidatedFields.add(field)
        if len(ValidatedFields) == 0:
            return None
        else:
            return ValidatedFields


    def ValidateSchema(self, char: Character) -> tuple[SchemaValidationCode, set]:
        ValidatedFields = set()

        Mandatory = self.ValidateMandatoryFields(char)
        AnyOf = self.ValidateAnyOfFields(char)
        if Mandatory is None or AnyOf is None:
            return SchemaValidationCode.SchemaNotImplemented, set()

        ValidatedFields |= Mandatory
        ValidatedFields |= self.ValidateOptionalFields(char)
        ValidatedFields |= AnyOf

        return SchemaValidationCode.SchemaImplemented, ValidatedFields


    @classmethod
    def Validate(cls, char: Character) -> tuple[EntityValidationCode, set, set, set]:

        DroppedSchemas = set()
        ImplementedSchemas = set()

        DefinedFields = set()

        ValidationSuccess = EntityValidationCode.Valid

        for schema in Schemas:
            if schema in DroppedSchemas:
                continue

            Required = cls.registry[schema].Required
            if not isinstance(Required, bool):
                Required = any(ConditionalSchema in ImplementedSchemas for ConditionalSchema in Required)

            Status, ValidatedFields = cls.registry[schema].ValidateSchema(char)

            if Status == SchemaValidationCode.SchemaImplemented:
                DefinedFields |= ValidatedFields
                ImplementedSchemas.add(schema)
            elif not Required:
                DroppedSchemas |= get_all_descendants(schema, SchemasReverseGraph)
            else:
                ValidationSuccess = EntityValidationCode.Invalid

        UndefinedFields = flatten_fields(to_dict(char)) - DefinedFields

        return ValidationSuccess, DefinedFields, UndefinedFields, ImplementedSchemas

CharacterSchema.loadAll()
SchemasGraph = {name: schema.Extends for name, schema in CharacterSchema.registry.items()}
Schemas = toposort(SchemasGraph)
SchemasReverseGraph = build_reverse_graph(SchemasGraph)
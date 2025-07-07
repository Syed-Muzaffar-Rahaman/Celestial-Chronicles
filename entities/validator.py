from __future__ import annotations

from utils.graphs import Toposort, BuildReverseGraph, GetAllDescendants
from utils.fields import HasField

from entities.entity import YamlEntity, ValidationCode


class YamlEntityValidator(YamlEntity):
    @classmethod
    def LoadAll(cls):
        for file in cls.files.glob('*.yaml'):
            name = file.stem
            if name not in cls.registry:
                cls.Load(name)

    def ValidateSchema(self, entity) -> tuple[ValidationCode, set]:
        FieldsFound = set()
        ErrorsFound = set()

        if self.Mandatory:
            for field in self.Mandatory:
                Fields, Errors = HasField(entity, field)
                FieldsFound |= Fields
                ErrorsFound |= Errors
            Success = ValidationCode.Valid if ErrorsFound == set() else ValidationCode.Invalid

        if self.Optional:
            for field in self.Optional:
                Fields, Errors = HasField(entity, field)
                FieldsFound |= Fields

        return Success, FieldsFound, ErrorsFound

    @classmethod
    def Validate(cls, entity) -> tuple[ValidationCode, set, set, set]:

        SchemasGraph = {name: schema.Extends for name, schema in cls.registry.items()}
        Schemas = Toposort(SchemasGraph)
        SchemasReverseGraph = BuildReverseGraph(SchemasGraph)

        DroppedSchemas = set()
        DefinedFields = set()
        ErrorsFound = set()

        for schema in Schemas:
            if schema in DroppedSchemas:
                continue

            Validation, ValidatedFields, Errors = cls.registry[schema].ValidateSchema(entity)

            if Validation == ValidationCode.Valid:
                DefinedFields |= ValidatedFields
            elif not cls.registry[schema].Required:
                DroppedSchemas |= GetAllDescendants(schema, SchemasReverseGraph)
            else:
                ErrorsFound |= Errors

        ValidationSuccess = ValidationCode.Valid if ErrorsFound == set() else ValidationCode.Invalid

        return ValidationSuccess
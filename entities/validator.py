from __future__ import annotations

from utils.graphs import Toposort, BuildReverseGraph, GetAllDescendants
from utils.fields import HasField, Dict, FlattenFields

from entities.entity import YamlEntity, ValidationCode


class YamlEntityValidator(YamlEntity):
    @classmethod
    def LoadAll(cls):
        for file in cls.files.glob('*.yaml'):
            name = file.stem
            if name not in cls.registry:
                cls.Load(name)

    def ValidateSchema(self, entity) -> tuple[ValidationCode, set]:
        ValidatedFields = set()
        MissingFields = set()

        if self.Mandatory:
            for field in self.Mandatory:
                if HasField(entity, field):
                    ValidatedFields.add(field)
                else:
                    MissingFields.add(field)

        if self.Optional:
            for field in self.Optional:
                if HasField(entity, field):
                    ValidatedFields.add(field)

        Success = ValidationCode.Valid if MissingFields == set() else ValidationCode.Invalid

        return Success, ValidatedFields

    @classmethod
    def Validate(cls, entity) -> tuple[ValidationCode, set, set, set]:

        SchemasGraph = {name: schema.Extends for name, schema in cls.registry.items()}
        Schemas = Toposort(SchemasGraph)
        SchemasReverseGraph = BuildReverseGraph(SchemasGraph)

        DroppedSchemas = set()
        DefinedFields = set()
        ValidationSuccess = ValidationCode.Valid

        for schema in Schemas:
            if schema in DroppedSchemas:
                continue

            Validation, ValidatedFields = cls.registry[schema].ValidateSchema(entity)

            if Validation == ValidationCode.Valid:
                DefinedFields |= ValidatedFields
            elif not cls.registry[schema].Required:
                DroppedSchemas |= GetAllDescendants(schema, SchemasReverseGraph)
            else:
                ValidationSuccess = ValidationCode.Invalid

        UndefinedFields = FlattenFields(Dict(entity)) - DefinedFields

        return ValidationSuccess, DefinedFields, UndefinedFields
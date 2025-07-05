from __future__ import annotations

from utils.graphs import Toposort, BuildReverseGraph, GetAllDescendants
from utils.fields import HasField, Dict, FlattenFields

from entities.entity import YamlEntity, SchemaValidationCode, EntityValidationCode



class YamlEntityValidator(YamlEntity):
    __slots__ = ('_file_path', 'Name', 'Extends', 'Required', 'Mandatory', 'Optional', 'AnyOf')

    @classmethod
    def LoadAll(cls):
        for file in cls.files.glob('*.yaml'):
            name = file.stem
            if name not in cls.registry:
                cls.Load(name)

    def ValidateMandatoryFields(self, entity):
        ValidatedFields = set()
        for field in self.Mandatory:
            if HasField(entity, field):
                ValidatedFields.add(field)
            else:
                return None
        return ValidatedFields

    def ValidateOptionalFields(self, entity):
        ValidatedFields = set()
        for field in self.Optional:
            if HasField(entity, field):
                ValidatedFields.add(field)
        return ValidatedFields

    def ValidateAnyOfFields(self, entity):
        ValidatedFields = set()
        for field in self.AnyOf:
            if HasField(entity, field):
                ValidatedFields.add(field)
        if len(ValidatedFields) == 0:
            return None
        else:
            return ValidatedFields


    def ValidateSchema(self, entity) -> tuple[SchemaValidationCode, set]:
        ValidatedFields = set()

        if self.Mandatory:
            Mandatory = self.ValidateMandatoryFields(entity)
        else:
            Mandatory = set()

        if self.AnyOf:
            AnyOf = self.ValidateAnyOfFields(entity)
        else:
            AnyOf = set()

        if self.Optional:
            Optional = self.ValidateOptionalFields(entity)
        else:
            Optional = set()

        if Mandatory is None or AnyOf is None:
            return SchemaValidationCode.SchemaNotImplemented, set()

        ValidatedFields |= Mandatory
        ValidatedFields |= Optional
        ValidatedFields |= AnyOf


        return SchemaValidationCode.SchemaImplemented, ValidatedFields


    @classmethod
    def Validate(cls, entity) -> tuple[EntityValidationCode, set, set, set]:

        SchemasGraph = {name: schema.Extends for name, schema in cls.registry.items()}
        Schemas = Toposort(SchemasGraph)
        print(Schemas)
        SchemasReverseGraph = BuildReverseGraph(SchemasGraph)

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

            print(schema)
            Status, ValidatedFields = cls.registry[schema].ValidateSchema(entity)

            if Status == SchemaValidationCode.SchemaImplemented:
                DefinedFields |= ValidatedFields
                ImplementedSchemas.add(schema)
            elif not Required:
                DroppedSchemas |= GetAllDescendants(schema, SchemasReverseGraph)
            else:
                ValidationSuccess = EntityValidationCode.Invalid

        UndefinedFields = FlattenFields(Dict(entity)) - DefinedFields

        return ValidationSuccess, DefinedFields, UndefinedFields, ImplementedSchemas
from entities.character import CharacterSchema, Character

CharacterSchema.LoadAll()

print(CharacterSchema.registry)

Character.Load('Xiao Xue')
print(Character.registry)

print(CharacterSchema.Validate(Character.registry['Xiao Xue']))

# print(Character.registry['Xiao Xue'].Resource)

# print(CharacterSchema.registry['resource_pool'].ValidateSchema(Character.registry['Xiao Xue']))



from entities.character import CharacterSchema, Character

CharacterSchema.LoadAll()

Character.Load('Xiao Xue')
Character.Load('Mu Ning Xue')


print(CharacterSchema.Validate(Character.registry['Xiao Xue']))
print(CharacterSchema.Validate(Character.registry['Mu Ning Xue']))


Character.registry['Xiao Xue'].Attack(Character.registry['Mu Ning Xue'], 'Fire Ball')

print(Character.registry['Xiao Xue'])
print(Character.registry['Mu Ning Xue'])

Character.registry['Xiao Xue'].Save()
Character.registry['Mu Ning Xue'].Save()



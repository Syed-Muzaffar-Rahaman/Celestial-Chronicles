def FlattenFields(data, prefix=""):
    fields = set()
    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            fields.add(full_key)
            fields |= FlattenFields(value, prefix=full_key)
    return fields

def Dict(obj):
    return {
        key: value
        for key, value in obj.__dict__.items()
        if not key.startswith('_')
    }
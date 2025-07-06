import re

def Parse(part):
    """
    Parses a field part into a key and a list of index groups.

    Examples of supported syntax:
        - 'field'              => ('field', [])
        - 'field[3]'           => ('field', [['3']])
        - 'field[HP|MP]'       => ('field', [['HP', 'MP']])
        - 'field[3][4]'        => ('field', [['3'], ['4']])
        - 'field[HP|MP][*]'    => ('field', [['HP', 'MP'], ['*']])

    Returns:
        key (str): The base field name.
        indices (List[List[str]]): List of index groups, where each group is a list of alternatives (e.g., ['HP', 'MP']).
    Raises:
        ValueError: If the field syntax is invalid.
    """
    match = re.match(r"^(\w+)", part)
    if not match:
        raise ValueError(f"Invalid field syntax: {part}")
    key = match.group(1)
    indices = re.findall(r"\[([^]]+)]", part)
    # Split alternatives
    indices = [i.split('|') if '|' in i else [i] for i in indices]
    return key, indices


def HasField(obj, field_path: str) -> bool:
    """
    Checks whether a nested field path exists in the object.

    The field path supports dot notation, list indices, alternatives, and wildcards:
        - Dot notation for nested fields (e.g., 'foo.bar').
        - List indices (e.g., 'foo[0]').
        - Alternatives for dict keys or indices (e.g., 'foo[HP|MP]').
        - Wildcards to match any key or index at that level (e.g., 'foo[*]').

    For dictionaries:
        - If alternatives are given, only those keys are allowed at that level (strict).
    For lists:
        - Only a single index or wildcard is allowed per segment.

    Args:
        obj: The object (dict, list, or object with attributes) to check.
        field_path (str): The field path string.

    Returns:
        bool: True if the field path exists (and matches strictness rules), False otherwise.
    """
    parts = field_path.split('.')
    current = obj

    for i, part in enumerate(parts):
        key, indices = Parse(part)

        # Navigate into dict or attribute
        if isinstance(current, dict):
            if key not in current:
                return False
            current = current[key]
        elif hasattr(current, key):
            current = getattr(current, key)
        else:
            return False

        for index_group in indices:
            if isinstance(current, list):
                if len(index_group) != 1:
                    return False
                index = index_group[0]
                if index == '*':
                    # Apply remaining path to all elements
                    rest = '.'.join(parts[i + 1:])
                    if not rest:
                        return True  # We're done, the list exists
                    return all(HasField(item, rest) for item in current)
                else:
                    try:
                        current = current[int(index)]
                    except (IndexError, ValueError):
                        return False
            elif isinstance(current, dict):
                if '*' in index_group:
                    rest = '.'.join(parts[i + 1:])
                    if not rest:
                        return True
                    return all(HasField(v, rest) for v in current.values())
                else:
                    # Check all alternatives exist as keys in the dict
                    if set(current.keys()) != set(index_group):
                        return False
                    # If more path remains, recurse for each alternative
                    if i + 1 < len(parts):
                        rest = '.'.join(parts[i + 1:])
                        return all(HasField(current[index], rest) for index in index_group)
                    else:
                        return True
    return True

def GetField(obj, field_path: str):
    """Retrieves the value at a nested field path, supporting dot notation and index access."""
    parts = field_path.split('.')
    current = obj

    for i, part in enumerate(parts):
        key, index = Parse(part)

        # dict or object access
        if isinstance(current, dict):
            if key not in current:
                raise KeyError(f"Key '{key}' not found in dict")
            current = current[key]
        elif hasattr(current, key):
            current = getattr(current, key)
        else:
            raise AttributeError(f"Attribute '{key}' not found")

        # handle indexing or recursive loop
        if isinstance(current, list):
            if index is not None:
                try:
                    current = current[int(index)]
                except (IndexError, ValueError):
                    raise IndexError(f"Invalid index [{index}] for list")
            else:
                # no index provided, collect from all
                rest = '.'.join(parts[i + 1:])
                if not rest:
                    return current
                return [GetField(item, rest) for item in current]

        elif isinstance(current, dict):
            if index is not None:
                if index not in current:
                    raise KeyError(f"Key [{index}] not found in dict")
                current = current[index]
            else:
                # no key provided, collect from all values
                rest = '.'.join(parts[i + 1:])
                if not rest:
                    return current
                return [GetField(value, rest) for value in current.values()]

        else:
            if index is not None:
                raise TypeError(f"Cannot index into non-container at '{key}'")

    return current

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
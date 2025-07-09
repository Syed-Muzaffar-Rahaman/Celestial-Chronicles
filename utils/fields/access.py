"""
Field path utilities for nested Python data structures.

This module provides generic utilities for parsing, validating, retrieving, and setting
values deep inside arbitrarily nested Python dicts, lists, and objects using a powerful
field path syntax. Supports dot notation, square bracket indices, wildcards, and index groups.

Main functions:
 - Parse: Parse a field path segment into a key and index groups
 - HasField: Check for the existence of a field path
 - GetField: Retrieve values at a field path (with wildcards/group support)
 - SetField: Assign values at a field path (with wildcards/group support)

Intended for use as a stable, rarely-modified utility module.
"""
import re
from typing import Any, Tuple, List, Set


def Parse(part: str) -> Tuple[str, List[List[str]]]:
    """
    Splits a field path segment into a base key and a list of index groups.

    A segment is a string like 'foo', 'bar[0]', or 'baz[1|2|3]'. The function
    extracts the base field name, and parses any trailing index expressions in
    square brackets as lists of alternatives, wildcards, or indices.

    Args:
        part (str): A segment of a field path, such as 'users[0|1]'.

    Returns:
        Tuple[str, List[List[str]]]:
            - The base field name.
            - A list of index groups, where each group is a list of alternatives or indices.

    Raises:
        ValueError: If the segment doesn't begin with a valid identifier.
    """
    m = re.match(r"^([^\[\]]+)", part)
    if not m:
        raise ValueError(f"Invalid field syntax: {part}")
    key = m.group(1)
    rest = part[len(key):]
    # Now extract all bracketed index groups
    index_strs = re.findall(r"\[([^]]+)]", rest)
    indices = [i.split('|') if '|' in i else [i] for i in index_strs]
    return key, indices


def HasField(
        obj: Any, field_path: str, current_field: str = ''
) -> Tuple[Set[str], Set[str]]:
    """
    Recursively checks if a nested field path exists in a Python object.

    Supports dot notation for nesting, square brackets for indices/keys,
    wildcards ([*]) for matching all elements of a container, and index groups ([A|B|C])
    for matching multiple keys/indices at the same position.

    Args:
        obj (Any): Object to traverse.
        field_path (str): Path string (e.g., 'users[0].email').
        current_field (str, optional): Internal tracker for traversal.

    Returns:
        Tuple[Set[str], Set[str]]:
            - Set of found field path labels.
            - Set of error messages for missing fields or invalid accesses.

    Notes:
        - Never raises; collects all errors encountered.
        - Returns all discovered labels along the traversed path.
        - An empty field_path results in empty sets.
        - When wildcards or groups are used, labels for all matching paths are included.
    """

    def handle_dict(current, key, next_field):
        if key not in current:
            return set(), {
                f"Missing key '{key}' in dict at '{current_field or '[root]'}'." +
                f" Full path attempted: '{next_field}'"
            }, None
        return {next_field}, set(), current[key]

    def handle_attr(current, key, next_field):
        if not hasattr(current, key):
            return set(), {
                f"Missing key or attribute '{key}' in object of type '{type(current).__name__}'" +
                f" at '{current_field or '[root]'}'. Full path attempted: '{next_field}'"
            }, None
        return {next_field}, set(), getattr(current, key)

    def handle_list_indices(lst, index_group, next_field):
        fields_found, errors = set(), set()
        next_objs = []
        if len(index_group) != 1:
            errors.add(f"Invalid index group {index_group} for list at '{next_field}'")
            return fields_found, errors, next_objs
        index = index_group[0]
        if index == '*':
            for idx, item in enumerate(lst):
                pathlabel = f"{next_field}[{idx}]"
                fields_found.add(pathlabel)
                next_objs.append((item, pathlabel))
        else:
            try:
                idx_int = int(index)
                item = lst[idx_int]
                pathlabel = f"{next_field}[{index}]"
                fields_found.add(pathlabel)
                next_objs.append((item, pathlabel))
            except (IndexError, ValueError):
                errors.add(f"Index '{index}' out of range for list at '{next_field}'." +
                           f" List length: {len(lst)}")
        return fields_found, errors, next_objs

    def handle_dict_indices(dct, index_group, next_field):
        fields_found, errors = set(), set()
        next_objs = []
        if '*' in index_group:
            for k, v in dct.items():
                pathlabel = f"{next_field}.{k}"
                fields_found.add(pathlabel)
                next_objs.append((v, pathlabel))
        else:
            missing = set(index_group) - set(dct.keys())
            if missing:
                errors.add(f"Expected dict keys {index_group} at '{next_field}'," +
                           f" but found {list(dct.keys())}")
            else:
                for k in index_group:
                    v = dct[k]
                    pathlabel = f"{next_field}.{k}"
                    fields_found.add(pathlabel)
                    next_objs.append((v, pathlabel))
        return fields_found, errors, next_objs

    if not field_path:
        return set(), set()

    parts = field_path.split('.', 1)
    part = parts[0]
    rest = parts[1] if len(parts) > 1 else None

    key, indices = Parse(part)
    next_field = (current_field + '.' if current_field else '') + key

    fields_found, errors = set(), set()
    current = None
    if isinstance(obj, dict):
        found, err, current = handle_dict(obj, key, next_field)
        fields_found |= found
        errors |= err
        if err:
            return fields_found, errors
    elif hasattr(obj, key):
        found, err, current = handle_attr(obj, key, next_field)
        fields_found |= found
        errors |= err
        if err:
            return fields_found, errors
    else:
        errors.add(
            f"Missing key or attribute '{key}' in object of type '{type(obj).__name__}'" +
            f" at '{current_field or '[root]'}'. Full path attempted: '{next_field}'")
        return fields_found, errors

    if not indices:
        if rest:
            subfields, suberrors = HasField(current, rest, next_field)
            fields_found |= subfields
            errors |= suberrors
        return fields_found, errors

    next_objs = [(current, next_field)]
    for index_group in indices:
        new_next_objs = []
        for current, next_field in next_objs:
            if isinstance(current, list):
                found, err, objs = handle_list_indices(current, index_group, next_field)
                fields_found |= found
                errors |= err
                new_next_objs += objs
            elif isinstance(current, dict):
                found, err, objs = handle_dict_indices(current, index_group, next_field)
                fields_found |= found
                errors |= err
                new_next_objs += objs
            else:
                errors.add(f"Expected container (list/dict) at '{next_field}" +
                           f"{type(current).__name__}")
        next_objs = new_next_objs

    if rest:
        for current, next_field in next_objs:
            subfields, suberrors = HasField(current, rest, next_field)
            fields_found |= subfields
            errors |= suberrors

    return fields_found, errors


def GetField(obj: Any, field_path: str) -> Any:
    """
    Retrieves the value(s) at a nested field path in a Python object.

    Supports dot notation, list/dict indexing, wildcards ([*]), and index groups ([a|b|c]).
    When wildcards or groups are used, returns a list of all matching results, possibly
    nested if wildcards/groups appear at multiple levels.

    Args:
        obj (Any): The root object to traverse.
        field_path (str): Field path string (e.g., 'users[*].name').

    Returns:
        Any: The value at the specified path, or a list of values if wildcards/groups are used.
             May be nested lists for multi-level wildcards.

    Raises:
        KeyError: If a dict key is missing at any step.
        AttributeError: If an attribute is missing at any step.
        IndexError: If a list index is out of range.
        TypeError: If a non-container is indexed.
    """

    def get(current, parts):
        if not parts:
            return current

        part, *rest_parts = parts
        key, index_groups = Parse(part)

        if isinstance(current, dict):
            if key not in current:
                raise KeyError(f"Key '{key}' not found in dict")
            current = current[key]
        elif hasattr(current, key):
            current = getattr(current, key)
        else:
            raise AttributeError(f"Attribute or key '{key}' not found")

        for indices in index_groups:
            if isinstance(current, list):
                if indices == ['*']:
                    return [get(item, rest_parts) for item in current]
                else:
                    return [get(current[int(idx)], rest_parts) for idx in indices]
            elif isinstance(current, dict):
                if indices == ['*']:
                    return [get(v, rest_parts) for v in current.values()]
                else:
                    return [get(current[k], rest_parts) for k in indices]
            else:
                raise TypeError(f"Cannot index into non-container ({type(current).__name__}) at '{key}'")

        if rest_parts:
            return get(current, rest_parts)
        return current

    parts = field_path.split('.')
    return get(obj, parts)


def SetField(obj: Any, field_path: str, newvalue: Any, mode: str = '=') -> None:
    """
    Sets or modifies the value(s) at a nested field path in a Python object, mutating in place.

    Supports dot notation, list/dict indexing, wildcards ([*]), and index groups ([a|b|c]).
    When wildcards or groups are used, applies the assignment or operation to all matching locations.
    If wildcards/groups are used at multiple levels, all combinations are set.

    Modes:
        '=' (default): Assigns the value at the target location(s).
        '+': Applies the '+' operator at the target location(s) (e.g., increment, concatenate, etc.).
        '-': Applies the '-' operator at the target location(s) (e.g., decrement, sequence removal, etc.).

    Args:
        obj (Any): The root object to modify.
        field_path (str): Field path string (e.g., 'users[*].name').
        newvalue (Any): Value to set at the target location(s), or to use with '+'/'-' mode.
        mode (str, optional): Assignment mode: '=' (assign), '+' (plus), '-' (minus).

    Returns:
        None

    Raises:
        KeyError: If a dict key is missing at any step.
        AttributeError: If an attribute is missing at any step.
        IndexError: If a list index is out of range.
        TypeError: If the requested operation is not supported by the value type,
            or if attempting to assign to an invalid structure.
        ValueError: If mode is not one of '=', '+', or '-'.

    Notes:
        - All resolved locations for wildcards/groups are set or modified according to mode.
        - Operator modes ('+', '-') rely on the underlying Python data type's implementation of those operators.
          If an operation is not supported (e.g., 'str - str'), a TypeError will be raised.
        - If field_path is empty, no operation is performed.
    """
    def update_value(old, new, mode):
        if mode == '=':
            return new
        elif mode == '+':
            try:
                return old + new
            except Exception as e:
                raise TypeError(f"Error applying '+' to {old!r} and {new!r}: {e}")
        elif mode == '-':
            try:
                return old - new
            except Exception as e:
                raise TypeError(f"Error applying '-' to {old!r} and {new!r}: {e}")
        else:
            raise ValueError(f"Unknown mode: {mode}")

    def set(current, parts):
        if not parts:
            return

        part, *rest_parts = parts
        key, index_groups = Parse(part)

        if isinstance(current, dict):
            if key not in current:
                raise KeyError(f"Key '{key}' not found in dict")
            target = current[key]
        elif hasattr(current, key):
            target = getattr(current, key)
        else:
            raise AttributeError(f"Attribute or key '{key}' not found")

        def do_assign(container, idx, rest):
            if not rest:
                if isinstance(container, dict):
                    old = container.get(idx)
                    container[idx] = update_value(old, newvalue, mode) if old is not None else newvalue
                elif isinstance(container, list):
                    idx_int = int(idx)
                    old = container[idx_int]
                    container[idx_int] = update_value(old, newvalue, mode)
                else:
                    raise TypeError(f"Cannot assign to non-container at '{key}'")
            else:
                set(container[idx], rest)

        for indices in index_groups:
            if isinstance(target, list):
                if indices == ['*']:
                    for i in range(len(target)):
                        if rest_parts:
                            set(target[i], rest_parts)
                        else:
                            do_assign(target, i, [])
                    return
                else:
                    for idx in indices:
                        idx_int = int(idx)
                        if rest_parts:
                            set(target[idx_int], rest_parts)
                        else:
                            do_assign(target, idx_int, [])
                    return
            elif isinstance(target, dict):
                if indices == ['*']:
                    for k in list(target.keys()):
                        if rest_parts:
                            set(target[k], rest_parts)
                        else:
                            do_assign(target, k, [])
                    return
                else:
                    for k in indices:
                        if k not in target:
                            raise KeyError(f"Key [{k}] not found in dict")
                        if rest_parts:
                            set(target[k], rest_parts)
                        else:
                            do_assign(target, k, [])
                    return
            else:
                raise TypeError(f"Cannot index into non-container ({type(target).__name__}) at '{key}'")

        if rest_parts:
            set(target, rest_parts)
        else:
            if isinstance(current, dict):
                old = current.get(key)
                current[key] = update_value(old, newvalue, mode) if old is not None else newvalue
            else:
                old = getattr(current, key)
                setattr(current, key, update_value(old, newvalue, mode))

    parts = field_path.split('.')
    set(obj, parts)

"""Where two chart specs differ, under the rules geneviewer-py's tests compare a
Python spec with R's by:

- an array of one element equals the element (R writes a vector of one as a
  scalar), except under "clusters" and "selection";
- numbers are equal within 1e-9 relative difference;
- a missing key equals null, and [] equals {}; key order does not matter.
"""

ALWAYS_ARRAYS = ("clusters", "selection")


def is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def differences(expected, actual, path=(), out=None):
    out = [] if out is None else out
    if (path[-1] if path else None) not in ALWAYS_ARRAYS:
        if isinstance(expected, list) and len(expected) == 1:
            expected = expected[0]
        if isinstance(actual, list) and len(actual) == 1:
            actual = actual[0]
    empty = lambda x: isinstance(x, (list, dict)) and not x  # noqa: E731
    if (expected is None and actual is None) or (empty(expected) and empty(actual)):
        return out
    where = ".".join(str(p) for p in path)
    if is_number(expected) and is_number(actual):
        scale = max(abs(expected), abs(actual))
        if expected != actual and abs(expected - actual) > 1e-9 * max(scale, 1e-3):
            out.append((where, expected, actual))
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            out.append((where, expected, actual))
        else:
            for i, (e, a) in enumerate(zip(expected, actual)):
                if (e is None) != (a is None):
                    out.append((f"{where}.{i}", e, a))
                else:
                    differences(e, a, (*path, i), out)
    elif isinstance(expected, dict) and isinstance(actual, dict):
        for name in dict.fromkeys([*expected, *actual]):
            differences(expected.get(name), actual.get(name), (*path, name), out)
    elif type(expected) is not type(actual) or expected != actual:
        out.append((where, expected, actual))
    return out

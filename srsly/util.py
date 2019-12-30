from pathlib import Path


def force_path(location, require_exists=True):
    if not isinstance(location, Path):
        location = Path(location)
    if require_exists and not location.exists():
        raise ValueError(f"Can't read file: {location}")
    return location


def force_string(location):
    if isinstance(location, str):
        return location
    return str(location)

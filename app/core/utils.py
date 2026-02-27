def split_csv(value: str) -> tuple[str, ...]:
    """Split a comma-separated string, stripping whitespace and dropping empties."""
    return tuple(item.strip() for item in value.split(",") if item.strip())

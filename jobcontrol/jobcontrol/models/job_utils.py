MAX_NAME_LENGTH = 36


def shorten_text(text: str, max_length: int = MAX_NAME_LENGTH) -> str:
    """
    Shortens a text to max_length
    """
    return f"{(text[:max_length - 4] + ' ...') if len(text) > max_length - 4 else text}"

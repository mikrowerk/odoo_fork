MAX_NAME_LENGTH = 28


def shorten_text(text: str, max_length: int) -> str:
    """
    Shortens a text to max_length
    """
    return f"{(text[:max_length] + '...') if len(text) > max_length else text}"

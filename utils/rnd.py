import random


def random_char() -> str:
    """Get random UTF-8 character.

    :return: non-space printable unicode character
    :rtype: str
    """
    random.seed()
    while True:
        char = chr(random.randint(0, 0x10FFFF))
        if char.isprintable() and not char.isspace():
            return char


def random_str(length: int = 9) -> str:
    """Get string with random UTF-8 characters.

    :param length: string's length (default = 9)
    :type length: int

    :return: string with random UTF-8 characters
    :rtype: str
    """
    return ''.join([random_char() for _ in range(length)])


def random_numstr(length: int = 9) -> str:
    """Get string with digits.

    :param length: string's length (default = 9)
    :type length: int

    :return: string with digits
    :rtype: str
    """
    random.seed()
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def random_session_id() -> str:
    """Generate random session ID.

    :return: session ID
    :rtype: str
    """
    random.seed()
    chars = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
             'a', 'b', 'c', 'd', 'e', 'f')
    parts = []
    for i in (8, 4, 4, 4, 12):
        parts.append(''.join([random.choice(chars) for _ in range(i)]))
    return '-'.join(parts)

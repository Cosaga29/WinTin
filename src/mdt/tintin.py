import re

from patterns import (
    TINTIN_ARRAY_BEGIN,
    TINTIN_ARRAY_BETWEEN,
    QUEUED_COMMAND_TEXT,
    MDT_COMMAND_QUEUE,
    TINTIN_COMMAND,
    TINTIN_COMMAND_TEXT,
    QUEUED_COMMAND_REGEX
)


def is_tintin_array(line: str) -> bool:
    """Determines if the line is a tt array. Arrays start with {1}

    Args:
        line (str): The line

    Returns:
        bool: If the line is a tintin array
    """
    # tt++ arrays have the format {1}text{2}text
    return line[0] == "{" and line[2] == "}"


def transform_tintin_array(tt_array: str) -> str:
    """Stringifys the tintin array to a normal string.

    Args:
        tt_array (str): The tintin array string

    Returns:
        str: The transformed string
    """
    end_punctuation = tt_array.rfind(".")
    previous_punctuation = max(
        [
            0,
            tt_array.rfind(".", 0, end_punctuation),
            tt_array.rfind("!", 0, end_punctuation),
            tt_array.rfind("?", 0, end_punctuation),
        ]
    )

    last_sentence = tt_array[previous_punctuation + 1 : end_punctuation]

    # Replace {101} with " "
    mdt_line = re.sub(QUEUED_COMMAND_REGEX, "", last_sentence, 1)
    mdt_line = re.sub(TINTIN_ARRAY_BETWEEN, " ", mdt_line)
    mdt_line = re.sub(TINTIN_ARRAY_BEGIN, "", mdt_line)

    # Fast optimization checks here attempting to catch common things that might
    # slip in client side before the buffer is written to file. Queued command and > seem
    # to be all that interferes atm
    if mdt_line.startswith(QUEUED_COMMAND_TEXT):
        mdt_line = re.sub(MDT_COMMAND_QUEUE, "", mdt_line, count=1)
    if mdt_line.startswith(TINTIN_COMMAND_TEXT):
        mdt_line = re.sub(TINTIN_COMMAND, "", mdt_line, count=1)

    return mdt_line.lstrip().rstrip().lstrip("{").rstrip("}")

import re

from patterns import (
    TINTIN_ARRAY_BEGIN,
    TINTIN_ARRAY_BETWEEN,
    CLIENT_ASYNC_TOKENS
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
    # Narrow down our problem space by a significant amount. In the MDT 
    # output, our target sentence is going to be right biased in the array
    end_punctuation = tt_array.rfind(".")
    previous_punctuation = max(
        [
            0,
            tt_array.rfind(".", 0, end_punctuation),
            tt_array.rfind("!", 0, end_punctuation),
            tt_array.rfind("?", 0, end_punctuation),
        ]
    )
    last_sentence = tt_array[previous_punctuation+1 : end_punctuation]

    # Remove tokens that can appear in the tintin output between 'mt' being entered
    # and map text being written
    # Keep these regex matches quick by first matching and only replacing 1 occurance
    for token in CLIENT_ASYNC_TOKENS:
        if re.match(token, last_sentence):
            last_sentence = re.sub(token, "", last_sentence, 1)
            # Optimization since these tokens are mutally exclusive
            break

    # The expensive ones :(. But on a reduced input :)
    mdt_line = re.sub(TINTIN_ARRAY_BETWEEN, " ", last_sentence)
    mdt_line = re.sub(TINTIN_ARRAY_BEGIN, "", mdt_line)

    return mdt_line.lstrip().rstrip().lstrip("{").rstrip("}")

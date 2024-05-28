"""
This function implements a string search algorithm using regular expressions
(regex) to find an exact match of the target string (pattern) within a list
of text lines.

Parameters:
- data: A list of strings representing the lines of text to search within.
- target: The target string (pattern) to search for within the text.

Returns:
- True if the target string is found within the text, False otherwise.
"""

import re


def regex_search(data: list, target: str) -> bool:
    # Compile a regular expression pattern that matches the exact target string
    pattern = re.compile(rf"^{re.escape(target)}$")

    for line in data:
        # Check if the pattern matches the stripped line
        if pattern.match(line.strip()):
            return True
    return False

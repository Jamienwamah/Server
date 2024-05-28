"""
This function implements the naive string search algorithm, which sequentially
checks each line of text to determine if it exactly matches the target
string (pattern).

Parameters:
- data: A list of strings representing the lines of text to search within.
- target: The target string (pattern) to search for within the text.

Returns:
- True if the target string is found within the text, False otherwise.
"""


def naive_search(data: list, target: str) -> bool:
    for line in data:
        if line.strip() == target:
            return True
    return False

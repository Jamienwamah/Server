"""
This function implements the Aho-Corasick string search algorithm,
a powerful and efficient algorithm used for string matching tasks.
It is designed to find all occurrences of multiple target strings
within a larger body of text.

The Aho-Corasick algorithm is a fundamental string search algorithm
known for its speed and versatility. This implementation utilizes the
ahocorasick library, which provides an efficient implementation of the
algorithm.

Parameters:
- data: A list of strings to build the search automaton from.
- target: The target string to search for in the data.

Returns:
- True if the target string is found in the data, False otherwise.
"""

import ahocorasick


def aho_corasick_search(data: list, target: str) -> bool:
    # Create an Aho-Corasick automaton
    A = ahocorasick.Automaton()

    # Add words from the data to the automaton
    for idx, line in enumerate(data):
        A.add_word(line.strip(), (idx, line.strip()))

    # Build the automaton
    A.make_automaton()

    # Search for the target string in the automaton
    for item in A.iter(target):
        if item[1][1] == target:
            return True

    # Target string not found
    return False

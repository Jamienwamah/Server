"""
This function implements a binary search algorithm to efficiently
locate a target element in a sorted list of data. The binary
search technique divides the list into smaller segments and
compares the target element with the middle element of each
segment, narrowing down the search space with each iteration.

The binary search is a fundamental algorithm commonly used in
computer science and data processing. This implementation
utilizes the bisect module, specifically the bisect_left function,
to perform the binary search efficiently on the sorted data.

Parameters:
- data: A sorted list of elements to search through.
- target: The element to search for in the data.

Returns:
- True if the target element is found in the data, False otherwise.
"""

import bisect


def binary_search(data, target) -> bool:
    # Use the bisect_left function to find the insertion point for the target
    # element
    index = bisect.bisect_left(data, target)

    # Check if the target element is found at the calculated index
    if index < len(data) and data[index].strip() == target:
        return True

    # Target element not found
    return False

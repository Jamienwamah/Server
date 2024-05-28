"""
This function implements the Boyer-Moore string search algorithm,
a highly efficient algorithm used for finding occurrences of
a substring (pattern) within a larger string (text). The algorithm
achieves its efficiency by utilizing two key heuristics:
the bad character rule and the good suffix rule.

Parameters:
- data: A list of strings representing the lines of text to search within.
- target: The target string (pattern) to search for within the text.

Returns:
- True if the target string is found within the text, False otherwise.
"""


def boyer_moore_search(data, target) -> bool:
    m = len(target)

    # Preprocessing
    bad_char = [-1] * 256
    for i in range(m):
        bad_char[ord(target[i])] = i

    def good_suffix_table(pattern):
        m = len(pattern)
        good_suffix = [0] * m
        last_prefix_position = m
        for i in range(m - 1, -1, -1):
            if is_prefix(pattern, i + 1):
                last_prefix_position = i + 1
            good_suffix[m - 1 - i] = last_prefix_position + (m - 1 - i)
        for i in range(m - 1):
            slen = suffix_length(pattern, i)
            good_suffix[slen] = m - 1 - i + slen
        return good_suffix

    def is_prefix(pattern, p):
        m = len(pattern)
        for i in range(p, m):
            if pattern[i] != pattern[i - p]:
                return False
        return True

    def suffix_length(pattern, p):
        m = len(pattern)
        length = 0
        for i in range(p, -1, -1):
            if pattern[i] == pattern[m - 1 - p + i]:
                length += 1
            else:
                break
        return length

    good_suffix = good_suffix_table(target)

    for line in data:
        line = line.strip()
        n = len(line)
        if n < m:
            continue
        s = 0
        while s <= n - m:
            j = m - 1
            while j >= 0 and target[j] == line[s + j]:
                j -= 1
            if j < 0:
                return True
            else:
                s += max(1, j - bad_char[ord(line[s + j])], good_suffix[j])
    return False

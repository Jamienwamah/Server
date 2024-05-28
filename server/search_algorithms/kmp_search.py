"""
This function implements the Knuth-Morris-Pratt (KMP) string search algorithm,
which efficiently searches for occurrences of a substring (pattern) within
a larger string (text) by utilizing the concept of a
"partial match" table (also known as the LPS array).

Parameters:
- data: A list of strings representing the lines of text to search within.
- target: The target string (pattern) to search for within the text.

Returns:
- True if the target string is found within the text, False otherwise.
"""


def kmp_search(data: list, target: str) -> bool:
    def KMPSearch(pat, txt):
        M = len(pat)
        N = len(txt)
        lps = [0] * M
        j = 0
        computeLPSArray(pat, M, lps)
        i = 0
        while i < N:
            if pat[j] == txt[i]:
                i += 1
                j += 1
            if j == M:
                return True
            elif i < N and pat[j] != txt[i]:
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1
        return False

    def computeLPSArray(pat, M, lps):
        length = 0
        lps[0] = 0
        i = 1
        while i < M:
            if pat[i] == pat[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1

    for line in data:
        if KMPSearch(target, line.strip()):
            return True
    return False

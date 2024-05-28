"""
This function implements the Rabin-Karp string search algorithm,
which uses hashing to find an exact match of the target string
(pattern) within a larger string (text).

Parameters:
- data: A list of strings representing the lines of text to search within.
- target: The target string (pattern) to search for within the text.

Returns:
- True if the target string is found within the text, False otherwise.
"""


def rabin_karp_search(data: list, target: str) -> bool:
    d = 256  # Number of characters in the input alphabet
    q = 101  # A prime number for hashing
    M = len(target)
    h = 1  # The value of h would be "pow(d, M-1)%q"

    # Precompute h = pow(d, M-1) % q
    for i in range(M - 1):
        h = (h * d) % q

    p = 0  # Hash value for the target pattern
    t = 0  # Hash value for the text

    # Precompute the hash value of the pattern and the first window of text
    for i in range(M):
        p = (d * p + ord(target[i])) % q

    for line in data:
        line = line.strip()
        n = len(line)
        if n < M:
            continue

        # Precompute the hash value of the first window of text
        t = 0
        for i in range(M):
            t = (d * t + ord(line[i])) % q

        # Slide the pattern over text one by one
        for i in range(n - M + 1):
            # Check the hash values of the current window of text and pattern
            if p == t:
                match = True
                for j in range(M):
                    if line[i + j] != target[j]:
                        match = False
                        break
                if match:
                    return True

            # Calculate hash value for the next window of text
            if i < n - M:
                t = (d * (t - ord(line[i]) * h) + ord(line[i + M])) % q
                if t < 0:
                    t += q

    return False

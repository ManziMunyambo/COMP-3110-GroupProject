"""
Module that stores existing similarity equations/functions to reuse across multiple steps
"""

def normalize_line(text: str) -> str:
    """Trim outer whitespace and collapse internal whitespace."""
    return " ".join(text.strip().split())


def levenshtein_distance(a: str, b: str) -> int:
    """Calculate edit distance """
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, char_a in enumerate(a, 1):
        current = [i]
        for j, char_b in enumerate(b, 1):
            current.append(min(
                current[j - 1] + 1,
                previous[j] + 1,
                previous[j - 1] + (char_a != char_b),
            ))
        previous = current
    return previous[-1]


def normalized_levenshtein(a: str, b: str) -> float:
    """NLD = edit distance divided by the length of the longer string."""
    a, b = normalize_line(a), normalize_line(b)
    denominator = max(len(a), len(b))
    return levenshtein_distance(a, b) / denominator if denominator else 0.0

def textual_similarity(a: str, b: str) -> float:
    """Convert normalized Levenshtein distance to similarity."""
    return 1.0 - normalized_levenshtein(a, b)
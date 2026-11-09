"""
Step 5 of the COMP 3110 line-mapping pipeline.

The detector accepts the candidate-list generator's dictionary, one-to-one
Hungarian assignments, and the complete File B dictionary. It returns revised
old-line -> list-of-new-lines mappings. Ground truth is used only by the
separate evaluate_mappings function.

Assumptions for this version:
* Hungarian assigns each old line to at most one new line.
* Splits extend forward from the Hungarian-assigned new line.
* Already assigned new lines cannot be consumed by another mapping.
* NLD must strictly decrease at every extension; ties stop expansion.
* File B includes all lines, even those excluded by candidate top-N filtering.
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


def detect_line_splits(
    candidates_FileA: dict,
    resolved: dict,
    FileB: dict,
    *,
    max_split_lines: int | None = None,
) -> dict[int, list[int]]:
    """Extend Hungarian matches with adjacent, unassigned new lines.

    candidates_FileA: {old_line: {"content": str, "context": str,
                      "candidate_list": {new_line: {...}}}}
    resolved: {old_line: new_line} (one-to-one Hungarian output)
    FileB: {new_line: {"content": str, "matching_line": ..., "context": ...}}

    Output: {old_line: [new_line, ...]}, including unchanged assignments.
    Keys from JSON (strings) are converted to integers.

    This version assumes forward-only consecutive splits; a line that appears
    before the Hungarian-assigned line is not considered.
    """
    candidates = {int(k): v for k, v in candidates_FileA.items()}
    file_b = {int(k): v for k, v in FileB.items()}
    revised: dict[int, list[int]] = {}

    for old_key, assigned in resolved.items():
        old_line = int(old_key)
        if isinstance(assigned, int) or isinstance(assigned, str):
            new_lines = [int(assigned)]
        elif isinstance(assigned, (list, tuple)):
            new_lines = [int(n) for n in assigned]
        else:
            raise TypeError("resolved values must be line numbers or lists of line numbers")
        if len(new_lines) != 1:
            raise ValueError("Expected one-to-one Hungarian assignments")
        if new_lines[0] not in file_b:
            raise ValueError(f"New line {new_lines[0]} is missing from FileB")
        revised[old_line] = new_lines

    occupied = [line for lines in revised.values() for line in lines]
    if len(set(occupied)) != len(occupied):
        raise ValueError("Hungarian assignments conflict: multiple old lines use the same new line")
    occupied_set = set(occupied)

    # Only examine old lines that appeared in the candidate-generation output.
    for old_line, candidate in candidates.items():
        if old_line not in revised:
            continue  # Hungarian left this line unmatched.

        old_text = candidate["content"]
        selected = revised[old_line][:]
        current_text = normalize_line(file_b[selected[0]]["content"])
        best_score = normalized_levenshtein(old_text, current_text)

        while max_split_lines is None or len(selected) < max_split_lines:
            next_line = selected[-1] + 1
            if next_line not in file_b or next_line in occupied_set:
                break

            extended_text = current_text + " " + normalize_line(file_b[next_line]["content"])
            new_score = normalized_levenshtein(old_text, extended_text)

            # Stop if adding another line does not improve similarity.
            if new_score >= best_score:
                break

            selected.append(next_line)
            occupied_set.add(next_line)
            current_text = extended_text
            best_score = new_score

        revised[old_line] = selected

    return revised


def evaluate_mappings(
    predicted: dict,
    expected: dict,
) -> dict:
    """Compare final mappings against ground truth, independently of detection.

    Reports per-old-line exact match accuracy. Missing and extra mappings are
    counted as errors. This is not a split-specific precision/recall metric.
    """
    predicted = {int(k): [int(n) for n in v] for k, v in predicted.items()}
    expected = {int(k): [int(n) for n in v] for k, v in expected.items()}
    lines = sorted(set(predicted) | set(expected))
    details = {
        old_line: {
            "predicted": predicted.get(old_line),
            "expected": expected.get(old_line),
            "match": old_line in predicted and old_line in expected
                     and predicted[old_line] == expected[old_line],
        }
        for old_line in lines
    }
    correct = sum(item["match"] for item in details.values())
    return {
        "correct": correct,
        "total": len(lines),
        "accuracy": correct / len(lines) if lines else None,
        "details": details,
    }
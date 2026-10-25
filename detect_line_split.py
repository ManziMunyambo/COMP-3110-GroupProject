"""
Runs Step 5 (line-split detection) against the synthetic JSON dataset.

Assumption:
- unchanged mappings and candidate generation were already completed.
- therefore this script starts from each entry in `candidate_list`.
- the stored candidate scores are NOT trusted; the script recomputes
  normalized Levenshtein distance from the text.

Detection rule:
1. Consider the candidate groups in increasing group size.
2. Keep extending while the normalized Levenshtein distance improves.
3. When adding another line makes the distance worse, stop.
4. A split is detected only if the best candidate contains >= 2 new lines.

Usage:
    python3 detect_line_split.py 
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def normalize_line(text: str) -> str:
    """
    Match the normalization used when the dataset was generated:
    - strip leading/trailing whitespace
    - collapse repeated whitespace to one space
    - preserve punctuation and case
    """
    return " ".join(text.strip().split())


def levenshtein_distance(a: str, b: str) -> int:
    """Return the ordinary Levenshtein edit distance between two strings."""
    if a == b:
        return 0

    # Keep b as the shorter string to reduce memory usage.
    if len(a) < len(b):
        a, b = b, a

    previous = list(range(len(b) + 1))

    for i, char_a in enumerate(a, start=1):
        current = [i]

        for j, char_b in enumerate(b, start=1):
            insertion = current[j - 1] + 1
            deletion = previous[j] + 1
            substitution = previous[j - 1] + (char_a != char_b)

            current.append(min(insertion, deletion, substitution))

        previous = current

    return previous[-1]


def normalized_levenshtein(a: str, b: str) -> float:
    """
    NLD(a, b) = LD(a, b) / max(len(a), len(b))

    Lower values mean the strings are more similar.
    """
    a = normalize_line(a)
    b = normalize_line(b)

    denominator = max(len(a), len(b))

    if denominator == 0:
        return 0.0

    return levenshtein_distance(a, b) / denominator


def get_line_text(contents: list[dict[str, Any]], line_number: int) -> str:
    """Get text for a 1-based line number from old_contents/new_contents."""
    for item in contents:
        if item["line"] == line_number:
            return item["text"]

    raise ValueError(f"Could not find line {line_number}")


def join_new_lines(
    new_contents: list[dict[str, Any]],
    line_numbers: list[int],
) -> str:
    """
    Normalize each new line independently, then join the lines with one space.
    """
    parts = [
        normalize_line(get_line_text(new_contents, line_number))
        for line_number in line_numbers
    ]
    return " ".join(parts)


def detect_split_for_candidate(
    old_text: str,
    candidate_groups: list[dict[str, Any]],
    new_contents: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Detect the best split from one already-generated candidate list.

    Candidate groups are evaluated in increasing number of new lines.

    Example:
        [1]       -> 0.55
        [1, 2]    -> 0.21
        [1, 2, 3] -> 0.00
        [1, 2, 3, 4] -> 0.18

    The best group is [1, 2, 3]. The fourth line caused the score to worsen.
    """
    if not candidate_groups:
        return {
            "is_split": False,
            "new_lines": [],
            "score": None,
            "evaluated": [],
        }

    ordered = sorted(
        candidate_groups,
        key=lambda candidate: (
            len(candidate["new_lines"]),
            candidate["new_lines"],
        ),
    )

    evaluated: list[dict[str, Any]] = []
    best_lines: list[int] = []
    best_score: float | None = None

    for candidate in ordered:
        new_lines = candidate["new_lines"]
        candidate_text = join_new_lines(new_contents, new_lines)
        score = normalized_levenshtein(old_text, candidate_text)

        evaluated.append(
            {
                "new_lines": new_lines,
                "joined_text": candidate_text,
                "score": score,
            }
        )

        if best_score is None:
            best_score = score
            best_lines = new_lines
            continue

        # Improvement: keep the larger candidate.
        if score < best_score:
            best_score = score
            best_lines = new_lines
            continue

        # No improvement. For the incremental prefix candidates generated
        # by the dataset, this is the stopping condition from the slides.
        if score > best_score:
            break

        # Equal score: keep the shorter mapping to avoid unnecessarily
        # consuming extra lines.
        break

    is_split = len(best_lines) >= 2

    return {
        "is_split": is_split,
        "new_lines": best_lines if is_split else [],
        "score": best_score,
        "evaluated": evaluated,
    }


def detect_commit_splits(commit: dict[str, Any]) -> list[dict[str, Any]]: 
    """
    Run split detection for every old line that has a generated candidate list.
    """
    predictions = []

    conflict_winners = {
        item["old_line"]: item["winner_new_lines"]
        for item in commit.get("conflict_resolution", [])
    }

    for item in commit.get("candidate_list", []):
        old_line = item["old_line"]
        old_text = get_line_text(commit["old_contents"], old_line)
        candidate_groups = item["candidates"]

        # Candidate conflict resolution happened before Step 5 in this dataset.
        # If a conflict winner exists, stay on that winner's candidate branch.
        # Example: winner [3, 4] means [3], [3, 4], [3, 4, 5] are relevant,
        # while an overlapping branch such as [2, 3] is ignored.
        winner = conflict_winners.get(old_line)
        if winner:
            winner_start = winner[0]
            candidate_groups = [
                candidate
                for candidate in candidate_groups
                if candidate["new_lines"]
                and candidate["new_lines"][0] == winner_start
            ]

        result = detect_split_for_candidate(
            old_text=old_text,
            candidate_groups=candidate_groups,
            new_contents=commit["new_contents"],
        )

        predictions.append(
            {
                "old_line": old_line,
                "old_text": old_text,
                **result,
            }
        )

    return predictions


def expected_split_map(commit: dict[str, Any]) -> dict[int, list[int]]:
    """
    Read ground truth only for evaluation.
    It is not used by the detector itself.
    """
    result: dict[int, list[int]] = {}

    for item in commit.get("ground_truth_line_splits", []):
        if item.get("expected_split"):
            result[item["old_line"]] = item["new_lines"]

    return result


def evaluate_commit(
    commit: dict[str, Any],
    predictions: list[dict[str, Any]],
) -> dict[str, Any]:
    expected = expected_split_map(commit)

    predicted = {
        item["old_line"]: item["new_lines"]
        for item in predictions
        if item["is_split"]
    }

    all_old_lines = sorted(set(expected) | set(predicted))

    details = []
    correct = 0

    for old_line in all_old_lines:
        expected_lines = expected.get(old_line)
        predicted_lines = predicted.get(old_line)

        match = expected_lines == predicted_lines

        if match:
            correct += 1

        details.append(
            {
                "old_line": old_line,
                "expected": expected_lines,
                "predicted": predicted_lines,
                "match": match,
            }
        )

    return {
        "expected": expected,
        "predicted": predicted,
        "details": details,
        "correct": correct,
        "total": len(all_old_lines),
    }


def print_commit_result(
    commit: dict[str, Any],
    predictions: list[dict[str, Any]],
    evaluation: dict[str, Any],
    verbose: bool,
) -> None:
    print("=" * 78)
    print(f'Commit:  {commit["commit"]}')
    print(f'Message: {commit["message"]}')

    unchanged = commit.get("unchanged_mappings", [])
    if unchanged:
        mappings = ", ".join(
            f'{item["old_line"]}->{item["new_line"]}'
            for item in unchanged
        )
        print(f"Already-known unchanged mappings: {mappings}")

    if not predictions:
        print("No line-split candidates were generated for this commit.")
    else:
        for prediction in predictions:
            old_line = prediction["old_line"]

            if prediction["is_split"]:
                lines = prediction["new_lines"]
                score = prediction["score"]
                print(
                    f"Detected split: old line {old_line} "
                    f"-> new lines {lines} "
                    f"(NLD={score:.4f})"
                )
            else:
                print(f"No split detected for old line {old_line}.")

            if verbose:
                print("  Candidate progression:")
                for candidate in prediction["evaluated"]:
                    print(
                        f'    {candidate["new_lines"]}: '
                        f'NLD={candidate["score"]:.4f} | '
                        f'{candidate["joined_text"]}'
                    )

    if evaluation["total"] == 0:
        print("Ground truth: no split expected.")
    else:
        for item in evaluation["details"]:
            status = "PASS" if item["match"] else "FAIL"
            print(
                f'{status}: old line {item["old_line"]} | '
                f'expected={item["expected"]} | '
                f'predicted={item["predicted"]}'
            )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Detect line splits using normalized Levenshtein distance."
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print every candidate and recomputed NLD score.",
    )

    args = parser.parse_args()

    #* change this to the input data 
    dataset_path = Path("mock_data/line_split_ground_truth_dataset.json")

    with dataset_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    commits = data["records"]

    total_cases = 0
    total_correct = 0

    for commit in commits:
        predictions = detect_commit_splits(commit)
        evaluation = evaluate_commit(commit, predictions)

        print_commit_result(
            commit,
            predictions,
            evaluation,
            args.verbose,
        )

        total_cases += evaluation["total"]
        total_correct += evaluation["correct"]

    print("=" * 78)
    print("SUMMARY")

    if total_cases == 0:
        print("No ground-truth split cases were found.")
    else:
        print(f"Correct split mappings: {total_correct}/{total_cases}")
        print(f"Accuracy: {total_correct / total_cases:.2%}")


if __name__ == "__main__":
    main()

"""
Perform conflict resolution on candidate list using hungarian algorithm
"""
from similarity_utils import textual_similarity
from scipy.optimize import linear_sum_assignment
import numpy as np

#Define constants
#Context and content weights - NOTE: using 0.6 and 0.4 as weights because those are in the slides (may change later on)
CONTEXT_WEIGHT = 0.4
CONTENT_WEIGHT = 0.6


def resolve_conflicts(candidates_FileA, threshold):
    """
    Candidate list from step 3 and threshold

    Resolves conflicts directly from candidate list calculating context and content similarity,
    converting to similarity matrix and computing hungarian algorithm
    """
    #dictionary storing all similarity scores
    similarity_scores = {}

    # Iterate through each line in File A
    for line_num, line_data in candidates_FileA.items():
        # Initialize dictionary for this File A line
        similarity_scores[line_num] = {}

        # file B (candidates)
        for candidate_num, candidate_data in line_data["candidate_list"].items():
            # 1. Calculate textual content similarity
            content_similarity = textual_similarity(
                line_data["content"],
                candidate_data["content"]
            )

            # 2. Calculate textual context similarity
            # 3. Combine them using the selected weights
            # The higher combined similarity the better
            if not line_data["context"] or not candidate_data["context"]: # case in which context does not exist
                similarity_score = content_similarity
            else:
                context_similarity = textual_similarity(
                    line_data["context"],
                    candidate_data["context"]
                )

                similarity_score = (
                    CONTENT_WEIGHT * content_similarity
                    + CONTEXT_WEIGHT * context_similarity
                )

            similarity_scores[line_num][candidate_num] = similarity_score

    # 4. Construct the assignment cost matrix
    old_lines = list(similarity_scores.keys())

    # handle an empty candidate dictionary
    if not old_lines:
        return {}

    new_lines = sorted({
        candidate_num
        for candidates in similarity_scores.values()
        for candidate_num in candidates
    })

    # empty stops are filled with negative infinity symbol
    # len(new_lines) + len(old_lines) for unmatched pairs
    similarity_matrix = np.full(
        (len(old_lines), len(new_lines) + len(old_lines)),
        -np.inf
    )

    # map File B line numbers to matrix column positions
    column_lookup = {
        line_num: j
        for j, line_num in enumerate(new_lines)
    }

    # Fill dummy columns to allow unmatched File A lines
    similarity_matrix[:, len(new_lines):] = threshold

    # iterate only through existing candidate pairs
    for i, old_line in enumerate(old_lines):
        for candidate_num, score in similarity_scores[old_line].items():
            j = column_lookup[candidate_num]
            similarity_matrix[i, j] = score

    

    # 5. Run Hungarian assignment
    row_indices, col_indices = linear_sum_assignment(
        similarity_matrix,
        maximize=True
    )


    # 6. Reject invalid or below-threshold matches
    # 7. Return resolved mappings
    resolved_mappings = {}

    for i, j in zip(row_indices, col_indices):
        # Skip dummy assignments
        if j >= len(new_lines):
            continue

        # Reject assignments below or equal to threshold
        if similarity_matrix[i, j] <= threshold:
            continue

        old_line = old_lines[i]
        new_line = new_lines[j]

        resolved_mappings[old_line] = new_line

    return resolved_mappings
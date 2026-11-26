from candidate_list_generation import generate_candidate_list
from conflict_resolution import resolve_conflicts
from detect_line_split import detect_line_splits

# Input from preprocessing
FileA = {
    1: {
        "content": "Hello world",
        "matching_line": None,
        "context": ""
    }
}

FileB = {
    1: {
        "content": "Hello",
        "matching_line": None,
        "context": ""
    },
    2: {
        "content": "world",
        "matching_line": None,
        "context": ""
    }
}

# Step 3: Generate candidate matches
candidates_FileA = generate_candidate_list(
    FileA, FileB,
    num_candidates=5,
    threshold=20
)

# Step 4: Resolve conflicts using Hungarian
resolved = resolve_conflicts(
    candidates_FileA,
    threshold=0.4
)

# Step 5: Detect line splits
revised = detect_line_splits(
    candidates_FileA,
    resolved,
    FileB
)

print("Candidates:", candidates_FileA)
print("Resolved:", resolved)
print("Revised:", revised)
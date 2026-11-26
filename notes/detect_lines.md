# How to Use Line Split Detection

The `detect_line_split.py` file implements **Step 5: Line Split Detection** in the COMP 3110 line-mapping pipeline. It includes the public function `detect_line_splits()` and the separate evaluation function `evaluate_mappings()`. The other functions (`normalize_line()`, `levenshtein_distance()`, and `normalized_levenshtein()`) are helpers and normally do not need to be called externally.

Call:

```python
revised = detect_line_splits(candidates_FileA, resolved, FileB)
```

The function uses initial one-to-one assignments from conflict resolution, checks whether adding consecutive lines from File B improves **normalized Levenshtein distance (NLD)**, and returns an updated mapping dictionary. **Ground truth is not used during detection.**

## Input for `detect_line_splits()`

### 1. `candidates_FileA`

- The dictionary produced by `generate_candidate_list(FileA, FileB, num_candidates, threshold)` in Step 3.
- Contains unmatched lines from File A and possible matches in File B.
- Expected format:

```python
candidates_FileA = {
    old_line_number: {
        "content": "original File A line",
        "context": "",
        "candidate_list": {
            new_line_number: {
                "content": "candidate File B line",
                "context": "",
                "hamming_distance": 0.3
            }
        }
    }
}
```

- The detector uses the outer old-line number and `content` to retrieve the original text. It does **not** currently use the `context` or `hamming_distance` fields to choose the split.
- Only old lines present in this dictionary are considered for split expansion. These old lines must also have a mapping in `resolved` to be examined.

### 2. `resolved`

- The dictionary returned by Step 4 (Hungarian conflict resolution), **assuming the team agrees on this format**:

```python
resolved = {
    old_line_number: new_line_number
}
```

- Each key is a line number in File A; each value is its selected line in File B.
- The function also accepts a single-element list as the value, e.g., `{1: [1]}`.
- These mappings provide the *starting positions* for split detection. Already-assigned new lines cannot be used by another old line.
- Mappings in `resolved` that have no entry in `candidates_FileA` are preserved as one-to-one assignments.
- Unmatched old lines absent from `resolved` are not added to the result.

### 3. `FileB`

- The complete new-file dictionary, in the same general format used by candidate generation:

```python
FileB = {
    new_line_number: {
        "content": "new file line",
        "matching_line": None,
        "context": ""
    }
}
```

- The detector reads the `content` field and the line numbers. `matching_line` and `context` are not used directly by this implementation.
- The **complete File B** is needed because adjacent lines might not be among the top-N candidates.

### 4. Optional `max_split_lines`

- Limits the total number of File B lines assigned to any one old line (including the initial matched line).
- Default: `None` (no explicit limit; searching still stops at occupied lines, missing lines, or non-improving distance).

```python
revised = detect_line_splits(candidates_FileA, resolved, FileB, max_split_lines=5)
```

## How the Detection Works

For each old line that appears in both `candidates_FileA` and `resolved`:

1. Start with the File B line assigned by Hungarian.
2. Compare the original File A text to that File B line using normalized Levenshtein distance.
3. Look at the **next consecutive** File B line.
4. If the next line exists and is not assigned to another mapping, concatenate it with a single space and recompute NLD.
5. If NLD **decreases**, keep that line and try the next one.
6. If NLD **increases or stays equal**, stop. Keep the shorter, previously accepted mapping.
7. Return all the original resolved assignments, revised where an extension was accepted.

This implementation searches **forward only** from the assigned line. It does not extend backward or reconsider which starting line Hungarian selected.

### Levenshtein distance (LD)

`levenshtein_distance(a, b)` returns the minimum number of single-character **insertions, deletions, or substitutions** needed to turn one string into another. It uses dynamic programming.

For the example below:

```text
File A line 1: "Hello world"
File B line 1: "Hello"
```

To transform `"Hello"` into `"Hello world"`, we add the six characters `" world"`. Therefore:

```text
LD("Hello world", "Hello") = 6
```

### Normalized Levenshtein distance (NLD)

The implementation divides edit distance by the length of the longer *normalized* string:

```text
NLD(a, b) = LD(normalize(a), normalize(b))
            / max(len(normalize(a)), len(normalize(b)))
```

- The helper `normalize_line()` trims leading/trailing whitespace and collapses runs of whitespace into single spaces **for comparison**.
- Smaller NLD means a better match; `0` means identical normalized strings.
- When both normalized strings are empty, the function returns `0.0`.

For `"Hello world"` (11 characters) and `"Hello"` (5 characters):

```text
LD = 6
NLD = 6 / max(11, 5) = 6 / 11 ≈ 0.5455
```

### Worked Example: First and Second Comparisons

Original File A and new File B:

```text
File A (old):                  File B (new):
Line 1: Hello world           Line 1: Hello
                              Line 2: world
```

**First comparison — the starting mapping**

```text
File A line 1: "Hello world"
File B line 1: "Hello"
LD  = 6
NLD = 6 / 11 ≈ 0.5455
Starting mapping = {1: [1]}
```

**Second comparison — extend to the next consecutive line**

```text
File A line 1: "Hello world"
File B lines 1 + 2: "Hello" + " " + "world" = "Hello world"
LD  = 0
NLD = 0 / 11 = 0.0
```

Since `0.0 < 0.5455`, the extension improves the match. The algorithm accepts line 2:

```python
revised = {1: [1, 2]}
```

There is no line 3 in File B, so the search stops. **This is one-to-many mapping:** old line 1 maps to new lines 1 and 2.

## Complete Example

```python
from detect_line_split import detect_line_splits, evaluate_mappings

# Mock Step 3 output (illustrative Hamming distances)
candidates_FileA = {
    1: {
        "content": "Hello world",
        "context": "",
        "candidate_list": {
            1: {"content": "Hello", "context": "", "hamming_distance": 0.3},
            2: {"content": "world", "context": "", "hamming_distance": 0.4},
        },
    }
}

# Mock Step 4 output: old line 1 initially maps to new line 1
resolved = {1: 1}

# Entire new file
FileB = {
    1: {"content": "Hello", "matching_line": None, "context": ""},
    2: {"content": "world", "matching_line": None, "context": ""},
}

# Step 5: production detection does not receive the expected answer
revised = detect_line_splits(candidates_FileA, resolved, FileB)
print(revised)
# {1: [1, 2]}

# Separate test/validation step
expected_mappings = {1: [1, 2]}
evaluation = evaluate_mappings(revised, expected_mappings)
print(evaluation["accuracy"])
# 1.0
```

## Output from `detect_line_splits()`

- Returns a dictionary in the following format:

```python
revised = {
    old_line_number: [new_line_number_1, new_line_number_2, ...]
}
```

- **One-to-one:** `{1: [1]}` means old line 1 remains assigned only to new line 1.
- **One-to-many split:** `{1: [1, 2]}` means old line 1 was split across new lines 1 and 2.
- The dictionary includes unchanged one-to-one mappings inherited from `resolved`; those are not separately re-evaluated unless their old line appears in the candidate dictionary.
- It returns mappings only. It does not print results or calculate ground-truth accuracy.

## Separate Evaluation: `evaluate_mappings()`

Call:

```python
evaluation = evaluate_mappings(revised, expected_mappings)
```

- `revised` is the predicted output from Step 5.
- `expected_mappings` is ground truth used **only for evaluation**.
- Returns `correct`, `total`, `accuracy`, and per-line `details`.
- This is **exact mapping accuracy per old line**, not a split-specific precision/recall measure.
- Missing or extra predicted mappings are counted as incorrect.

## Notes and Current Assumptions

- The Hungarian output dictionary shown above is a **proposed interface** until confirmed with the conflict-resolution teammate.
- `hamming_distance` is used upstream to rank candidate lines; the split detector recomputes similarity using **normalized Levenshtein distance**, not Hamming distance.
- The forward-only greedy rule can miss a better combined mapping if the distance first stays equal or increases. That is a known limitation of this version.
- An occupied File B line is not available for split extension. The detector assumes the initial Hungarian assignments are conflict-free.
- The algorithm does not modify File B or the candidate-list dictionary; it produces a new mapping dictionary.
- If a shared preprocessing step already normalizes whitespace, the `normalize_line()` helper may be redundant, but keeping it for scoring comparisons does not change the stored input data.

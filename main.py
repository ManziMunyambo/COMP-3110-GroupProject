from PythonDriver import main as preprocess_data
from comparison import final_step as detect_unchanged_lines
from candidate_list_generation import generate_candidate_list
from conflict_resolution import resolve_conflicts
from detect_line_split import detect_line_splits
import json


# Step 1: Preprocess data
preprocess_data()

# Step 2: detect unchanged lines
# * need to integrate preprocessed data

#* loop through preprocessed files 


detect_unchanged_lines()

# ouptuts a json ->

# read as json 
with open("mapping_output.json", "r", encoding="utf-8") as file:
    file_overview = json.load(file)

file_A = file_overview["file_A"]
file_B = file_overview["file_B"]

# Step 3: Generate candidate matches
candidates_FileA = generate_candidate_list(
    file_A, file_B,
    num_candidates=5,
    threshold=0.2
)

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(candidates_FileA, f, indent=4)

# print("Candidates:", candidates_FileA)

# Step 4: Resolve conflicts using Hungarian
resolved = resolve_conflicts(
    candidates_FileA,
    threshold=0.4
)

#print(resolved)

# Step 5: Detect line splits
revised = detect_line_splits(
    candidates_FileA,
    resolved,
    file_B
)

print(f"revised: {revised}")

# print("Candidates:", candidates_FileA)
# print("Resolved:", resolved)
# print("Revised:", revised)
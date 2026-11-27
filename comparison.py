# Dictionary format:
# {
#    content
#    matching line
#    context (for unmatched lines)
# }

# Create different versions of a file where the changes are not too obvious.
# Mutations can also be included.

# Figure out which lines have not changed.
# Save the results in a JSON file so Ashlynn's candidate list step can use it.


import difflib   # used to compare two lists of lines
import json      # used to save the results as a JSON file


# CONTEXT_SIZE is the number of lines we look at above and below
# a line that has no match. This helps show what is around that line.

OLD_FILE_PATH = "old_file.txt"
NEW_FILE_PATH = "new_file.txt"
OUTPUT_PATH = "mapping_output.json"
CONTEXT_SIZE = 2


# Opens the file, reads each line and closes it after.

def read_lines(path):
    with open(path, "r") as file:
        lines = []
        for line in file:
            lines.append(line.rstrip("\n"))
    return lines



# STEP 2: Create a dictionary for each line in the file.
# Each line gets its own line number and stores its content,
# matching line and context. The matching line starts as None
# because we have not compared the files yet. Context is also
# left empty for now because we add that later.
# We start counting from 1.

def build_dictionary(lines):
    dictionary = {}
    line_number = 1 #counter
    for text in lines:
        dictionary[line_number] = {
            "content": text,
            "matching_line": -1,
            "context": ""
        }
        line_number = line_number + 1
    return dictionary


# STEP 3: Compare both files and find the lines that stayed the same.
# difflib gives each line a code depending on what happened:
#     "  " = line is the same in both files
#     "- " = line is only in the old file
#     "+ " = line is only in the new file
#     "? " = extra information from difflib that we do not need.
#
# We use two counters to keep track of the line numbers in each file.
# If a line is the same, we save its matching line in both dictionaries
# and move both counters forward. If it only appears in one file,
# we only move that file's counter.

def fill_in_matches(old_lines, new_lines, old_dict, new_dict):
    differ = difflib.Differ()
    results = differ.compare(old_lines, new_lines)

    old_number = 1
    new_number = 1

    for result in results:
        code = result[:2]   # the first 2 characters of the result line

        if code == "  ":
            # The line is the same in both files, so we save the match.
            old_dict[old_number]["matching_line"] = new_number
            new_dict[new_number]["matching_line"] = old_number
            old_number = old_number + 1
            new_number = new_number + 1
        elif code == "- ":
            # Line only appears in the old file.
            old_number = old_number + 1
        elif code == "+ ":
            # Line only appears in the new file.
            new_number = new_number + 1
        # We skip "? " because it is not an actual file line.


# STEP 4: Add context to lines that do not have a match.
# We look at the lines around each unmatched line to get an idea
# of where it belongs. We take the number of lines set by
# CONTEXT_SIZE above and below it, then save them as one string.
# max() and min() help make sure we stay within the file's line numbers.

def add_context(dictionary):
    total_lines = len(dictionary)

    for line_number in dictionary:
        if dictionary[line_number]["matching_line"] is None:
            first = max(1, line_number - CONTEXT_SIZE)
            last = min(total_lines, line_number + CONTEXT_SIZE)

            neighbours = []
            for other in range(first, last + 1):
                if other != line_number:
                    neighbours.append(dictionary[other]["content"])

            dictionary[line_number]["context"] = " ".join(neighbours)


# STEP 5: Run everything in the right order.
# Read both files, create the dictionaries, find the matching lines
# and add context to the ones without a match. After that, save
# everything into a JSON file so it can be used by the next step.
# indent=2 just makes the JSON easier to read.

def final_step(): #change main, make it comparison total there is already a driver.
    old_lines = read_lines(OLD_FILE_PATH)
    new_lines = read_lines(NEW_FILE_PATH)

    old_dict = build_dictionary(old_lines)
    new_dict = build_dictionary(new_lines)

    fill_in_matches(old_lines, new_lines, old_dict, new_dict)

    add_context(old_dict)
    add_context(new_dict)

    output = {
        "file_A": {"total_lines": len(old_lines), "lines": old_dict},
        "file_B": {"total_lines": len(new_lines), "lines": new_dict}
    }

    with open(OUTPUT_PATH, "w") as out_file:
        json.dump(output, out_file, indent=2)

    print("Done! Results saved to", OUTPUT_PATH)


# This makes sure main() only runs when we run this file directly.
# Other files can still import and use the functions without
# automatically running the whole program.
if __name__ == "__main__":
    final_step()

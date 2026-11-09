from detect_line_split import detect_line_splits

# candidates: while lines in file B might match to file A
candidates_FileA = {
    1: {
        "content": "Hello world",
        "context": "",
        "candidate_list": {
            1: {
                "content": "Hello",
                "context": "",
                "hamming_distance": 0.3
            },
            2: {
                "content": "world",
                "context": "",
                "hamming_distance": 0.4
            }
        }
    }
}

# Mock output from Hungarian conflict resolution
# which one-to-one mappings were selected by hungarian
# in this example: Hello world -> Hello
resolved = {
    1: 1,
}

# File B dictionary
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

# Call split detection
# Shoes if any selected mapping needs to e expanded to multple consecutive lines
revised = detect_line_splits(candidates_FileA, resolved, FileB)

print(revised)
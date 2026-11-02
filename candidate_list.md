How to Use the Candidate List Generation

There are 5 functions in the candidate_list_generation.py file. 4 of the 5 are helper functions which should not need to be called externally. 
Call generate_candidate_list(FileA, FileB, num_candidates, threshold) -> total_candidate_list to generate the candidate lists for lines in File A 

Input for generate_candidate_list():

- FileA: 
    -  a dictionary designed based on the difflib.Differ().compare(fileA, fileB) function
    - the format of the dictionary should be as follows:
        File_A_lines = {
            line#:{
                content: "",
                matching_line: ""
                context: "",
            }
        }

    - Filling FileA:
        - The "line#" should be filled by keeping track of the index of lines in File A and lines in File B
            - Note: if the line in difflib.Differ().compare(fileA, fileB) begins with "  ", then it is identical in A and B
                - In this case, the "matching_line" should be filled in with the index - same in FileA and FileB, increment both index markers
            - If the line in difflib.Differ().compare(fileA, fileB) begins with "- ", then it is in File A only - increment file A's index marker
            - If the line in difflib.Differ().compare(fileA, fileB) begins with "+ ", then it is in File B only - increment file B's index marker
        - "content" is filled with the line that was returned in difflib.Differ().compare(fileA, fileB), but removing the first 2 characters
        - Once all lines are added to the dictionary, "context" should be filled in only for the lines which have no value for "matching_line"
            - Concatenate the line's content for all lines N before and N after the one that requires the context

- FileB: 
    -  a dictionary designed based on the difflib.Differ().compare(fileA, fileB) function
    - the format of the dictionary should be as follows:
        File_B_lines = {
            line#:{
                content: "",
                matching_line: ""
                context: "",
            }
        }
    
    - FileB should be filled the same way as File A, and the 2 may be filled at the same time

- num_candidates 
    - The top n candidates should be chosen for each unmatched line in FileA

- threshold
    - The maximum threshold of the hamming distance that is acceptable
    - Ranges from 0-1: 0 is identical, 1 is not similar at all
    - Even if the num_candidates is not reached, if there are no more possible matchings that are below the threshold, then no other possibole matchings will be added to the candidate list for that line in FileA - they are too different to be considered


Output for generate_candidate_list():
- The output will be a dictionary of the following format:
    - candidates_FileA = {
        line#: {
            content: "",
            context: "",
            candidate_list: {
                line#: {
                    content: "",
                    context: "",
                    hamming_distance: ""
                }
            }
        }
    }
- Note: hamming_distance is the distance from the line in File A to the line in File B
- Not sure if context is necessary for further steps yet, but most likely not

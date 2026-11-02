#This file defines methods to use with simhashing and hamming distance
#Note: the final method, create_full_candidate_list, will be the one called externally to create the full candidate list
    # All other functions are helper functions to get to the final candidate list
from simhash import Simhash

#Define constants
#Context and content weights - NOTE: using 0.6 and 0.4 as weights because those are in the slides (may change later on)
CONTEXT_WEIGHT = 0.4
CONTENT_WEIGHT = 0.6

# Method 1: Calculate simhash of a line
# Parameters: A line (or lines) of a file
# Output: the simhash for the line
def calculate_simhash(line):
    hashed_line = Simhash(line)
    return hashed_line

# Method 2: Calculate hamming distance between 2 simhashes
# Parameters: 2 simhashes
# Output: the hamming distance between the 2 simhashes
def calculate_hamming_distance(line1, line2):
    hamming_distance = line1.distance(line2)
    return hamming_distance

# Method 3: calculate combined content and context distance
# Parameters: line1 and line 2's simhashes, then line1 and line2's context simhashes
# Output: the combined distance
def calculate_combined_distance(line1_simhash, line1context_simhash, line2_simhash, line2context_simhash):
    #Calculate hamming distance for content
    content_distance = calculate_hamming_distance(line1_simhash, line2_simhash)
    #Calculate hamming distance for context
    context_distance = calculate_hamming_distance(line1context_simhash, line2context_simhash)
    #Calculate combined hamming distance
    combined_distance = CONTENT_WEIGHT*content_distance +CONTEXT_WEIGHT*context_distance
    return combined_distance

# Method 4: Compare the hamming distances for a single line in the 1st file to find n candidate pairings
# Parameters: a line from File A's metadata, the dictionary of lines for File B, the number of candidates that should be chosen, threshold for similarity
# Output: a dictionary of pairings in the form candidate_list = {line#:{content:"", context:"", hamming_distance:""}}
def candidate_pairings_one_line(lineA_values, FileB, candidate_length, threshold):
    #Define the counter for number of candidates chosen
    candidate_count = 0
    #Find simhash for the first line (from File A)
    simhash_lineA = calculate_simhash(lineA_values["content"])
    #Find simhash for the context of the first line
    simhash_context_lineA = calculate_simhash(lineA_values["context"])
    #Define a dictionary for the top n candidate pairings
    top_candidates = {}
    #For each line passed for file B:
    for line_num, line_data in FileB.items():
        #Calculate the line's simhash
        simhash_lineB = calculate_simhash(line_data["content"])
        # Calculate the line's context simhash    
        simhash_context_lineB = calculate_simhash(line_data["context"])
        #Calculate the combined distance for line1 and line 2
        combined_distance = calculate_combined_distance(simhash_lineA, simhash_context_lineA, simhash_lineB, simhash_context_lineB)
        #If the distance is below the threshold...
        if combined_distance < threshold:
            #Add the candidate pairing and its distance to the list
            if line_num not in top_candidates:
                top_candidates[line_num] = {"content": "",
                                            "context": "",
                                            "hamming_distance": ""
                                            }
            top_candidates[line_num]["content"] = line_data["content"]
            top_candidates[line_num]["context"] = line_data["context"]
            top_candidates[line_num]["hamming_distance"] = combined_distance
            candidate_count = candidate_count+1
            #If the length of the candidate list is greater than candidateLength, remove the line with the largest hamming distance
            if candidate_count>candidate_length:
                sorted_candidates = sorted(top_candidates.items(), key=lambda item: item[1]["hamming_distance"])
                top_candidates = dict(sorted_candidates[:candidate_length])
    #Return the final candidateList with the top n pairings
    return top_candidates


# Method 5: Create full candidate list
# Parameters: File A's dictionary,File B's dictionary, how many candidates should be chosen for each line in File A, and the threshold of similarity
# Output: full candidate list (in dictionary format)
def generate_candidate_list(FileA, FileB, num_candidates, threshold):
    #Define dictionary that will hold all candidate lists
    total_candidate_list = {}
    # Iterate through each line in File A
    for line_num, line_data in FileA.items():
        #Call candidate_pairing_one_line for lines which have not yet been matched - returns candidates for that line in File A
        if line_num["matching_line"] == None:
            #Creat the entry in the dictionary
            if line_num not in total_candidate_list:
                total_candidate_list[line_num] = {"content":"",
                                                "context":"",
                                                "candidate_list":{}
                                                }
            candidates = candidate_pairings_one_line(line_data, FileB, num_candidates, threshold)
            #Convert the candidates into the proper dictionary format and add to the total candidates dictionary
            total_candidate_list[line_num]["content"] = FileA[line_num]["content"]
            total_candidate_list[line_num]["context"] = FileA[line_num]["context"]
            total_candidate_list[line_num]["candidate_list"] = candidates
    #Return the full candidate list
    return total_candidate_list

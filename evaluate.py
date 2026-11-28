import xml.etree.ElementTree as ET #reads prof's XML file
import json                       #reads our JSON file
import sys                        #reads file paths typed into the terminal

#grading function 
def evaluate_tool(xml_path, json_path):
    # Read the answer key (XML)
    #open prof's XML file and load it into memory
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    ground_truth = {} #store the answers in a dictionary
    
    #loop through every "VERSION" in the XML
    for version in root.findall('VERSION'):
        #only look at the new version (Version 2) 
        if version.get('NUMBER') == '2': 
            #loop through every "LOCATION" tag in Version 2
            for loc in version.findall('LOCATION'):
                #grab old Line (ORIG) and new Line (NEW)
                old_line = int(loc.get('ORIG')) #convert text to number x2
                new_line = int(loc.get('NEW'))  
                #save it in our dictionary
                ground_truth[old_line] = new_line


    # Now we read our test (JSON) 
    #open JSON file that our tool generated and load it to memory
    with open(json_path, 'r') as f:
        tool_output = json.load(f)
    
    # Note: In JSON files, all keys are read as text ("123"), not numbers (123).
    #so convert them back to numbers so we can compare them to XML file
    tool_output = {int(k): v for k, v in tool_output.items()}

    # Check accuracy of test
    correct = 0           #count how many we got right
    total = len(ground_truth) #total num of lines in the answer key
    errors = []           #list to hold all mistakes

    #loop through every correct answer in our answer key
    for old_line, expected_new in ground_truth.items():
        #What is our tool's answer for this old_line?
        actual = tool_output.get(old_line)
        
        # Line Splits
        #if our tool split one line into two, `actual` will be a list.
        if isinstance(actual, list):
            #check the first line of the split to see if it matches the expected answer
            actual_new = actual[0] 
        else:
            #if it's a normal mapping, we just use the number they gave us
            actual_new = actual

        #compare our answer (actual_new) to the answer key (expected_new)
        if expected_new == actual_new:
            correct += 1
        else:
            errors.append(f"Old {old_line}: Expected {expected_new}, Got {actual}")

    # Print Results
    accuracy = (correct / total) * 100 if total > 0 else 0 #prevents a crash if xml file is empty

    print(f"\nEvaluation Results for {xml_path}")
    print(f"Correct Mappings: {correct}/{total}")
    print(f"Accuracy: {accuracy:.0f}%") 
    
    if errors:
        print("\nErrors:")
        for err in errors:
            print(err)
    else:
        print("Perfect score! :D")

# Run script from terminal
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python evaluate.py <path_to_xml> <path_to_json>")
        print("Example: python evaluate.py ArrayReference.xml output.json")
        sys.exit(1) #stop the script if user didn't type it right
        
    #saave the file paths
    xml_file = sys.argv[1]
    json_file = sys.argv[2]
    
    #run the evaluation
    evaluate_tool(xml_file, json_file)
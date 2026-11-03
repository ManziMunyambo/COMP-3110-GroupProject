import re
from pathlib import Path 
from typing import Optional 

def preprocess(source_path: Path) -> Optional[str]:
    try:
        #read all lines from the source file
        print("Reading Python file lines...")
        lines = source_path.read_text(encoding="utf-8").splitlines()
        processedCode = []

        for line in lines:
            #handle comments by splitting them into separate lines 
            comment = ""
            comment_index = line.find("#")
            if comment_index != -1:
                comment = line[comment_index:]
                line = line[:comment_index]

            #remove excess indentation and turn multiple whitespaces into one
            match = re.match(r'^(\s*)(.*)$', line)
            if match:
                indent, code = match.groups() 
                #trim whitespaces inside the code and afterwards 
                code = re.sub(r'\s+', ' ', code).rstrip()

                #rebuild the line with its original indentation
                if code and comment:
                    processedCode.append(f"{indent}{code} {comment}")
                elif code:
                    processedCode.append(f"{indent}{code}")
                elif comment:
                    processedCode.append(f"{indent}{comment}")
                else:
                    #preserve blank lines
                    processedCode.append("") 

            else:
                processedCode.append(line)

        finalCode = "\n".join(processedCode)
        print("Preprocessing complete! Starting syntax check...")

        #make sure the code can still compile. Syntax check
        if testPythonCode(finalCode):
            print("Syntax check passed! Preprocessed file can successfully compile :)")
            return finalCode 
        else:
            return None 

    except Exception as e:
        print(f"Error reading file: ", e)
        return None 


def testPythonCode(processedCode: str) -> bool:
    try:
        #compile() checks if the syntax is valid. How convenient!
        compile(processedCode, '<preprocessed_string', 'exec')
        return True 
    except SyntaxError as e:
        print("Syntax check failed! Preprocessed code cannot compile ;(")
        print("Error message: ",e)
        return False
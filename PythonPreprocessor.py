import re
from pathlib import Path 
from typing import Optional, Union

PROJECT_DIR = Path(__file__).resolve().parent 
DEFAULT_OUTPUT_DIR = PROJECT_DIR / "preprocessed_files"

def preprocess(source_path: Union[str,Path], output_path: Optional[Union[str,Path]] = None) -> Optional[Path]:
    try:
        #read all lines from the source file
        source = Path(source_path)
        print(f"Reading Python files from {source.name}...")
        lines = source.read_text(encoding="utf-8-sig").splitlines()
        processedCode = []

        for line in lines:
            #handling comments
            comment = ""
            comment_index = line.find("#")
            if comment_index != -1:
                comment = line[comment_index:]
                line = line[:comment_index]

            #remove excess indentation and trim excess whitespaces
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
                    processedCode.append("") #preserve blank lines

            else:
                processedCode.append(line)

        finalCode = "\n".join(processedCode)

        print("=== finalCode start===")
        print(repr(finalCode))
        print("=== finalCode end ===")
        print(f"Preprocessing complete! Starting syntax check...")

        if testPythonCode(finalCode):
            print("Syntax check passed! Preprocessed file can successfully compile :)")

            if output_path is None:
                destination = DEFAULT_OUTPUT_DIR / f"{source.stem}_preprocessed.py"
            else:
                destination = Path(output_path)

            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(finalCode, encoding="utf-8")
            print(f"Preprocessed file successfully saved to: {destination.resolve()}")

            return destination

        else:
            return None

    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def testPythonCode(processedCode: str) -> bool:
    try:
        #compile() checks if the syntax is valid. How convenient!
        compile(processedCode, '<preprocessed_string>', 'exec')
        return True 
    except SyntaxError as e:
        print("Syntax check failed! Preprocessed code cannot compile :(")
        print(f"Error message: {e}")
        return False
from pathlib import Path 
from PythonPreprocessor import preprocess

def main():
    sampleFileName = "testing.py" #<- replace this guy!
    sampleFile = Path(sampleFileName)
    print("Running preprocessor on ", sampleFileName)

    result = preprocess(sampleFile)

    if result is not None:
        print("\nPreprocessing complete!\n--- Preprocessed Code ---\n")
        print(result, "\n")
    else:
        print("\n--- Preprocessing Failed! ---\nNone was returned")

if __name__ == "__main__":
    main()
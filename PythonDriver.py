from pathlib import Path 
from PythonPreprocessor import preprocess

PROJECT_DIR = Path(__file__).resolve().parent 

def main():
    sample_file = PROJECT_DIR / "preprocessed_files" /"sample.py" #<- enter your desired file here!

    output_dir = PROJECT_DIR / "preprocessed_files"
    output_file = output_dir / "sample_preprocessed.py"

    preprocessed_file = preprocess(sample_file, output_file)

    if preprocessed_file is not None:
        print(f"Preprocessed file written to {preprocessed_file}")
    else:
        print("Preprocessing failed due to syntax errors")

if __name__ == "__main__":
    main()
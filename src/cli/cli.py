import os
from pathlib import Path


def run_cli():
    cwd = Path(os.getcwd())

    correct = False
    while not correct:
        print(f"Your current working directory is: {cwd}")
        print("Specify the relative path to the input file for pairwise ranking")
    
        relative_target = input("> ")
        target_path = (cwd / relative_target).resolve()
        correct = input(f"{target_path} | Is that correct? (y/n) ")[0].lower() == "y"
    
    
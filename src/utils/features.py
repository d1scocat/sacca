from pathlib import Path

import pandas as pd

_SLICE_SYMBOLS = "SME"
_WIDE_SYMBOLS = "rludfbw"
_ROTATION_SYMBOLS = "xyz"
_FACE_SYMBOLS = "R L U D F B".split()


def parse_features(filepath: Path, output_path: Path):
    """
    Takes a .csv file with the headers ['Label', 'Algorithm'] and
    parses each algorithm's features. Writes the results into a
    csv-syntax file.

    Arguments:
        filepath (pathlib.Path): the path to the input data
        output_path (pathlib.Path): the path to write the output to
    """
    df = pd.read_csv(filepath)

    df["moves"] = df["Algorithm"].str.split().str.len()
    df["primes"] = df["Algorithm"].str.count("'")
    df["doubles"] = df["Algorithm"].str.count("2")
    df["slices"] = df["Algorithm"].str.count("|".join(_SLICE_SYMBOLS))
    df["wide"] = df["Algorithm"].str.count("|".join(_WIDE_SYMBOLS))
    df["rot"] = df["Algorithm"].str.count("|".join(_ROTATION_SYMBOLS))

    for face in _FACE_SYMBOLS:
        df[face] = df["Algorithm"].str.upper().str.count(face)

    df.to_csv(output_path, index=False)

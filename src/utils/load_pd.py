from pathlib import Path

import pandas as pd


def load_or_init_csv(path: Path, columns: list[str]) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)

    df = pd.DataFrame(columns=columns)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)

    return df

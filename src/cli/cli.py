import os
import itertools

import typer
import pandas as pd

from click import exceptions
from pathlib import Path
from rich.console import Console
from rich.status import Status
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from rich.theme import Theme

from pairwise import ssot
from utils import load_pd


app = typer.Typer()


theme = Theme(
    {"warning": "magenta", "danger": "bold red"}
)
console = Console(theme=theme)

info = """
Specify the relative path to the pairwise ranking storage directory.
The specified directory must contain the following files:
- a file ending in `_features.csv`
- a file ending in `_algs.csv`

Both of these files must have the same exact prefix. Example:
- `oll_features.csv`
- `oll_algs.csv`

Additionally, the directory may or may not contain a file with the same prefix
and the suffix `_pairs.csv`. This file will contain the ranking progress and
it allows for the process to be resumable.

Your current working directory is: `{cwd}`
(your input will be treated relative to it)
"""

rank = """
##### Write "stop" to pause and save the current ranking data.
# Which is easier?
1. {label1}: {alg1}
2. {label2}: {alg2}
"""


@app.command()
def run_cli():
    try:
        cwd = Path(os.getcwd())

        console.print(Panel(
            Markdown(info.format(cwd=cwd)),
            title="Instructions",
            border_style="white",
        ))

        correct = False
        while not correct:    
            relative_target = Prompt.ask("Directory")
            target_path = (cwd / relative_target).resolve()
            correct = Confirm.ask(f"{target_path} | is that correct?", console=console)

            if correct and (not target_path.exists() or not target_path.is_dir()):
                console.print("The directory does not exist or is a file.", style="danger")
                correct = False
        
        data = [file for file in target_path.rglob("*_features.csv")]
        if not data:
            console.print("No features file found.", style="danger")
            raise typer.Exit(code=1)
        
        if len(data) > 1:
            console.print("Ambiguous directory - multiple files end in \"_features.csv\".", style="danger")
            raise typer.Exit(code=1)
        
        features_file = data[0]
        prefix = features_file.stem.removesuffix("_features")
        pairs_file = target_path / f"{prefix}_pairs.csv"
        algs_file = target_path / f"{prefix}_algs.csv"

        if not algs_file.exists():
            console.print("No algorithms file found.", style="danger")
            raise typer.Exit(code=1)

        with Status("Loading data...", spinner="dots", console=console):
            algs = pd.read_csv(algs_file)
            pairs = load_pd.load_or_init_csv(pairs_file, ssot.HEADERS)

            if pairs.empty:
                algs_list = algs["Label"].to_list()
                rows = [
                    (alg1, alg2, "N")
                    for alg1, alg2 in itertools.combinations(algs_list, 2)
                ]
                
                pairs = pd.DataFrame(rows, columns=pairs.columns)
            
            unranked = pairs.loc[pairs["easier"] == "N"]
            updated_ranking = {}

        algs_by_label = algs.set_index("Label")
        ranked_already = (pairs["easier"] != "N").sum()
        total = len(pairs)

        for row in unranked.itertuples():
            ranked_already += 1

            alg1 = algs_by_label.loc[row.alg_a]
            alg2 = algs_by_label.loc[row.alg_b]
            console.print(Panel(
                Markdown(rank.format(
                    label1=alg1.name,
                    label2=alg2.name,
                    alg1=alg1["Algorithm"],
                    alg2=alg2["Algorithm"],
                )),
                title=f"{ranked_already} / {total}",
                border_style="white",
            ))

            value = Prompt.ask("> ", choices=["1", "2", "stop"])
            if value == "stop":
                break

            updated_ranking[row.Index] = value
            
        if updated_ranking:
            pairs.loc[list(updated_ranking.keys()), "easier"] = list(updated_ranking.values())
            pairs.to_csv(pairs_file, index=False)
        
        console.print(f"Saved {len(updated_ranking)} new rankings.\nBye")
    except exceptions.Exit:
        raise
    except KeyboardInterrupt:
        console.print("\nBye")
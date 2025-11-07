import sqlite3
import pandas as pd
from glob import glob
from pathlib import Path

def loadQcsvFiles (pattern,db_path,table):
    csv_files = sorted(glob(pattern))

    if not csv_files:
        raise SystemExit("No CSV files matched the pattern")

    with sqlite3.connect(db_path) as conn:
        # Create table from the first file (or skip if table already exists)
        df0 = pd.read_csv(csv_files[0])
        df0.to_sql(table, conn, if_exists="replace", index=False)  # creates schema
        # Append the rest
        for p in csv_files[1:]:
            dfi = pd.read_csv(p)
            # Optionally align columns in case of ordering differences
            dfi = dfi[df0.columns]
            dfi.to_sql(table, conn, if_exists="append", index=False)


def loadQanswers():
    # Expand your pattern into file paths
    base = Path().resolve()  # equivalent to $PWD
    pattern = str(base / "quiz-time" / "anos" / "ano*" / "*" / "*" / "an*.csv")
    db_path = "quiz.db"
    table = "responses"

    loadQcsvFiles(pattern,db_path,table)

def loadQlinks():
    # Expand your pattern into file paths
    base = Path().resolve()  # equivalent to $PWD
    pattern = str(base / "quiz-time" / "links.csv")
    db_path = "quiz.db"
    table = "links"
    loadQcsvFiles(pattern,db_path,table)

def loadQtemas():
    # Expand your pattern into file paths
    base = Path().resolve()  # equivalent to $PWD
    pattern = str(base / "quiz-time" / "temas.csv")
    db_path = "quiz.db"
    table = "temas"
    loadQcsvFiles(pattern,db_path,table)


def loadQaulas():
    # Expand your pattern into file paths
    base = Path().resolve()  # equivalent to $PWD
    pattern = str(base / "quiz-time" / "aulas.csv")
    db_path = "quiz.db"
    table = "aulas"
    loadQcsvFiles(pattern,db_path,table)

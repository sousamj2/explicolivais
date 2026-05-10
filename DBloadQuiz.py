"""
This module handles loading quiz data from CSV files into a SQLite database.

NOTE: This module uses `sqlite3` and `pandas`, which is inconsistent with the
rest of the application's database helpers that use `pymysql` for MySQL.
This may be part of a legacy data loading process or a separate utility.
"""
import sqlite3
import pandas as pd
from glob import glob
from pathlib import Path

def loadQcsvFiles (pattern,db_path,table):
    """
    Loads data from multiple CSV files into a SQLite database table.

    This function finds all CSV files matching a specified glob pattern, then
    loads them into a single database table using pandas. The schema for the
    table is inferred from the columns of the first CSV file found. The data
    from all subsequent files is appended.

    Args:
        pattern (str): A glob pattern to match the CSV files to be loaded.
        db_path (str): The file path for the SQLite database.
        table (str): The name of the table to create and/or append data to.

    Raises:
        SystemExit: If no CSV files are found matching the pattern.
    """
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
    """
    Loads quiz answers from CSV files into the 'responses' table in 'quiz.db'.
    
    This function defines a specific pattern to find all answer-related CSV files
    and calls the generic `loadQcsvFiles` utility to load them.
    """
    # Expand your pattern into file paths
    base = Path().resolve()  # equivalent to $PWD
    pattern = str(base / "quiz-time" / "anos" / "ano*" / "*" / "*" / "an*.csv")
    db_path = "quiz.db"
    table = "responses"

    loadQcsvFiles(pattern,db_path,table)

def loadQlinks():
    """
    Loads quiz-related links from 'links.csv' into the 'links' table in 'quiz.db'.
    
    This function calls the generic `loadQcsvFiles` utility to load the main
    links file for the quiz.
    """
    # Expand your pattern into file paths
    base = Path().resolve()  # equivalent to $PWD
    pattern = str(base / "quiz-time" / "links.csv")
    db_path = "quiz.db"
    table = "links"
    loadQcsvFiles(pattern,db_path,table)

def loadQtemas():
    """
    Loads quiz themes from 'temas.csv' into the 'temas' table in 'quiz.db'.
    
    This function calls the generic `loadQcsvFiles` utility to load the main
    themes file for the quiz.
    """
    # Expand your pattern into file paths
    base = Path().resolve()  # equivalent to $PWD
    pattern = str(base / "quiz-time" / "temas.csv")
    db_path = "quiz.db"
    table = "temas"
    loadQcsvFiles(pattern,db_path,table)


def loadQaulas():
    """
    Loads quiz class/lesson data from 'aulas.csv' into the 'aulas' table in 'quiz.db'.
    
    This function calls the generic `loadQcsvFiles` utility to load the main
    'aulas' file for the quiz.
    """
    # Expand your pattern into file paths
    base = Path().resolve()  # equivalent to $PWD
    pattern = str(base / "quiz-time" / "aulas.csv")
    db_path = "quiz.db"
    table = "aulas"
    loadQcsvFiles(pattern,db_path,table)
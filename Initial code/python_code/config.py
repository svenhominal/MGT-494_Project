from pathlib import Path

# Base directory for this project (relative to the workspace root)
BASE_DIR = Path("EPFL/MA1/Economics for challenging times/Initial code").resolve()

# Paths mirroring Stata globals
DIRPATH = BASE_DIR  # `$dirpath` in Stata
STATA_DATA_DIR = DIRPATH / "stata_data"
TABLES_DIR = DIRPATH / "tables"
FIGURES_DIR = DIRPATH / "figures"
MATLAB_DATA_DIR = DIRPATH / "matlab_data"

# Raw data path (Stata `$datapath`)
# NOTE: This repository typically doesn't include raw files. Update if you have them locally.
DATAPATH = Path("/Volumes/Dades/Dropbox/DATA")  # customize as needed


def ensure_output_dirs():
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    MATLAB_DATA_DIR.mkdir(parents=True, exist_ok=True)


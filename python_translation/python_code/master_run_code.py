"""
Master script replicating `master_run_code.do`.

Runs the sequence of translated analyses to regenerate figures and tables.
"""

from __future__ import annotations

from analysis_passthrough_rf import main as passthrough_main
from analysis_internalization_str import main as internalization_main
from analysis_markups import main as markups_main
from analysis_rigidities import main as rigidities_main
from analysis_passthrough_robustness import main as robustness_main
from prelim_graphs import main as prelim_main


def main() -> None:
    """
    Execute all translated analysis scripts in order.
    """
    prelim_main() # Almost correct, only erate_hours doesn't quite the same
    passthrough_main()
    internalization_main()
    markups_main()
    rigidities_main()
    robustness_main()


if __name__ == "__main__":
    main()

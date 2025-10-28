from __future__ import annotations

"""
Master runner translating `master_run_code.do`.

Order:
1) Data clean-up / preliminaries (commented; requires raw data)
2) Summary figures (prelim_graphs)
3) Main analysis (pass-through, internalization, markups, rigidities)
4) Additional material (robustness)
"""

from config import ensure_output_dirs


def main():
    ensure_output_dirs()

    # 1) Data clean-up (requires raw data)
    # from . import data_create, data_create_demand, data_merge, data_create_matlab
    # data_create.main()
    # data_create_demand.main()
    # data_merge.main()
    # data_create_matlab.main()

    # 2) Summary figures
    import prelim_graphs
    prelim_graphs.main()

    # 3) Main analysis
    import analysis_passthrough_rf
    analysis_passthrough_rf.main()

    import analysis_internalization_str
    analysis_internalization_str.main()

    import analysis_markups
    analysis_markups.main()

    import analysis_rigidities
    analysis_rigidities.main()

    # 4) Additional material
    import analysis_passthrough_robustness
    analysis_passthrough_robustness.main()


if __name__ == "__main__":
    main()


# MGT-494 Project: Pass-through of Emissions Costs in Electricity Markets

**Course**: MGT-494 Economics for Challenging Times  
**Authors**: Sven Hominal, Julien Délez, Rose Schlageter   

## Overview

This project replicates and extends the analysis from:

> **Fabra, N., & Reguant, M. (2014).** *Pass-through of emissions costs in electricity markets.* American Economic Review, 104(9), 2872-2899.

The study examines how EU-ETS carbon prices affected Spanish electricity market prices during 2004-2007, analyzing cost pass-through, market power, and emissions internalization.

---

## Main File 

### [`main_replication_extension.ipynb`](main_replication_extension.ipynb)

This is the **main notebook** containing the complete replication and first extension analyses, in Python.

---

## Repository Structure

```
MGT-494_Project/
│
├── NOTEBOOKS
│   ├── main_replication_extension.ipynb  # Main Notebook for Replication and Extensions 
│   ├── causal_forest.ipynb               # Causal Forest 
│   ├── did.ipynb                         # DiD 
│   └── LSTM.ipynb                        # LSTM  
│
├── DATA & RESULTS
│   ├── DATA.md                           # Detailed data documentation
│   ├── predictions_2007.csv              # LightGBM Model predictions for 2007
│   │
│   ├── ml_tables_results/                # Machine learning results
│   │   ├── table1_2sls_results.csv
│   │   ├── table1_dml_results.csv
│   │   ├── table1_dml_*.tex              # LaTeX tables (RF, Lasso, GBoost)
│   │   ├── causalml_robustness_results.csv
│   │   └── dml_timeblocked_*.csv
│   │
│   ├── More_data/                        # Additional data sources
│   │   ├── from_paper_2013.csv
│   │   ├── prix_annuel_espagne.csv       
│   │   └── share-elec-by-source.csv      # From Our World in Data website
│   │
│   └── plots_png/                        # Generated plots
│       ├── event_study_ets.png
│       ├── event_study_plot.png
│       └── plot_*_by_col.png
│
├── ORIGINAL CODE (STATA & MATLAB)
│   └── Initial code/
│       ├── stata_code/                   # Stata do-files
│       │   ├── analysis_passthrough_rf.do
│       │   ├── analysis_markups.do
│       │   └── ...
│       │
│       ├── matlab_code/                  # MATLAB functions
│       │   ├── elasticityMarkupAnalysis.m
│       │   ├── marketClearing.m
│       │   └── ...
│       │
│       ├── stata_data/                   # Stata datasets (.dta)
│       ├── matlab_data/                  # Daily bidding data (CSV)
│       ├── figures/                      # Generated figures
│       ├── original_figures/             # Figures from the paper
│       └── tables/                       # Generated tables
│
├── STREAMLIT WEB APP (PRICE PREDICTOR)
│   └── price_predictor_app.py            # Streamlit price prediction web app
│
├── REFERENCES
│   └── papers/
│       └── fabra-reguant-2014-*.pdf      # Original paper and notes  
        └── fabra1.pdf                    # Second paper of same authors (2013)
│
├── CONFIGURATION
│   ├── requirements.txt                  # Python dependencies for the web app 
│   ├── .streamlit/                       # Streamlit config
│   └── src/                              # Helper modules for the streamlit web app 
│
└── README.md                             # This file
```

---

## Installation

```bash
# Clone the repository
git clone https://github.com/svenhominal/MGT-494_Project.git
cd MGT-494_Project

# Install dependencies (for Streamlit app)
pip install -r requirements.txt
```

---

## Key Analyses

| Analysis | File | Description |
|----------|------|-------------|
| **Main Replication** | `main_replication_extension.ipynb` | Full paper replication with IV regressions |
| **Double ML** | `ml_tables_results/` | Double Machine Learning extensions |
| **Causal Forest** | `casual_forest.ipynb` | Heterogeneous treatment effects |
| **DiD Analysis** | `did.ipynb` | Event study around ETS introduction |
| **LSTM Forecasting** | `LSTM.ipynb` | Neural network price predictions |
| **Streamlit App** | `price_predictor_app.py` | Interactive price predictor |

---

## Data Documentation

See [`DATA.md`](DATA.md) for detailed documentation of all datasets, including:
- `data_regressions_passthrough.dta` — Main pass-through regression data
- `data_regressions_structural.dta` — Structural internalization analysis
- Daily bidding curves in `matlab_data/`

---

## References

- Fabra, N., & Reguant, M. (2014). Pass-through of emissions costs in electricity markets. *American Economic Review*, 104(9), 2872-2899.
- Original replication package: [AEA Data Repository](https://www.aeaweb.org/articles?id=10.1257/aer.104.9.2872)

---  

### 21
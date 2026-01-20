# Data for Replication Project: Pass-through of Emissions Costs in Electricity Markets

**Paper**: Fabra, N., & Reguant, M. (2014). *Pass-through of emissions costs in electricity markets*. American Economic Review, 104(9), 2872-2899.


## 📊 Data Description

### 1. Stata Data Files (`Initial code/stata_data/`)

#### `data_regressions_passthrough.dta`
**Main dataset for pass-through regressions** — 30,648 rows × 45 columns

| Variable | Description |
|----------|-------------|
| `year`, `month`, `day`, `hour` | Time identifiers (2004-2007, hours 1-24) |
| `mg_price` | Market clearing price (€/MWh) |
| `eprice` | EU Allowance (carbon) price (€/ton CO2) |
| `coal`, `gas`, `brent` | Commodity prices (coal, natural gas, Brent oil) |
| `totalcost`, `totalcost2` | Total marginal cost and squared |
| `ecost`, `ecost2` | Emissions cost component (erate × eprice) |
| `erate` | Average emission rate (tons CO2/MWh) |
| `peak` | Peak hour dummy (1 = hours 8-20) |
| `rd` | Royal Decree period dummy |
| `temp`, `tempx`, `humid`, `windx` | Weather controls (temperature, max temp, humidity, wind) |
| `weekd` | Day of week (1-7) |
| `ym`, `yb`, `yq` | Year-month, year-bimonth, year-quarter identifiers |
| `*_peak`, `*_off` | Variables interacted with peak/off-peak dummies |

---

#### `data_regressions_structural.dta`
**Dataset for structural internalization analysis** — 9,349 rows × 25 columns

| Variable | Description |
|----------|-------------|
| `up` | Power plant unit identifier (e.g., "ABO1") |
| `year`, `month`, `day`, `hour` | Time identifiers |
| `price` | Bid price submitted (€/MWh) |
| `firm_code` | Firm identifier (1, 2, 3, or 4) |
| `mg_cost` | Marginal cost estimate (€/MWh) |
| `cost_CO2` | Carbon cost component |
| `markup` | Estimated markup = price - marginal cost |
| `pricehat` | Predicted price from model |
| `summer`, `winter`, `spring` | Season dummies |
| `summerw`, `winterw`, `springw` | Season × weekday interactions |
| `weekdays` | Weekday dummy |
| `temp`, `humid`, `windx`, `temperatura` | Weather variables |
| `id`, `firmday`, `firmym` | Panel identifiers |

---

#### `data_eua_prices.dta`
**EU Allowance price time series** — 2,191 rows × 4 columns

| Variable | Description |
|----------|-------------|
| `year`, `month`, `day` | Date identifiers |
| `eprice` | Daily EUA spot price (€/ton CO2) |

---

#### `passthrough_results.dta`
**MATLAB counterfactual simulation results** — 18,960 rows × 38 columns

Contains market outcomes under 3 scenarios: baseline (0), +€1 carbon (1), +€1 uniform (2)

| Variable | Description |
|----------|-------------|
| `year`, `month`, `day`, `hour` | Time identifiers |
| `price0`, `price1`, `price2` | Market clearing prices under each scenario |
| `pricea0`, `pricea1`, `pricea2` | Alternative price measures |
| `demand0`, `demand1`, `demand2` | Total demand (MWh) |
| `eratem` | Market average emission rate |
| `slope[1-4]_[0-2]` | Residual demand slope for firms 1-4 under each scenario |
| `qfirm[1-4]_[0-2]` | Quantity produced by firms 1-4 under each scenario |

---

#### `data_regressions_lite.dta`
**Detailed bid-level data** — 1,081,264 rows × 19 columns

| Variable | Description |
|----------|-------------|
| `up` | Unit identifier |
| `year`, `month`, `day`, `hour` | Time identifiers |
| `price` | Bid price (€/MWh) |
| `cummwh` | Cumulative MWh offered |
| `accepted`, `rejected` | Bid status dummies |
| `bilateral` | Bilateral contract indicator |
| `firm`, `firm_code` | Firm name and code |
| `fuel` | Fuel type |
| `eprice` | Carbon price |
| `cost_CO2` | Carbon cost |
| `mw`, `minmw` | Capacity (MW) |
| `erate` | Emission rate |
| `weekd` | Weekday |

---

### 2. MATLAB Data Files (`Initial code/matlab_data/`)

#### Daily Bidding CSV Files: `data_YYYYMMDD.csv`

**Sample**: 30 files from June 2005 (`data_20050601.csv` to `data_20050630.csv`)

Each file contains hourly supply bids from all generators for one day.

| Column | Type | Description |
|--------|------|-------------|
| `year` | int | Year (2005) |
| `month` | int | Month (6 = June) |
| `day` | int | Day of month (1-30) |
| `hour` | int | Hour of day (1-24) |
| `firm_code` | int | Anonymized firm ID (1, 2, 3, or 4) |
| `id` | int | Power plant unit ID (e.g., 1001, 1002, 1003) |
| `price` | float | Bid price (€/MWh) — 0 = baseload, 180.3 = price cap |
| `mwh` | float | Quantity offered at this price (MWh) |
| `erate` | float | Unit emission rate (tons CO2/MWh) |
| `direction` | int | 1 = demand bid, **2 = supply bid** |
| `accepted` | binary | 1 = bid accepted in market clearing |
| `rejected` | binary | 1 = bid rejected (for filtering) |
| `mg_cost` | float | Estimated marginal cost (€/MWh) |

**Example bid structure** (firm 1001, hour 1):
```
price=0,    mwh=180  → baseload (must-run) capacity
price=24.48, mwh=30  → first step of supply curve  
price=25.48, mwh=30  → second step
price=29.48, mwh=50  → third step
price=180.3, mwh=20  → capacity at price cap
```

---

#### `passthrough_results.csv`

**Output from MATLAB elasticity analysis** — same structure as `passthrough_results.dta`

Contains simulated market outcomes for counterfactual carbon price scenarios.

### 3. Output Tables (`Initial code/tables/`)

LaTeX tables containing regression results and summary statistics from the paper:

#### Pass-through Regression Tables

| Table | Description |
|-------|-------------|
| `table_cost_pt_base.tex` | **Main pass-through results (Table 2 in paper)**. IV regression of electricity prices on marginal emissions costs. Key finding: ρ ≈ 0.83-0.86, meaning ~85% pass-through. Controls: temperature, wind speed, coal/gas/oil prices. N=16,186 obs. |
| `table_cost_pt_first.tex` | **First-stage IV results**. Regresses marginal emissions costs on the EUA price instrument. Coefficient ≈ 0.57-0.59, showing strong relevance of the instrument. |
| `table_cost_pt_peak.tex` | **Peak vs Off-Peak analysis (Table 3)**. Separates pass-through by time of day: Peak hours (8am-8pm) show ρ ≈ 1.05-1.11 (full pass-through), Off-peak shows ρ ≈ 0.50-0.63 (incomplete). |
| `table_cost_pt_rd.tex` | **Extended sample including Royal Decree period**. Sample Jan 2004 - June 2007 (N=26,050). Pass-through coefficient drops to ρ ≈ 0.60-0.72 when including post-regulation period. |
| `table_cost_pt_additional.tex` | **Robustness with additional controls**. Adds quadratic input prices, temperature squared, wind speed trends. Pass-through remains stable at ρ ≈ 0.85-0.89. |
| `table_cost_pt_interpolated.tex` | **Robustness to emissions rate assumptions**. Compares results using interpolated vs. unit-specific vs. technology-based emission rates. All specifications yield ρ ≈ 0.80-0.92. |
| `table_cost_pt_peak_alternatives.tex` | Alternative peak hour definitions for robustness. |

#### Structural Analysis Tables

| Table | Description |
|-------|-------------|
| `table_internalization.tex` | **Structural internalization test (Table 4)**. Tests whether firms fully internalize carbon costs (γ=1) in their bidding. Results by firm: γ ranges from 0.78 (Firm 4) to 1.12 (Firm 3). Also reports input cost coefficients (β) and markup coefficients (θ). N≈9,257 obs. |
| `table_internalization_stderrors.tex` | Same as above with alternative standard error computation. |

#### Elasticity and Market Structure Tables

| Table | Description |
|-------|-------------|
| `table_elas.tex` | **Residual demand elasticity summary (Table 5)**. Reports firm-level elasticities (η) estimated from residual demand slopes. Firm 1: η≈1.8, Firm 2: η≈0.9, Firm 3: η≈6.6, Firm 4: η≈4.5. Estimated using Gaussian kernel (bandwidth=3€). |
| `table_qfirm.tex` | **Counterfactual quantity/markup changes (Table 6)**. Shows % changes in quantities, residual demand slopes, and markups for a €1 increase in carbon prices. Aggregate demand falls ~0.2%, firm markups decline 0.1-0.9%. |
| `tab_frequency.tex` | **Bid change frequency statistics**. Measures how often firms change their bids: 36% change day-to-day, 70% change week-to-week. Higher frequency on Mondays/Saturdays. |

#### Table File Types

- `.tex` files: LaTeX source code for tables (importable into papers)
- `.log` files: Stata log output from table generation

### 4. Output Figures (`Initial code/figures/`)

| Figure | Description |
|--------|-------------|
| `erate_hour.pdf/.eps` | Emission rates by hour of day |
| `prices_sample_reduced.pdf/.eps` | Sample electricity prices |

---

## 💻 Code Description

### Stata Code (`Initial code/stata_code/`)

| Script | Purpose |
|--------|---------|
| `master_run_code.do` | **Master script** - runs entire analysis pipeline |
| `data_create.do` | Raw data cleaning and preparation |
| `data_create_demand.do` | Demand-side data preparation |
| `data_merge.do` | Merge datasets |
| `data_create_matlab.do` | Prepare data for MATLAB analysis |
| `prelim_graphs.do` | Preliminary summary figures |
| `analysis_passthrough_rf.do` | Main pass-through reduced form regressions |
| `analysis_internalization_str.do` | Structural internalization analysis |
| `analysis_markups.do` | Markup estimation |
| `analysis_rigidities.do` | Price rigidity analysis |
| `analysis_passthrough_robustness.do` | Robustness checks |

### MATLAB Code (`Initial code/matlab_code/`)

| Script | Purpose |
|--------|---------|
| `elasticityMarkupAnalysis.m` | **Main script** - elasticity and markup computation |
| `marketClearing.m` | Market clearing algorithm (optimization) |
| `getResidualDemand.m` | Compute residual demand curves |
| `slopeResidualDemand.m` | Estimate residual demand slopes |

**Note**: MATLAB code requires IBM CPLEX solver for optimization.

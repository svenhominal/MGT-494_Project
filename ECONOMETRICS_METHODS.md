# Econometric Methods Guide

## Fabra, N., & Reguant, M. (2014). "Pass-through of Emissions Costs in Electricity Markets"
### American Economic Review, 104(9), 2872-2899

This document describes the econometric tools and methods used in the replication of each table and figure from the paper.

---

## Overview of Identification Strategy

The paper studies **cost pass-through** in the Spanish electricity market during the EU-ETS trial period (2004-2007). The main econometric challenge is that marginal costs are **endogenous** — they depend on the market equilibrium. The authors use the **EU Allowance (EUA) carbon price** as an **instrumental variable** because:

1. Carbon prices are set in a separate, EU-wide market (exogenous to Spanish electricity)
2. Carbon costs enter firms' marginal costs through the emission rate
3. The instrument is **relevant** (strong first-stage) and **excludable** (affects prices only through costs)

---

## Preliminary Figures

### Figure 1: CO₂ Prices and Electricity Prices (2004-2006)

**Method**: Descriptive time series visualization

**Econometrics**: None (purely descriptive)

**Purpose**: Shows the co-movement between EUA carbon prices and Spanish electricity prices during the sample period. This motivates the research question — do carbon costs pass through to electricity prices?

**Implementation**:
- Daily averages of market clearing price (`mg_price`)
- Daily EUA spot price (`eprice`)
- Simple line plot over time

---

### Figure 2: Marginal Emissions Rate by Hour of Day

**Method**: Cross-sectional summary statistics with confidence intervals

**Econometrics**: 
- Compute hourly means: $\bar{e}_h = \frac{1}{N_h} \sum_{t \in h} e_t$
- Standard errors: $SE_h = \frac{\sigma_h}{\sqrt{N_h}}$
- 95% confidence intervals: $\bar{e}_h \pm 1.96 \times SE_h$

**Purpose**: Documents that the marginal technology (and hence emission rate) varies systematically across hours. Peak hours have different emission rates than off-peak, which is key for the heterogeneous pass-through analysis.

**Economic interpretation**: Higher emission rates during peak hours suggest different marginal technologies (more gas/coal peakers vs. baseload).

---

## Table 1: Cost Pass-through Regression Results

**Paper Reference**: Table 2 in the published paper

### Econometric Model

**Reduced-form regression** with instrumental variables (2SLS):

$$P_t = \alpha + \rho \cdot (e_t \times p^{CO2}_t) + X_t'\beta + \gamma_m + \delta_h + \eta_w + \varepsilon_t$$

Where:
- $P_t$ = Market clearing price (€/MWh)
- $e_t \times p^{CO2}_t$ = Marginal emissions cost (emission rate × carbon price)
- $X_t$ = Control variables (weather, commodity prices)
- $\gamma_m, \delta_h, \eta_w$ = Month, hour, and weekday fixed effects
- $\rho$ = **Pass-through coefficient** (key parameter)

### Identification Strategy

**Endogeneity problem**: The marginal emissions cost $e_t \times p^{CO2}_t$ is endogenous because:
- The emission rate $e_t$ depends on which plants are marginal
- Which plants are marginal depends on the equilibrium price

**Instrumental variable**: Use $p^{CO2}_t$ (EUA price) as instrument for $e_t \times p^{CO2}_t$

**First-stage regression**:
$$e_t \times p^{CO2}_t = \pi_0 + \pi_1 \cdot p^{CO2}_t + X_t'\pi_2 + FE + u_t$$

**Relevance condition**: $\pi_1 \neq 0$ (carbon price predicts emissions cost)  
**Exclusion restriction**: Carbon price affects electricity price only through marginal costs

### Estimation Method

**Two-Stage Least Squares (2SLS)** with high-dimensional fixed effects:

1. **First stage**: Regress endogenous variable on instrument and controls
2. **Second stage**: Regress outcome on fitted values from first stage

**Software implementation**: `pyfixest` package with IV syntax:
```python
formula = 'mg_price ~ controls | FE | ecost2 ~ eprice'
```

### Specifications (5 columns)

| Spec | Month×Temp | Month×Hour FE | Hour×Input |
|------|------------|---------------|------------|
| (1)  | No         | No            | No         |
| (2)  | Yes        | No            | No         |
| (3)  | No         | Yes           | No         |
| (4)  | Yes        | Yes           | No         |
| (5)  | Yes        | Yes           | Yes        |

### Standard Errors

**Robust (heteroskedasticity-consistent)** standard errors (HC1/Eicker-Huber-White)

### Key Result

$\hat{\rho} \approx 0.83$ — approximately **83% pass-through** of carbon costs to electricity prices.

---

## Table 2: Peak vs. Off-Peak Pass-through

**Paper Reference**: Table 3 in the published paper

### Econometric Model

**Heterogeneous pass-through** by time of day:

$$P_t = \alpha + \rho_{peak} \cdot (e_t \times p^{CO2}_t) \times \mathbb{1}_{peak} + \rho_{off} \cdot (e_t \times p^{CO2}_t) \times \mathbb{1}_{off} + X_t'\beta + FE + \varepsilon_t$$

Where:
- $\mathbb{1}_{peak}$ = 1 if hour ∈ [8, 20], 0 otherwise
- $\mathbb{1}_{off}$ = 1 if hour ∉ [8, 20], 0 otherwise

### Instruments

Two instruments for two endogenous variables:
1. $p^{CO2}_t$ (carbon price)
2. $p^{CO2}_t \times \mathbb{1}_{peak}$ (carbon price interacted with peak dummy)

### Estimation

**2SLS with multiple endogenous variables**:
- First stage for `ecost2_peak`
- First stage for `ecost2_off`
- Second stage with both fitted values

### Key Result

- **Peak pass-through**: $\hat{\rho}_{peak} \approx 1.05$ (full or over-pass-through)
- **Off-peak pass-through**: $\hat{\rho}_{off} \approx 0.50$ (incomplete pass-through)

**Economic interpretation**: During peak hours, firms have more market power (steeper residual demand), allowing full cost pass-through. During off-peak, excess capacity limits pricing power.

---

## Table 3: Structural Internalization Test

**Paper Reference**: Table 4 in the published paper

### Economic Model

From Section III.A of the paper, the **first-order condition** for profit maximization implies:

$$P_{it} = MC_{it} + \mu_{it}$$

Where markup $\mu_{it} = \frac{q_{it}}{\partial D^r_i / \partial P}$ (Lerner condition)

The marginal cost decomposes as:
$$MC_{it} = \beta \cdot InputCost_{it} + \gamma \cdot CO2Cost_{it}$$

Under **full cost internalization**: $\gamma = \beta = 1$

### Econometric Specification

**Structural regression** (no constant, as in Stata `nocons`):

$$\hat{P}_{it} = \beta \cdot InputCost_{it} + \gamma \cdot CO2Cost_{it} + \theta \cdot Markup_{it} + \varepsilon_{it}$$

Where $\hat{P}_{it} = P_t - \mu_{it}$ is the "marginal cost predictor"

### Specifications

1. **No FE**: Pooled OLS without constant
2. **Unit FE**: Fixed effects by power plant
3. **Unit FE + Season**: Add seasonal controls
4. **Spec.3 + Markup (IV)**: Instrument markup with weather variables

### Estimation Details

**Spec 1-3**: OLS with no constant (`sm.OLS` without intercept)

**Spec 4**: 2SLS where markup is endogenous
- Instruments: temperature, wind speed, humidity
- Rationale: Weather affects demand elasticity, hence markups

### Clustering

Standard errors clustered at the **unit level** (power plant) to account for serial correlation

### Key Result

$\hat{\gamma} \approx 0.96$ — firms **fully internalize** carbon costs in their bidding (cannot reject $\gamma = 1$)

---

## Table 4: Counterfactual Quantity and Markup Changes

**Paper Reference**: Table 6 in the published paper

### Method

**Counterfactual simulation** using the structural model

### Computational Approach

1. **Baseline equilibrium** (observed): Solve market clearing with actual carbon price
2. **Counterfactual equilibrium**: Solve market clearing with carbon price + €1
3. **Compute changes**: 
   - $\Delta Q = \frac{Q_1 - Q_0}{Q_0} \times 100\%$
   - $\Delta \mu = \frac{\mu_1 - \mu_0}{\mu_0} \times 100\%$

### Market Clearing Algorithm

From MATLAB code (`marketClearing.m`):
- **Linear programming** to find equilibrium price and quantities
- Uses CPLEX solver for optimization
- Aggregates supply bids to construct supply curve
- Finds intersection with demand

### Summary Statistics

Report percentiles (P25, P50, P75) and moments (mean, SD) across all hours in sample

### Key Results

- Aggregate demand decreases ~0.2% for €1 carbon price increase
- Markups generally decrease (firms absorb some cost)
- Heterogeneous responses across firms

---

## Table 5: Emissions vs. Total Marginal Costs

**Paper Reference**: Table 5 in the published paper

### Econometric Model

Compare pass-through of **emissions costs only** vs. **total marginal costs**:

**Linear specification**:
$$P_t = \rho_{peak} \cdot Cost_{peak,t} + \rho_{off} \cdot Cost_{off,t} + X_t'\beta + FE + \varepsilon_t$$

**Log specification**:
$$\ln(P_t) = \rho_{peak} \cdot \ln(Cost_{peak,t}) + \rho_{off} \cdot \ln(Cost_{off,t}) + X_t'\beta + FE + \varepsilon_t$$

### Variables

| Cost measure | Description |
|--------------|-------------|
| `ecost2` | Emissions cost only ($e_t \times p^{CO2}_t$) |
| `totalcost2` | Total marginal cost (fuel + emissions) |

### Purpose

Test whether **emissions costs pass through differently** than other fuel costs. This addresses concerns that the carbon cost pass-through might be mechanical.

---

## Table 6: Frequency of Bid Changes

**Paper Reference**: Table 1 in the published paper

### Method

**Descriptive statistics** on bid rigidity/stickiness

### Variables Constructed

1. **adj1** (Previous day, unit-level):
   $$adj1_{it} = \mathbb{1}\{Price_{it} \neq Price_{i,t-1}\}$$
   
2. **adj3** (Previous week, unit-level):
   $$adj3_{it} = \mathbb{1}\{Price_{it} \neq Price_{i,t-7}\}$$
   
3. **adj5** (Firm-level):
   $$adj5_{ft} = \max_{i \in f} adj1_{it}$$

### Panel Data Construction

- Sort by unit-hour-day
- Use `groupby().shift()` for lagged comparisons
- Requires proper panel identification (as in Stata `xtset`)

### Key Finding

- ~37% of bids change day-to-day
- ~71% change week-to-week
- Higher change frequency on Mondays (after weekend information arrival)

---

## Figure 3: Inverse Residual Demand Curves

**Paper Reference**: Figure 3 in the published paper

### Economic Concept

**Residual demand** for firm $i$:
$$D^r_i(P) = D(P) - \sum_{j \neq i} S_j(P)$$

Where:
- $D(P)$ = Total market demand at price $P$
- $S_j(P)$ = Supply from firm $j$ at price $P$

**Inverse residual demand**: The price at which firm $i$ can sell quantity $Q$

### Computation Algorithm

For each price level $P$:
1. Compute total demand: $D(P) = \sum_{k: P_k \geq P} Q_k$ (demand bids willing to pay ≥ P)
2. Compute other supply: $S_{-i}(P) = \sum_{j \neq i} \sum_{k: P_{jk} \leq P} Q_{jk}$ (other firms' bids at ≤ P)
3. Residual demand: $D^r_i(P) = D(P) - S_{-i}(P)$

### Visualization

- **Step functions** (characteristic of bid-based markets)
- X-axis: Quantity (GWh)
- Y-axis: Price (€/MWh)
- Multiple curves for different days overlay

### Economic Interpretation

- **Downward-sloping**: Higher prices → less residual demand
- **Inelastic**: Steep curves indicate market power
- **Variation**: Different curves for different days show demand uncertainty

---

## Summary of Econometric Tools

| Method | Tables/Figures | Purpose |
|--------|---------------|---------|
| **2SLS (IV regression)** | Tables 1, 2, 3, 5 | Address endogeneity of costs |
| **High-dimensional FE** | Tables 1, 2, 5 | Control for time patterns |
| **Clustered SE** | Table 3 | Account for serial correlation |
| **Panel data methods** | Table 6 | Construct lagged comparisons |
| **LP optimization** | Table 4 | Market clearing simulation |
| **Step function construction** | Figure 3 | Residual demand visualization |

---

## Software Requirements

| Package | Purpose |
|---------|---------|
| `pyfixest` | IV regression with high-dimensional FE |
| `statsmodels` | OLS, standard errors |
| `scipy.optimize.linprog` | Linear programming (market clearing) |
| `pandas` | Data manipulation |
| `numpy` | Numerical computations |
| `matplotlib` | Visualization |

---

## Extension: LightGBM Price Forecasting

### Overview

As an extension to the econometric analysis, we implement a **machine learning approach** using **LightGBM** (Light Gradient Boosting Machine) to forecast hourly electricity prices. This complements the causal inference methods by providing:

1. **Predictive accuracy**: Out-of-sample price forecasting
2. **Feature importance**: Data-driven variable selection
3. **Non-linear relationships**: Captures complex interactions missed by linear models
4. **Model validation**: Cross-checks the importance of variables identified econometrically

---

### LightGBM Algorithm

**LightGBM** is a gradient boosting framework that uses tree-based learning algorithms. It is designed for efficiency and scalability.

#### Gradient Boosting Fundamentals

The model builds an **additive ensemble** of decision trees:

$$\hat{y}_i = \sum_{k=1}^{K} f_k(x_i), \quad f_k \in \mathcal{F}$$

Where:
- $K$ = number of trees (boosting rounds)
- $f_k$ = individual decision tree
- $\mathcal{F}$ = space of regression trees

#### Objective Function

At each iteration $t$, minimize:

$$\mathcal{L}^{(t)} = \sum_{i=1}^{n} l(y_i, \hat{y}_i^{(t-1)} + f_t(x_i)) + \Omega(f_t)$$

Where:
- $l(y, \hat{y}) = (y - \hat{y})^2$ (squared loss for regression)
- $\Omega(f) = \gamma T + \frac{1}{2}\lambda \|w\|^2$ (regularization on tree complexity)
- $T$ = number of leaves
- $w$ = leaf weights

#### LightGBM Innovations

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Gradient-based One-Side Sampling (GOSS)** | Keeps instances with large gradients, randomly samples small gradients | Faster training, maintains accuracy |
| **Exclusive Feature Bundling (EFB)** | Bundles mutually exclusive features | Reduces dimensionality |
| **Histogram-based splitting** | Buckets continuous features | Memory efficient, faster |
| **Leaf-wise tree growth** | Grows tree leaf-wise (vs. level-wise) | Better accuracy, risk of overfitting |

---

### Feature Engineering

#### 1. Temporal Features

Capture hourly, daily, and seasonal patterns in electricity prices:

| Feature | Formula | Rationale |
|---------|---------|-----------|
| `hour` | $h \in \{0, ..., 23\}$ | Demand cycle |
| `dayofweek` | $d \in \{0, ..., 6\}$ | Weekday/weekend patterns |
| `month` | $m \in \{1, ..., 12\}$ | Seasonal variation |
| `is_peak` | $\mathbb{1}\{8 \leq h \leq 20\}$ | Peak pricing |
| `is_weekend` | $\mathbb{1}\{d \geq 5\}$ | Demand reduction |

**Cyclical encoding** (avoids discontinuity at boundaries):
$$hour_{sin} = \sin\left(\frac{2\pi \cdot h}{24}\right), \quad hour_{cos} = \cos\left(\frac{2\pi \cdot h}{24}\right)$$

#### 2. Fuel and Carbon Cost Features

Direct inputs to marginal cost (validates econometric findings):

| Feature | Description | Expected Importance |
|---------|-------------|---------------------|
| `gas_d` | Daily gas price | High (marginal fuel) |
| `coal_d` | Daily coal price | High (baseload fuel) |
| `eprice` | Carbon allowance price | High (main paper focus) |
| `erate` | Marginal emission rate | Medium |
| `emissions_cost` | $e_t \times p^{CO2}_t$ | Very High |

#### 3. Weather Features

Affect both demand and supply:

| Feature | Mechanism |
|---------|-----------|
| `temp_d` | Temperature → heating/cooling demand |
| `wind_d` | Wind → renewable generation |
| `hydro_d` | Hydro availability → cheap supply |

#### 4. Lag Features (Autoregressive)

Capture price persistence and momentum:

$$P_{t-k} \text{ for } k \in \{1, 2, 3, 6, 12, 24, 48, 168\}$$

**Rolling statistics**:
$$\bar{P}_{t,w} = \frac{1}{w}\sum_{j=1}^{w} P_{t-j}, \quad \sigma_{t,w} = \sqrt{\frac{1}{w}\sum_{j=1}^{w}(P_{t-j} - \bar{P}_{t,w})^2}$$

For windows $w \in \{6, 12, 24, 48\}$ hours.

**Same-hour lags** (capture daily patterns):
- `price_same_hour_yesterday`: $P_{t-24}$
- `price_same_hour_lastweek`: $P_{t-168}$

---

### Model Specification

#### Hyperparameters

| Parameter | Value | Purpose |
|-----------|-------|---------|
| `objective` | `regression` | Minimize squared error |
| `boosting_type` | `gbdt` | Gradient boosting decision tree |
| `num_leaves` | 63 | Tree complexity (≤ $2^{max\_depth}$) |
| `max_depth` | 8 | Prevent overfitting |
| `learning_rate` | 0.05 | Step size shrinkage |
| `feature_fraction` | 0.8 | Column subsampling |
| `bagging_fraction` | 0.8 | Row subsampling |
| `lambda_l1` | 0.1 | L1 regularization (Lasso) |
| `lambda_l2` | 0.1 | L2 regularization (Ridge) |
| `min_child_samples` | 20 | Minimum leaf size |

#### Early Stopping

Training halts when validation metric doesn't improve for 50 rounds:
$$\text{Stop if } RMSE_{valid}^{(t)} \geq \min_{k < t} RMSE_{valid}^{(k)} \text{ for 50 consecutive } t$$

---

### Train/Test Split

**Time-based split** (respects temporal ordering):

$$\text{Train: } t \in [1, 0.8T], \quad \text{Test: } t \in (0.8T, T]$$

**Rationale**: Random splits would cause **data leakage** through lag features. A model could "see the future" if test observations precede training observations.

---

### Cross-Validation: Time Series Split

**K-fold with temporal ordering**:

```
Fold 1: Train [----] Test [--]
Fold 2: Train [------] Test [--]
Fold 3: Train [--------] Test [--]
Fold 4: Train [----------] Test [--]
Fold 5: Train [------------] Test [--]
```

Each fold:
1. Train on all data up to split point
2. Test on subsequent window
3. Ensures no future information leakage

---

### Evaluation Metrics

| Metric | Formula | Interpretation |
|--------|---------|----------------|
| **RMSE** | $\sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}$ | Penalizes large errors |
| **MAE** | $\frac{1}{n}\sum_{i=1}^{n}|y_i - \hat{y}_i|$ | Average absolute error |
| **MAPE** | $\frac{100}{n}\sum_{i=1}^{n}\left|\frac{y_i - \hat{y}_i}{y_i}\right|$ | Percentage error |
| **R²** | $1 - \frac{\sum(y_i - \hat{y}_i)^2}{\sum(y_i - \bar{y})^2}$ | Variance explained |

#### Baseline Comparison

**Naive forecast** (persistence model):
$$\hat{P}_t = P_{t-1}$$

Improvement over naive:
$$\text{Improvement} = \frac{RMSE_{naive} - RMSE_{model}}{RMSE_{naive}} \times 100\%$$

---

### Feature Importance Analysis

#### Gain-based Importance

Total reduction in loss attributed to feature $j$:
$$I_j^{gain} = \sum_{t=1}^{T} \sum_{splits \text{ on } j} \Delta \mathcal{L}_{split}$$

#### Split-based Importance

Number of times feature $j$ is used for splitting:
$$I_j^{split} = \sum_{t=1}^{T} \#\{\text{splits on feature } j \text{ in tree } t\}$$

#### SHAP Values (SHapley Additive exPlanations)

Game-theoretic approach to feature attribution:

$$\phi_j = \sum_{S \subseteq F \setminus \{j\}} \frac{|S|!(|F|-|S|-1)!}{|F|!} [f_{S \cup \{j\}}(x) - f_S(x)]$$

Where:
- $\phi_j$ = contribution of feature $j$ to prediction
- $S$ = subset of features
- $f_S(x)$ = model prediction using only features in $S$

**Property**: $\sum_j \phi_j = f(x) - E[f(x)]$ (contributions sum to deviation from mean)

---

### Recursive Multi-Step Forecasting

For forecasting beyond the dataset (where actual values are unavailable):

#### Algorithm

```
Input: Last 168 known prices, feature values for future dates
For h = 1 to H (forecast horizon):
    1. Construct feature vector X_{t+h}
    2. Fill lag features from price buffer:
       - lag_1 = buffer[-1]
       - lag_24 = buffer[-24]
       - etc.
    3. Predict: P̂_{t+h} = model.predict(X_{t+h})
    4. Append P̂_{t+h} to price buffer
    5. Compute confidence interval
Output: {P̂_{t+1}, ..., P̂_{t+H}} with confidence bands
```

#### Confidence Intervals

Based on historical residual standard deviation, widening with horizon:

$$CI_{t+h} = \hat{P}_{t+h} \pm z_{\alpha/2} \cdot \sigma_{resid} \cdot \left(1 + \frac{h}{2H}\right)$$

Where the multiplier $(1 + h/2H)$ accounts for **error accumulation** in recursive forecasting.

#### Feature Assumptions for Future Dates

| Feature Type | Assumption | Justification |
|--------------|------------|---------------|
| Temporal | Computed exactly | Known from calendar |
| Fuel prices | Last value (persistence) | Short-term stability |
| Weather | Monthly seasonal average | Climatological norms |
| Demand | Hourly pattern average | Regular daily cycle |
| Lag prices | Recursively updated | Model predictions |

---

### Connection to Econometric Analysis

#### Validation of Econometric Findings

| Econometric Result | ML Validation |
|--------------------|---------------|
| Carbon costs matter | `emissions_cost` high importance |
| Fuel costs drive prices | `gas_d`, `coal_d` important |
| Hourly heterogeneity | `hour`, `is_peak` important |
| Price persistence | Lag features dominate importance |

#### Complementary Insights

1. **Non-linearity**: LightGBM captures threshold effects (e.g., price spikes when capacity constrained)

2. **Interaction effects**: Tree splits naturally model interactions (e.g., high demand × low wind → high prices)

3. **Variable importance ranking**: Data-driven confirmation of which controls matter

#### Limitations vs. Econometrics

| Aspect | LightGBM | IV Regression |
|--------|----------|---------------|
| **Causal inference** | ❌ Correlation only | ✅ Causal with valid IV |
| **Prediction accuracy** | ✅ Optimized | ❌ Not the goal |
| **Interpretability** | ⚠️ Black box | ✅ Clear coefficients |
| **Out-of-sample** | ✅ Designed for | ❌ In-sample focus |
| **Policy counterfactuals** | ❌ Cannot simulate | ✅ Structural model |

---

### Implementation Summary

```python
# LightGBM Training
import lightgbm as lgb

params = {
    'objective': 'regression',
    'metric': ['rmse', 'mae'],
    'num_leaves': 63,
    'max_depth': 8,
    'learning_rate': 0.05,
    'feature_fraction': 0.8,
    'bagging_fraction': 0.8,
    'lambda_l1': 0.1,
    'lambda_l2': 0.1
}

model = lgb.train(
    params,
    train_data,
    num_boost_round=1000,
    valid_sets=[train_data, valid_data],
    callbacks=[lgb.early_stopping(50)]
)
```

---

### Software Requirements (ML Extension)

| Package | Purpose |
|---------|---------|
| `lightgbm` | Gradient boosting model |
| `scikit-learn` | Train/test split, metrics, CV |
| `shap` | Feature importance interpretation |
| `numpy` | Numerical operations |
| `pandas` | Feature engineering |

---

## References

- Fabra, N., & Reguant, M. (2014). Pass-through of emissions costs in electricity markets. *American Economic Review*, 104(9), 2872-2899.
- Angrist, J. D., & Pischke, J. S. (2009). *Mostly Harmless Econometrics*. Princeton University Press. (Chapter 4: IV methods)
- Wooldridge, J. M. (2010). *Econometric Analysis of Cross Section and Panel Data*. MIT Press. (Chapters 5, 8: Panel data, IV)
- Ke, G., et al. (2017). LightGBM: A Highly Efficient Gradient Boosting Decision Tree. *NIPS*.
- Lundberg, S. M., & Lee, S. I. (2017). A Unified Approach to Interpreting Model Predictions. *NIPS*. (SHAP values)
- Weron, R. (2014). Electricity price forecasting: A review of the state-of-the-art. *International Journal of Forecasting*, 30(4), 1030-1081.

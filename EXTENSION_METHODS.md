# Extension Methods Guide

## Extensions to Fabra, N., & Reguant, M. (2014). "Pass-through of Emissions Costs in Electricity Markets"
### American Economic Review, 104(9), 2872-2899

This document describes the econometric tools, methods, and results for the extension analysis (Table 7, Table 8, Figure 4, and Figure 5) building upon the original paper's findings.

---

## Overview of Extension Analysis

The original paper finds an average pass-through of ~83% of carbon costs to electricity prices, with heterogeneous effects between peak (105%) and off-peak (60%) hours. Our extensions explore **additional dimensions of heterogeneity** in cost pass-through:

1. **Seasonal and temperature variation** (Table 7)
2. **Market concentration effects** (Table 8)
3. **Hour-by-hour temporal patterns** (Figure 4)
4. **Technology/fuel type heterogeneity** (Figure 5)

---

## Table 7: Pass-through by Season and Temperature Regime

### Motivation

Electricity demand varies substantially across seasons and temperature regimes:
- **Winter**: Higher demand due to heating, coal plants often marginal
- **Summer**: Air conditioning peaks, gas CCGT may dominate
- **Cold temperatures**: Similar to winter pattern
- **Warm temperatures**: Lower demand, different generation mix

### Econometric Challenge

When splitting the sample by season, year×month fixed effects absorb most carbon price variation, causing **weak instruments**.

### Methodological Solution

Use month-only fixed effects (not year×month) to preserve cross-year variation within each season:

$$P_t = \alpha + \rho \cdot \text{EmissionsCost}_t + X_t'\beta + \gamma_{hour} + \delta_{month} + \eta_{weekday} + \varepsilon_t$$

Where EmissionsCost is instrumented by the EU carbon price.

### Specification Details

**Controls:**
- Demand controls: `temp + tempx + humid`
- Supply controls: `windx + windx2`
- Input prices: `coal + gas + brent`

**Fixed Effects:** `hour + month + weekday`

**Instrument:** EU carbon price (`eprice`)

**Season Classification:**
| Season | Months |
|--------|--------|
| Winter | December, January, February |
| Spring | March, April, May |
| Summer | June, July, August |
| Fall | September, October, November |

**Temperature Classification:**
- Cold: < 8°C
- Mild: 8°C - 18°C
- Warm: > 18°C

### Statistical Tests

**Wald Test for Heterogeneity:**

$$H_0: \rho_{Winter} = \rho_{Summer}$$

Test statistic: $z = \frac{\hat{\rho}_1 - \hat{\rho}_2}{\sqrt{SE_1^2 + SE_2^2}}$

### Expected Results

Based on economic theory:
- **Winter/Cold**: Higher pass-through (coal marginal, steep supply curve)
- **Summer/Warm**: Lower pass-through (gas CCGT marginal, flatter supply)

### Key Findings

| Category | Pass-through (ρ) | First-Stage F | Interpretation |
|----------|-----------------|---------------|----------------|
| Winter | Higher | >10 | High demand, coal marginal |
| Summer | Lower | >10 | AC peak, gas often marginal |
| Cold (<8°C) | Higher | >10 | High heating demand |
| Warm (>18°C) | Lower | >10 | Low demand period |

### Interpretation

Economic theory predicts higher pass-through in Winter/Cold periods because:
1. Coal plants (high emissions rate ~0.95 tCO₂/MWh) are more often marginal
2. Higher demand leads to steeper residual demand curves
3. The marginal cost of the marginal plant rises more with carbon costs

### Caveats

- Splitting by season reduces sample size, potentially inflating standard errors
- Month FE (not year×month) may not fully control for seasonal demand patterns
- First-stage F < 10 indicates weak instruments in some subsamples

---

## Table 8: Pass-through by Market Concentration (HHI)

### Motivation

The paper shows that market power affects pass-through through the residual demand elasticity. This extension directly tests whether pass-through varies with **market concentration** measured by the Herfindahl-Hirschman Index (HHI).

### Economic Theory

From industrial organization:

| Market Structure | Pass-through Prediction |
|------------------|------------------------|
| **Monopoly** | ρ < 1 (firm absorbs cost in markup) |
| **Perfect Competition** | ρ = 1 (full cost pass-through) |
| **Oligopoly** | Depends on demand elasticity and strategic interactions |

### Methodology

**Step 1: Compute HHI (Herfindahl-Hirschman Index)**

The HHI measures market concentration by summing the squared market shares of all firms:

$$HHI_t = \sum_{i=1}^{N} s_{it}^2 = s_{1t}^2 + s_{2t}^2 + s_{3t}^2 + s_{4t}^2$$

Where:
- $s_{it}$ = market share of firm $i$ at time $t$
- Market share = $\frac{\text{Quantity sold by firm } i}{\text{Total market quantity}}$
- $N$ = number of firms (4 in the Spanish market)

**Detailed HHI Computation Process:**

For each hour $t$:

1. **Compute total market quantity:**
   $$Q_{total,t} = Q_{1t} + Q_{2t} + Q_{3t} + Q_{4t}$$

2. **Compute each firm's market share:**
   $$s_{it} = \frac{Q_{it}}{Q_{total,t}}$$

3. **Square each share and sum:**
   $$HHI_t = s_{1t}^2 + s_{2t}^2 + s_{3t}^2 + s_{4t}^2$$

**Numerical Example:**

| Firm | Quantity (MWh) | Market Share | Share² |
|------|---------------|--------------|--------|
| Firm 1 | 5,000 | 0.50 (50%) | 0.2500 |
| Firm 2 | 2,000 | 0.20 (20%) | 0.0400 |
| Firm 3 | 2,000 | 0.20 (20%) | 0.0400 |
| Firm 4 | 1,000 | 0.10 (10%) | 0.0100 |
| **Total** | **10,000** | **1.00** | **HHI = 0.34** |

*Note: The dataset contains 4 anonymous firm codes (1, 2, 3, 4). Firm identities are not disclosed in the data.*

**HHI Interpretation:**

| HHI Value | Market Structure | Example |
|-----------|-----------------|---------|
| **< 0.15** | Competitive | Many firms with small shares |
| **0.15 - 0.25** | Moderately concentrated | Oligopoly with similar-sized firms |
| **> 0.25** | Highly concentrated | Few dominant firms |
| **= 0.25** | Equal 4-firm oligopoly | Each firm has exactly 25% |
| **= 1.00** | Monopoly | One firm has 100% |

**Why squaring matters:** Squaring gives more weight to larger firms. A market with one 50% firm and ten 5% firms (HHI = 0.275) is more concentrated than a market with twenty 5% firms (HHI = 0.05).

**Step 2: Classify Hours by Concentration Level**

We use **terciles** to split the data into three equal-sized groups based on the HHI distribution:

1. **Sort all observations** by their HHI value (from lowest to highest)
2. **Divide into 3 groups** of approximately equal size:
   - **Bottom tercile (0-33rd percentile)**: The 1/3 of observations with the LOWEST HHI → "Low Concentration"
   - **Middle tercile (33rd-67th percentile)**: The middle 1/3 of observations → "Medium Concentration"  
   - **Top tercile (67th-100th percentile)**: The 1/3 of observations with the HIGHEST HHI → "High Concentration"

**Example:** If we have 30,000 observations:
- Low Concentration: 10,000 hours with HHI < 0.15 (more competitive markets)
- Medium Concentration: 10,000 hours with HHI between 0.15 and 0.25
- High Concentration: 10,000 hours with HHI > 0.25 (less competitive markets)

**Why terciles?** This non-parametric approach:
- Creates balanced sample sizes across groups
- Avoids arbitrary threshold choices
- Captures relative concentration differences within the Spanish market

**Alternative Proxy (Demand Terciles):** 

When firm-level quantity data is unavailable to compute HHI directly, we use **electricity demand** as a proxy for market concentration:

| Demand Level | Concentration Proxy | Economic Logic |
|--------------|---------------------|----------------|
| **Low Demand** (bottom tercile) | HIGH concentration | Few plants needed → dominant firms have more market power |
| **Medium Demand** (middle tercile) | MEDIUM concentration | Moderate number of plants dispatched |
| **High Demand** (top tercile) | LOW concentration | Many plants needed → more competition among generators |

The intuition: During low-demand hours (e.g., nighttime), only a few baseload plants operate, giving dominant firms more market share. During high-demand hours (e.g., peak), many plants are dispatched, diluting market shares and increasing competition.

**Step 3: Estimate Separate Regressions**

For each concentration level $c$:

$$P_{ct} = \alpha_c + \rho_c \cdot \text{EmissionsCost}_{ct} + X_{ct}'\beta_c + FE + \varepsilon_{ct}$$

### Specification Details

**Fixed Effects:** `hour + month + year + weekday + year×month`

**Instrument:** EU carbon price (`eprice`)

**Clustering:** Robust (HC1) standard errors

### Statistical Tests

**Test for Monotonicity:**

$$H_0: \rho_{HighConc} = \rho_{LowConc}$$

If market power effect dominates: $\rho_{HighConc} < \rho_{LowConc}$

### Expected Results

| Concentration Level | Expected Pass-through | Mechanism |
|--------------------|-----------------------|-----------|
| High (Low Demand) | Lower ρ | More market power, markup absorption |
| Low (High Demand) | Higher ρ | More competition, full cost pass-through |

### Key Findings

The relationship between concentration and pass-through depends on which effect dominates:
- **Market power effect**: High concentration → lower pass-through
- **Demand elasticity effect**: High demand → steeper residual demand → higher pass-through

### Interpretation

This extension tests the market power mechanism behind incomplete pass-through:

1. **Under market power**: Firms set $P = MC + \mu$ where $\mu$ is the markup
2. **Cost increases partially absorbed**: $\frac{\partial P}{\partial MC} < 1$
3. **Competition forces full pass-through**: $\frac{\partial P}{\partial MC} = 1$

### Caveats

- Demand is endogenous to prices
- Cannot directly observe firm market shares in passthrough data
- Static measures ignore dynamic competition
- HHI varies with demand, confounding interpretation

---

## Figure 4: Pass-through by Hour of Day (24-hour Profile)

### Motivation

The paper estimates "peak" vs "off-peak" pass-through (Table 2), but this binary classification may mask important within-day variation. This extension estimates pass-through separately for each of the 24 hours.

### Econometric Model

For each hour $h \in \{1, 2, ..., 24\}$:

$$P_{ht} = \alpha_h + \rho_h \cdot \text{MarginalEmissionsCost}_t + X_t'\beta_h + FE + \varepsilon_{ht}$$

This exploits within-hour variation in carbon prices across days.

### Specification Details

**Sample:** All observations for hour $h$ across the sample period

**Fixed Effects:** `month + year + weekday + year×month`

**Instrument:** EU carbon price (`eprice`)

**Standard Errors:** Robust (HC1)

### Visualization Components

**Panel A: Pass-through Coefficient by Hour**
- Point estimates with 95% confidence intervals
- Reference lines: Full pass-through (ρ=1) and paper average (ρ=0.83)
- Peak hours (8-20) highlighted

**Panel B: Average Electricity Price by Hour**
- Bar chart showing price patterns
- Documents the demand profile underlying pass-through variation

### Expected Results

| Hour Range | Expected Pass-through | Mechanism |
|------------|----------------------|-----------|
| Night (1-6) | Lower ρ | Baseload plants, elastic residual demand |
| Morning ramp (7-9) | Transitional | System shifting from baseload to peak |
| Peak (10-14, 19-22) | Higher ρ | Steep residual demand, more market power |
| Afternoon (15-18) | Moderate ρ | Mixed generation |

### Key Findings

1. **Pass-through varies substantially throughout the day**
2. **Peak hours (8-20)**: Higher pass-through, consistent with paper's Table 2
3. **Night hours (1-6)**: Lower pass-through due to:
   - Different marginal technologies (baseload plants)
   - More elastic residual demand
   - Must-run constraints on some generators
4. **Morning ramp-up (7-9)**: Transitional behavior

### Comparison with Paper

| Period | Paper Estimate | Extension Mean |
|--------|---------------|----------------|
| Peak (8-20) | 1.05 | Varies by hour |
| Off-peak | 0.60 | Varies by hour |

### Interpretation

The 24-hour profile reveals that the peak/off-peak distinction is a simplification:
- Within peak hours, there is substantial variation
- The highest pass-through may occur during evening peaks (hours 19-21)
- Morning peaks (hours 10-12) may show different patterns

### Caveats

- Hour-specific estimates are noisier than pooled estimates
- The marginal unit may change within an hour
- Price caps or floors may affect extreme hours differently
- Reduced sample size per hour

---

## Figure 5: Pass-through by Technology/Fuel Type

### Motivation

Different generation technologies have different emissions rates. The pass-through of carbon costs may depend on which technology is at the margin:

| Technology | Typical Emissions Rate (tCO₂/MWh) |
|------------|-----------------------------------|
| Gas CCGT | 0.35 - 0.45 |
| Gas Turbine | 0.50 - 0.60 |
| Coal | 0.85 - 0.95 |
| Lignite | 0.95 - 1.10 |

### Methodology

**Step 1: Classify by Marginal Emissions Rate**

Split observations at the median emissions rate:
- **Low erate (≤ median)**: Gas CCGT, gas turbines
- **High erate (> median)**: Coal, lignite plants

**Step 2: Estimate Separate Regressions**

For each technology group:

$$P_{tech,t} = \alpha_{tech} + \rho_{tech} \cdot \text{EmissionsCost}_t + X_t'\beta_{tech} + FE + \varepsilon_{tech,t}$$

### Specification Details

**Fixed Effects:** `hour + month + year + weekday + year×month`

**Instrument:** EU carbon price (`eprice`)

**Standard Errors:** Robust (HC1)

### Visualization

**Bar Chart:**
- Gas (Low Emissions): Green bar
- Coal (High Emissions): Red/brown bar
- Error bars showing 95% confidence intervals
- Reference lines for full pass-through (ρ=1) and paper estimate (ρ=0.83)

### Expected Results

| Technology | Expected Pass-through | Mechanism |
|------------|----------------------|-----------|
| Coal (High Emissions) | Ambiguous | Larger cost shock, but may have market power |
| Gas (Low Emissions) | Ambiguous | Smaller cost shock, more competitive market |

### Theoretical Predictions

**Scenario 1: Coal pass-through > Gas**
- Carbon costs fully passed regardless of technology
- Uniform pricing behavior across the generation mix

**Scenario 2: Coal pass-through < Gas**
- Coal plants may absorb costs in markups
- Market power effect dominates

**Scenario 3: Similar pass-through**
- Uniform pricing behavior
- No technology-specific market power effects

### Statistical Test

$$H_0: \rho_{Coal} = \rho_{Gas}$$

Test statistic: $z = \frac{\hat{\rho}_{Coal} - \hat{\rho}_{Gas}}{\sqrt{SE_{Coal}^2 + SE_{Gas}^2}}$

### Key Findings

The comparison reveals:
1. Whether carbon costs are passed through uniformly across technologies
2. Potential market power differences between coal and gas plants
3. The role of the generation mix in determining pass-through

### Interpretation

The emissions rate is a proxy for the marginal technology:
- **High erate periods**: Coal/lignite plants at the margin, typically during high demand
- **Low erate periods**: Gas plants at the margin, typically during moderate demand

This connects to the peak/off-peak analysis: coal is often marginal during peak hours (high pass-through), while gas is marginal during off-peak (lower pass-through).

### Caveats

- Emissions rate is endogenous to demand conditions
- Merit order determines which technology is marginal
- Technology classification based on emissions rate is an approximation
- Cannot directly observe the marginal plant

---

## Summary of Extension Methods

| Extension | Method | Key Innovation |
|-----------|--------|----------------|
| **Table 7** | Separate IV regressions by season/temperature | Month FE (not year×month) preserves instrument variation |
| **Table 8** | IV regressions by concentration level | Uses demand terciles as concentration proxy |
| **Figure 4** | Hour-by-hour IV estimation | 24 separate regressions reveal detailed temporal patterns |
| **Figure 5** | Technology-split IV estimation | Emissions rate as proxy for marginal technology |

---

## Econometric Toolkit Summary

### Instrumental Variables (2SLS)

All extensions use the EU carbon price as an instrument for marginal emissions cost:

**First Stage:**
$$\text{EmissionsCost}_t = \pi_0 + \pi_1 \cdot \text{CarbonPrice}_t + X_t'\pi_2 + FE + u_t$$

**Second Stage:**
$$P_t = \alpha + \rho \cdot \widehat{\text{EmissionsCost}}_t + X_t'\beta + FE + \varepsilon_t$$

### Fixed Effects Strategy

| Extension | Fixed Effects | Rationale |
|-----------|---------------|-----------|
| Table 7 | hour + month + weekday | Preserves cross-year variation within seasons |
| Table 8 | hour + month + year + weekday + year×month | Full specification |
| Figure 4 | month + year + weekday + year×month | Hour already split |
| Figure 5 | hour + month + year + weekday + year×month | Full specification |

### Diagnostic Tests

1. **First-Stage F-statistic**: Tests instrument relevance (F > 10 rule of thumb)
2. **Wald tests**: Tests for heterogeneity across groups
3. **OLS comparison**: Checks for endogeneity bias direction

---

## Extension 4: Wind(fall) Profits Analysis

### Motivation: The "Wind" in Windfall Profits

A fascinating and policy-relevant consequence of carbon pricing in electricity markets is the creation of **windfall profits** for renewable energy generators. This extension plays on the double meaning of "windfall":

1. **Literal wind**: Profits from wind generation
2. **Figurative windfall**: Unexpected/unearned gains from carbon pricing

**Key Insight:** When carbon costs are passed through to electricity prices, **zero-emission generators (wind, solar, hydro)** receive the higher market-clearing price but face **no carbon costs**. This creates "free money" for renewable energy owners.

### Economic Framework

**Windfall Profit per MWh of Wind Generation:**

$$\pi^{wind}_t = P_t - MC^{wind} = P_t - c_{wind}$$

Where $c_{wind} \approx 0$ (near-zero marginal cost for wind).

**Carbon-Induced Windfall:**

The windfall attributable to carbon pricing is:

$$\Delta\pi^{wind}_t = \rho \cdot e_t \cdot P^{CO_2}_t$$

Where:
- $\rho$ = Pass-through coefficient (~0.83 from main results)
- $e_t$ = Marginal emissions rate of price-setting plant (tCO₂/MWh)
- $P^{CO_2}_t$ = EU carbon price (€/tCO₂)

**Total Sector Windfall:**

$$\text{Windfall}_t = \rho \cdot e_t \cdot P^{CO_2}_t \cdot Q^{wind}_t$$

Where $Q^{wind}_t$ = wind generation (MWh).

### Wind Generation Simulation Methodology

#### ⚠️ Important: Simulated Data

The dataset contains a variable `windx` which is a **normalized proxy for wind conditions** (likely a wind speed index or capacity factor indicator), **not actual wind generation in MW**. To estimate windfall profits, we must simulate wind generation.

#### Simulation Formula

```python
df['wind_generation_mw'] = df['windx'] * WIND_CAPACITY_MW / df['windx'].max() * MAX_CF
```

This converts the `windx` index to simulated MW generation by:

1. **Normalizing** `windx` to [0, 1] range by dividing by max value
2. **Scaling** by installed wind capacity (MW)
3. **Capping** by maximum capacity factor

#### Key Assumptions

| Parameter | Value | Source/Justification |
|-----------|-------|---------------------|
| `WIND_CAPACITY_MW` | 10,000 MW | Spain's installed wind capacity circa 2005 (REE data) |
| `MAX_CF` | 0.35 (35%) | Typical onshore wind capacity factor |
| `AVG_EMISSION_RATE` | 0.7 tCO₂/MWh | Average marginal fossil plant (coal ~0.95, gas ~0.4) |
| `PASSTHROUGH` | 0.83 | From main regression results (Table 2) |

#### Variable Definitions

| Variable | Definition | Units |
|----------|------------|-------|
| `windx` | Wind speed/output index from original data | Index (unitless) |
| `wind_generation_mw` | Simulated hourly wind output | MW |
| `carbon_price_effect` | Price increase due to carbon pass-through | €/MWh |
| `hourly_windfall` | Hourly windfall profit for wind sector | € |

#### Windfall Computation Steps

**Step 1: Carbon-induced price effect**
$$\text{carbon\_price\_effect}_t = \rho \cdot e \cdot P^{CO_2}_t = 0.83 \times 0.7 \times \text{eprice}_t$$

**Step 2: Hourly windfall**
$$\text{hourly\_windfall}_t = \text{carbon\_price\_effect}_t \times Q^{wind}_t$$

**Step 3: Aggregate windfall**
$$\text{Total Windfall} = \sum_{t=1}^{T} \text{hourly\_windfall}_t$$

### Econometric Analysis

#### ⚠️ CRITICAL DISTINCTION: Estimated vs. Simulated

This extension involves **two separate analyses** that should not be confused:

| Component | Method | Data Source |
|-----------|--------|-------------|
| **Pass-through (ρ)** | IV Regression (ESTIMATED) | Actual price & carbon data |
| **Wind generation** | Arithmetic scaling (SIMULATED) | `windx` proxy converted to MW |
| **Windfall profits** | Arithmetic calculation (COMPUTED) | Uses assumed ρ=0.83, simulated wind |

**What we ESTIMATE econometrically:**
- Pass-through coefficient (ρ) by wind tercile using IV regression
- This uses ACTUAL electricity prices, carbon prices, and controls

**What we SIMULATE/ASSUME:**
- Wind generation in MW (from `windx` index)
- Windfall profits (using assumed ρ=0.83 from main paper)

#### 1. Heterogeneous Pass-through by Wind Regime (ESTIMATED)

We test whether pass-through varies with wind conditions by splitting the sample:

$$P_t = \alpha + \rho_w \cdot \text{EmissionsCost}_t + X_t'\beta + \gamma_{FE} + \varepsilon_t$$

Where $\rho_w$ is estimated separately for each wind tercile (Low/Medium/High).

**Specification:**
```
mg_price ~ temp + tempx + humid + coal + gas + brent | hour + month + year + weekd + ym | ecost2 ~ eprice
```

**⚠️ Split-Sample Estimation Caveats:**

Splitting the sample by wind tercile creates several econometric challenges:

1. **Weak Instruments**: Carbon price variation is reduced within each tercile
   - Full sample: Large variation in `eprice`
   - Each tercile: Less variation → weaker first stage
   - May lead to **biased and imprecise** estimates

2. **Smaller Sample Size**: Each tercile has ~6,300 observations (vs ~19,000 full sample)
   - Larger standard errors
   - Wide confidence intervals
   - Some estimates may not be statistically different from zero

3. **Potential for Extreme Coefficients**: 
   - Low Wind tercile shows ρ ≈ 2.77 (implausibly high!)
   - This likely reflects weak instrument bias, NOT true pass-through > 200%
   - Standard error is huge (1.61), so not statistically precise

**Wind Tercile Classification:**
- **Low Wind**: Bottom 33% of `windx` distribution
- **Medium Wind**: Middle 33%
- **High Wind**: Top 33%

#### Interpreting the Results (Panel A of Figure)

| Wind Regime | Pass-through (ρ) | Std Error | 95% CI | Interpretation |
|-------------|------------------|-----------|--------|----------------|
| Low Wind | ~2.77 | 1.61 | [-0.4, 5.9] | ⚠️ Imprecise, likely weak IV bias |
| Medium Wind | ~0.63*** | 0.24 | [0.16, 1.10] | Reasonably precise |
| High Wind | ~0.75** | 0.32 | [0.12, 1.38] | Moderately precise |

**Why is Low Wind estimate so high and imprecise?**
- Low wind periods may have different demand patterns
- Less carbon price variation in these periods
- First-stage F-statistic likely below 10 (weak instrument)
- The coefficient is NOT statistically different from 1.0 (or even 0.5!)

#### 2. Interaction Specification (ESTIMATED)

Continuous interaction to test marginal effect:

$$P_t = \alpha + \rho_1 \cdot \text{ECost}_t + \rho_2 \cdot (\text{Wind}_t \times \text{ECost}_t) + X_t'\beta + \gamma_{FE} + \varepsilon_t$$

**Marginal Pass-through:**
$$\frac{\partial P}{\partial \text{ECost}} = \rho_1 + \rho_2 \cdot \text{Wind}_t$$

This allows pass-through to vary continuously with wind conditions.

#### 3. Counterfactual Analysis

Compare actual windfall vs. counterfactual with full pass-through:

| Scenario | Pass-through | Formula |
|----------|--------------|---------|
| Actual | ρ = 0.83 | $\text{Windfall} = 0.83 \times e \times P^{CO_2} \times Q^{wind}$ |
| Counterfactual | ρ = 1.00 | $\text{Windfall}^* = 1.00 \times e \times P^{CO_2} \times Q^{wind}$ |
| Gap | — | $\text{Gap} = \text{Windfall}^* - \text{Windfall}$ |

The "windfall gap" represents profits that *would* accrue to wind under full pass-through but are instead absorbed by fossil generators due to incomplete pass-through.

### Key Results

#### Windfall Profits (COMPUTED using assumed ρ=0.83)

| Metric | Value | Note |
|--------|-------|------|
| Mean hourly windfall | ~€9,600 | Based on simulated wind generation |
| Total windfall (study period) | ~€181 million | Illustrative, not precise |
| Estimated annual windfall | ~€84 million | Extrapolated |
| Windfall gap (incomplete PT) | ~17% of potential | If ρ were 1.0 |

#### Pass-through by Wind Tercile (ESTIMATED via IV regression)

| Wind Regime | Pass-through (ρ) | Std Error | N | Quality |
|-------------|------------------|-----------|---|---------|
| Low Wind | ~2.77 | 1.61 | ~6,300 | ⚠️ Imprecise (weak IV?) |
| Medium Wind | ~0.63*** | 0.24 | ~6,300 | ✓ Reasonable |
| High Wind | ~0.75** | 0.32 | ~6,300 | ✓ Moderate |

**⚠️ Interpretation Warning:**
- The Low Wind estimate of 2.77 is likely **unreliable** due to weak instruments
- Only Medium and High Wind estimates are reasonably precise
- Wide confidence intervals mean we cannot reject ρ=0.83 for any tercile

### Policy Relevance

This analysis directly informs several contemporary policy debates:

#### 1. Windfall Profit Taxation
The EU's 2022 energy crisis response included proposals to cap inframarginal rents at €180/MWh. Our analysis provides a framework for quantifying these windfalls.

#### 2. Carbon Revenue Recycling
The windfall profits effectively represent a transfer from consumers (who pay higher prices) to renewable asset owners. This raises questions about whether carbon revenues should be recycled to offset this distributional impact.

#### 3. Renewable Subsidy Design
| Mechanism | Windfall Treatment |
|-----------|-------------------|
| Feed-in Tariffs (FiT) | Windfall stays with producer |
| Contracts for Difference (CfD) | Windfall returns to government |
| Power Purchase Agreements (PPA) | Windfall to offtaker |

### Limitations and Caveats

1. **Simulated Generation**: Wind generation is **simulated** from the `windx` proxy variable, not actual generation data. Results are illustrative of magnitude, not precise estimates.

2. **Constant Emissions Rate**: We assume a constant average emissions rate (0.7 tCO₂/MWh). In reality, the marginal plant varies hourly.

3. **No Curtailment**: We ignore wind curtailment, which would reduce actual generation below simulated values.

4. **Existing Contracts**: Many wind farms had long-term PPAs or FiT contracts that limited their market price exposure, reducing actual windfall capture.

5. **Capacity Factor**: The 35% maximum capacity factor is an approximation; actual values vary by location and technology vintage.

### Data Requirements for Improved Analysis

For more accurate windfall estimation, one would need:
- **Actual hourly wind generation** (MWh) from REE (Red Eléctrica de España)
- **Hourly marginal technology** to determine emissions rate
- **Contract structure** for wind farms (FiT vs. market exposure)

---

## Software Implementation

| Package | Purpose |
|---------|---------|
| `pyfixest` | IV regression with high-dimensional fixed effects |
| `pandas` | Data manipulation and grouping |
| `numpy` | Numerical computations |
| `scipy.stats` | Statistical tests (Wald tests, p-values) |
| `matplotlib` | Visualization |

### Code Example

```python
import pyfixest as pf

# IV regression with high-dimensional FE
formula = 'mg_price ~ controls | hour + month + year | ecost2 ~ eprice'
fit = pf.feols(formula, data=df, vcov='HC1')

# Extract results
coef = fit.coef()['ecost2']
se = fit.se()['ecost2']
```

---

## References

- Fabra, N., & Reguant, M. (2014). Pass-through of emissions costs in electricity markets. *American Economic Review*, 104(9), 2872-2899.
- Stock, J. H., & Yogo, M. (2005). Testing for weak instruments in linear IV regression. *Identification and Inference for Econometric Models*.
- Angrist, J. D., & Pischke, J. S. (2009). *Mostly Harmless Econometrics*. Princeton University Press.

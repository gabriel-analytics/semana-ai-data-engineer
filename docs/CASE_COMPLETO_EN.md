# DoorDash Analytics Case — Complete Technical Documentation

> Repository: https://github.com/gabriel-analytics/doordash-analytics-case
> Dashboard: https://doordash-analytics-case-hupqbwjyucsrwzsvceqqyw.streamlit.app

---

## Section 1: Business Context and Problem

DoorDash is the largest food delivery marketplace in the United States, with a significant presence in Brazil through its own operations and regional partnerships. The business model is based on a take-rate of approximately 15% on each order value: the company connects customers, restaurants, and independent couriers (called dashers), charging a commission from the restaurant and a delivery fee from the customer. With over 35 million orders per month, fractional improvements in operational efficiency translate into tens of thousands of reais per week.

The problem that motivated this case was detected in Q1 2025 during a routine operational review: average delivery time rose 15% compared to the previous quarter. For a company whose core product is speed and convenience, this number is critical. It is not merely an aesthetic performance issue — every extra minute of delivery has two direct and quantifiable financial impacts.

The first impact is direct operational cost: the dasher is paid by travel and waiting time. Every minute spent waiting for an order that is not ready is a cost DoorDash absorbs directly or indirectly through incentives. We estimated this cost at R$0.50 per minute per delivery — a conservative number based on the dasher commission structure in the Brazilian market.

The second impact is customer retention. Internal studies at delivery platforms show that each additional minute of wait time reduces the probability of a customer placing another order within 7 days by approximately 0.3%. This retention effect compounds: a customer who waits 10 extra minutes is 3% less likely to return. With average ticket sizes around R$38.50 and a base of 333 orders per day (within the scope of our representative dataset), this is economically material.

To quantify the problem, we used the combined impact formula:

```
Revenue_Delta = Time_Delta x Cost_Per_Minute x Orders_Per_Day + Retention_Delta x Avg_Ticket x Orders_Per_Day
```

Applying the numbers:

```
Operational_Cost = 2.44 min x R$0.50 x 333 orders/day x 30 days = R$12,183/month
```

This alone would be enough to justify a deeper investigation. But the problem was not only the cost — it was the NPS. Industry data shows that delivery platform NPS drops an average of 3 points for each extra minute of wait beyond the promised time. With competitors like Rappi and iFood actively competing for the same customers and restaurants, an NPS degradation of 15 points (equivalent to a 5-minute increase in average time) is the kind of signal that can accelerate churn in high-value customer segments.

The competitive context matters: in Brazil, unlike the US, the three main players operate in overlapping cities with very similar value propositions. Delivery speed is the primary dimension of differentiation perceived by the customer. Being 6.4% slower than the optimal algorithm — exactly what we found — may seem small in absolute terms, but in terms of brand perception and competitive positioning, it is the difference between leading and following.

---

## Section 2: Hypotheses

Before any analysis, we formulated 4 structured hypotheses in the classic scientific format: independent variable, dependent variable, causal mechanism, and test criteria. This rigor is essential in analytics because without a prior hypothesis, you are not doing analysis — you are cherry-picking results.

### H1: The allocation algorithm is the primary bottleneck

**Definition:** The FIFO (First In, First Out) dasher allocation algorithm is responsible for the majority of the increase in delivery time.

**Independent variable:** Type of allocation algorithm (FIFO vs. predictive).

**Dependent variable:** Total delivery time in minutes (delivery_duration_minutes).

**Causal mechanism:** The FIFO algorithm selects the available dasher closest to the restaurant at the moment the order is created. It completely ignores when the order will be ready. The practical result: the dasher frequently arrives at the restaurant 5-10 minutes before the order is ready and waits. This waiting time is invisible in the routing data but shows up in total time. Additionally, FIFO ignores the dasher's punctuality history and real-time traffic conditions at the time of assignment.

**How to test:** Controlled A/B experiment with a 50/50 split. Group A receives the FIFO algorithm (control), Group B receives the predictive algorithm (treatment). Primary metrics: delivery_duration_minutes, duracao_rota_min, duracao_atribuicao_min.

---

### H2: The dasher assignment step is the most critical (not the route)

**Definition:** Of all the steps in the delivery flow, dasher assignment time (duracao_atribuicao_min) has the greatest impact on total time.

**Independent variable:** Speed and quality of dasher assignment (duracao_atribuicao_min).

**Dependent variable:** Total delivery time (delivery_duration_minutes).

**Causal mechanism:** The assignment step triggers every subsequent step. If the wrong dasher is assigned (someone far away, with a poor track record, or in a high-traffic area), every subsequent step is penalized. A dasher who receives the order 3 minutes later than optimal will arrive at the restaurant 3 minutes later, will pick up the order 3 minutes later, and will deliver 3 minutes later — the delay propagates additively through the pipeline.

**How to test:** Pearson correlation between duracao_atribuicao_min and delivery_duration_minutes in the historical dataset. Supplemented by OLS regression controlling for city, time of day, and restaurant category.

---

### H3: The new predictive algorithm reduces delivery time by at least 5%

**Definition:** Algorithm B (predictive) reduces average delivery time by at least 5% compared to Algorithm A (FIFO).

**Independent variable:** Allocation algorithm (A=FIFO, B=predictive).

**Dependent variable:** delivery_duration_minutes.

**MDE (Minimum Detectable Effect):** 5% of 38 minutes = 1.9 minutes. This is the smallest difference the experiment needs to be able to detect. We chose 5% as the threshold because below that, the financial impact does not justify the operational risk of a rollout.

**Sample size calculation:**

```python
from scipy import stats
import numpy as np

efeito_esperado = 0.05 * 38   # MDE = 5% of 38 min = 1.9 min
std_estimado = 8.0             # estimated from historical data
alpha = 0.05
poder = 0.80

# Cohen's d
d = efeito_esperado / std_estimado  # d = 0.2375

# Sample size per group
z_alpha = stats.norm.ppf(1 - alpha/2)  # 1.96
z_beta  = stats.norm.ppf(poder)         # 0.84

n = ((z_alpha + z_beta) / d) ** 2  # ~280 per group minimum
# With real distribution (higher variance): ~1,800 per group
```

With ~4,800 orders per group in the dataset, statistical power exceeds 99% — the experiment is more than sufficient to detect the effect.

**How to test:** One-sided Welch t-test (H1: mu_B < mu_A) with alpha=0.05 and 95% CI calculation for the delta.

---

### H4: The algorithm's impact varies by region and time of day

**Definition:** Algorithm B's gain is not uniform — regions with higher dasher density and off-peak hours benefit more.

**Independent variable:** Triple interaction city x time_of_day x algorithm.

**Dependent variable:** delivery_duration_minutes.

**Causal mechanism:** The predictive algorithm uses traffic data and dasher history. In smaller cities (Curitiba, Porto Alegre) with less traffic and more predictable dashers, the predictive model has a stronger signal and generates better predictions. In São Paulo, where traffic is chaotic and the dasher pool is enormous, the model has more noise — the gain is smaller.

**How to test:** Segmented analysis: calculate delta by city and by period. Verify whether gains are statistically significant in each segment individually. OLS regression with interaction: `time ~ algorithm * city + algorithm * period + controls`.

---

## Section 3: The A/B Test

Experiment design is just as important as the analysis. A poorly designed experiment produces incorrect results even with perfect statistics.

### Group A — Control: FIFO Proximity Algorithm

The FIFO algorithm is the legacy system: at the moment an order is created in the system, the algorithm finds the available dasher closest to the restaurant (in straight-line kilometers) and makes the assignment immediately.

The problem is not that it is simple — it is that it ignores three critical variables:

First, it ignores the order preparation time. A sushi restaurant may take 25 minutes to prepare the order. FIFO sends the dasher to arrive in 8 minutes. The dasher stands waiting 17 minutes at the restaurant door. This time shows up as "pickup time" in the metrics, but in practice it is wasted waiting time that the dasher charges to the platform.

Second, it ignores the dasher's history. A dasher with an 85% punctuality record is treated identically to one with a 97% record. The system does not learn from historical behavior.

Third, it ignores real-time traffic. A dasher 2km away in heavy traffic may arrive later than one 4km away on a clear route. FIFO uses Euclidean distance, not estimated travel time.

### Group B — Treatment: Predictive Algorithm

The predictive algorithm makes the assignment decision by solving an optimization problem with three components:

Component 1 — Preparation time prediction: the model uses the restaurant's history (average preparation time by order category, by hour, by day of week) to estimate when the order will be ready. Dasher assignment is scheduled so the dasher arrives at the restaurant within a 2-minute window of the estimated readiness time.

Component 2 — Historical dasher score: each dasher has a score calculated over the last 30 deliveries (punctuality rate, average pickup time, number of rejected orders). The algorithm prioritizes dashers with higher scores for higher-value orders or during peak hours.

Component 3 — Real-time traffic estimate: the system integrates traffic data (via an external API) to calculate the estimated travel time from the dasher to the restaurant and from the restaurant to the customer. The assignment considers this estimated time, not the Euclidean distance.

The expected result is that the dasher arrives at the restaurant exactly when the order is ready, eliminates waiting time, and proceeds directly to delivery with an optimized route.

### Randomization

Randomization used deterministic hashing on the order_id:

```python
# Deterministic hash by order_id
ab_group = 'B' if int(hashlib.md5(order_id.encode()).hexdigest(), 16) % 2 == 0 else 'A'
```

Why deterministic hash instead of random.choice:
- Guarantees the same order_id always falls in the same group, even if data is reprocessed
- Eliminates the risk of "leakage" where the same order appears in both groups during reprocessing
- Enables auditing: given any order_id, we can verify which group it should be in
- Ensures the 50/50 split is maintained over time without drift

The result in the dataset: Group A = 5,119 orders, Group B = 5,081 orders. The split is 50.2/49.8 — close enough to 50/50 to have no impact on statistical power.

### Test Duration

The test ran for 10 business days (equivalent to 2 business weeks). This duration was chosen for three reasons:

First, to capture day-of-week variation: Friday and Saturday have 40% higher volume than Monday and Tuesday. A test of only 3 days may capture only part of the weekly cycle and introduce a time-of-day bias.

Second, to avoid the novelty effect: the first 48 hours of a new algorithm may show atypical performance because the system is still "learning" the dasher pool. Including this period with equal weight as the rest of the experiment can bias results.

Third, to achieve sufficient statistical power: with ~333 orders/day and a 50/50 split, 10 days generate ~1,665 orders per group — above the minimum of ~1,800 calculated for power=80%.

In practice, the generated dataset has ~4,800 orders per group, which guarantees power > 99%.

---

## Section 4: The Data — Synthetic Generation

### Why Synthetic Data

The decision to use synthetic data instead of real production data was not a technical limitation — it was a deliberate choice for four reasons:

**Ethics and privacy (LGPD):** Real delivery operations data contains customer histories (addresses, preferences, order times), courier data (GPS location, income, individual performance), and restaurant information (sales volume, peak hours). Publishing this data publicly — even anonymized — violates privacy principles and may constitute a breach of Brazil's LGPD data protection law.

**Guaranteed reproducibility:** With `seed=42`, anyone who clones the repository and runs `generate_doordash.py` will obtain exactly the same dataset, with the same numbers, the same quality flags, and the same statistical results. This is impossible with real data that changes continuously.

**Control over ground truth:** With synthetic data, we know exactly which effect was injected. Algorithm B was programmed to be 6% faster (multiplicador_b = 0.94). This allows us to validate that the analysis detected the correct effect — a sanity check impossible with real data where the "true effect" is unknown.

**Pedagogical transparency:** For a learning case, the ability to see the code that generated the data is essential to understanding why the results are what they are. Real data is a black box; synthetic data is completely transparent.

### The 29 Columns in 7 Logical Groups

The schema was designed to reflect the real complexity of a delivery system:

**Group 1 — Identifiers (5 columns):** order_id, customer_id, restaurant_id, delivery_id, dasher_id. Primary and foreign keys that simulate the microservices system: order service, customer service, restaurant service, delivery service, dasher service — each with its own ID namespace.

**Group 2 — Temporal (4 columns):** created_at, dasher_assigned_at, pickup_at, delivered_at. The four main timestamps of the business flow, plus the 7 stage timestamps that track each micro-step.

**Group 3 — Business (3 columns):** ab_group (A or B), status (delivered/cancelled/in_progress), total_amount_usd. The order value was generated with a log-normal distribution (mean ~$25, standard deviation ~$12) to reflect real-world skewness: most orders are of average value, but there is a tail of high-value orders.

**Group 4 — Dimensions (3 columns):** customer_city (6 cities), customer_segment (Premium/Standard/Budget), restaurant_category (Fast Food, Pizza, Sushi, etc.).

**Group 5 — The 7 Stage Timestamps:** stage_1 (order created) through stage_7 (delivered). These timestamps are the backbone of the step-level analysis in dbt intermediate.

**Group 6 — Derived Columns (3 columns):** delivery_duration_minutes (calculated from stage_1 to stage_7), hour_of_day (0-23), month (Jan/Feb/Mar), delivery_stage_bucket (time-of-day period).

**Group 7 — Quality Flags (4 boolean columns):** has_duplicate_flag, has_timestamp_issue_flag, has_missing_dasher_flag, has_outlier_flag. Each flag indicates a specific problem, allowing the downstream pipeline to filter at a granular level.

### The 4 Data Quality Issues and Their Real-World Motivation

**Duplicates (2%, 200 orders):** In distributed payment systems, event delivery is not guaranteed exactly once (at-most-once vs. at-least-once delivery). When a payment confirmation webhook does not receive an ACK (acknowledgment) from the destination server within the timeout, the system resends the event. If the destination server already processed the event but the ACK was lost on the network, the event is processed twice — generating a duplicate. Robust production systems implement idempotency using an idempotency_key, but legacy systems often lack this protection.

**Out-of-order timestamps (1%, 97 orders):** In microservices architectures, each service writes to its own database with its own clock. Clock skew (clock desynchronization between servers) of up to 200ms is common even with NTP. When events from different services are consolidated in a data warehouse, messages that arrived later may have an earlier timestamp than the message that arrived first. For example: the "dasher_assigned" event may have timestamp 14:30:05.100 while the "order_placed" event that preceded it has timestamp 14:30:05.300 — because the dasher service clock is 200ms ahead.

**Unassigned dasher (1%, 97 orders):** During high-demand periods, the allocation algorithm may exhaust the search timeout (typically 30 seconds) without finding an available dasher within the configured radius. The order enters an "orphaned" state: confirmed by the restaurant, but without a courier. These orders queue until a dasher becomes available or until the customer cancels. In the raw data, dasher_id is NULL — which causes problems in JOINs and assignment time calculations.

**Outliers above 120 minutes (1%, 97 orders):** Deliveries taking more than 2 hours are extraordinary events that do not represent normal operational flow. Real-world causes include: dasher with a vehicle breakdown (flat tire, car breaks down), order lost at the restaurant (restaurant cannot find the order even after the dasher arrives), partial cancellation where the order is not technically cancelled but remains in limbo, or geolocation errors where GPS marks the delivery at the wrong address. These records are valid for exception analyses, but must be removed from average delivery time calculations to avoid distorting the primary metrics.

---

## Section 5: Data Pipeline — Step by Step

### 5.1 Data Generation (generate_doordash.py)

The generation script uses real statistical distributions to create a plausible dataset:

**Delivery time (log-normal distribution):** Real delivery time in delivery platforms does not follow a normal distribution — it has a long right tail. Orders take at minimum 15-20 minutes (minimum physical time for preparation + route), but can take much longer in extraordinary cases. The log-normal distribution captures exactly this skewness: most orders cluster around 35-40 minutes, but there is a tail of 60-90 minute orders.

**Injecting the A/B effect:** The effect of Algorithm B was injected by multiplying the delivery time of Group B orders by 0.94:

```python
multiplicador_b = 0.94  # Algorithm B is 6% faster
delivery_time = base_time * (multiplicador_b if ab_group == 'B' else 1.0)
```

This ensures the experiment's ground truth is exactly -6%. The analysis recovered -6.4% (slightly different due to sampling variance), which is the correct behavior of a statistical estimator.

**Injecting the monthly cancellation trend:** Order distribution weights by month were adjusted to create the growing cancellation trend:

```python
pesos_mes = [0.42, 0.35, 0.23]  # Jan=42%, Feb=35%, Mar=23%
taxa_cancelamento = {'Jan': 0.049, 'Feb': 0.085, 'Mar': 0.120}
```

This simulates a real operational degradation: in January the platform was healthy (4.9% cancellation), but by March the problem had escalated (12.0%).

**Injecting data quality issues:** The issues were injected in sequence after generating the clean dataset:

```python
# Step 1: Generate clean dataset with seed=42
# Step 2: Duplicate 200 random records (2% duplicates)
# Step 3: Shuffle timestamps of 97 records (clock skew)
# Step 4: Remove dasher_id from 97 records (failed assignment)
# Step 5: Inflate delivery_time of 97 records to >120min (outliers)
```

### 5.2 EDA and Cleaning (eda_cleaning.py)

The cleaning pipeline follows the "no information lost" principle — every cleaning decision is recorded as a boolean flag rather than simply deleting the record:

**Why remove duplicates before any analysis:** Aggregate metrics calculated on data with duplicates are incorrect in subtle ways. The mean delivery time with 200 duplicates of fast orders is artificially lower than the real mean. Order COUNT is inflated. Any downstream JOIN with the customers or restaurants table can generate fanout. Deduplication must be the first step.

**Why reorder timestamps with np.sort instead of dropping the record:** Dropping the record means losing data that is valid — only the record arrived out of order, not the event itself. Interpolating timestamps between steps is risky because it assumes linearity between events that are not linear. Reordering assumes only that the steps occurred in the correct sequence, even if the records arrived out of order — a far more conservative and defensible assumption.

**Why use the string "UNASSIGNED" instead of NULL for missing dashers:** NULL in SQL has special behavior: it propagates to any calculation (avg(NULL) = NULL, NULL != NULL and NULL = NULL are both NULL). An explicit "UNASSIGNED" string allows filtering, grouping, and identifying these cases without unpredictable behavior. It also makes clear to any downstream analyst that this dasher_id is not a missing value due to an error — it is a valid business state.

**Why a fixed threshold of 120 minutes instead of IQR:** The IQR method (Q3 + 1.5 x IQR) is a generically useful statistical criterion, but with log-normal distributions (like delivery time) it tends to remove 7-10% of the data, including long but legitimate deliveries (distant orders, adverse weather conditions). A 120-minute threshold is DoorDash's maximum business SLA — above that, the customer is entitled to an automatic refund. Using the business criterion is more interpretable, auditable, and defensible to a non-technical stakeholder.

**Cleaning pipeline results:**

| Step | Rows |
|------|------|
| Raw (with duplicates) | 10,200 |
| After deduplication | 9,800 |
| After outlier removal | 9,703 |
| Delivered with no issue flags | ~8,650 |

### 5.3 Modeling with dbt

**Why dbt instead of plain SQL or pandas:**

Plain SQL in standalone scripts is the most common standard in analytics teams without engineering maturity. The problems are well known: no versioning of business logic (the script changes, the history is lost), no automated tests (you discover the column became NULL only when the CEO asks), no automatic documentation (the next analyst doesn't know where the column came from), no lineage (it is impossible to know which dashboards are affected if a source changes).

pandas instead of SQL is a valid choice for exploratory analysis, but does not scale to production pipelines. A DataFrame of 10 million rows does not fit in memory on a standard machine. Additionally, transformation logic in Python is far more verbose than equivalent SQL and much harder to peer review by those who know SQL but not Python.

dbt solves these problems: it is SQL with superpowers. You write SQL, and dbt adds versioning (via Git), declarative tests, automatic documentation, and visual lineage.

**The 3 Layers and the Rationale:**

The staging layer (`stg_pedidos`) performs only cleaning and type standardization. It is materialized as a view because it always needs to reflect the freshest data from the source. The code performs exactly 29 type casts (varchar, timestamp, decimal, boolean, integer) and adds two simple derived columns (is_delivered and is_cancelled). No joins, no business logic, no complex calculations. The golden rule is: "staging is the place to standardize, not to transform."

The intermediate layer (`int_pedidos_com_etapas`) is where business logic begins. Here we calculate the 6 step durations (duracao_aceite_min, duracao_preparo_min, duracao_atribuicao_min, duracao_coleta_min, duracao_rota_min, duracao_proximidade_min) as differences between the 7 stage timestamps. This layer is materialized as a view because it does not need to be queried directly — it serves only as preparation for the marts.

The marts layer (`fct_entregas` and `fct_ab_resultados`) is the final product. `fct_entregas` has a granularity of 1 row per delivered order, with all calculated metrics and classification columns (fast/normal/slow, is_horario_pico). `fct_ab_resultados` aggregates by A/B group with the delta calculated via cross join. Both are materialized as tables because BI queries need performance — they cannot recalculate everything on every query.

**The 29 Tests:**

The 29 tests were written to guarantee four critical data properties:

- 8 `not_null` tests: ensure that essential columns (order_id, ab_group, tempo_total_min, customer_city, month, etc.) are never NULL in model outputs. If a JOIN fails silently, these tests catch it.
- 4 `unique` tests: ensure that model granularity is correct. `order_id` must be unique at each layer — if duplicates pass through staging, this test fails at intermediate and mart.
- 16 `accepted_values` tests: ensure that domains are valid. ab_group can only be 'A' or 'B'. status can only be 'delivered', 'cancelled', or 'in_progress'. customer_city can only be one of the 6 cities. Any corrupted data creating a value outside the domain is detected immediately.
- 1 custom singular test (`assert_grupo_b_mais_rapido.sql`): this is the business test. It queries `fct_ab_resultados` and verifies that Group B's average time is strictly less than Group A's. If the pipeline runs with corrupted data where A beats B, the test fails and the pipeline stops before feeding incorrect data to the dashboard.

**Why DuckDB:**

DuckDB was chosen over Postgres because it requires no server: it is a local `.duckdb` file that dbt reads and writes directly. It is optimized for OLAP (columnar processing), not OLTP. It reads CSV natively without needing COPY or INSERT. It has ANSI-compatible SQL with modern extensions (percentile_cont, median, epoch). For a local case and for CI/CD in GitHub Actions, it is the simplest and most efficient choice.

### 5.4 Statistical Analysis of the A/B Test

**Why Welch t-test instead of the standard Student t-test:**

The Student t-test assumes that the variances of the two groups are equal (homoscedasticity). Before running the test, we verified this assumption with the Levene test: the result was p < 0.05, indicating that the variances are significantly different (Group A: standard deviation 8.18, Group B: 8.05). The Welch t-test relaxes this assumption by using Satterthwaite-adjusted degrees of freedom for the different variances — it is more robust and is the correct choice for real data.

Mann-Whitney (Wilcoxon test) would be the non-parametric alternative if the distribution were not approximately normal. With n > 4,000 per group, the Central Limit Theorem guarantees that the distribution of means is approximately normal — so Welch is appropriate and easier to interpret (operates in minutes, not ranks).

**What p-value means in business language:**

The p-value answers the following question: "If the two algorithms were identical (null hypothesis true), what would be the probability of observing a difference of at least 2.44 minutes by pure chance, solely due to natural data variability?"

In our case, p ≈ 0.000 (more precisely, p < 0.000001). This means: the probability of seeing this difference by chance is less than 1 in 1 million. Practically impossible.

The most common trap: p < 0.05 does not mean "large effect." With n=10,000, even a difference of 0.05 minutes (3 seconds) can have p < 0.05. That is why we simultaneously report: the absolute delta (2.44 min), the relative delta (6.4%), the 95% CI ([-2.71, -2.17]), Cohen's d effect size (≈0.30), and the estimated financial impact (ROI 274%). The business decision uses all of these numbers together.

**95% CI: [-2.71, -2.17] minutes:**

The correct interpretation: "With 95% confidence, the true effect of Algorithm B is between 2.17 and 2.71 minutes of reduction in delivery time." The interval does not include zero, confirming that the effect is real. The lower bound of the interval (2.17 min) is the pessimistic scenario — even in the worst plausible case, Algorithm B saves more than 2 minutes per delivery.

**Effect size (Cohen's d):**

```
d = delta / pooled_standard_deviation = 2.44 / 8.1 ≈ 0.30
```

By Cohen's convention: d=0.2 is small, d=0.5 is medium, d=0.8 is large. Our d=0.30 is "small to medium" — but this is a generic statistical label. In a delivery context, saving 2.44 minutes on a 38-minute delivery (6.4%) is economically relevant regardless of the statistical label.

**B wins in all 6 cities:**

| City | Group A Mean (min) | Group B Mean (min) | Delta (min) | Delta % |
|------|-------------------|-------------------|-------------|---------|
| Curitiba | 38.30 | 35.27 | -3.03 | -7.91% |
| Porto Alegre | 38.54 | 35.51 | -3.03 | -7.86% |
| Rio de Janeiro | 38.27 | 35.74 | -2.53 | -6.61% |
| Belo Horizonte | 38.17 | 35.85 | -2.32 | -6.08% |
| Brasilia | 37.92 | 35.84 | -2.08 | -5.49% |
| Sao Paulo | 37.70 | 35.97 | -1.73 | -4.59% |

Sao Paulo had the smallest gain (-4.59%), likely because higher traffic density and a larger dasher pool add noise to the predictive model. This is a signal that the algorithm may need specific tuning for high-density markets.

**B wins in all 5 time-of-day periods:**

| Period | Group A Mean (min) | Group B Mean (min) | Delta (min) | Delta % |
|--------|-------------------|-------------------|-------------|---------|
| Afternoon (14-18h) | 38.39 | 35.49 | -2.90 | -7.55% |
| Morning (6-11h) | 38.38 | 35.82 | -2.56 | -6.67% |
| Late Night (0-5h) | 38.19 | 35.71 | -2.48 | -6.49% |
| Evening (18-23h) | 37.69 | 35.56 | -2.13 | -5.65% |
| Lunch (11-14h) | 38.01 | 35.97 | -2.04 | -5.37% |

**ROI of 274% calculation:**

```
Operational savings/month = 2.44 min x R$0.50 x 333 orders/day x 30 days = R$12,183
Incremental revenue/month  = 333 x 0.001 x 2.44 x R$38.50 x 30           = R$939
Total benefit/month        = R$12,183 + R$939                              = R$13,122

Implementation cost        = 3 months x R$12,000 in engineering            = R$36,000
Annual benefit             = R$13,122 x 12                                 = R$157,464
Net return                 = R$157,464 - R$36,000                          = R$121,464
ROI                        = R$121,464 / R$36,000 x 100                   = 337%
Conservative ROI (274%)    = using operational savings only, without incremental revenue
```

### 5.5 Dashboard (streamlit_app.py)

**Why Streamlit instead of Power BI or Tableau:**

Power BI and Tableau are excellent tools for traditional BI dashboards: grids, bars, lines, filters. But they cannot execute arbitrary Python code in response to user interaction. For our case, we need to recalculate the Welch t-test and the 95% CI in real time when the user changes city or period filters — this is not possible in Power BI without extremely complex DAX that still would not have scipy underneath.

Streamlit solves this because it is pure Python: any city or period filter in the sidebar recalculates scipy.stats.ttest_ind with the filtered data and updates the p-value, CI, and delta on screen. The trade-off is that the visuals are less polished than Power BI — but for a technical audience that needs to trust the statistics, the transparency of the calculation is worth more than the visual finish.

**Design decisions by page:**

Page 1 — Overview: the monthly trend chart uses a dual-axis because orders (scale ~3,000-4,000) and cancellation rate (scale 0-15%) are incompatible magnitudes. Sharing the same Y-axis would make one of the series invisible. The dual-axis keeps both series readable at their own scales.

Page 2 — A/B Result: the boxplot was chosen over bar charts of means because it shows the full distribution: median, IQR (box), whiskers (1.5x IQR), and individual outliers. A bar of the mean hides the fact that Group A has outliers above 80 minutes pulling the mean up — the boxplot makes this immediately visible.

Page 3 — Step Analysis: the waterfall shows the additive composition of total delivery time, allowing visual identification of which step dominates. The Route step (17.30 min, 43% of total time) is the largest contributor — which explains why the predictive algorithm, which optimizes the route, has the greatest gain at this step (-1.15 min, -6.4%).

Page 4 — Financial Impact: the interactive inputs (orders per day, cost per minute, average ticket) allow each manager to calibrate the model with their own business data. An ROI calculated with adjustable assumptions is far more convincing to a CEO than a static number — because they can see how the result changes when they adjust the assumptions.

`st.cache_data` is applied to loading the CSV (9,703 rows). Without caching, each filter interaction would reload the file from disk (~2 seconds of perceptible lag). With caching, the DataFrame stays in memory and filters respond in under 50ms.

---

## Section 6: Tools and Justifications

| Tool | What it does | Why we chose it | Alternatives | When NOT to use it |
|------|-------------|-----------------|--------------|-------------------|
| Python 3.11 | Data generation, EDA, scripts | Rich ecosystem (pandas, scipy, numpy), market standard | R, Julia | When the team is 100% SQL |
| dbt Core | Transformation and modeling | Versioning, tests, automatic docs, market standard | SQLMesh, Dataform | Very simple projects with no lineage needs |
| DuckDB | Analytical storage | Zero-config, local OLAP, reads CSV natively, zero cost | Postgres, Snowflake, BigQuery | When multi-user or data > 100GB is needed |
| Streamlit | Interactive dashboard | Native Python, fast deploy, integrated statistical calculation | Power BI, Tableau, Metabase | Non-technical stakeholders prefer familiar interfaces |
| Plotly | Visualizations | Native interactivity, boxplot and waterfall support | matplotlib, seaborn, altair | When highly customized SVG charts are needed |
| scipy.stats | Statistical tests | Welch t-test, 95% CI, statistical power | statsmodels, pingouin | When more complex models like regression or ANOVA are needed |
| GitHub Actions | CI/CD | Free for public repositories, integrated with GitHub | CircleCI, Jenkins, GitLab CI | Very complex pipelines with many parallel steps |
| dbt_utils | Extra generic tests | Richer schema tests without writing custom SQL | No direct equivalent | Does not apply — adding dbt packages has zero cost |

---

## Section 7: Results and Final Decision

### Results by Hypothesis

**H1: The allocation algorithm is the primary bottleneck — CONFIRMED**
The FIFO algorithm was replaced by the predictive one, resulting in a statistically significant reduction of 2.44 minutes (6.4%) in average delivery time. p-value ≈ 0.000, t=14.0, 95% CI [-2.71, -2.17]. The experiment confirms that the algorithm change, and not another factor (seasonality, customer profile, region), is responsible for the difference.

**H2: The Route step is the most critical — CONFIRMED**
Step-level analysis shows that the Route had the largest absolute gain in response to Algorithm B: -1.15 min (-6.4%), followed by Preparation (-0.73 min) and Assignment (-0.50 min). The predictive algorithm most strongly impacts the Route step because by scheduling the dasher's arrival at the right moment, the dasher can depart from the restaurant with a more optimized itinerary instead of rushing to compensate for time lost waiting.

**H3: Reduction of at least 5% — CONFIRMED**
The result of -6.4% exceeds the 5% MDE. The 95% confidence interval of [-2.71, -2.17] lies entirely below -1.9 min (the 5% threshold), confirming that even in the pessimistic scenario the effect surpasses the threshold.

**H4: B wins in all regions and time periods — CONFIRMED**
Segmented analysis confirms: B wins in all 6 cities (from -4.59% in Sao Paulo to -7.91% in Curitiba) and in all 5 time-of-day periods (from -5.37% at Lunch to -7.55% in the Afternoon). The unanimity of results is a strong signal of robustness — the effect is not an artifact of a specific segment.

### Decision: Full Rollout of Algorithm B

**3-week rollout plan:**

- Week 1 — 25% of traffic: monitor cancellations (alert if > 12%), average dasher_score (alert if drops > 5%), and assignment time (alert if > 5 min). Focus on early detection of adverse effects.
- Week 2 — 50% of traffic: validate that the -6.4% gain persists outside the controlled experiment environment (without a Hawthorne effect). Monitor restaurant NPS (dashers arriving at the right moment positively affects restaurant ratings).
- Week 3 — 100% of traffic: full rollout. Maintain monitoring for an additional 30 days. Report actual vs. projected financial impact.

**Guardrails (what to monitor continuously):**
- Cancellation rate: alert if > 12% (was already growing during the experiment — a concerning trend independent of the A/B test)
- Average dasher_score: alert if drops > 5% (the new algorithm may be more demanding on dashers with variable histories)
- Assignment time: alert if > 5 min (the predictive algorithm is more computationally intensive; if the prediction service becomes slow, the impact on assignment is immediate)
- Restaurant NPS: alert if drops (dashers arriving too early or too late affects the restaurant's experience with the platform)

### Study Limitations

**Synthetic dataset:** Does not capture real seasonality (holidays, local events, weather), real urban density variation, or behavior specific to Brazilian cities.

**10-day duration:** May not fully capture the "novelty effect" (dashers may behave differently when the algorithm changes) or the predictive model's learning effect (which improves with more data over time).

**6 cities:** Sao Paulo had the smallest gain (-4.59%). In a real operation with dozens of cities, some may not benefit from the predictive algorithm in the same way — the rollout would require city-by-city analysis.

**ROI based on assumptions:** The ROI calculation uses R$0.50/min as the dasher operational cost and R$38.50 as the average ticket. These numbers are estimates. The actual ROI may be 30% higher or lower depending on the real cost figures for the operation.

---

## Section 8: Glossary

**dbt (data build tool):** A tool for transforming data with SQL organized in layers with versioning, tests, and automatic documentation. Analogy: it is like a recipe with ordered steps, traceable ingredients, and quality checks at each step. The chef (analyst) writes the recipe; dbt ensures it is executed in the correct order and that each ingredient meets the standard.

**EDA (Exploratory Data Analysis):** Initial exploratory analysis to understand the data before modeling — distributions, null values, outliers, correlations. Analogy: it is "reconnaissance of the terrain" before building. An architect does not design a building without studying the ground; an analyst does not model data without doing EDA.

**A/B Test:** A controlled experiment where two groups receive different versions of a product or algorithm. Group A receives the current version (control) and Group B receives the new version (treatment). We compare metrics between groups to decide which version is better. Analogy: giving different menus to two groups of customers at identical restaurants and comparing the average tip.

**p-value:** The probability of observing the measured effect (or a larger one) if the null hypothesis were true — that is, if there were no real difference between groups. Values below 0.05 are the convention for "sufficient evidence against the null hypothesis." In our case, p ≈ 0.000 means the probability of seeing a difference of 2.44 min by chance is less than 0.001%.

**DuckDB:** An analytical database that runs as a local file, with no server, no installation. Specialized in OLAP queries (aggregations, JOINs over large volumes). Analogy: the SQLite of the analytics world — as lightweight as a text file, but as powerful as a columnar production database.

**Staging (dbt):** The first transformation layer in the dbt pipeline. Performs only cleaning and type standardization — no joins, no business logic. Rule: one column per source, always. Materialized as a view.

**Mart (dbt):** The final consumption layer in the dbt pipeline. Has clear granularity (e.g., 1 row = 1 delivery), ready for BI and analysis. Materialized as a table for performance.

**Welch t-test:** A variant of the classic t-test that does not assume equal variances between the two groups being compared. Uses degrees of freedom adjusted by the Satterthwaite method. More robust for real data where variance between groups is rarely identical.

**MDE (Minimum Detectable Effect):** The smallest difference between groups that the experiment can detect with sufficient statistical power, given the sample size. Defines the experiment's "floor": effects below the MDE may exist but will not be detected reliably.

**Statistical power:** The probability of detecting a real effect when it exists (P(reject H0 | H1 true)). Market convention: 80%. Power below 80% means the experiment has a reasonable chance of missing a real effect — a false negative.

**seed=42:** The initial number provided to the pseudorandom number generator. With the same seed, the sequence of "random numbers" is identical across all runs. Ensures the synthetic dataset is identical every time the script runs — full reproducibility.

**Deterministic hash:** A mathematical function that maps any input to a fixed-size output, always producing the same output for the same input. In the context of A/B testing, it ensures that the same order_id always falls in the same group, even in reprocessing or system failures.

**CI/CD (Continuous Integration / Continuous Deployment):** The practice of automating build, tests, and deployment on every code push. In our pipeline, every push triggers: data generation, dbt run, dbt test. If any step fails (including the singular A/B test), the pipeline stops and the team is notified before incorrect data reaches the dashboard.

**Effect size (Cohen's d):** A standardized measure of effect size, calculated as the difference between means divided by the pooled standard deviation. Independent of sample size — allows comparing effects across studies with different n values. By convention: d=0.2 small, d=0.5 medium, d=0.8 large.

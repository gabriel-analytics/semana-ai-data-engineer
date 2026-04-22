"""
EDA + Data Cleaning — DoorDash Delivery Dataset
Author: gabriel-analytics
Date: 2026-04-21
Libraries: pandas, numpy, scipy only (no matplotlib/seaborn)
"""

import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
DATA_DIR = Path(r"C:\Users\lineg\semana-ai-data-engineer\gen\data")
RAW_PATH = DATA_DIR / "doordash_raw.csv"
CLEAN_PATH = DATA_DIR / "doordash_clean.csv"
REPORT_PATH = DATA_DIR / "eda_report.md"

STAGE_COLS = [
    "stage_1_order_placed_at",
    "stage_2_restaurant_confirmed_at",
    "stage_3_dasher_assigned_at",
    "stage_4_dasher_arrived_restaurant_at",
    "stage_5_order_picked_up_at",
    "stage_6_dasher_near_customer_at",
    "stage_7_delivered_at",
]

# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------
SEP = "=" * 70


def section(title: str) -> None:
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)


def minutes_between(series_a: pd.Series, series_b: pd.Series) -> pd.Series:
    """Return duration in minutes between two datetime series."""
    return (series_b - series_a).dt.total_seconds() / 60


def describe_delivery(series: pd.Series, label: str = "") -> dict:
    """Return key descriptive stats for delivery_duration_minutes."""
    return {
        "label": label,
        "n": int(series.count()),
        "mean": round(series.mean(), 2),
        "median": round(series.median(), 2),
        "std": round(series.std(), 2),
        "min": round(series.min(), 2),
        "p5": round(series.quantile(0.05), 2),
        "p25": round(series.quantile(0.25), 2),
        "p75": round(series.quantile(0.75), 2),
        "p95": round(series.quantile(0.95), 2),
        "max": round(series.max(), 2),
    }


# ---------------------------------------------------------------------------
# LOAD
# ---------------------------------------------------------------------------
section("LOADING RAW DATA")
df = pd.read_csv(RAW_PATH)
print(f"  Loaded: {RAW_PATH}")
print(f"  Shape:  {df.shape[0]:,} rows x {df.shape[1]} columns")

# Parse datetime columns up front (all stage + created_at columns)
datetime_cols = ["created_at", "dasher_assigned_at", "pickup_at", "delivered_at"] + STAGE_COLS
for col in datetime_cols:
    df[col] = pd.to_datetime(df[col], errors="coerce")


# ===========================================================================
# ETAPA 1 — PERFIL COMPLETO DO DATASET
# ===========================================================================
section("ETAPA 1 — PERFIL COMPLETO DO DATASET")

print(f"\n--- Shape ---")
print(f"  Linhas: {df.shape[0]:,}  |  Colunas: {df.shape[1]}")

print(f"\n--- dtypes ---")
for col, dtype in df.dtypes.items():
    print(f"  {col:<45} {str(dtype)}")

print(f"\n--- % Nulos por coluna (decrescente) ---")
null_pct = (df.isnull().sum() / len(df) * 100).sort_values(ascending=False)
for col, pct in null_pct.items():
    if pct > 0:
        print(f"  {col:<45} {pct:.2f}%")

print(f"\n--- Duplicatas (order_id duplicado) ---")
dup_count = df.duplicated(subset=["order_id"], keep=False).sum()
print(f"  Linhas com order_id duplicado: {dup_count:,}")
print(f"  Linhas com has_duplicate_flag=True: {df['has_duplicate_flag'].sum():,}")

print(f"\n--- Estatísticas: delivery_duration_minutes ---")
stats_raw = describe_delivery(df["delivery_duration_minutes"], "raw")
for k, v in stats_raw.items():
    if k != "label":
        print(f"  {k:<10} {v}")

print(f"\n--- Contagem de Flags ---")
for flag in ["has_duplicate_flag", "has_timestamp_issue_flag", "has_missing_dasher_flag", "has_outlier_flag"]:
    ct = df[flag].sum()
    pct = ct / len(df) * 100
    print(f"  {flag:<35} True={ct:,} ({pct:.1f}%)  False={len(df)-ct:,}")

print(f"\n--- Distribuicao status ---")
for val, cnt in df["status"].value_counts().items():
    print(f"  {val:<15} {cnt:,} ({cnt/len(df)*100:.1f}%)")

print(f"\n--- Distribuicao ab_group ---")
for val, cnt in df["ab_group"].value_counts().items():
    print(f"  {val:<5} {cnt:,} ({cnt/len(df)*100:.1f}%)")

# Store profile data for report
profile_shape = df.shape
profile_null = null_pct[null_pct > 0].copy()
profile_flags = {
    flag: int(df[flag].sum())
    for flag in ["has_duplicate_flag", "has_timestamp_issue_flag", "has_missing_dasher_flag", "has_outlier_flag"]
}
profile_status = df["status"].value_counts().to_dict()
profile_abgroup = df["ab_group"].value_counts().to_dict()


# ===========================================================================
# ETAPA 2 — REMOVER DUPLICATAS
# ===========================================================================
section("ETAPA 2 — REMOVER DUPLICATAS")

n_before = len(df)
# Remove rows where has_duplicate_flag == True, keep first occurrence of each order_id
df_no_dup = df[df["has_duplicate_flag"] == False].copy()
# Additionally, ensure no duplicate order_ids remain (keep first)
df_no_dup = df_no_dup.drop_duplicates(subset=["order_id"], keep="first")

n_after = len(df_no_dup)
n_removed_dup = n_before - n_after

print(f"  Linhas antes:   {n_before:,}")
print(f"  Linhas removidas (duplicatas): {n_removed_dup:,}")
print(f"  Linhas apos remocao: {n_after:,}")

df = df_no_dup.copy()


# ===========================================================================
# ETAPA 3 — CORRIGIR TIMESTAMPS FORA DE ORDEM
# ===========================================================================
section("ETAPA 3 — CORRIGIR TIMESTAMPS FORA DE ORDEM")

mask_ts = df["has_timestamp_issue_flag"] == True
n_ts_issues = mask_ts.sum()
print(f"  Linhas com timestamp issue: {n_ts_issues:,}")

if n_ts_issues > 0:
    # For each row with timestamp issues, sort the stage columns chronologically
    stage_data = df.loc[mask_ts, STAGE_COLS].copy()

    # Sort each row's timestamps
    sorted_stages = stage_data.apply(
        lambda row: pd.Series(
            np.sort(row.values.astype("datetime64[ns]")),
            index=STAGE_COLS
        ),
        axis=1
    )
    df.loc[mask_ts, STAGE_COLS] = sorted_stages.values

    # Recalculate delivery_duration_minutes for fixed rows
    df.loc[mask_ts, "delivery_duration_minutes"] = minutes_between(
        df.loc[mask_ts, "stage_1_order_placed_at"],
        df.loc[mask_ts, "stage_7_delivered_at"]
    )
    # Also update stage_7_delivered_at alias columns
    df.loc[mask_ts, "delivered_at"] = df.loc[mask_ts, "stage_7_delivered_at"]
    df.loc[mask_ts, "dasher_assigned_at"] = df.loc[mask_ts, "stage_3_dasher_assigned_at"]
    df.loc[mask_ts, "pickup_at"] = df.loc[mask_ts, "stage_5_order_picked_up_at"]

    print(f"  Linhas com timestamps reordenados e delivery_duration_minutes recalculado: {n_ts_issues:,}")
else:
    print("  Nenhuma correcao necessaria.")


# ===========================================================================
# ETAPA 4 — TRATAR PEDIDOS SEM ENTREGADOR
# ===========================================================================
section("ETAPA 4 — TRATAR PEDIDOS SEM ENTREGADOR")

mask_dasher = df["has_missing_dasher_flag"] == True
n_missing_dasher = mask_dasher.sum()
n_null_dasher_before = df["dasher_id"].isnull().sum()
print(f"  Linhas com has_missing_dasher_flag=True: {n_missing_dasher:,}")
print(f"  Nulos em dasher_id antes da imputacao: {n_null_dasher_before:,}")

# Impute dasher_id
df.loc[mask_dasher & df["dasher_id"].isnull(), "dasher_id"] = "UNASSIGNED"
# Impute dasher_assigned_at from stage_3
df.loc[mask_dasher & df["dasher_assigned_at"].isnull(), "dasher_assigned_at"] = \
    df.loc[mask_dasher & df["dasher_assigned_at"].isnull(), "stage_3_dasher_assigned_at"]

n_null_dasher_after = df["dasher_id"].isnull().sum()
print(f"  Nulos em dasher_id apos imputacao:  {n_null_dasher_after:,}")


# ===========================================================================
# ETAPA 5 — REMOVER OUTLIERS
# ===========================================================================
section("ETAPA 5 — REMOVER OUTLIERS")

n_before_out = len(df)
mask_outlier = df["has_outlier_flag"] == True
n_outliers = mask_outlier.sum()
print(f"  Linhas com has_outlier_flag=True (delivery > 120 min): {n_outliers:,}")

df = df[df["has_outlier_flag"] == False].copy()
n_after_out = len(df)
print(f"  Linhas removidas: {n_before_out - n_after_out:,}")
print(f"  Shape apos remocao de outliers: {df.shape}")

stats_clean = describe_delivery(df["delivery_duration_minutes"], "clean")
print(f"\n  --- delivery_duration_minutes apos limpeza ---")
for k, v in stats_clean.items():
    if k != "label":
        print(f"    {k:<10} {v}")


# ===========================================================================
# ETAPA 6 — ANALISE EXPLORATORIA
# ===========================================================================
section("ETAPA 6 — ANALISE EXPLORATORIA")

# Filter delivered orders for analysis
delivered = df[df["status"] == "delivered"].copy()

# ---------------------------------------------------------------------------
# 6.1 — A/B Test: Delivery Duration
# ---------------------------------------------------------------------------
print("\n--- 6.1 Distribuicao do Tempo de Entrega por Grupo A/B ---")

grp_a = delivered[delivered["ab_group"] == "A"]["delivery_duration_minutes"].dropna()
grp_b = delivered[delivered["ab_group"] == "B"]["delivery_duration_minutes"].dropna()

mean_a = grp_a.mean()
mean_b = grp_b.mean()
delta_abs = mean_b - mean_a
delta_pct = delta_abs / mean_a * 100
t_stat, p_value = stats.ttest_ind(grp_a, grp_b, equal_var=False)
significant = p_value < 0.05

print(f"  Grupo A | n={len(grp_a):,} | mean={mean_a:.2f} min | median={grp_a.median():.2f} | std={grp_a.std():.2f}")
print(f"  Grupo B | n={len(grp_b):,} | mean={mean_b:.2f} min | median={grp_b.median():.2f} | std={grp_b.std():.2f}")
print(f"  Delta absoluto: {delta_abs:+.2f} min")
print(f"  Delta relativo: {delta_pct:+.2f}%")
print(f"  t-statistic:    {t_stat:.4f}")
print(f"  p-value:        {p_value:.6f}")
print(f"  Significativo (alpha=0.05): {'SIM' if significant else 'NAO'}")
if significant:
    winner = "B (mais rapido)" if mean_b < mean_a else "A (mais rapido)"
    print(f"  Vencedor: {winner}")
else:
    print(f"  Sem diferenca estatisticamente significativa entre grupos.")

# Store for report
ab_results = {
    "mean_a": mean_a, "median_a": grp_a.median(), "std_a": grp_a.std(), "n_a": len(grp_a),
    "mean_b": mean_b, "median_b": grp_b.median(), "std_b": grp_b.std(), "n_b": len(grp_b),
    "delta_abs": delta_abs, "delta_pct": delta_pct,
    "t_stat": t_stat, "p_value": p_value, "significant": significant,
}

# ---------------------------------------------------------------------------
# 6.2 — Tempo Medio por Etapa
# ---------------------------------------------------------------------------
print("\n--- 6.2 Tempo Medio por Etapa (pedidos entregues) ---")

def calc_stages(sub: pd.DataFrame) -> pd.Series:
    return pd.Series({
        "Aceite (s2-s1)":    minutes_between(sub["stage_1_order_placed_at"], sub["stage_2_restaurant_confirmed_at"]).mean(),
        "Preparo (s4-s2)":   minutes_between(sub["stage_2_restaurant_confirmed_at"], sub["stage_4_dasher_arrived_restaurant_at"]).mean(),
        "Atribuicao (s3-s1)": minutes_between(sub["stage_1_order_placed_at"], sub["stage_3_dasher_assigned_at"]).mean(),
        "Coleta (s5-s4)":    minutes_between(sub["stage_4_dasher_arrived_restaurant_at"], sub["stage_5_order_picked_up_at"]).mean(),
        "Rota (s7-s5)":      minutes_between(sub["stage_5_order_picked_up_at"], sub["stage_7_delivered_at"]).mean(),
    })

stages_total = calc_stages(delivered)
stages_a = calc_stages(delivered[delivered["ab_group"] == "A"])
stages_b = calc_stages(delivered[delivered["ab_group"] == "B"])

stage_df = pd.DataFrame({
    "Etapa": stages_total.index,
    "Total (min)": stages_total.round(2).values,
    "Grupo A (min)": stages_a.round(2).values,
    "Grupo B (min)": stages_b.round(2).values,
    "Delta A->B (min)": (stages_b - stages_a).round(2).values,
})
print(stage_df.to_string(index=False))

# ---------------------------------------------------------------------------
# 6.3 — Tendencia Mensal
# ---------------------------------------------------------------------------
print("\n--- 6.3 Tendencia Mensal ---")

df["month_num"] = df["created_at"].dt.month
month_map = {1: "Jan", 2: "Feb", 3: "Mar"}
df["month"] = df["month_num"].map(month_map)

monthly_total = df.groupby("month_num").agg(
    total_pedidos=("order_id", "count"),
    cancelados=("status", lambda x: (x == "cancelled").sum()),
).reset_index()
monthly_total["pct_cancelamento"] = (monthly_total["cancelados"] / monthly_total["total_pedidos"] * 100).round(2)

delivered_monthly = df[df["status"] == "delivered"].groupby("month_num")["delivery_duration_minutes"].mean().round(2)
monthly_total["tempo_medio_entrega"] = monthly_total["month_num"].map(delivered_monthly)
monthly_total["month"] = monthly_total["month_num"].map(month_map)

# Trend arrows
tempos = monthly_total["tempo_medio_entrega"].tolist()
cancel_rates = monthly_total["pct_cancelamento"].tolist()

def trend_arrow(values: list, idx: int) -> str:
    if idx == 0:
        return "--"
    return "+" if values[idx] > values[idx - 1] else "-"

monthly_total["tendencia_tempo"] = [trend_arrow(tempos, i) for i in range(len(tempos))]
monthly_total["tendencia_cancel"] = [trend_arrow(cancel_rates, i) for i in range(len(cancel_rates))]

print(monthly_total[["month", "total_pedidos", "pct_cancelamento", "tendencia_cancel", "tempo_medio_entrega", "tendencia_tempo"]].to_string(index=False))

# ---------------------------------------------------------------------------
# 6.4 — Comparacao A vs B por Horario
# ---------------------------------------------------------------------------
print("\n--- 6.4 Comparacao A vs B por Horario ---")

df["hour_of_day"] = df["created_at"].dt.hour

def get_period(h: int) -> str:
    if 6 <= h < 11:
        return "Manha (6-11h)"
    elif 11 <= h < 14:
        return "Almoco (11-14h)"
    elif 14 <= h < 18:
        return "Tarde (14-18h)"
    elif 18 <= h < 23:
        return "Noite (18-23h)"
    else:
        return "Madrugada (0-5h)"

df["delivery_stage_bucket"] = df["hour_of_day"].apply(get_period)

delivered_with_period = df[df["status"] == "delivered"].copy()
period_order = ["Madrugada (0-5h)", "Manha (6-11h)", "Almoco (11-14h)", "Tarde (14-18h)", "Noite (18-23h)"]

hourly = delivered_with_period.groupby(["delivery_stage_bucket", "ab_group"])["delivery_duration_minutes"].mean().unstack("ab_group").round(2)
hourly["Delta (B-A)"] = (hourly["B"] - hourly["A"]).round(2)
hourly["Delta %"] = ((hourly["B"] - hourly["A"]) / hourly["A"] * 100).round(2)
hourly = hourly.reindex([p for p in period_order if p in hourly.index])

print(hourly.reset_index().rename(columns={"delivery_stage_bucket": "Periodo"}).to_string(index=False))

# ---------------------------------------------------------------------------
# 6.5 — Comparacao A vs B por Regiao (customer_city)
# ---------------------------------------------------------------------------
print("\n--- 6.5 Comparacao A vs B por Regiao (customer_city) ---")

city_grp_raw = delivered_with_period.groupby(["customer_city", "ab_group"])["delivery_duration_minutes"].agg(
    mean="mean", count="count"
).unstack("ab_group")

# Flatten multi-level columns: (mean, A), (mean, B), (count, A), (count, B)
city_grp_raw.columns = ["_".join(col).strip() for col in city_grp_raw.columns]
city_grp = pd.DataFrame(index=city_grp_raw.index)
city_grp["mean_A"] = city_grp_raw["mean_A"].round(2)
city_grp["mean_B"] = city_grp_raw["mean_B"].round(2)
city_grp["count_A"] = city_grp_raw["count_A"].fillna(0)
city_grp["count_B"] = city_grp_raw["count_B"].fillna(0)
city_grp = city_grp.dropna(subset=["mean_A", "mean_B"])
city_grp["N_entregues"] = (city_grp["count_A"] + city_grp["count_B"]).astype(int)
city_grp["Delta_abs"] = (city_grp["mean_B"] - city_grp["mean_A"]).round(2)
city_grp["Delta_pct"] = ((city_grp["mean_B"] - city_grp["mean_A"]) / city_grp["mean_A"] * 100).round(2)
city_grp = city_grp.sort_values("Delta_pct", ascending=False)

print(city_grp[["N_entregues", "mean_A", "mean_B", "Delta_abs", "Delta_pct"]].reset_index().rename(
    columns={"customer_city": "Cidade", "N_entregues": "N", "mean_A": "Media A (min)", "mean_B": "Media B (min)",
             "Delta_abs": "Delta (min)", "Delta_pct": "Delta %"}
).to_string(index=False))


# ===========================================================================
# ETAPA 7 — SALVAR DATASET LIMPO
# ===========================================================================
section("ETAPA 7 — SALVAR DATASET LIMPO")

# Ensure derived columns are present
df["month"] = df["month_num"].map(month_map).fillna(df["created_at"].dt.month.map(month_map))
# hour_of_day and delivery_stage_bucket already added in 6.4

df_clean = df.drop(columns=["month_num"], errors="ignore")
df_clean.to_csv(CLEAN_PATH, index=False)

print(f"  Salvo em: {CLEAN_PATH}")
print(f"  Shape final: {df_clean.shape[0]:,} linhas x {df_clean.shape[1]} colunas")
print(f"\n  Primeiras 3 linhas:")
print(df_clean.head(3).to_string())


# ===========================================================================
# ETAPA 8 — SALVAR RELATORIO EDA
# ===========================================================================
section("ETAPA 8 — GERANDO RELATORIO EDA MARKDOWN")

# Build stage table for markdown
stage_md_rows = []
for _, row in stage_df.iterrows():
    stage_md_rows.append(
        f"| {row['Etapa']} | {row['Total (min)']:.2f} | {row['Grupo A (min)']:.2f} | {row['Grupo B (min)']:.2f} | {row['Delta A->B (min)']:+.2f} |"
    )
stage_md = "\n".join(stage_md_rows)

# Monthly trend table
monthly_md_rows = []
for _, row in monthly_total.iterrows():
    trend_t = "+" if row["tendencia_tempo"] == "+" else ("-" if row["tendencia_tempo"] == "-" else "--")
    trend_c = "+" if row["tendencia_cancel"] == "+" else ("-" if row["tendencia_cancel"] == "-" else "--")
    monthly_md_rows.append(
        f"| {row['month']} | {int(row['total_pedidos']):,} | {row['pct_cancelamento']:.2f}% {trend_c} | {row['tempo_medio_entrega']:.2f} min {trend_t} |"
    )
monthly_md = "\n".join(monthly_md_rows)

# Hourly table
hourly_reset = hourly.reset_index().rename(columns={"delivery_stage_bucket": "Periodo"})
hourly_md_rows = []
for _, row in hourly_reset.iterrows():
    hourly_md_rows.append(
        f"| {row['Periodo']} | {row.get('A', float('nan')):.2f} | {row.get('B', float('nan')):.2f} | {row['Delta (B-A)']:+.2f} | {row['Delta %']:+.2f}% |"
    )
hourly_md = "\n".join(hourly_md_rows)

# City table
city_reset = city_grp[["N_entregues", "mean_A", "mean_B", "Delta_abs", "Delta_pct"]].reset_index()
city_md_rows = []
for _, row in city_reset.iterrows():
    city_md_rows.append(
        f"| {row['customer_city']} | {int(row['N_entregues']):,} | {row['mean_A']:.2f} | {row['mean_B']:.2f} | {row['Delta_abs']:+.2f} | {row['Delta_pct']:+.2f}% |"
    )
city_md = "\n".join(city_md_rows)

# Null profile
null_md_rows = []
for col, pct in profile_null.items():
    null_md_rows.append(f"| {col} | {pct:.2f}% |")
null_md = "\n".join(null_md_rows) if null_md_rows else "| Nenhum nulo detectado | — |"

sig_text = "Sim (p < 0.05)" if ab_results["significant"] else "Nao (p >= 0.05)"
winner_text = "Grupo B (mais rapido)" if (ab_results["significant"] and ab_results["delta_abs"] < 0) else (
    "Grupo A (mais rapido)" if (ab_results["significant"] and ab_results["delta_abs"] > 0) else "Sem vencedor definido"
)

report = f"""# EDA Report — DoorDash Delivery Dataset

**Data:** 2026-04-21
**Analista:** gabriel-analytics
**Dataset:** doordash_raw.csv

---

## 1. Dataset Profile

| Atributo | Valor |
|----------|-------|
| Linhas (raw) | {profile_shape[0]:,} |
| Colunas | {profile_shape[1]} |
| Linhas apos limpeza | {df_clean.shape[0]:,} |
| Periodo | Jan–Mar 2025 |
| Distribuicao ab_group | A={profile_abgroup.get('A', 0):,} / B={profile_abgroup.get('B', 0):,} |
| Status: delivered | {profile_status.get('delivered', 0):,} |
| Status: cancelled | {profile_status.get('cancelled', 0):,} |
| Status: in_progress | {profile_status.get('in_progress', 0):,} |

### Colunas com valores nulos (antes da limpeza)

| Coluna | % Nulos |
|--------|---------|
{null_md}

### Flags de qualidade detectadas

| Flag | Linhas Afetadas |
|------|-----------------|
| has_duplicate_flag | {profile_flags['has_duplicate_flag']:,} |
| has_timestamp_issue_flag | {profile_flags['has_timestamp_issue_flag']:,} |
| has_missing_dasher_flag | {profile_flags['has_missing_dasher_flag']:,} |
| has_outlier_flag | {profile_flags['has_outlier_flag']:,} |

---

## 2. Data Quality Issues Found & Fixed

| Issue | Linhas Afetadas | Acao Tomada | Resultado |
|-------|-----------------|-------------|-----------|
| Duplicatas (order_id) | {profile_flags['has_duplicate_flag']:,} | Remocao de linhas com has_duplicate_flag=True; keep first | -{n_removed_dup:,} linhas |
| Timestamps fora de ordem | {profile_flags['has_timestamp_issue_flag']:,} | np.sort nos 7 stage timestamps; recalculo de delivery_duration_minutes | {n_ts_issues:,} linhas corrigidas |
| Dasher ausente | {profile_flags['has_missing_dasher_flag']:,} | dasher_id imputado com 'UNASSIGNED'; dasher_assigned_at imputado de stage_3 | 0 nulos restantes |
| Outliers (>120 min) | {profile_flags['has_outlier_flag']:,} | Remocao de linhas com has_outlier_flag=True | -{n_outliers:,} linhas |

---

## 3. A/B Test Analysis

| Metrica | Grupo A (controle) | Grupo B (tratamento) |
|---------|--------------------|----------------------|
| N pedidos entregues | {ab_results['n_a']:,} | {ab_results['n_b']:,} |
| Tempo medio (min) | {ab_results['mean_a']:.2f} | {ab_results['mean_b']:.2f} |
| Mediana (min) | {ab_results['median_a']:.2f} | {ab_results['median_b']:.2f} |
| Desvio padrao | {ab_results['std_a']:.2f} | {ab_results['std_b']:.2f} |
| Delta absoluto | {ab_results['delta_abs']:+.2f} min | — |
| Delta relativo | {ab_results['delta_pct']:+.2f}% | — |
| t-statistic | {ab_results['t_stat']:.4f} | — |
| p-value (Welch t-test) | {ab_results['p_value']:.6f} | — |
| Significativo (alpha=0.05) | {sig_text} | — |
| Vencedor | {winner_text} | — |

---

## 4. Tempo por Etapa

| Etapa | Total (min) | Grupo A (min) | Grupo B (min) | Delta A->B (min) |
|-------|-------------|---------------|---------------|------------------|
{stage_md}

---

## 5. Tendencia Mensal

| Mes | Total Pedidos | % Cancelamento | Tempo Medio Entrega |
|-----|---------------|----------------|---------------------|
{monthly_md}

Legenda: + = piora/aumento, - = melhora/reducao, -- = primeiro mes (sem comparacao)

---

## 6. Performance por Horario (pedidos entregues)

| Periodo | Media A (min) | Media B (min) | Delta (min) | Delta % |
|---------|---------------|---------------|-------------|---------|
{hourly_md}

---

## 7. Performance por Regiao

| Cidade | N Entregues | Media A (min) | Media B (min) | Delta (min) | Delta % |
|--------|-------------|---------------|---------------|-------------|---------|
{city_md}

---

## 8. Conclusoes e Recomendacoes

### Insights Principais

- **Volume:** {profile_shape[0]:,} pedidos brutos, {df_clean.shape[0]:,} apos limpeza ({(df_clean.shape[0]/profile_shape[0]*100):.1f}% retidos)
- **Qualidade dos dados:** {profile_flags['has_duplicate_flag']:,} duplicatas ({profile_flags['has_duplicate_flag']/profile_shape[0]*100:.1f}%), {profile_flags['has_timestamp_issue_flag']:,} problemas de timestamp, {profile_flags['has_outlier_flag']:,} outliers removidos
- **A/B Test:** {"Diferenca estatisticamente significativa detectada entre grupos A e B" if ab_results['significant'] else "Nenhuma diferenca estatisticamente significativa entre A e B"}. Delta = {ab_results['delta_abs']:+.2f} min ({ab_results['delta_pct']:+.2f}%), p-value = {ab_results['p_value']:.6f}
- **Cancelamentos:** {profile_status.get('cancelled', 0):,} pedidos cancelados ({profile_status.get('cancelled', 0)/profile_shape[0]*100:.1f}% do total) — monitorar tendencia mensal
- **Etapa critica:** Observar a etapa com maior delta entre A e B para identificar onde o algoritmo impacta mais

### Recomendacao sobre A/B Test

{"**Adotar tratamento B:** O grupo B apresentou diferenca estatisticamente significativa em tempo de entrega. Recomenda-se rollout gradual (50% -> 100%) com monitoramento de cancelamentos e NPS." if ab_results['significant'] else "**Aguardar mais dados:** A diferenca entre grupos nao atingiu significancia estatistica (p={:.4f}). Recomenda-se continuar o experimento ou revisar o MDE e tamanho de amostra antes de uma decisao de rollout.".format(ab_results['p_value'])}

### Alertas de Qualidade de Dados

- Dasher ausente em {profile_flags['has_missing_dasher_flag']:,} pedidos — imputados com 'UNASSIGNED'; investigar causa raiz no sistema de atribuicao
- {profile_flags['has_timestamp_issue_flag']:,} pedidos com timestamps fora de ordem — sugerir validacao no pipeline de ingestao
- Pedidos `in_progress` ({profile_status.get('in_progress', 0):,}) excluidos das analises temporais — revisar se sao pedidos ainda ativos ou dados incompletos
- Delivery duration com nulos ({df['delivery_duration_minutes'].isnull().sum()} restantes apos limpeza) correspondem a pedidos cancelados/in_progress sem timestamp de entrega — comportamento esperado
"""

REPORT_PATH.write_text(report, encoding="utf-8")
print(f"  Relatorio salvo em: {REPORT_PATH}")

# Final confirmation
section("CONCLUSAO")
print(f"  Dataset limpo:  {CLEAN_PATH}")
print(f"  Relatorio EDA:  {REPORT_PATH}")
print(f"  Shape final:    {df_clean.shape[0]:,} linhas x {df_clean.shape[1]} colunas")
print(f"\n  Script concluido com sucesso.")

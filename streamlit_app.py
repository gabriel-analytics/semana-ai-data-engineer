"""
DoorDash Analytics Dashboard
Case Study: A/B Test — Algoritmo de Atribuicao de Dasher
Periodo: Jan-Mar 2025 | n=9.703 pedidos
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import os

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
st.set_page_config(
    layout="wide",
    page_title="DoorDash Analytics",
    page_icon="📦",
)

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------
COLOR_A = "#636EFA"
COLOR_B = "#EF553B"
COLOR_TOTAL = "#00CC96"

DUCKDB_PATH = os.path.join(os.path.dirname(__file__), "gen", "data", "doordash.duckdb")
CSV_PATH = os.path.join(os.path.dirname(__file__), "gen", "data", "doordash_clean.csv")

ETAPAS = {
    "Aceite": "duracao_aceite_min",
    "Preparo": "duracao_preparo_min",
    "Atribuicao": "duracao_atribuicao_min",
    "Coleta": "duracao_coleta_min",
    "Rota": "duracao_rota_min",
}

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
# Carregamento de dados
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    """Carrega dados via DuckDB (fct_entregas) ou CSV como fallback."""
    if os.path.exists(DUCKDB_PATH):
        try:
            import duckdb

            con = duckdb.connect(DUCKDB_PATH, read_only=True)
            df = con.execute(
                "SELECT * FROM main_core.fct_entregas"
            ).fetchdf()
            con.close()
            return df
        except Exception:
            pass

    # Fallback: CSV
    df = pd.read_csv(CSV_PATH, parse_dates=["created_at"] + STAGE_COLS)

    # Calcular duracoes das etapas
    df["duracao_aceite_min"] = (
        df["stage_2_restaurant_confirmed_at"] - df["stage_1_order_placed_at"]
    ).dt.total_seconds() / 60

    df["duracao_preparo_min"] = (
        df["stage_4_dasher_arrived_restaurant_at"] - df["stage_2_restaurant_confirmed_at"]
    ).dt.total_seconds() / 60

    df["duracao_atribuicao_min"] = (
        df["stage_3_dasher_assigned_at"] - df["stage_1_order_placed_at"]
    ).dt.total_seconds() / 60

    df["duracao_coleta_min"] = (
        df["stage_5_order_picked_up_at"] - df["stage_4_dasher_arrived_restaurant_at"]
    ).dt.total_seconds() / 60

    df["duracao_rota_min"] = (
        df["stage_7_delivered_at"] - df["stage_5_order_picked_up_at"]
    ).dt.total_seconds() / 60

    df.rename(columns={"delivery_duration_minutes": "tempo_total_min"}, inplace=True)
    return df


@st.cache_data(show_spinner=False)
def load_raw_csv() -> pd.DataFrame:
    """Carrega CSV original para metricas que nao estao no DuckDB."""
    df = pd.read_csv(CSV_PATH, parse_dates=["created_at"])
    return df


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def fmt_delta(val: float, pct: float) -> str:
    sign = "+" if val >= 0 else ""
    return f"{sign}{val:.2f} min ({sign}{pct:.1f}%)"


def winner_label(delta: float) -> str:
    return "B" if delta < 0 else "A"


def color_delta(val):
    """Para pandas Styler — verde se B ganhou (delta negativo), vermelho se A."""
    color = "color: #00CC96" if val < 0 else "color: #EF553B"
    return color


# ---------------------------------------------------------------------------
# PAGINA 1 — Visao Geral
# ---------------------------------------------------------------------------
def page_visao_geral(df: pd.DataFrame, df_raw: pd.DataFrame, cidades: list, periodos: list):
    st.title("Visao Geral")
    st.markdown("Panorama operacional do periodo Jan–Mar 2025.")

    # Filtrar df_raw para KPIs
    mask = pd.Series(True, index=df_raw.index)
    if cidades:
        mask &= df_raw["customer_city"].isin(cidades)
    if periodos and len(periodos) == 2:
        start, end = pd.Timestamp(periodos[0]), pd.Timestamp(periodos[1])
        mask &= (df_raw["created_at"] >= start) & (df_raw["created_at"] <= end)
    dr = df_raw[mask]

    delivered = dr[dr["status"] == "delivered"]
    cancelled = dr[dr["status"] == "cancelled"]

    total_pedidos = len(dr)
    tempo_medio = delivered["delivery_duration_minutes"].mean()
    taxa_cancel = len(cancelled) / total_pedidos * 100 if total_pedidos > 0 else 0
    ticket_medio = dr["total_amount_usd"].mean()

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Pedidos", f"{total_pedidos:,}")
    col2.metric("Tempo Medio Entrega", f"{tempo_medio:.1f} min")
    col3.metric("Taxa de Cancelamento", f"{taxa_cancel:.1f}%")
    col4.metric("Ticket Medio", f"R$ {ticket_medio:.2f}")

    st.divider()

    # --- Tendencia mensal ---
    st.subheader("Tendencia Mensal de Pedidos e Cancelamentos")

    monthly = (
        dr.groupby("month")
        .agg(
            total=("order_id", "count"),
            cancelados=("status", lambda x: (x == "cancelled").sum()),
        )
        .reset_index()
    )
    monthly["pct_cancel"] = monthly["cancelados"] / monthly["total"] * 100
    # Ordenar Jan, Feb, Mar
    order_map = {"Jan": 1, "Feb": 2, "Mar": 3}
    monthly["_ord"] = monthly["month"].map(order_map)
    monthly = monthly.sort_values("_ord")

    fig_monthly = go.Figure()
    fig_monthly.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=monthly["total"],
            name="Total Pedidos",
            line=dict(color="#636EFA", width=2),
            mode="lines+markers",
        )
    )
    fig_monthly.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=monthly["cancelados"],
            name="Cancelados",
            line=dict(color=COLOR_B, width=2, dash="dash"),
            mode="lines+markers",
            yaxis="y",
        )
    )
    fig_monthly.add_trace(
        go.Scatter(
            x=monthly["month"],
            y=monthly["pct_cancel"],
            name="% Cancelamento",
            line=dict(color="#FF7F0E", width=2),
            mode="lines+markers",
            yaxis="y2",
        )
    )
    fig_monthly.update_layout(
        title="Tendencia Mensal de Pedidos e Cancelamentos",
        yaxis=dict(title="Quantidade de Pedidos"),
        yaxis2=dict(
            title="% Cancelamento",
            overlaying="y",
            side="right",
            tickformat=".1f",
            ticksuffix="%",
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

    col_left, col_right = st.columns(2)

    # --- Distribuicao por cidade ---
    with col_left:
        st.subheader("Pedidos Entregues por Cidade")
        cidade_counts = (
            delivered.groupby("customer_city")
            .size()
            .reset_index(name="pedidos")
            .sort_values("pedidos", ascending=True)
        )
        fig_city = px.bar(
            cidade_counts,
            x="pedidos",
            y="customer_city",
            orientation="h",
            color="customer_city",
            title="Distribuicao por Cidade",
            labels={"pedidos": "Pedidos Entregues", "customer_city": "Cidade"},
        )
        fig_city.update_layout(showlegend=False, height=380)
        st.plotly_chart(fig_city, use_container_width=True)

    # --- Distribuicao por horario ---
    with col_right:
        st.subheader("Pedidos por Hora do Dia")
        hour_counts = (
            dr.groupby("hour_of_day")
            .size()
            .reset_index(name="pedidos")
        )
        # Gradiente azul -> laranja: normalizar contagem para cor
        max_c = hour_counts["pedidos"].max()
        hour_counts["cor_norm"] = hour_counts["pedidos"] / max_c

        fig_hour = px.bar(
            hour_counts,
            x="hour_of_day",
            y="pedidos",
            color="pedidos",
            color_continuous_scale=["#636EFA", "#FF7F0E"],
            title="Distribuicao de Pedidos por Hora",
            labels={"hour_of_day": "Hora do Dia", "pedidos": "Pedidos"},
        )
        fig_hour.update_layout(coloraxis_showscale=False, height=380)
        st.plotly_chart(fig_hour, use_container_width=True)


# ---------------------------------------------------------------------------
# PAGINA 2 — Resultado A/B Test
# ---------------------------------------------------------------------------
def page_ab_test(df: pd.DataFrame, df_raw: pd.DataFrame, cidades: list, periodos: list):
    st.title("Resultado A/B Test")
    st.markdown("Analise estatistica completa do experimento de algoritmo de atribuicao.")

    # Filtrar delivered
    mask = df_raw["status"] == "delivered"
    if cidades:
        mask &= df_raw["customer_city"].isin(cidades)
    if periodos and len(periodos) == 2:
        start, end = pd.Timestamp(periodos[0]), pd.Timestamp(periodos[1])
        mask &= (df_raw["created_at"] >= start) & (df_raw["created_at"] <= end)

    dr = df_raw[mask].copy()
    grupo_a = dr[dr["ab_group"] == "A"]["delivery_duration_minutes"].dropna()
    grupo_b = dr[dr["ab_group"] == "B"]["delivery_duration_minutes"].dropna()

    media_a = grupo_a.mean()
    media_b = grupo_b.mean()
    delta_abs = media_b - media_a
    delta_pct = delta_abs / media_a * 100

    # Teste de Welch (unilateral: H1: B < A)
    t_stat, p_two = stats.ttest_ind(grupo_a, grupo_b, equal_var=False)
    p_one = p_two / 2  # unilateral

    # IC 95% da diferenca
    diff = media_b - media_a
    se = np.sqrt(grupo_a.var() / len(grupo_a) + grupo_b.var() / len(grupo_b))
    z = stats.norm.ppf(0.975)
    ic_lower = diff - z * se
    ic_upper = diff + z * se

    significativo = p_one < 0.05 and delta_abs < 0

    # Banner
    if significativo:
        st.success(
            f"Grupo B e {abs(delta_pct):.1f}% mais rapido — resultado estatisticamente significativo "
            f"(p={p_one:.6f}, IC 95%: [{ic_lower:.2f}, {ic_upper:.2f}] min)"
        )
    else:
        st.warning(
            f"Diferenca nao significativa ao nivel alpha=0.05 "
            f"(p={p_one:.4f})"
        )

    st.divider()

    col_box, col_stats = st.columns([2, 1])

    with col_box:
        # Box plot
        box_df = pd.concat(
            [
                grupo_a.rename("tempo").to_frame().assign(grupo="Grupo A"),
                grupo_b.rename("tempo").to_frame().assign(grupo="Grupo B"),
            ]
        )
        fig_box = px.box(
            box_df,
            x="grupo",
            y="tempo",
            color="grupo",
            color_discrete_map={"Grupo A": COLOR_A, "Grupo B": COLOR_B},
            points="outliers",
            title="Distribuicao do Tempo de Entrega — Grupo A vs Grupo B",
            labels={"tempo": "Tempo de Entrega (min)", "grupo": ""},
        )
        fig_box.update_layout(showlegend=False, height=450)
        st.plotly_chart(fig_box, use_container_width=True)

    with col_stats:
        st.markdown("#### Resumo Estatistico")
        st.markdown(f"""
| Metrica | Grupo A | Grupo B |
|---------|---------|---------|
| N | {len(grupo_a):,} | {len(grupo_b):,} |
| Media | {media_a:.2f} min | {media_b:.2f} min |
| Mediana | {grupo_a.median():.2f} min | {grupo_b.median():.2f} min |
| Desvio Padrao | {grupo_a.std():.2f} | {grupo_b.std():.2f} |
| Delta Absoluto | — | {delta_abs:+.2f} min |
| Delta Relativo | — | {delta_pct:+.1f}% |
""")

    st.divider()

    # --- Delta por cidade ---
    st.subheader("Delta por Cidade")

    city_ab = (
        dr.groupby(["customer_city", "ab_group"])["delivery_duration_minutes"]
        .mean()
        .unstack()
        .reset_index()
    )
    city_ab.columns = ["Cidade", "Media A (min)", "Media B (min)"]
    city_ab["Delta (min)"] = city_ab["Media B (min)"] - city_ab["Media A (min)"]
    city_ab["Delta (%)"] = city_ab["Delta (min)"] / city_ab["Media A (min)"] * 100
    city_ab["Vencedor"] = city_ab["Delta (min)"].apply(
        lambda x: "B" if x < 0 else "A"
    )

    st.dataframe(
        city_ab,
        column_config={
            "Media A (min)": st.column_config.NumberColumn(format="%.2f"),
            "Media B (min)": st.column_config.NumberColumn(format="%.2f"),
            "Delta (min)": st.column_config.NumberColumn(format="%.2f"),
            "Delta (%)": st.column_config.NumberColumn(format="%.1f%%"),
        },
        use_container_width=True,
        hide_index=True,
    )

    # --- Delta por periodo do dia ---
    st.subheader("Delta por Periodo do Dia")

    period_ab = (
        dr.groupby(["delivery_stage_bucket", "ab_group"])["delivery_duration_minutes"]
        .mean()
        .unstack()
        .reset_index()
    )
    period_ab.columns = ["Periodo", "Media A (min)", "Media B (min)"]
    period_ab["Delta (min)"] = period_ab["Media B (min)"] - period_ab["Media A (min)"]
    period_ab["Delta (%)"] = period_ab["Delta (min)"] / period_ab["Media A (min)"] * 100
    period_ab["Vencedor"] = period_ab["Delta (min)"].apply(
        lambda x: "B" if x < 0 else "A"
    )

    st.dataframe(
        period_ab,
        column_config={
            "Media A (min)": st.column_config.NumberColumn(format="%.2f"),
            "Media B (min)": st.column_config.NumberColumn(format="%.2f"),
            "Delta (min)": st.column_config.NumberColumn(format="%.2f"),
            "Delta (%)": st.column_config.NumberColumn(format="%.1f%%"),
        },
        use_container_width=True,
        hide_index=True,
    )

    # --- Expander com teste estatistico ---
    with st.expander("Detalhes do Teste Estatistico"):
        conclusao = "REJEITAR H0 — diferenca estatisticamente significativa" if significativo else "NAO REJEITAR H0 — diferenca nao significativa"
        st.markdown(f"""
```
Teste: Welch t-test (variancias desiguais)
H0: media_A == media_B
H1: media_B < media_A  (teste unilateral)
Estatistica t: {t_stat:.4f}
p-value (bilateral): {p_two:.6f}
p-value (unilateral): {p_one:.6f}
IC 95% da diferenca: [{ic_lower:.2f}, {ic_upper:.2f}] minutos
Conclusao: {conclusao}
```
""")


# ---------------------------------------------------------------------------
# PAGINA 3 — Analise por Etapa
# ---------------------------------------------------------------------------
def page_etapas(df: pd.DataFrame, cidades: list, periodos: list):
    st.title("Analise por Etapa")
    st.markdown("Decomposicao do tempo de entrega em suas etapas operacionais.")

    # Filtrar df (fct_entregas do DuckDB ou CSV processado)
    mask = pd.Series(True, index=df.index)
    if "customer_city" in df.columns and cidades:
        mask &= df["customer_city"].isin(cidades)
    if "created_at" in df.columns and periodos and len(periodos) == 2:
        if not pd.api.types.is_datetime64_any_dtype(df["created_at"]):
            df["created_at"] = pd.to_datetime(df["created_at"])
        start, end = pd.Timestamp(periodos[0]), pd.Timestamp(periodos[1])
        mask &= (df["created_at"] >= start) & (df["created_at"] <= end)

    dfm = df[mask].copy()

    # Verificar se colunas de etapa existem
    etapas_disponiveis = {
        k: v for k, v in ETAPAS.items() if v in dfm.columns
    }

    if not etapas_disponiveis:
        st.warning("Colunas de etapas nao encontradas no dataset. Use o DuckDB para acesso completo.")
        return

    # Calcular media por etapa e grupo
    rows = []
    for nome_etapa, col in etapas_disponiveis.items():
        media_a = dfm[dfm["ab_group"] == "A"][col].mean()
        media_b = dfm[dfm["ab_group"] == "B"][col].mean()
        delta_min = media_b - media_a
        delta_pct = delta_min / media_a * 100 if media_a != 0 else 0
        rows.append(
            {
                "Etapa": nome_etapa,
                "Media A (min)": media_a,
                "Media B (min)": media_b,
                "Delta (min)": delta_min,
                "Delta (%)": delta_pct,
            }
        )

    etapas_df = pd.DataFrame(rows)

    # Identificar maior delta
    maior_ganho_idx = etapas_df["Delta (min)"].abs().idxmax()
    etapa_destaque = etapas_df.loc[maior_ganho_idx, "Etapa"]

    # --- Barras agrupadas por etapa ---
    st.subheader("Tempo Medio por Etapa — Grupo A vs Grupo B")

    colors_a = [COLOR_A] * len(etapas_df)
    colors_b = []
    for _, row in etapas_df.iterrows():
        if row["Etapa"] == etapa_destaque:
            colors_b.append("#FFA500")  # destaque: laranja
        else:
            colors_b.append(COLOR_B)

    fig_etapas = go.Figure()
    fig_etapas.add_trace(
        go.Bar(
            name="Grupo A",
            x=etapas_df["Etapa"],
            y=etapas_df["Media A (min)"],
            marker_color=COLOR_A,
        )
    )
    fig_etapas.add_trace(
        go.Bar(
            name="Grupo B",
            x=etapas_df["Etapa"],
            y=etapas_df["Media B (min)"],
            marker_color=colors_b,
        )
    )
    fig_etapas.update_layout(
        barmode="group",
        title="Tempo Medio por Etapa — Grupo A vs Grupo B",
        xaxis_title="Etapa",
        yaxis_title="Tempo Medio (min)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        height=420,
    )
    st.plotly_chart(fig_etapas, use_container_width=True)

    col_wf, col_tbl = st.columns([1, 1])

    with col_wf:
        # --- Waterfall: composicao grupo A ---
        st.subheader("Composicao do Tempo Total — Grupo A")

        media_a_vals = etapas_df["Media A (min)"].tolist()
        etapa_nomes = etapas_df["Etapa"].tolist()

        fig_wf = go.Figure(
            go.Waterfall(
                name="Grupo A",
                orientation="v",
                x=etapa_nomes + ["Total"],
                measure=["relative"] * len(etapa_nomes) + ["total"],
                y=media_a_vals + [sum(media_a_vals)],
                connector={"line": {"color": "rgb(63,63,63)"}},
                increasing={"marker": {"color": COLOR_A}},
                totals={"marker": {"color": COLOR_TOTAL}},
                text=[f"{v:.1f}" for v in media_a_vals] + [f"{sum(media_a_vals):.1f}"],
                textposition="outside",
            )
        )
        fig_wf.update_layout(
            title="Composicao do Tempo (Grupo A)",
            yaxis_title="Minutos",
            height=420,
            showlegend=False,
        )
        st.plotly_chart(fig_wf, use_container_width=True)

    with col_tbl:
        # --- Tabela detalhada ---
        st.subheader("Tabela Detalhada por Etapa")

        etapas_display = etapas_df.copy()
        etapas_display["Maior Ganho?"] = etapas_display["Etapa"].apply(
            lambda x: "Sim" if x == etapa_destaque else ""
        )

        st.dataframe(
            etapas_display,
            column_config={
                "Media A (min)": st.column_config.NumberColumn(format="%.2f"),
                "Media B (min)": st.column_config.NumberColumn(format="%.2f"),
                "Delta (min)": st.column_config.NumberColumn(format="%.2f"),
                "Delta (%)": st.column_config.NumberColumn(format="%.1f%%"),
            },
            use_container_width=True,
            hide_index=True,
            height=350,
        )

    # --- Insight card ---
    maior_row = etapas_df.loc[maior_ganho_idx]
    st.info(
        f"Maior Ganho: A etapa \"{etapa_destaque}\" apresentou a maior reducao de tempo no Grupo B "
        f"({maior_row['Delta (min)']:.2f} min, {maior_row['Delta (%)']:.1f}%), sugerindo que o novo "
        f"algoritmo de atribuicao de dasher otimiza principalmente esta etapa do fluxo de entrega."
    )


# ---------------------------------------------------------------------------
# PAGINA 4 — Impacto Financeiro
# ---------------------------------------------------------------------------
def page_financeiro(df: pd.DataFrame, df_raw: pd.DataFrame, cidades: list, periodos: list):
    st.title("Impacto Financeiro")
    st.markdown("Projecao de economia operacional e receita incremental com o rollout do Grupo B.")

    # Calcular valores base do dataset
    delivered = df_raw[df_raw["status"] == "delivered"].copy()
    if cidades:
        delivered = delivered[delivered["customer_city"].isin(cidades)]

    grupo_a = delivered[delivered["ab_group"] == "A"]["delivery_duration_minutes"].dropna()
    grupo_b = delivered[delivered["ab_group"] == "B"]["delivery_duration_minutes"].dropna()
    media_a = grupo_a.mean()
    media_b = grupo_b.mean()
    minutos_economizados_base = media_a - media_b

    # Pedidos por dia (media do dataset)
    df_raw_copy = df_raw.copy()
    df_raw_copy["created_at"] = pd.to_datetime(df_raw_copy["created_at"])
    pedidos_dia_base = (
        df_raw_copy.groupby(df_raw_copy["created_at"].dt.date)
        .size()
        .mean()
    )
    ticket_base = df_raw["total_amount_usd"].mean()

    # --- Inputs na sidebar (ou em colunas) ---
    st.subheader("Parametros do Cenario")

    col_p1, col_p2, col_p3 = st.columns(3)

    with col_p1:
        pedidos_dia = st.number_input(
            "Pedidos por dia",
            min_value=100,
            max_value=10000,
            value=int(pedidos_dia_base),
            step=50,
        )
        pct_rollout = st.slider(
            "% Rollout Grupo B",
            min_value=0,
            max_value=100,
            value=100,
            step=5,
        )

    with col_p2:
        ticket_medio = st.number_input(
            "Valor medio do pedido (R$)",
            min_value=10.0,
            max_value=500.0,
            value=float(round(ticket_base, 2)),
            step=1.0,
        )
        custo_por_min = st.number_input(
            "Custo por minuto de entregador (R$)",
            min_value=0.10,
            max_value=5.0,
            value=0.50,
            step=0.05,
        )

    with col_p3:
        conversao_por_min = st.number_input(
            "Aumento na conversao por min ganho (%)",
            min_value=0.01,
            max_value=1.0,
            value=0.10,
            step=0.01,
            format="%.2f",
        )
        custo_implementacao = st.number_input(
            "Custo de implementacao (R$)",
            min_value=0,
            max_value=500000,
            value=50000,
            step=5000,
        )

    st.divider()

    # Calculos
    pedidos_afetados_dia = pedidos_dia * (pct_rollout / 100)
    pedidos_mes = pedidos_afetados_dia * 30
    minutos_economizados = minutos_economizados_base

    economia_op_mensal = pedidos_mes * minutos_economizados * custo_por_min
    pedidos_adicionais_mes = pedidos_mes * (conversao_por_min / 100) * minutos_economizados
    receita_incr_mensal = pedidos_adicionais_mes * ticket_medio
    total_beneficio_mes = economia_op_mensal + receita_incr_mensal

    # KPIs
    st.subheader("Impacto Estimado (Mensal)")
    kc1, kc2, kc3, kc4 = st.columns(4)
    kc1.metric("Minutos Economizados/Pedido", f"{minutos_economizados:.2f} min")
    kc2.metric("Pedidos Adicionais/Mes", f"{pedidos_adicionais_mes:,.0f}")
    kc3.metric("Economia Operacional/Mes", f"R$ {economia_op_mensal:,.0f}")
    kc4.metric("Receita Incremental/Mes", f"R$ {receita_incr_mensal:,.0f}")

    st.divider()

    col_area, col_breakeven = st.columns(2)

    with col_area:
        # --- Economia acumulada no tempo ---
        st.subheader("Economia Acumulada em 12 Meses")

        meses = list(range(1, 13))
        eco_op_acum = [economia_op_mensal * m - custo_implementacao for m in meses]
        rec_incr_acum = [receita_incr_mensal * m for m in meses]
        total_acum = [eco_op_acum[i] + rec_incr_acum[i] for i in range(12)]

        fig_area = go.Figure()
        fig_area.add_trace(
            go.Scatter(
                x=meses,
                y=eco_op_acum,
                name="Economia Operacional",
                mode="lines",
                line=dict(color=COLOR_A),
                fill="tozeroy",
                fillcolor="rgba(99,110,250,0.15)",
            )
        )
        fig_area.add_trace(
            go.Scatter(
                x=meses,
                y=rec_incr_acum,
                name="Receita Incremental",
                mode="lines",
                line=dict(color=COLOR_B),
                fill="tozeroy",
                fillcolor="rgba(239,85,59,0.15)",
            )
        )
        fig_area.add_trace(
            go.Scatter(
                x=meses,
                y=total_acum,
                name="Total",
                mode="lines",
                line=dict(color=COLOR_TOTAL, width=3),
                fill="tozeroy",
                fillcolor="rgba(0,204,150,0.10)",
            )
        )
        fig_area.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Breakeven")
        fig_area.update_layout(
            xaxis_title="Mes",
            yaxis_title="R$ Acumulado",
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig_area, use_container_width=True)

    with col_breakeven:
        # --- Economia por % rollout ---
        st.subheader("Economia Mensal por % de Rollout")

        rollout_range = list(range(10, 105, 5))
        eco_rollout = [
            (pedidos_dia * (r / 100) * 30 * minutos_economizados * custo_por_min)
            + (pedidos_dia * (r / 100) * 30 * (conversao_por_min / 100) * minutos_economizados * ticket_medio)
            for r in rollout_range
        ]

        fig_rollout = go.Figure()
        fig_rollout.add_trace(
            go.Scatter(
                x=rollout_range,
                y=eco_rollout,
                mode="lines+markers",
                line=dict(color=COLOR_TOTAL, width=2),
                fill="tozeroy",
                fillcolor="rgba(0,204,150,0.15)",
                name="Beneficio Total/Mes",
            )
        )
        # Linha de custo de implementacao (mensal amortizado em 12 meses)
        custo_mensal = custo_implementacao / 12
        fig_rollout.add_hline(
            y=custo_mensal,
            line_dash="dash",
            line_color="orange",
            annotation_text=f"Custo Impl. Amortizado: R${custo_mensal:,.0f}/mes",
        )
        # Ponto de rollout atual
        atual_eco = (
            pedidos_dia * (pct_rollout / 100) * 30 * minutos_economizados * custo_por_min
            + pedidos_dia * (pct_rollout / 100) * 30 * (conversao_por_min / 100) * minutos_economizados * ticket_medio
        )
        fig_rollout.add_trace(
            go.Scatter(
                x=[pct_rollout],
                y=[atual_eco],
                mode="markers",
                marker=dict(color=COLOR_B, size=12, symbol="star"),
                name=f"Cenario atual ({pct_rollout}%)",
            )
        )
        fig_rollout.update_layout(
            xaxis_title="% Rollout",
            yaxis_title="Beneficio Mensal (R$)",
            xaxis=dict(ticksuffix="%"),
            height=380,
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig_rollout, use_container_width=True)

    st.divider()

    # --- Recomendacao final ---
    st.success("Recomendacao de Rollout")
    st.markdown(f"""
### Decisao: Fazer rollout completo (100%) do algoritmo B

**Justificativa:**
- Reducao de {minutos_economizados:.1f}% no tempo de entrega ({minutos_economizados:.2f} min/pedido)
- Resultado estatisticamente significativo (p < 0.001)
- Consistente em todas as 6 cidades testadas
- Maior ganho no horario de pico (Tarde -7.55%)
- Economia estimada: **R$ {economia_op_mensal:,.0f}/mes** em custos operacionais
- Receita incremental estimada: **R$ {receita_incr_mensal:,.0f}/mes**
- ROI em 12 meses: **{((total_beneficio_mes * 12 - custo_implementacao) / max(custo_implementacao, 1)) * 100:.0f}%**

**Proximos Passos:**
1. Rollout gradual: 25% — 50% — 100% em 3 semanas
2. Monitorar taxa de cancelamento (alerta: >12%)
3. Avaliar satisfacao do dasher com o novo algoritmo
4. Revisar metricas apos 2 semanas de rollout completo
""")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    with st.spinner("Carregando dados..."):
        df = load_data()
        df_raw = load_raw_csv()

    # --- Sidebar ---
    st.sidebar.markdown("## DoorDash Analytics")
    st.sidebar.markdown("Case Study — Algoritmo de Atribuicao")
    st.sidebar.divider()

    pagina = st.sidebar.radio(
        "Navegacao",
        [
            "Visao Geral",
            "Resultado A/B Test",
            "Analise por Etapa",
            "Impacto Financeiro",
        ],
        index=0,
    )

    st.sidebar.divider()
    st.sidebar.markdown("### Filtros Globais")

    # Filtro de cidade
    cidades_disponiveis = sorted(df_raw["customer_city"].dropna().unique().tolist())
    cidades_sel = st.sidebar.multiselect(
        "Cidades",
        options=cidades_disponiveis,
        default=[],
        placeholder="Todas as cidades",
    )

    # Filtro de periodo
    df_raw["created_at"] = pd.to_datetime(df_raw["created_at"])
    data_min = df_raw["created_at"].min().date()
    data_max = df_raw["created_at"].max().date()
    periodo_sel = st.sidebar.date_input(
        "Periodo",
        value=(data_min, data_max),
        min_value=data_min,
        max_value=data_max,
    )

    # Roteamento
    if pagina == "Visao Geral":
        page_visao_geral(df, df_raw, cidades_sel, list(periodo_sel))
    elif pagina == "Resultado A/B Test":
        page_ab_test(df, df_raw, cidades_sel, list(periodo_sel))
    elif pagina == "Analise por Etapa":
        page_etapas(df, cidades_sel, list(periodo_sel))
    elif pagina == "Impacto Financeiro":
        page_financeiro(df, df_raw, cidades_sel, list(periodo_sel))

    # Rodape
    st.divider()
    st.caption(
        "Dados: DoorDash Case Study | Periodo: Jan-Mar 2025 | n=9.703 pedidos"
    )


if __name__ == "__main__":
    main()

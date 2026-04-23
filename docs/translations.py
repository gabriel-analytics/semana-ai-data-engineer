"""
translations.py — PT/EN strings for the DoorDash Analytics Dashboard.
Every hardcoded UI string in streamlit_app.py must have a key here.
"""

TRANSLATIONS = {
    "pt": {
        # --- Sidebar ---
        "sidebar_title": "DoorDash Analytics",
        "sidebar_subtitle": "Case Study — Algoritmo de Atribuicao",
        "nav_label": "Navegacao",
        "nav_visao_geral": "Visao Geral",
        "nav_ab_test": "Resultado A/B Test",
        "nav_etapas": "Analise por Etapa",
        "nav_financeiro": "Impacto Financeiro",
        "filtros_globais": "Filtros Globais",
        "filtro_cidades": "Cidades",
        "filtro_cidades_placeholder": "Todas as cidades",
        "filtro_periodo": "Periodo",
        # --- Spinner ---
        "carregando": "Carregando dados...",
        # --- Footer ---
        "footer": "Dados: DoorDash Case Study | Periodo: Jan-Mar 2025 | n=9.703 pedidos",
        # ----------------------------------------------------------------
        # PAGE 1 — Visao Geral
        # ----------------------------------------------------------------
        "pg1_title": "Visao Geral",
        "pg1_subtitle": "Panorama operacional do periodo Jan\u2013Mar 2025.",
        # KPI labels
        "kpi_total_pedidos": "Total Pedidos",
        "kpi_tempo_medio": "Tempo Medio Entrega",
        "kpi_taxa_cancel": "Taxa de Cancelamento",
        "kpi_ticket_medio": "Ticket Medio",
        # Monthly chart
        "pg1_mensal_header": "Tendencia Mensal de Pedidos e Cancelamentos",
        "pg1_mensal_title": "Tendencia Mensal de Pedidos e Cancelamentos",
        "pg1_mensal_total": "Total Pedidos",
        "pg1_mensal_cancelados": "Cancelados",
        "pg1_mensal_pct": "% Cancelamento",
        "pg1_mensal_yaxis": "Quantidade de Pedidos",
        "pg1_mensal_y2axis": "% Cancelamento",
        # City chart
        "pg1_cidade_header": "Pedidos Entregues por Cidade",
        "pg1_cidade_title": "Distribuicao por Cidade",
        "pg1_cidade_x": "Pedidos Entregues",
        "pg1_cidade_y": "Cidade",
        # Hour chart
        "pg1_hora_header": "Pedidos por Hora do Dia",
        "pg1_hora_title": "Distribuicao de Pedidos por Hora",
        "pg1_hora_x": "Hora do Dia",
        "pg1_hora_y": "Pedidos",
        # ----------------------------------------------------------------
        # PAGE 2 — A/B Test
        # ----------------------------------------------------------------
        "pg2_title": "Resultado A/B Test",
        "pg2_subtitle": "Analise estatistica completa do experimento de algoritmo de atribuicao.",
        # Banners
        "pg2_banner_sig": "Grupo B e {pct:.1f}% mais rapido \u2014 resultado estatisticamente significativo (p={p:.6f}, IC 95%: [{lo:.2f}, {hi:.2f}] min)",
        "pg2_banner_nosig": "Diferenca nao significativa ao nivel alpha=0.05 (p={p:.4f})",
        # Box plot
        "pg2_box_title": "Distribuicao do Tempo de Entrega \u2014 Grupo A vs Grupo B",
        "pg2_box_y": "Tempo de Entrega (min)",
        "pg2_box_x": "",
        "pg2_grupo_a": "Grupo A",
        "pg2_grupo_b": "Grupo B",
        # Stats table
        "pg2_stats_header": "#### Resumo Estatistico",
        "pg2_stats_metrica": "Metrica",
        "pg2_stats_n": "N",
        "pg2_stats_media": "Media",
        "pg2_stats_mediana": "Mediana",
        "pg2_stats_std": "Desvio Padrao",
        "pg2_stats_delta_abs": "Delta Absoluto",
        "pg2_stats_delta_rel": "Delta Relativo",
        # Subheaders
        "pg2_cidade_header": "Delta por Cidade",
        "pg2_periodo_header": "Delta por Periodo do Dia",
        # Table column names
        "tbl_cidade": "Cidade",
        "tbl_periodo": "Periodo",
        "tbl_media_a": "Media A (min)",
        "tbl_media_b": "Media B (min)",
        "tbl_delta_min": "Delta (min)",
        "tbl_delta_pct": "Delta (%)",
        "tbl_vencedor": "Vencedor",
        # Expander
        "pg2_expander": "Detalhes do Teste Estatistico",
        "pg2_conclusao_sig": "REJEITAR H0 \u2014 diferenca estatisticamente significativa",
        "pg2_conclusao_nosig": "NAO REJEITAR H0 \u2014 diferenca nao significativa",
        # ----------------------------------------------------------------
        # PAGE 3 — Etapas
        # ----------------------------------------------------------------
        "pg3_title": "Analise por Etapa",
        "pg3_subtitle": "Decomposicao do tempo de entrega em suas etapas operacionais.",
        "pg3_no_cols": "Colunas de etapas nao encontradas no dataset. Use o DuckDB para acesso completo.",
        # Bar chart
        "pg3_bar_header": "Tempo Medio por Etapa \u2014 Grupo A vs Grupo B",
        "pg3_bar_title": "Tempo Medio por Etapa \u2014 Grupo A vs Grupo B",
        "pg3_bar_xaxis": "Etapa",
        "pg3_bar_yaxis": "Tempo Medio (min)",
        "pg3_grupo_a": "Grupo A",
        "pg3_grupo_b": "Grupo B",
        # Waterfall
        "pg3_wf_header": "Composicao do Tempo Total \u2014 Grupo A",
        "pg3_wf_title": "Composicao do Tempo (Grupo A)",
        "pg3_wf_yaxis": "Minutos",
        "pg3_wf_total": "Total",
        # Table
        "pg3_tbl_header": "Tabela Detalhada por Etapa",
        "pg3_tbl_etapa": "Etapa",
        "pg3_tbl_maior_ganho": "Maior Ganho?",
        "pg3_tbl_sim": "Sim",
        # Insight
        "pg3_insight": 'Maior Ganho: A etapa "{etapa}" apresentou a maior reducao de tempo no Grupo B ({delta_min:.2f} min, {delta_pct:.1f}%), sugerindo que o novo algoritmo de atribuicao de dasher otimiza principalmente esta etapa do fluxo de entrega.',
        # ETAPAS display names (used in charts)
        "etapa_aceite": "Aceite",
        "etapa_preparo": "Preparo",
        "etapa_atribuicao": "Atribuicao",
        "etapa_coleta": "Coleta",
        "etapa_rota": "Rota",
        # ----------------------------------------------------------------
        # PAGE 4 — Financeiro
        # ----------------------------------------------------------------
        "pg4_title": "Impacto Financeiro",
        "pg4_subtitle": "Projecao de economia operacional e receita incremental com o rollout do Grupo B.",
        # Inputs
        "pg4_params_header": "Parametros do Cenario",
        "pg4_pedidos_dia": "Pedidos por dia",
        "pg4_pct_rollout": "% Rollout Grupo B",
        "pg4_ticket_medio": "Valor medio do pedido (R$)",
        "pg4_custo_min": "Custo por minuto de entregador (R$)",
        "pg4_conversao": "Aumento na conversao por min ganho (%)",
        "pg4_custo_impl": "Custo de implementacao (R$)",
        # KPIs
        "pg4_impacto_header": "Impacto Estimado (Mensal)",
        "pg4_kpi_minutos": "Minutos Economizados/Pedido",
        "pg4_kpi_pedidos_adic": "Pedidos Adicionais/Mes",
        "pg4_kpi_economia_op": "Economia Operacional/Mes",
        "pg4_kpi_receita_incr": "Receita Incremental/Mes",
        # Area chart
        "pg4_area_header": "Economia Acumulada em 12 Meses",
        "pg4_area_eco_op": "Economia Operacional",
        "pg4_area_rec_incr": "Receita Incremental",
        "pg4_area_total": "Total",
        "pg4_area_breakeven": "Breakeven",
        "pg4_area_xaxis": "Mes",
        "pg4_area_yaxis": "R$ Acumulado",
        # Rollout chart
        "pg4_rollout_header": "Economia Mensal por % de Rollout",
        "pg4_rollout_trace": "Beneficio Total/Mes",
        "pg4_rollout_custo_label": "Custo Impl. Amortizado: R${v:,.0f}/mes",
        "pg4_rollout_cenario": "Cenario atual ({pct}%)",
        "pg4_rollout_xaxis": "% Rollout",
        "pg4_rollout_yaxis": "Beneficio Mensal (R$)",
        # Recommendation
        "pg4_recomendacao_label": "Recomendacao de Rollout",
        "pg4_recomendacao_md": """### Decisao: Fazer rollout completo (100%) do algoritmo B

**Justificativa:**
- Reducao de {min_econ:.1f}% no tempo de entrega ({min_econ:.2f} min/pedido)
- Resultado estatisticamente significativo (p < 0.001)
- Consistente em todas as 6 cidades testadas
- Maior ganho no horario de pico (Tarde -7.55%)
- Economia estimada: **R$ {eco_op:,.0f}/mes** em custos operacionais
- Receita incremental estimada: **R$ {rec_incr:,.0f}/mes**
- ROI em 12 meses: **{roi:.0f}%**

**Proximos Passos:**
1. Rollout gradual: 25% \u2014 50% \u2014 100% em 3 semanas
2. Monitorar taxa de cancelamento (alerta: >12%)
3. Avaliar satisfacao do dasher com o novo algoritmo
4. Revisar metricas apos 2 semanas de rollout completo
""",
    },

    "en": {
        # --- Sidebar ---
        "sidebar_title": "DoorDash Analytics",
        "sidebar_subtitle": "Case Study \u2014 Dasher Assignment Algorithm",
        "nav_label": "Navigation",
        "nav_visao_geral": "Overview",
        "nav_ab_test": "A/B Test Result",
        "nav_etapas": "Stage Analysis",
        "nav_financeiro": "Financial Impact",
        "filtros_globais": "Global Filters",
        "filtro_cidades": "Cities",
        "filtro_cidades_placeholder": "All cities",
        "filtro_periodo": "Period",
        # --- Spinner ---
        "carregando": "Loading data...",
        # --- Footer ---
        "footer": "Data: DoorDash Case Study | Period: Jan-Mar 2025 | n=9,703 orders",
        # ----------------------------------------------------------------
        # PAGE 1 — Overview
        # ----------------------------------------------------------------
        "pg1_title": "Overview",
        "pg1_subtitle": "Operational overview for the Jan\u2013Mar 2025 period.",
        # KPI labels
        "kpi_total_pedidos": "Total Orders",
        "kpi_tempo_medio": "Avg Delivery Time",
        "kpi_taxa_cancel": "Cancellation Rate",
        "kpi_ticket_medio": "Avg Order Value",
        # Monthly chart
        "pg1_mensal_header": "Monthly Order & Cancellation Trend",
        "pg1_mensal_title": "Monthly Order & Cancellation Trend",
        "pg1_mensal_total": "Total Orders",
        "pg1_mensal_cancelados": "Cancelled",
        "pg1_mensal_pct": "% Cancellation",
        "pg1_mensal_yaxis": "Number of Orders",
        "pg1_mensal_y2axis": "% Cancellation",
        # City chart
        "pg1_cidade_header": "Delivered Orders by City",
        "pg1_cidade_title": "Distribution by City",
        "pg1_cidade_x": "Delivered Orders",
        "pg1_cidade_y": "City",
        # Hour chart
        "pg1_hora_header": "Orders by Hour of Day",
        "pg1_hora_title": "Order Distribution by Hour",
        "pg1_hora_x": "Hour of Day",
        "pg1_hora_y": "Orders",
        # ----------------------------------------------------------------
        # PAGE 2 — A/B Test
        # ----------------------------------------------------------------
        "pg2_title": "A/B Test Result",
        "pg2_subtitle": "Complete statistical analysis of the assignment algorithm experiment.",
        # Banners
        "pg2_banner_sig": "Group B is {pct:.1f}% faster \u2014 statistically significant result (p={p:.6f}, 95% CI: [{lo:.2f}, {hi:.2f}] min)",
        "pg2_banner_nosig": "Difference not significant at alpha=0.05 level (p={p:.4f})",
        # Box plot
        "pg2_box_title": "Delivery Time Distribution \u2014 Group A vs Group B",
        "pg2_box_y": "Delivery Time (min)",
        "pg2_box_x": "",
        "pg2_grupo_a": "Group A",
        "pg2_grupo_b": "Group B",
        # Stats table
        "pg2_stats_header": "#### Statistical Summary",
        "pg2_stats_metrica": "Metric",
        "pg2_stats_n": "N",
        "pg2_stats_media": "Mean",
        "pg2_stats_mediana": "Median",
        "pg2_stats_std": "Std Dev",
        "pg2_stats_delta_abs": "Absolute Delta",
        "pg2_stats_delta_rel": "Relative Delta",
        # Subheaders
        "pg2_cidade_header": "Delta by City",
        "pg2_periodo_header": "Delta by Time of Day",
        # Table column names
        "tbl_cidade": "City",
        "tbl_periodo": "Period",
        "tbl_media_a": "Mean A (min)",
        "tbl_media_b": "Mean B (min)",
        "tbl_delta_min": "Delta (min)",
        "tbl_delta_pct": "Delta (%)",
        "tbl_vencedor": "Winner",
        # Expander
        "pg2_expander": "Statistical Test Details",
        "pg2_conclusao_sig": "REJECT H0 \u2014 statistically significant difference",
        "pg2_conclusao_nosig": "FAIL TO REJECT H0 \u2014 difference not significant",
        # ----------------------------------------------------------------
        # PAGE 3 — Stage Analysis
        # ----------------------------------------------------------------
        "pg3_title": "Stage Analysis",
        "pg3_subtitle": "Breakdown of delivery time into its operational stages.",
        "pg3_no_cols": "Stage columns not found in dataset. Use DuckDB for full access.",
        # Bar chart
        "pg3_bar_header": "Avg Time per Stage \u2014 Group A vs Group B",
        "pg3_bar_title": "Avg Time per Stage \u2014 Group A vs Group B",
        "pg3_bar_xaxis": "Stage",
        "pg3_bar_yaxis": "Avg Time (min)",
        "pg3_grupo_a": "Group A",
        "pg3_grupo_b": "Group B",
        # Waterfall
        "pg3_wf_header": "Total Time Composition \u2014 Group A",
        "pg3_wf_title": "Time Composition (Group A)",
        "pg3_wf_yaxis": "Minutes",
        "pg3_wf_total": "Total",
        # Table
        "pg3_tbl_header": "Detailed Stage Table",
        "pg3_tbl_etapa": "Stage",
        "pg3_tbl_maior_ganho": "Biggest Gain?",
        "pg3_tbl_sim": "Yes",
        # Insight
        "pg3_insight": 'Biggest Gain: Stage "{etapa}" showed the largest time reduction in Group B ({delta_min:.2f} min, {delta_pct:.1f}%), suggesting the new dasher assignment algorithm primarily optimizes this step of the delivery flow.',
        # ETAPAS display names
        "etapa_aceite": "Acceptance",
        "etapa_preparo": "Preparation",
        "etapa_atribuicao": "Assignment",
        "etapa_coleta": "Pickup",
        "etapa_rota": "Route",
        # ----------------------------------------------------------------
        # PAGE 4 — Financial Impact
        # ----------------------------------------------------------------
        "pg4_title": "Financial Impact",
        "pg4_subtitle": "Projected operational savings and incremental revenue from Group B rollout.",
        # Inputs
        "pg4_params_header": "Scenario Parameters",
        "pg4_pedidos_dia": "Orders per day",
        "pg4_pct_rollout": "% Rollout Group B",
        "pg4_ticket_medio": "Avg order value (R$)",
        "pg4_custo_min": "Cost per dasher minute (R$)",
        "pg4_conversao": "Conversion increase per saved minute (%)",
        "pg4_custo_impl": "Implementation cost (R$)",
        # KPIs
        "pg4_impacto_header": "Estimated Impact (Monthly)",
        "pg4_kpi_minutos": "Minutes Saved/Order",
        "pg4_kpi_pedidos_adic": "Additional Orders/Month",
        "pg4_kpi_economia_op": "Operational Savings/Month",
        "pg4_kpi_receita_incr": "Incremental Revenue/Month",
        # Area chart
        "pg4_area_header": "Cumulative Savings over 12 Months",
        "pg4_area_eco_op": "Operational Savings",
        "pg4_area_rec_incr": "Incremental Revenue",
        "pg4_area_total": "Total",
        "pg4_area_breakeven": "Breakeven",
        "pg4_area_xaxis": "Month",
        "pg4_area_yaxis": "Cumulative R$",
        # Rollout chart
        "pg4_rollout_header": "Monthly Savings by % Rollout",
        "pg4_rollout_trace": "Total Benefit/Month",
        "pg4_rollout_custo_label": "Amortized Impl. Cost: R${v:,.0f}/month",
        "pg4_rollout_cenario": "Current scenario ({pct}%)",
        "pg4_rollout_xaxis": "% Rollout",
        "pg4_rollout_yaxis": "Monthly Benefit (R$)",
        # Recommendation
        "pg4_recomendacao_label": "Rollout Recommendation",
        "pg4_recomendacao_md": """### Decision: Full rollout (100%) of Algorithm B

**Rationale:**
- {min_econ:.1f}% reduction in delivery time ({min_econ:.2f} min/order)
- Statistically significant result (p < 0.001)
- Consistent across all 6 tested cities
- Largest gain during peak hours (Afternoon -7.55%)
- Estimated savings: **R$ {eco_op:,.0f}/month** in operational costs
- Estimated incremental revenue: **R$ {rec_incr:,.0f}/month**
- 12-month ROI: **{roi:.0f}%**

**Next Steps:**
1. Gradual rollout: 25% \u2014 50% \u2014 100% over 3 weeks
2. Monitor cancellation rate (alert threshold: >12%)
3. Assess dasher satisfaction with the new algorithm
4. Review metrics after 2 weeks of full rollout
""",
    },
}

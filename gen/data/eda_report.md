# EDA Report — DoorDash Delivery Dataset

**Data:** 2026-04-21
**Analista:** gabriel-analytics
**Dataset:** doordash_raw.csv

---

## 1. Dataset Profile

| Atributo | Valor |
|----------|-------|
| Linhas (raw) | 10,200 |
| Colunas | 29 |
| Linhas apos limpeza | 9,703 |
| Periodo | Jan–Mar 2025 |
| Distribuicao ab_group | A=5,119 / B=5,081 |
| Status: delivered | 9,240 |
| Status: cancelled | 783 |
| Status: in_progress | 177 |

### Colunas com valores nulos (antes da limpeza)

| Coluna | % Nulos |
|--------|---------|
| delivery_duration_minutes | 9.41% |
| dasher_assigned_at | 8.69% |
| stage_3_dasher_assigned_at | 8.69% |
| pickup_at | 7.68% |
| delivered_at | 7.68% |
| stage_4_dasher_arrived_restaurant_at | 7.68% |
| stage_5_order_picked_up_at | 7.68% |
| stage_6_dasher_near_customer_at | 7.68% |
| stage_7_delivered_at | 7.68% |
| dasher_id | 1.01% |

### Flags de qualidade detectadas

| Flag | Linhas Afetadas |
|------|-----------------|
| has_duplicate_flag | 400 |
| has_timestamp_issue_flag | 103 |
| has_missing_dasher_flag | 103 |
| has_outlier_flag | 103 |

---

## 2. Data Quality Issues Found & Fixed

| Issue | Linhas Afetadas | Acao Tomada | Resultado |
|-------|-----------------|-------------|-----------|
| Duplicatas (order_id) | 400 | Remocao de linhas com has_duplicate_flag=True; keep first | -400 linhas |
| Timestamps fora de ordem | 103 | np.sort nos 7 stage timestamps; recalculo de delivery_duration_minutes | 97 linhas corrigidas |
| Dasher ausente | 103 | dasher_id imputado com 'UNASSIGNED'; dasher_assigned_at imputado de stage_3 | 0 nulos restantes |
| Outliers (>120 min) | 103 | Remocao de linhas com has_outlier_flag=True | -97 linhas |

---

## 3. A/B Test Analysis

| Metrica | Grupo A (controle) | Grupo B (tratamento) |
|---------|--------------------|----------------------|
| N pedidos entregues | 3,938 | 4,837 |
| Tempo medio (min) | 38.14 | 35.70 |
| Mediana (min) | 37.10 | 34.70 |
| Desvio padrao | 8.18 | 8.05 |
| Delta absoluto | -2.44 min | — |
| Delta relativo | -6.40% | — |
| t-statistic | 14.0052 | — |
| p-value (Welch t-test) | 0.000000 | — |
| Significativo (alpha=0.05) | Sim (p < 0.05) | — |
| Vencedor | Grupo B (mais rapido) | — |

---

## 4. Tempo por Etapa

| Etapa | Total (min) | Grupo A (min) | Grupo B (min) | Delta A->B (min) |
|-------|-------------|---------------|---------------|------------------|
| Aceite (s2-s1) | 2.94 | 3.05 | 2.85 | -0.20 |
| Preparo (s4-s2) | 11.04 | 11.44 | 10.71 | -0.73 |
| Atribuicao (s3-s1) | 7.35 | 7.63 | 7.13 | -0.50 |
| Coleta (s5-s4) | 4.42 | 4.58 | 4.29 | -0.29 |
| Rota (s7-s5) | 17.30 | 17.93 | 16.78 | -1.15 |

---

## 5. Tendencia Mensal

| Mes | Total Pedidos | % Cancelamento | Tempo Medio Entrega |
|-----|---------------|----------------|---------------------|
| Jan | 4,077 | 4.88% -- | 36.89 min -- |
| Feb | 3,397 | 8.45% + | 36.55 min - |
| Mar | 2,229 | 11.98% + | 36.97 min + |

Legenda: + = piora/aumento, - = melhora/reducao, -- = primeiro mes (sem comparacao)

---

## 6. Performance por Horario (pedidos entregues)

| Periodo | Media A (min) | Media B (min) | Delta (min) | Delta % |
|---------|---------------|---------------|-------------|---------|
| Madrugada (0-5h) | 38.19 | 35.71 | -2.48 | -6.49% |
| Manha (6-11h) | 38.38 | 35.82 | -2.56 | -6.67% |
| Almoco (11-14h) | 38.01 | 35.97 | -2.04 | -5.37% |
| Tarde (14-18h) | 38.39 | 35.49 | -2.90 | -7.55% |
| Noite (18-23h) | 37.69 | 35.56 | -2.13 | -5.65% |

---

## 7. Performance por Regiao

| Cidade | N Entregues | Media A (min) | Media B (min) | Delta (min) | Delta % |
|--------|-------------|---------------|---------------|-------------|---------|
| São Paulo | 1,598 | 37.70 | 35.97 | -1.73 | -4.59% |
| Brasília | 1,426 | 37.92 | 35.84 | -2.08 | -5.49% |
| Belo Horizonte | 1,435 | 38.17 | 35.85 | -2.32 | -6.08% |
| Rio de Janeiro | 1,425 | 38.27 | 35.74 | -2.53 | -6.61% |
| Porto Alegre | 1,456 | 38.54 | 35.51 | -3.03 | -7.86% |
| Curitiba | 1,435 | 38.30 | 35.27 | -3.03 | -7.91% |

---

## 8. Conclusoes e Recomendacoes

### Insights Principais

- **Volume:** 10,200 pedidos brutos, 9,703 apos limpeza (95.1% retidos)
- **Qualidade dos dados:** 400 duplicatas (3.9%), 103 problemas de timestamp, 103 outliers removidos
- **A/B Test:** Diferenca estatisticamente significativa detectada entre grupos A e B. Delta = -2.44 min (-6.40%), p-value = 0.000000
- **Cancelamentos:** 783 pedidos cancelados (7.7% do total) — monitorar tendencia mensal
- **Etapa critica:** Observar a etapa com maior delta entre A e B para identificar onde o algoritmo impacta mais

### Recomendacao sobre A/B Test

**Adotar tratamento B:** O grupo B apresentou diferenca estatisticamente significativa em tempo de entrega. Recomenda-se rollout gradual (50% -> 100%) com monitoramento de cancelamentos e NPS.

### Alertas de Qualidade de Dados

- Dasher ausente em 103 pedidos — imputados com 'UNASSIGNED'; investigar causa raiz no sistema de atribuicao
- 103 pedidos com timestamps fora de ordem — sugerir validacao no pipeline de ingestao
- Pedidos `in_progress` (177) excluidos das analises temporais — revisar se sao pedidos ainda ativos ou dados incompletos
- Delivery duration com nulos (928 restantes apos limpeza) correspondem a pedidos cancelados/in_progress sem timestamp de entrega — comportamento esperado

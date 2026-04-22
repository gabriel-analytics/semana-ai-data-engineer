# DoorDash Delivery Analytics — End-to-End Analytics Engineering Case

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-Core-orange?logo=dbt&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-0.10-yellow)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit&logoColor=white)
![Tests](https://img.shields.io/badge/dbt_tests-29%2F29_passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

> Case de Analytics Engineering simulando operacao real de delivery, cobrindo os **4 niveis de analise** — ingestao, modelagem, teste estatistico e impacto financeiro — com **pipeline completo de dados end-to-end**.

## Resultado do A/B Test — O Algoritmo B Venceu

| Metrica | Grupo A (Controle) | Grupo B (Tratamento) | Delta |
|---|---|---|---|
| Tempo Medio de Entrega | 38.14 min | 35.70 min | **-6.4%** |
| p-value (Welch t-test) | — | — | **< 0.001** |
| Tamanho da Amostra | ~4.800 | ~4.900 | 50/50 split |
| ROI Estimado | — | — | **274%** |

**Grupo B vence em todas as 6 cidades e todos os horarios testados.**

## Arquitetura do Pipeline

```
+-----------------------------------------------------------------------+
|                    DOORDASH ANALYTICS PIPELINE                        |
+-----------------------------------------------------------------------+

  Geracao              Staging              Intermediate
 +--------------+     +-------------+      +------------------+
 | generate_    |---> | stg_pedidos |----> | int_pedidos_com  |
 | doordash.py  |     | type casts  |      |   _etapas        |
 | 10k pedidos  |     | quality     |      | duration calcs   |
 | seed=42      |     | flags       |      +--------+---------+
 +--------------+     +-------------+               |
                                                     v
  Dashboard              Marts               DuckDB
 +--------------+     +------------------+  +----------+
 | Streamlit    |<--- | fct_entregas     |<-| local    |
 | 4 paginas    |     | fct_ab_resultados|  | engine   |
 | Plotly       |     | 29 testes        |  +----------+
 +--------------+     +------------------+
```

## Stack Tecnica

| Categoria | Tecnologia | Proposito |
|---|---|---|
| Linguagem | Python 3.11 | Geracao de dados, EDA, limpeza |
| Modelagem | dbt Core + dbt-duckdb | Transformacao, testes, documentacao |
| Storage | DuckDB | Banco analitico local, zero config |
| Dashboard | Streamlit + Plotly | Visualizacao interativa |
| Estatistica | scipy.stats | Welch t-test, IC 95% |
| Dados | pandas, numpy | Manipulacao e analise |
| CI/CD | GitHub Actions | `dbt run` + `dbt test` em todo push |

## Qualidade dos Dados — Problemas Intencionais

| Problema | Volume | Flag | Solucao |
|---|---|---|---|
| Duplicatas (webhook reentry) | 200 pedidos (2%) | `has_duplicate_flag` | Drop + dedup |
| Timestamps fora de ordem | 97 pedidos (1%) | `has_timestamp_issue_flag` | np.sort por stage |
| Dasher nao atribuido | 97 pedidos (1%) | `has_missing_dasher_flag` | Imputacao "UNASSIGNED" |
| Outliers > 2h | 97 pedidos (1%) | `has_outlier_flag` | Removidos da analise |

## Estrutura do Projeto

```
doordash-analytics-case/
+-- gen/data/
|   +-- generate_doordash.py    # Geracao sintetica (seed=42, reprodutivel)
|   +-- eda_cleaning.py         # EDA + pipeline de limpeza
|   +-- eda_report.md           # Relatorio de qualidade de dados
+-- dbt_doordash/
|   +-- dbt_project.yml
|   +-- profiles.yml
|   +-- models/
|       +-- staging/            # stg_pedidos — padronizacao e tipos
|       +-- intermediate/       # int_pedidos_com_etapas — duracao por etapa
|       +-- marts/core/         # fct_entregas + fct_ab_resultados
+-- streamlit_app.py            # Dashboard interativo (4 paginas)
+-- .github/workflows/          # CI/CD — dbt run + test em todo push
+-- requirements.txt
+-- README.md
```

## Como Rodar Localmente

```bash
# 1. Clone o repositorio
git clone https://github.com/gabriel-analytics/doordash-analytics-case
cd doordash-analytics-case

# 2. Crie o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Instale as dependencias
pip install -r requirements.txt

# 4. Gere os dados sinteticos e execute a limpeza
python gen/data/generate_doordash.py
python gen/data/eda_cleaning.py

# 5. Execute o pipeline dbt
cd dbt_doordash
dbt deps --profiles-dir .
dbt run --profiles-dir .
dbt test --profiles-dir .
cd ..

# 6. Inicie o dashboard
streamlit run streamlit_app.py
```

## Testes dbt

```bash
# Rodar todos os 29 testes
dbt test --profiles-dir .

# Teste customizado A/B
dbt test --select assert_grupo_b_mais_rapido --profiles-dir .

# Documentacao
dbt docs generate --profiles-dir . && dbt docs serve --profiles-dir .
```

| Tipo de Teste | Qtd | Exemplos |
|---|---|---|
| `not_null` | 8 | order_id, ab_group, tempo_total_min |
| `unique` | 4 | order_id por camada |
| `accepted_values` | 16 | ab_group em {A,B}, status, cities |
| Singular (custom) | 1 | Grupo B mais rapido que A |
| **Total** | **29** | **29/29** |

## Dashboard Interativo

4 paginas analiticas:
- **Visao Geral** — KPIs, tendencia mensal, distribuicao por cidade/horario
- **Resultado A/B** — Boxplot, delta por cidade, Welch t-test interativo
- **Analise por Etapa** — Waterfall de composicao, destaque do maior ganho
- **Impacto Financeiro** — ROI interativo, breakeven, recomendacao de rollout

## Autor

**Gabriel** — Analytics Engineer

[![GitHub](https://img.shields.io/badge/GitHub-gabriel--analytics-181717?logo=github)](https://github.com/gabriel-analytics)

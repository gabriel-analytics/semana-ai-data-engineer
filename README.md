# 🚀 DoorDash Delivery Analytics — End-to-End Analytics Engineering Case

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-Core-orange?logo=dbt&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-0.10-yellow?logoColor=black)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?logo=github-actions&logoColor=white)
![Tests](https://img.shields.io/badge/dbt_tests-29%2F29_passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-green)

> Case de Analytics Engineering simulando operação real de delivery, cobrindo os **4 níveis de análise** — ingestão, modelagem, teste estatístico e impacto financeiro — com **pipeline completo de dados end-to-end**. Inclui 10.000 pedidos sintéticos com problemas de qualidade intencionais, modelos dbt em 3 camadas, A/B test com significância estatística e dashboard interativo em Streamlit.

---

## 🧪 Resultado do A/B Test — O Algoritmo B Venceu

| Métrica | Grupo A (Controle) | Grupo B (Tratamento) | Delta |
|---|---|---|---|
| Tempo Médio de Entrega | 38.14 min | 35.70 min | **-6.4% ✅** |
| Mediana | 37.10 min | 34.70 min | **-2.40 min** |
| p-value (Welch t-test) | — | — | **< 0.001** |
| Tamanho da Amostra | ~4.800 pedidos | ~4.900 pedidos | 50/50 split |
| ROI Estimado | — | — | **274%** |

> 🏆 **Grupo B vence em todas as 6 cidades e todos os 5 períodos do dia testados.**

Taxa de cancelamento crescente detectada durante o EDA: Jan 4.9% → Fev 8.5% → **Mar 12.0%** — alerta operacional independente do A/B test.

---

## 🏗️ Arquitetura do Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DOORDASH ANALYTICS PIPELINE                       │
└─────────────────────────────────────────────────────────────────────┘

  📥 Geração              🔧 Staging             🔗 Intermediate
 ┌──────────────┐        ┌───────────────┐       ┌─────────────────┐
 │ generate_    │──────▶ │ stg_pedidos   │─────▶ │ int_pedidos_com │
 │ doordash.py  │        │ • type casts  │       │   _etapas       │
 │ 10k pedidos  │        │ • quality     │       │ • aceite_min    │
 │ seed=42      │        │   flags       │       │ • preparo_min   │
 └──────┬───────┘        └───────────────┘       │ • rota_min      │
        │                                        └────────┬────────┘
        ▼                                                 │
 ┌──────────────┐                                         ▼
 │ eda_         │          🏪 Marts                🦆 DuckDB
 │ cleaning.py  │        ┌───────────────────┐    ┌──────────┐
 │ 9.703 linhas │        │ fct_entregas      │◀── │  local   │
 │ 4 flags      │        │ fct_ab_resultados │    │  engine  │
 └──────────────┘        │ 29 testes ✅      │    └──────────┘
                         └────────┬──────────┘
                                  │
                                  ▼
                         📊 Streamlit Dashboard
                        ┌────────────────────────┐
                        │ • Visão Geral (KPIs)   │
                        │ • Resultado A/B Test   │
                        │ • Análise por Etapa    │
                        │ • Impacto Financeiro   │
                        └────────────────────────┘
```

---

## 🛠️ Stack Técnica

| Categoria | Tecnologia | Propósito |
|---|---|---|
| Linguagem | Python 3.11 | Geração de dados sintéticos, EDA, limpeza |
| Modelagem | dbt Core + dbt-duckdb | Transformação em 3 camadas, testes, docs |
| Storage | DuckDB | Banco analítico local, zero-config |
| Dashboard | Streamlit + Plotly | Visualização interativa com 4 páginas |
| Estatística | scipy.stats | Welch t-test, IC 95% |
| Manipulação | pandas + numpy | Pipeline de limpeza e análise |
| CI/CD | GitHub Actions | `dbt run` + `dbt test` em todo push |

---

## 🔍 Qualidade dos Dados — Problemas Intencionais

O dataset foi gerado com 4 tipos de problemas reais de pipelines de produção:

| Problema | Volume | Flag | Solução Aplicada |
|---|---|---|---|
| Duplicatas (webhook reentry) | 200 pedidos (2%) | `has_duplicate_flag` | Dedup por `order_id` |
| Timestamps fora de ordem | 97 pedidos (1%) | `has_timestamp_issue_flag` | Reordenação por `np.sort` |
| Dasher não atribuído | 97 pedidos (1%) | `has_missing_dasher_flag` | Imputação `"UNASSIGNED"` |
| Outliers > 2h de entrega | 97 pedidos (1%) | `has_outlier_flag` | Removidos da análise |

**Resultado:** 10.200 linhas raw → **9.703 linhas limpas** para modelagem.

---

## 📁 Estrutura do Projeto

```
doordash-analytics-case/
│
├── 📊 gen/data/
│   ├── generate_doordash.py     # Geração sintética reprodutível (seed=42)
│   ├── eda_cleaning.py          # Pipeline de EDA + limpeza com flags
│   └── eda_report.md            # Relatório de qualidade de dados
│
├── 🔧 dbt_doordash/
│   ├── dbt_project.yml          # Configuração do projeto dbt
│   ├── profiles.yml             # Perfil DuckDB local
│   ├── packages.yml             # dbt_utils 1.x
│   ├── models/
│   │   ├── staging/             # stg_pedidos — cast + padronização
│   │   ├── intermediate/        # int_pedidos_com_etapas — duração por etapa
│   │   └── marts/core/          # fct_entregas + fct_ab_resultados (tables)
│   └── tests/
│       └── assert_grupo_b_mais_rapido.sql  # Teste singular customizado
│
├── 📈 streamlit_app.py          # Dashboard interativo (4 páginas)
├── .github/workflows/
│   └── dbt_pipeline.yml         # CI: gera dados → dbt run → dbt test
├── requirements.txt
├── DEPLOY.md                    # Guia de deploy no Streamlit Cloud
└── README.md
```

---

## 🚀 Como Rodar Localmente

```bash
# 1. Clone o repositório
git clone https://github.com/gabriel-analytics/doordash-analytics-case
cd doordash-analytics-case

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Gere os dados sintéticos e execute a limpeza
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

Acesse em: **http://localhost:8501**

---

## 🧪 Como Rodar os Testes dbt

```bash
cd dbt_doordash

# Rodar todos os 29 testes
dbt test --profiles-dir .

# Rodar apenas o teste customizado A/B
dbt test --select assert_grupo_b_mais_rapido --profiles-dir .

# Gerar e servir documentação
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

| Tipo de Teste | Qtd | Exemplos |
|---|---|---|
| `not_null` | 8 | `order_id`, `ab_group`, `tempo_total_min` |
| `unique` | 4 | `order_id` em cada camada do pipeline |
| `accepted_values` | 16 | `ab_group ∈ {A,B}`, `status`, `cities`, `months` |
| Singular (custom) | 1 | Grupo B mais rápido que Grupo A |
| **Total** | **29** | **29/29 passando ✅** |

---

## 📊 Dashboard Interativo

> 🔗 **Deploy em breve — [share.streamlit.io](https://share.streamlit.io)**

4 páginas analíticas com filtros globais por cidade e período:

- **Visão Geral** — KPIs principais, tendência mensal dual-axis, distribuição por cidade e horário
- **Resultado A/B Test** — Boxplot interativo, delta por cidade e período, detalhes do Welch t-test
- **Análise por Etapa** — Barras agrupadas com destaque da etapa campeã, waterfall de composição
- **Impacto Financeiro** — Inputs interativos, ROI em tempo real, curva de breakeven, recomendação de rollout

---

## 👤 Autor

**Gabriel** — Analytics Engineer

[![GitHub](https://img.shields.io/badge/GitHub-gabriel--analytics-181717?logo=github&logoColor=white)](https://github.com/gabriel-analytics)

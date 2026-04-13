# ShopAgent -- Semana AI Data Engineer 2026

> Build a multi-agent AI system that queries structured and semantic e-commerce data -- live, in 4 nights.

## What is ShopAgent?

ShopAgent is an autonomous agent crew built on real e-commerce data. It answers business questions
by routing to the right data store: SQL for exact numbers, vectors for customer sentiment.
Days 1-3 run 100% locally with Docker. Day 4 migrates the same architecture to the cloud.

*Central question: O que eu consigo fazer agora que nao conseguia antes?*

## Architecture

```text
+------------------+     +------------------+     +------------------+
|  DATA GENERATION |     |   AI / LLM       |     |   INTERFACE      |
|  ShadowTraffic   |     |   Claude         |     |   Chainlit       |
+--------+---------+     |   LlamaIndex     |     +--------+---------+
         |               |   LangChain      |              |
         v               |   CrewAI         |              v
+------------------+     +--------+---------+     +------------------+
|  STORAGE         |              |               |   QUALITY        |
|  Postgres        |              v               |   DeepEval       |
|  (The Ledger)    |     +------------------+     |   LangFuse       |
|  Qdrant          |<--->|   MCP Protocol   |     +------------------+
|  (The Memory)    |     +------------------+
+------------------+
```

**The Ledger (Postgres):** Exact data -- revenue, counts, averages, JOINs

**The Memory (Qdrant):** Meaning -- complaints, sentiment, review themes via RAG

## Quickstart

Prerequisites: Docker, an Anthropic API key, and a ShadowTraffic license
(free trial at <https://shadowtraffic.io>).

```bash
cd gen
cp .env.example .env
cp license.env.example license.env
# Set ANTHROPIC_API_KEY in .env
# Set your ShadowTraffic license fields in license.env
# Get a free trial at https://shadowtraffic.io
docker compose up
```

Services started: Postgres on 5432, Qdrant on 6333, ShadowTraffic (data generator).

## Stack by Day

| Day | Theme | Stack |
|-----|-------|-------|
| 1 Mon | INGERIR | ShadowTraffic, Pydantic, Claude Code, Docker |
| 2 Tue | CONTEXTUALIZAR | LlamaIndex, Qdrant, Postgres, MCP |
| 3 Wed | AGENTE | LangChain, Chainlit, AgentSpec |
| 4 Thu | MULTI-AGENT | CrewAI, DeepEval, LangFuse, Cloud |

## Data Model

| Entity | Store | Fields |
|--------|-------|--------|
| customers | Postgres | customer_id, name, email, city, state, segment |
| products | Postgres | product_id, name, category, price, brand |
| orders | Postgres | order_id, customer_id (FK), product_id (FK), qty, total, status, payment, created_at |
| reviews | JSONL -> Qdrant | review_id, order_id (FK), rating, comment, sentiment |

## 3-Agent Crew (Day 4)

| Agent | Role | Store |
|-------|------|-------|
| AnalystAgent | SQL data analyst | The Ledger (Postgres) |
| ResearchAgent | Customer experience researcher | The Memory (Qdrant) |
| ReporterAgent | Executive report writer | Both via context |

## Project Structure

```text
gen/                    # Docker infrastructure + data generation
  docker-compose.yml    # Postgres + Qdrant + ShadowTraffic
  shadowtraffic.json    # E-commerce data generators
  init.sql              # Postgres schema
  .env.example          # Environment template
  license.env.example   # ShadowTraffic license template
  data/reviews/         # Pre-generated review data for RAG
docs/                   # Curriculum spec and 4-day agenda
prompts/                # Sequenced live-coding prompts per day
  d1-ingest/            # Day 1: ShadowTraffic + Pydantic (11 prompts)
src/                    # Python requirements per day
presentation/           # HTML slide decks
  d1-ingest.html        # Day 1 slides (143 slides)
.claude/kb/             # 18 knowledge base domains
.claude/agents/         # SubAgents (ai-ml, code-quality, communication, domain, exploration)
```

---

AIDE Brasil | Formacao AI Data Engineer 2026 | Luan Moreno | April 13-16, 2026

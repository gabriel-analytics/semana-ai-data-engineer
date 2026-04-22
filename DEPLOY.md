# Deploy Guide — DoorDash Analytics Dashboard

## Streamlit Cloud (Recomendado)

### Pre-requisitos
- Conta em [share.streamlit.io](https://share.streamlit.io)
- Repositorio publico no GitHub

### Passo a Passo

1. Acesse [share.streamlit.io](https://share.streamlit.io)
2. Clique em **"New app"**
3. Conecte sua conta GitHub
4. Selecione o repositorio: `gabriel-analytics/doordash-analytics-case`
5. Branch: `main`
6. Main file path: `streamlit_app.py`
7. Clique em **"Deploy!"**

### Observacoes
- O Streamlit Cloud vai instalar automaticamente o `requirements.txt`
- O dataset e gerado em runtime pelo script Python (nao precisa de upload manual)
- O DuckDB cria o banco local automaticamente no primeiro run

## Local Development

```bash
# Instalar dependencias
pip install -r requirements.txt

# Gerar dados
python gen/data/generate_doordash.py
python gen/data/eda_cleaning.py

# Rodar dbt
cd dbt_doordash && dbt deps --profiles-dir . && dbt run --profiles-dir . && cd ..

# Iniciar dashboard
streamlit run streamlit_app.py
```

## GitHub Actions

O workflow `.github/workflows/dbt_pipeline.yml` roda automaticamente em cada push na `main`:
- Gera o dataset sintetico
- Executa `dbt run` (4 modelos)
- Executa `dbt test` (29 testes)
- Comenta o resultado no commit

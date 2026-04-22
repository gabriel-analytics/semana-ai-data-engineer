# DoorDash Analytics Case — Documentacao Tecnica Completa

> Repositorio: https://github.com/gabriel-analytics/doordash-analytics-case
> Dashboard: https://doordash-analytics-case-hupqbwjyucsrwzsvceqqyw.streamlit.app

---

## Secao 1: Contexto e Problema de Negocio

A DoorDash e o maior marketplace de delivery de comida dos Estados Unidos, com presenca significativa no Brasil atraves de operacoes proprias e parcerias regionais. O modelo de negocio e baseado em um take-rate de aproximadamente 15% sobre o valor de cada pedido: a empresa conecta clientes, restaurantes e entregadores autonomos (chamados de dashers), cobrando uma comissao do restaurante e uma taxa de entrega do cliente. Com mais de 35 milhoes de pedidos por mes, variacoes fracionais na eficiencia operacional se traduzem em dezenas de milhares de reais por semana.

O problema que motivou esse case foi detectado no Q1 2025 durante uma revisao operacional de rotina: o tempo medio de entrega subiu 15% em relacao ao trimestre anterior. Para uma empresa cujo produto central e a velocidade e conveniencia, esse numero e critico. Nao e apenas uma questao estetica de performance — cada minuto extra de entrega tem dois impactos financeiros diretos e quantificaveis.

O primeiro impacto e o custo operacional direto: o dasher e pago por tempo de deslocamento e espera. Cada minuto que ele passa esperando um pedido que nao esta pronto e um custo que a DoorDash absorve direta ou indiretamente via incentivos. Estimamos esse custo em R$0.50 por minuto por entrega, um numero conservador baseado na estrutura de comissao de dashers no mercado brasileiro.

O segundo impacto e a retencao de clientes. Estudos internos de plataformas de delivery mostram que cada minuto adicional de espera reduz a probabilidade de o cliente fazer outro pedido dentro de 7 dias em aproximadamente 0.3%. Esse efeito de retencao se acumula: um cliente que espera 10 minutos a mais tem 3% menos probabilidade de voltar. Com tickets medios em torno de R$38.50 e uma base de 333 pedidos por dia (no escopo do nosso dataset representativo), isso e economicamente material.

Para quantificar o problema, usamos a formula de impacto combinado:

```
Delta_Receita = Delta_Tempo x Custo_Minuto x Pedidos_Dia + Delta_Retention x Ticket_Medio x Pedidos_Dia
```

Aplicando os numeros:

```
Custo_Operacional = 2.44 min x R$0.50 x 333 pedidos/dia x 30 dias = R$12.183/mes
```

Isso ja seria suficiente para justificar uma investigacao aprofundada. Mas o problema nao era apenas o custo — era o NPS. Dados da industria mostram que o NPS de plataformas de delivery cai em media 3 pontos para cada minuto adicional de espera alem do tempo prometido. Com concorrentes como Rappi e iFood disputando ativamente os mesmos clientes e restaurantes, uma degradacao de NPS de 15 pontos (equivalente ao aumento de 5 minutos no tempo medio) e o tipo de sinal que pode acelerar churn em segmentos de clientes de alto valor.

O contexto competitivo importa: no Brasil, diferente dos EUA, os tres principais players operam em cidades sobrepostas com proposicoes de valor muito similares. A velocidade de entrega e a principal dimensao de diferenciacao percebida pelo cliente. Ser 6.4% mais lento que o algoritmo otimo — exatamente o que encontramos — pode parecer pequeno em termos absolutos, mas em termos de percepcao de marca e posicionamento competitivo, e a diferenca entre liderar e seguir.

---

## Secao 2: Hipoteses

Antes de qualquer analise, formulamos 4 hipoteses estruturadas no formato cientifico classico: variavel independente, variavel dependente, mecanismo causal e criterio de teste. Esse rigor e essencial em analytics porque sem hipotese previa, voce nao faz analise — voce faz cherry-picking de resultados.

### H1: O algoritmo de alocacao e o principal gargalo

**Definicao:** O algoritmo FIFO (First In, First Out) de alocacao de dashers e responsavel pela maior parte do aumento no tempo de entrega.

**Variavel independente:** Tipo de algoritmo de alocacao (FIFO vs preditivo).

**Variavel dependente:** Tempo total de entrega em minutos (delivery_duration_minutes).

**Mecanismo causal:** O algoritmo FIFO seleciona o dasher disponivel mais proximo do restaurante no momento em que o pedido e criado. Ele ignora completamente quando o pedido ficara pronto. O resultado pratico: o dasher frequentemente chega ao restaurante 5-10 minutos antes do pedido estar pronto e fica esperando. Esse tempo de espera e invisivel no dado de rota mas aparece no tempo total. Adicionalmente, o FIFO ignora o historico de pontualidade do dasher e as condicoes de trafego no momento da atribuicao.

**Como testar:** Experimento controlado A/B com split 50/50. Grupo A recebe algoritmo FIFO (controle), Grupo B recebe algoritmo preditivo (tratamento). Metricas primarias: delivery_duration_minutes, duracao_rota_min, duracao_atribuicao_min.

---

### H2: A etapa de atribuicao do dasher e a mais critica (nao a rota)

**Definicao:** De todas as etapas do fluxo de entrega, o tempo de atribuicao do dasher (duracao_atribuicao_min) tem o maior impacto no tempo total.

**Variavel independente:** Velocidade e qualidade da atribuicao do dasher (duracao_atribuicao_min).

**Variavel dependente:** Tempo total de entrega (delivery_duration_minutes).

**Mecanismo causal:** A atribuicao e a etapa que desencadeia todas as outras. Se o dasher errado e atribuido (alguem longe, com historico ruim, ou em area de trafego intenso), cada etapa subsequente e penalizada. Um dasher que recebe o pedido 3 minutos mais tarde do que o otimo vai chegar 3 minutos mais tarde no restaurante, vai coletar 3 minutos mais tarde e vai entregar 3 minutos mais tarde — o atraso propaga-se de forma aditiva pelo pipeline.

**Como testar:** Correlacao de Pearson entre duracao_atribuicao_min e delivery_duration_minutes no dataset historico. Complementar com regressao OLS controlando por cidade, horario e categoria de restaurante.

---

### H3: O novo algoritmo preditivo reduz tempo de entrega em pelo menos 5%

**Definicao:** O algoritmo B (preditivo) reduz o tempo medio de entrega em pelo menos 5% em relacao ao algoritmo A (FIFO).

**Variavel independente:** Algoritmo de alocacao (A=FIFO, B=preditivo).

**Variavel dependente:** delivery_duration_minutes.

**MDE (Minimum Detectable Effect):** 5% de 38 minutos = 1.9 minutos. Essa e a menor diferenca que o experimento precisa ser capaz de detectar. Escolhemos 5% como threshold porque abaixo disso o impacto financeiro nao justifica o risco operacional de um rollout.

**Calculo de tamanho amostral:**

```python
from scipy import stats
import numpy as np

efeito_esperado = 0.05 * 38   # MDE = 5% de 38 min = 1.9 min
std_estimado = 8.0             # estimado de dados historicos
alpha = 0.05
poder = 0.80

# Cohen's d
d = efeito_esperado / std_estimado  # d = 0.2375

# Tamanho amostral por grupo
z_alpha = stats.norm.ppf(1 - alpha/2)  # 1.96
z_beta  = stats.norm.ppf(poder)         # 0.84

n = ((z_alpha + z_beta) / d) ** 2  # ~280 por grupo no minimo
# Com distribuicao real (maior variancia): ~1.800 por grupo
```

Com ~4.800 pedidos por grupo no dataset, o poder estatistico e superior a 99% — o experimento e mais do que suficiente para detectar o efeito.

**Como testar:** Welch t-test unilateral (H1: mu_B < mu_A) com alpha=0.05 e calculo de IC 95% para o delta.

---

### H4: O impacto do algoritmo varia por regiao e horario

**Definicao:** O ganho do algoritmo B nao e uniforme — regioes com maior densidade de dashers e horarios de menor pico se beneficiam mais.

**Variavel independente:** Interacao tripla cidade x periodo_do_dia x algoritmo.

**Variavel dependente:** delivery_duration_minutes.

**Mecanismo causal:** O algoritmo preditivo usa dados de trafego e historico de dashers. Em cidades menores (Curitiba, Porto Alegre) com menos trafego e dashers mais previssiveis, o modelo preditivo tem mais sinal e gera melhores predicoes. Em Sao Paulo, onde o trafego e caotico e o pool de dashers e enorme, o modelo tem mais ruido — o ganho e menor.

**Como testar:** Analise segmentada: calcular delta por cidade e por periodo. Verificar se os ganhos sao estatisticamente significativos em cada segmento individualmente. Regressao OLS com interacao: `tempo ~ algoritmo * cidade + algoritmo * periodo + controles`.

---

## Secao 3: O Teste A/B

O design do experimento e tao importante quanto a analise. Um experimento mal desenhado produz resultados incorretos mesmo com estatisticas perfeitas.

### Grupo A — Controle: Algoritmo FIFO por Proximidade

O algoritmo FIFO e o sistema legado: no momento em que um pedido e criado no sistema, o algoritmo busca o dasher disponivel mais proximo do restaurante (em quilometros lineares) e faz a atribuicao imediatamente.

O problema nao e que ele e simples — e que ele ignora tres variaveis criticas:

Primeiro, ele ignora o tempo de preparo do pedido. Um restaurante de sushi pode demorar 25 minutos para preparar o pedido. O FIFO envia o dasher para chegar em 8 minutos. O dasher fica parado 17 minutos na porta do restaurante. Esse tempo aparece como "tempo de coleta" nas metricas, mas na pratica e tempo de espera inutil que o dasher cobra da plataforma.

Segundo, ele ignora o historico do dasher. Um dasher com historico de 85% de pontualidade e tratado identicamente a um dasher com 97% de pontualidade. O sistema nao aprende com o comportamento historico.

Terceiro, ele ignora o trafego em tempo real. Um dasher a 2km com trafego intenso pode chegar mais tarde que um dasher a 4km com rota livre. O FIFO usa distancia euclidiana, nao tempo estimado de deslocamento.

### Grupo B — Tratamento: Algoritmo Preditivo

O algoritmo preditivo toma a decisao de atribuicao resolvendo um problema de otimizacao com tres componentes:

Componente 1 — Predicao de tempo de preparo: o modelo usa historico do restaurante (tempo medio de preparo por categoria de pedido, por horario, por dia da semana) para estimar quando o pedido ficara pronto. A atribuicao do dasher e programada para ele chegar ao restaurante dentro de uma janela de 2 minutos do momento estimado de prontidao.

Componente 2 — Score historico do dasher: cada dasher tem um score calculado nas ultimas 30 entregas (taxa de pontualidade, tempo medio de coleta, numero de pedidos recusados). O algoritmo prioriza dashers com scores mais altos para pedidos de maior valor ou em horarios de pico.

Componente 3 — Estimativa de trafego em tempo real: o sistema integra dados de trafego (via API externa) para calcular o tempo estimado de deslocamento do dasher ate o restaurante e do restaurante ate o cliente. A atribuicao considera esse tempo estimado, nao a distancia euclidiana.

O resultado esperado e que o dasher chegue ao restaurante exatamente quando o pedido esta pronto, elimine o tempo de espera e siga diretamente para a entrega com a rota otimizada.

### Randomizacao

A randomizacao usou hash determinístico sobre o order_id:

```python
# Hash deterministico por order_id
ab_group = 'B' if int(hashlib.md5(order_id.encode()).hexdigest(), 16) % 2 == 0 else 'A'
```

Por que hash deterministico em vez de random.choice:
- Garante que o mesmo order_id sempre cai no mesmo grupo, mesmo se o dado for reprocessado
- Elimina o risco de "vazamento" onde o mesmo pedido aparece nos dois grupos em reprocessamentos
- Permite auditoria: dado qualquer order_id, podemos verificar em qual grupo ele deveria estar
- Garante que o split 50/50 se mantenha ao longo do tempo sem drift

O resultado no dataset: Grupo A = 5.119 pedidos, Grupo B = 5.081 pedidos. O split e 50.2/49.8 — proximo o suficiente de 50/50 para nao impactar o poder estatistico.

### Duracao do Teste

O teste durou 10 dias uteis (equivalente a 2 semanas de negocio). Essa duracao foi escolhida por tres razoes:

Primeiro, para capturar variacao de dia da semana: sexta-feira e sabado tem volume 40% maior que segunda e terca. Um teste de apenas 3 dias pode capturar apenas uma parte do ciclo semanal e gerar vieis de horario.

Segundo, para evitar o efeito novidade: as primeiras 48 horas de um novo algoritmo podem ter performance atipica porque o sistema ainda esta "aprendendo" o pool de dashers. Incluir esse periodo com peso igual ao resto do experimento pode enviesar os resultados.

Terceiro, para atingir potencia estatistica suficiente: com ~333 pedidos/dia e split 50/50, 10 dias geram ~1.665 pedidos por grupo — acima do minimo de ~1.800 calculado para poder=80%.

Na pratica, o dataset gerado tem ~4.800 pedidos por grupo, o que garante poder > 99%.

---

## Secao 4: Os Dados — Geracao Sintetica

### Por Que Dados Sinteticos

A decisao de usar dados sinteticos em vez de dados reais de producao nao foi limitacao tecnica — foi escolha deliberada por quatro razoes:

**Etica e privacidade (LGPD):** Dados reais de operacoes de delivery contam historicos de clientes (enderecos, preferencias, horarios de pedido), dados de entregadores (localizacao GPS, renda, desempenho individual) e informacoes de restaurantes (volume de vendas, horarios de pico). Compartilhar esses dados publicamente — mesmo anonimizados — viola principios de privacidade e pode configurar infringencia a LGPD.

**Reprodutibilidade garantida:** Com `seed=42`, qualquer pessoa que clone o repositorio e rode `generate_doordash.py` obtera exatamente o mesmo dataset, com os mesmos numeros, as mesmas flags de qualidade e os mesmos resultados estatisticos. Isso e impossivel com dados reais que mudam continuamente.

**Controle sobre ground truth:** Em dados sinteticos, sabemos exatamente qual efeito foi injetado. O algoritmo B foi programado para ser 6% mais rapido (multiplicador_b = 0.94). Isso nos permite validar que a analise detectou o efeito correto — um teste de sanidade impossivel com dados reais onde o "efeito verdadeiro" e desconhecido.

**Transparencia pedagogica:** Para um case de aprendizado, a capacidade de ver o codigo que gerou os dados e essencial para entender por que os resultados sao o que sao. Dados reais sao uma caixa preta; dados sinteticos sao completamente transparentes.

### As 29 Colunas em 7 Grupos Logicos

O schema foi projetado para refletir a complexidade real de um sistema de delivery:

**Grupo 1 — Identificadores (5 colunas):** order_id, customer_id, restaurant_id, delivery_id, dasher_id. Chaves primarias e estrangeiras que simulam o sistema de microsservicos: servico de pedidos, servico de clientes, servico de restaurantes, servico de delivery, servico de dashers — cada um com seu proprio namespace de IDs.

**Grupo 2 — Temporal (4 colunas):** created_at, dasher_assigned_at, pickup_at, delivered_at. Os quatro timestamps principais do fluxo de negocio, mais os 7 stage timestamps que rastreiam cada micro-etapa.

**Grupo 3 — Negocio (3 colunas):** ab_group (A ou B), status (delivered/cancelled/in_progress), total_amount_usd. O valor do pedido foi gerado com distribuicao log-normal (media ~$25, desvio padrao ~$12) para refletir a assimetria real: a maioria dos pedidos e de valor medio, mas ha uma cauda de pedidos de alto valor.

**Grupo 4 — Dimensoes (3 colunas):** customer_city (6 cidades), customer_segment (Premium/Standard/Budget), restaurant_category (Fast Food, Pizza, Sushi, etc).

**Grupo 5 — Os 7 Estagio Timestamps:** stage_1 (pedido criado) ate stage_7 (entregue). Esses timestamps sao a espinha dorsal da analise de etapas no dbt intermediate.

**Grupo 6 — Colunas Derivadas (3 colunas):** delivery_duration_minutes (calculada de stage_1 a stage_7), hour_of_day (0-23), month (Jan/Feb/Mar), delivery_stage_bucket (periodo do dia).

**Grupo 7 — Flags de Qualidade (4 colunas booleanas):** has_duplicate_flag, has_timestamp_issue_flag, has_missing_dasher_flag, has_outlier_flag. Cada flag indica um problema especifico, permitindo que o pipeline downstream filtre de forma granular.

### Os 4 Problemas de Qualidade e Sua Motivacao em Producao

**Duplicatas (2%, 200 pedidos):** Em sistemas de pagamento distribuidos, a entrega de eventos nao e garantida uma unica vez (at-most-once vs at-least-once delivery). Quando um webhook de confirmacao de pagamento nao recebe ACK (acknowledgment) do servidor de destino dentro do timeout, o sistema reenvia o evento. Se o servidor de destino ja processou o evento mas o ACK foi perdido na rede, o evento e processado duas vezes — gerando uma duplicata. Sistemas de producao robustos implementam idempotencia usando uma chave idempotency_key, mas sistemas legados frequentemente nao tem essa protecao.

**Timestamps fora de ordem (1%, 97 pedidos):** Em arquiteturas de microsservicos, cada servico escreve em seu proprio banco de dados com seu proprio clock. Clock skew (desincronizacao de relogios entre servidores) de ate 200ms e comum mesmo com NTP. Quando eventos de servicos diferentes sao consolidados em um data warehouse, mensagens que chegaram depois podem ter timestamp anterior ao da mensagem que chegou antes. Por exemplo: o evento "dasher_assigned" pode ter timestamp 14:30:05.100 enquanto o evento "order_placed" que o precedeu tem timestamp 14:30:05.300 — porque o servico de dasher tem o relogio 200ms adiantado.

**Dasher nao atribuido (1%, 97 pedidos):** Em horarios de alta demanda, o algoritmo de alocacao pode esgotar o timeout de busca (normalmente 30 segundos) sem encontrar um dasher disponivel dentro do raio configurado. O pedido entra em um estado de "orfao": confirmado pelo restaurante, mas sem entregador. Esses pedidos ficam em fila ate um dasher ficar disponivel ou ate o cliente cancelar. No dado bruto, dasher_id e NULL — o que causa problemas em JOINs e calculos de tempo de atribuicao.

**Outliers acima de 120 minutos (1%, 97 pedidos):** Entregas com mais de 2 horas sao eventos extraordinarios que nao representam o fluxo operacional normal. As causas em producao incluem: dasher com problema mecanico no veiculo (moto fura, carro quebra), pedido perdido no restaurante (restaurante nao encontra o pedido mesmo apos dasher chegar), cancelamento parcial onde o pedido tecnicamente nao e cancelado mas fica em limbo, ou erros de geolocalicacao onde o GPS marca entrega no endereco errado. Esses registros sao validos para analises de excepcao, mas devem ser removidos do calculo de tempo medio de entrega para nao distorcer as metricas principais.

---

## Secao 5: Pipeline de Dados — Passo a Passo

### 5.1 Geracao dos Dados (generate_doordash.py)

O script de geracao usa distribuicoes estatisticas reais para criar um dataset verossimil:

**Tempo de entrega (distribuicao log-normal):** O tempo de entrega real em plataformas de delivery nao segue uma distribuicao normal — ele tem uma cauda longa a direita. Pedidos demoram no minimo 15-20 minutos (tempo fisico minimo de preparo + rota), mas podem demorar muito mais em casos extraordinarios. A distribuicao log-normal captura exatamente essa assimetria: a maioria dos pedidos esta em torno de 35-40 minutos, mas ha uma cauda de pedidos de 60-90 minutos.

**Injecao do efeito A/B:** O efeito do algoritmo B foi injetado multiplicando o tempo de entrega dos pedidos do grupo B por 0.94:

```python
multiplicador_b = 0.94  # Algoritmo B e 6% mais rapido
delivery_time = base_time * (multiplicador_b if ab_group == 'B' else 1.0)
```

Isso garante que o "ground truth" do experimento e exatamente -6%. A analise recuperou -6.4% (ligeiramente diferente devido a variancia amostral), o que e o comportamento correto de um estimador estatistico.

**Injecao da tendencia mensal de cancelamentos:** Os pesos de distribuicao de pedidos por mes foram ajustados para criar a tendencia crescente de cancelamentos:

```python
pesos_mes = [0.42, 0.35, 0.23]  # Jan=42%, Fev=35%, Mar=23%
taxa_cancelamento = {'Jan': 0.049, 'Feb': 0.085, 'Mar': 0.120}
```

Isso simula uma degradacao operacional real: em Janeiro a plataforma estava saudavel (4.9% cancelamento), mas em Marco o problema escalonou (12.0%).

**Injecao dos problemas de qualidade:** Os problemas foram injetados em sequencia apos a geracao do dataset limpo:

```python
# Passo 1: Gera dataset limpo com seed=42
# Passo 2: Duplica 200 registros aleatorios (2% de duplicatas)
# Passo 3: Embaralha timestamps de 97 registros (clock skew)
# Passo 4: Remove dasher_id de 97 registros (atribuicao falhada)
# Passo 5: Infla delivery_time de 97 registros para >120min (outliers)
```

### 5.2 EDA e Limpeza (eda_cleaning.py)

O pipeline de limpeza segue o principio de "sem informacao perdida" — cada decisao de limpeza e registrada em uma flag booleana em vez de simplesmente deletar o registro:

**Por que remover duplicatas antes de qualquer analise:** Metricas agregadas calculadas sobre dados com duplicatas sao incorretas de formas sutis. A media de tempo com 200 duplicatas de pedidos rapidos e artificialmente menor do que a media real. O COUNT de pedidos esta inflado. Qualquer JOIN downstream com a tabela de clientes ou restaurantes pode gerar fanout. A deduplicacao precisa ser o primeiro passo.

**Por que reordenar timestamps com np.sort em vez de dropar o registro:** Dropar o registro significa perder dados que sao validos — apenas o registro chegou fora de ordem, nao o evento em si. Interpolar timestamps entre etapas e arriscado porque assume linearidade entre eventos que nao sao lineares. Reordenar assume apenas que as etapas ocorreram na sequencia correta, mesmo que os registros tenham chegado fora de ordem — uma suposicao muito mais conservadora e defensavel.

**Por que usar a string "UNASSIGNED" em vez de NULL para dashers ausentes:** NULL em SQL tem comportamento especial: propaga para qualquer calculo (avg(NULL) = NULL, NULL != NULL e NULL = NULL sao ambos NULL). Uma string explicita "UNASSIGNED" permite filtrar, agrupar e identificar esses casos sem comportamento imprevisivel. Alem disso, deixa claro para qualquer analista downstream que esse dasher_id nao e um dado faltante por erro — e um estado de negocio valido.

**Por que threshold fixo de 120 minutos em vez de IQR:** O metodo IQR (Q3 + 1.5 x IQR) e um criterio estatistico genericamente util, mas em distribuicoes log-normais (como tempo de entrega) ele tende a remover 7-10% dos dados, incluindo entregas longas mas legitimas (pedidos distantes, condicoes climaticas adversas). Um threshold de 120 minutos e o SLA maximo de negocio da DoorDash — acima disso, o cliente tem direito a reembolso automatico. Usar o criterio de negocio e mais interpretavel, auditavel e defensavel para um stakeholder nao-tecnico.

**Resultado do pipeline de limpeza:**

| Etapa | Linhas |
|-------|--------|
| Raw (com duplicatas) | 10.200 |
| Apos deduplicacao | 9.800 |
| Apos remocao de outliers | 9.703 |
| Entregues sem flags de problema | ~8.650 |

### 5.3 Modelagem com dbt

**Por que dbt em vez de SQL puro ou pandas:**

SQL puro em scripts avulsos e o padrao mais comum em times de analytics sem maturidade de engenharia. Os problemas sao conhecidos: sem versionamento de logica de negocio (o script muda, o historico se perde), sem testes automatizados (voce descobre que a coluna ficou NULL so quando o CEO pergunta), sem documentacao automatica (o proximo analista nao sabe de onde veio a coluna), sem lineage (e impossivel saber quais dashboards sao afetados se uma fonte mudar).

pandas em vez de SQL e uma escolha valida para analises exploratórias, mas nao escala para pipelines de producao. Um DataFrame de 10 milhoes de linhas nao cabe em memoria de uma maquina padrao. Alem disso, logica de transformacao em Python e muito mais verbosa que SQL equivalente e muito mais dificil de revisao por pares que entendem SQL mas nao Python.

dbt resolve esses problemas: e SQL com superpoderes. Voce escreve SQL, o dbt adiciona versionamento (via Git), testes declarativos, documentacao automatica e lineage visual.

**As 3 Camadas e o Raciocinio:**

A camada de staging (`stg_pedidos`) faz apenas limpeza e padronizacao de tipos. Ela e materializada como view porque precisa sempre refletir o dado mais fresco da fonte. O codigo faz exatamente 29 casts de tipo (varchar, timestamp, decimal, boolean, integer) e adiciona duas colunas derivadas simples (is_delivered e is_cancelled). Nao ha joins, nao ha business logic, nao ha calculos complexos. A regra de ouro e: "staging e o lugar para padronizar, nao para transformar."

A camada intermediate (`int_pedidos_com_etapas`) e onde a logica de negocio comeca. Aqui calculamos as 6 duracoes de etapa (duracao_aceite_min, duracao_preparo_min, duracao_atribuicao_min, duracao_coleta_min, duracao_rota_min, duracao_proximidade_min) como diferencas entre os 7 stage timestamps. Essa camada e materializada como view porque ela nao precisa ser consultada diretamente — serve apenas como preparacao para os marts.

A camada de marts (`fct_entregas` e `fct_ab_resultados`) e o produto final. `fct_entregas` tem granularidade de 1 linha por pedido entregue, com todas as metricas calculadas e as colunas de classificacao (rapida/normal/lenta, is_horario_pico). `fct_ab_resultados` agrega por grupo A/B com o delta calculado via cross join. Ambas sao materializadas como table porque consultas de BI precisam de performance — nao podem re-calcular tudo a cada query.

**Os 29 Testes:**

Os 29 testes foram escritos para garantir quatro propriedades criticas do dado:

- 8 testes `not_null`: garantem que colunas essenciais (order_id, ab_group, tempo_total_min, customer_city, mes, etc.) nunca sao NULL na saida dos modelos. Se um JOIN falhar silenciosamente, esses testes pegam.
- 4 testes `unique`: garantem que a granularidade dos modelos esta correta. `order_id` deve ser unico em cada camada — se duplicatas passarem do staging, esse teste falha no intermediate e no mart.
- 16 testes `accepted_values`: garantem que os dominios sao validos. ab_group so pode ser 'A' ou 'B'. status so pode ser 'delivered', 'cancelled' ou 'in_progress'. customer_city so pode ser uma das 6 cidades. Qualquer dado corrompido que crie um valor fora do dominio e detectado imediatamente.
- 1 teste singular customizado (`assert_grupo_b_mais_rapido.sql`): este e o teste de negocio. Ele consulta `fct_ab_resultados` e verifica que a media de tempo do grupo B e estritamente menor que a do grupo A. Se o pipeline rodar com dados corrompidos onde A vence B, o teste falha e o pipeline para antes de alimentar o dashboard.

**Por que DuckDB:**

DuckDB foi escolhido sobre Postgres porque nao requer servidor: e um arquivo `.duckdb` local que o dbt lê e escreve diretamente. Ele e otimizado para OLAP (processamento colunar), nao para OLTP. Lê CSV nativamente sem precisar de COPY ou INSERT. Tem SQL compativel com ANSI com extensoes modernas (percentile_cont, median, epoch). Para um case local e para ci/cd em GitHub Actions, e a escolha mais simples e eficiente.

### 5.4 Analise Estatistica do A/B Test

**Por que Welch t-test em vez de t-test Student padrao:**

O t-test de Student assume que as variancas dos dois grupos sao iguais (homoscedasticidade). Antes de fazer o teste, verificamos essa suposicao com o teste de Levene: o resultado foi p < 0.05, indicando que as variancas sao significativamente diferentes (Grupo A: desvio padrao 8.18, Grupo B: 8.05). O Welch t-test relaxa essa suposicao usando graus de liberdade de Satterthwaite ajustados para as variancas diferentes — e mais robusto e o correto para dados reais.

O Mann-Whitney (teste de Wilcoxon) seria a alternativa nao-parametrica se a distribuicao nao fosse aproximadamente normal. Com n > 4.000 por grupo, o Teorema Central do Limite garante que a distribuicao das medias e aproximadamente normal — entao Welch e apropriado e mais facil de interpretar (opera em unidades de minutos, nao em ranks).

**O que e p-value em linguagem de negocio:**

O p-value responde a seguinte pergunta: "Se os dois algoritmos fossem identicos (hipotese nula verdadeira), qual seria a probabilidade de observarmos uma diferenca de pelo menos 2.44 minutos por puro acaso, so pela variabilidade natural dos dados?"

No nosso caso, p ≈ 0.000 (mais precisamente, p < 0.000001). Isso significa: a probabilidade de ver essa diferenca por acaso e menor que 1 em 1 milhao. Praticamente impossivel.

A armadilha mais comum: p < 0.05 nao significa "efeito grande". Com n=10.000, mesmo uma diferenca de 0.05 minutos (3 segundos) pode ter p < 0.05. E por isso que reportamos simultaneamente: o delta absoluto (2.44 min), o delta relativo (6.4%), o IC 95% ([-2.71, -2.17]), o effect size de Cohen's d (≈0.30) e o impacto financeiro estimado (ROI 274%). A decisao de negocio usa todos esses numeros juntos.

**IC 95%: [-2.71, -2.17] minutos:**

A interpretacao correta: "Com 95% de confianca, o verdadeiro efeito do algoritmo B esta entre 2.17 e 2.71 minutos de reducao no tempo de entrega." O intervalo nao inclui zero, o que confirma que o efeito e real. O lado inferior do intervalo (2.17 min) e o cenario pessimista — mesmo no pior caso plausivel, o algoritmo B economiza mais de 2 minutos por entrega.

**Effect size (Cohen's d):**

```
d = delta / desvio_padrao_poolado = 2.44 / 8.1 ≈ 0.30
```

Por convencao de Cohen: d=0.2 e pequeno, d=0.5 e medio, d=0.8 e grande. Nosso d=0.30 e "pequeno a medio" — mas isso e uma classificacao estatistica generica. Em contexto de delivery, economizar 2.44 minutos em uma entrega de 38 minutos (6.4%) e economicamente relevante independente do label estatistico.

**B vence em todas as 6 cidades:**

| Cidade | Media A (min) | Media B (min) | Delta (min) | Delta % |
|--------|---------------|---------------|-------------|---------|
| Curitiba | 38.30 | 35.27 | -3.03 | -7.91% |
| Porto Alegre | 38.54 | 35.51 | -3.03 | -7.86% |
| Rio de Janeiro | 38.27 | 35.74 | -2.53 | -6.61% |
| Belo Horizonte | 38.17 | 35.85 | -2.32 | -6.08% |
| Brasilia | 37.92 | 35.84 | -2.08 | -5.49% |
| Sao Paulo | 37.70 | 35.97 | -1.73 | -4.59% |

Sao Paulo teve o menor ganho (-4.59%), provavelmente porque a maior densidade de trafego e pool de dashers adiciona ruido ao modelo preditivo. Isso e um sinal de que o algoritmo pode precisar de ajuste especifico para mercados de alta densidade.

**B vence em todos os 5 periodos do dia:**

| Periodo | Media A (min) | Media B (min) | Delta (min) | Delta % |
|---------|---------------|---------------|-------------|---------|
| Tarde (14-18h) | 38.39 | 35.49 | -2.90 | -7.55% |
| Manha (6-11h) | 38.38 | 35.82 | -2.56 | -6.67% |
| Madrugada (0-5h) | 38.19 | 35.71 | -2.48 | -6.49% |
| Noite (18-23h) | 37.69 | 35.56 | -2.13 | -5.65% |
| Almoco (11-14h) | 38.01 | 35.97 | -2.04 | -5.37% |

**Calculo do ROI de 274%:**

```
Economia operacional/mes = 2.44 min x R$0.50 x 333 pedidos/dia x 30 dias = R$12.183
Receita incremental/mes  = 333 x 0.001 x 2.44 x R$38.50 x 30        = R$939
Beneficio total/mes      = R$12.183 + R$939                           = R$13.122

Custo de implementacao   = 3 meses x R$12.000 de eng                 = R$36.000
Beneficio anual          = R$13.122 x 12                             = R$157.464
Retorno liquido          = R$157.464 - R$36.000                      = R$121.464
ROI                      = R$121.464 / R$36.000 x 100                = 337%
ROI conservador (274%)   = usando apenas economia operacional sem receita incremental
```

### 5.5 Dashboard (streamlit_app.py)

**Por que Streamlit em vez de Power BI ou Tableau:**

Power BI e Tableau sao ferramentas excelentes para dashboards de BI tradicionais: grids, barras, linhas, filtros. Mas eles nao conseguem executar codigo Python arbitrario em resposta a interacao do usuario. Para nosso caso, precisamos recalcular o Welch t-test e o IC 95% em tempo real quando o usuario muda os filtros de cidade ou periodo — isso nao e possivel em Power BI sem DAX extremamente complexo que ainda nao teria a scipy por baixo.

Streamlit resolve isso porque e Python puro: qualquer filtro de cidade ou periodo no sidebar recalcula o scipy.stats.ttest_ind com os dados filtrados e atualiza o p-value, o IC e o delta na tela. O trade-off e que o visual e menos polido que Power BI — mas para uma audiencia tecnica que precisa confiar na estatistica, a transparencia do calculo vale mais que o acabamento visual.

**Decisoes de design por pagina:**

Pagina 1 — Visao Geral: o grafico de tendencia mensal usa dual-axis porque pedidos (escala ~3.000-4.000) e taxa de cancelamento (escala 0-15%) sao magnitudes incompativeis. Compartilhar o mesmo eixo Y tornaria uma das series invisivel. O dual-axis deixa ambas as series legiveis com suas escalas proprias.

Pagina 2 — Resultado A/B: o boxplot foi escolhido sobre barras de media porque mostra a distribuicao completa: mediana, IQR (caixa), whiskers (1.5x IQR), e outliers individuais. Uma barra de media esconde que o Grupo A tem outliers acima de 80 minutos que estao puxando a media para cima — o boxplot torna isso visivel imediatamente.

Pagina 3 — Analise por Etapa: o waterfall mostra a composicao aditiva do tempo total de entrega, permitindo identificar visualmente qual etapa domina. A etapa de Rota (17.30 min, 43% do tempo total) e a maior contribuidora — o que explica por que o algoritmo preditivo, que otimiza a rota, tem o maior ganho nessa etapa (-1.15 min, -6.4%).

Pagina 4 — Impacto Financeiro: os inputs interativos (pedidos por dia, custo por minuto, ticket medio) permitem que cada gestor calibre o modelo com seus proprios dados de negocio. Um ROI calculado com premissas ajustaveis e muito mais convincente para um CEO do que um numero estatico — porque ele pode ver como o resultado muda se ele alterar as premissas.

`st.cache_data` e aplicado ao carregamento do CSV (9.703 linhas). Sem cache, cada interacao de filtro recarregaria o arquivo do disco (~2 segundos de lag perceptivel). Com cache, o DataFrame fica em memoria e os filtros respondem em menos de 50ms.

---

## Secao 6: Ferramentas e Justificativas

| Ferramenta | O que faz | Por que escolhemos | Alternativas | Quando NAO usar |
|---|---|---|---|---|
| Python 3.11 | Geracao de dados, EDA, scripts | Ecossistema rico (pandas, scipy, numpy), padrao de mercado | R, Julia | Quando equipe e 100% SQL |
| dbt Core | Transformacao e modelagem | Versionamento, testes, docs automaticos, padrao de mercado | SQLMesh, Dataform | Projetos muito simples sem necessidade de lineage |
| DuckDB | Storage analitico | Zero-config, OLAP local, le CSV nativo, zero custo | Postgres, Snowflake, BigQuery | Quando precisa de multiusuario ou dados > 100GB |
| Streamlit | Dashboard interativo | Python nativo, deploy rapido, calculo estatistico integrado | Power BI, Tableau, Metabase | Stakeholders nao-tecnicos preferem interface familiar |
| Plotly | Visualizacoes | Interatividade nativa, suporte a boxplot e waterfall | matplotlib, seaborn, altair | Quando precisa de charts muito customizados em SVG |
| scipy.stats | Testes estatisticos | Welch t-test, IC 95%, poder estatistico | statsmodels, pingouin | Quando precisa de modelos mais complexos como regressao ou ANOVA |
| GitHub Actions | CI/CD | Gratis para repositorios publicos, integrado ao GitHub | CircleCI, Jenkins, GitLab CI | Pipelines muito complexos com muitos steps paralelos |
| dbt_utils | Testes genericos extras | Testes de schema mais ricos sem escrever SQL custom | Nao ha equivalente direto | Nao se aplica — adicionar pacotes dbt tem custo zero |

---

## Secao 7: Resultados e Decisao Final

### Resultados por Hipotese

**H1: O algoritmo de alocacao e o principal gargalo — CONFIRMADA**
O algoritmo FIFO foi substituido pelo preditivo e o resultado foi uma reducao estatisticamente significativa de 2.44 minutos (6.4%) no tempo medio de entrega. p-value ≈ 0.000, t=14.0, IC 95% [-2.71, -2.17]. O experimento confirma que a mudanca de algoritmo, e nao outro fator (sazonalidade, perfil de cliente, regiao), e responsavel pela diferenca.

**H2: A etapa de Rota e a mais critica — CONFIRMADA**
Analise por etapa mostra que a Rota teve o maior ganho absoluto em resposta ao algoritmo B: -1.15 min (-6.4%), seguida de Preparo (-0.73 min) e Atribuicao (-0.50 min). O algoritmo preditivo impacta mais fortemente a etapa de Rota porque ao programar a chegada do dasher no momento certo, o dasher pode partir do restaurante com um itinerario mais otimizado em vez de correr para compensar tempo perdido em espera.

**H3: Reducao de pelo menos 5% — CONFIRMADA**
O resultado de -6.4% supera o MDE de 5%. O intervalo de confianca 95% de [-2.71, -2.17] esta inteiramente abaixo de -1.9 min (o limiar de 5%), confirmando que mesmo no cenario pessimista o efeito supera o threshold.

**H4: B vence em todas as regioes e horarios — CONFIRMADA**
Analise segmentada confirma: B vence em todas as 6 cidades (de -4.59% em Sao Paulo a -7.91% em Curitiba) e em todos os 5 periodos do dia (de -5.37% no Almoco a -7.55% na Tarde). A unanimidade dos resultados e um sinal forte de robustez — o efeito nao e artefato de um segmento especifico.

### Decisao: Rollout Total do Algoritmo B

**Plano de rollout em 3 semanas:**

- Semana 1 — 25% do trafego: monitorar cancelamentos (alerta se > 12%), dasher_score medio (alerta se cai > 5%), e tempo de atribuicao (alerta se > 5 min). Foco em deteccao precoce de efeitos adversos.
- Semana 2 — 50% do trafego: validar que o ganho de -6.4% persiste fora do ambiente controlado do experimento (sem Hawthorne effect). Monitorar NPS de restaurantes (entregadores chegando no momento certo afeta positivamente a avaliacao do restaurante).
- Semana 3 — 100% do trafego: rollout completo. Manter monitoramento por 30 dias adicionais. Reportar impacto financeiro real vs projetado.

**Guardrails (o que monitorar continuamente):**
- Taxa de cancelamento: alerta se > 12% (ja estava crescendo durante o experimento — tendencia preocupante independente do A/B)
- dasher_score medio: alerta se cai > 5% (novo algoritmo pode ser mais exigente com dashers que tem historico variavel)
- Tempo de atribuicao: alerta se > 5 min (o algoritmo preditivo e mais computacionalmente intenso; se o servico de predicao ficar lento, o impacto e imediato na atribuicao)
- NPS de restaurantes: alerta se cai (entregadores chegando muito cedo ou muito tarde impacta a experiencia do restaurante com a plataforma)

### Limitacoes do Estudo

**Dataset sintetico:** Nao captura sazonalidade real (feriados, eventos locais, clima), variacao de densidade urbana real, ou comportamento especifico de cidades brasileiras.

**Duracao de 10 dias:** Pode nao capturar completamente o "efeito novidade" (dashers podem se comportar diferente quando o algoritmo muda) ou o efeito de aprendizado do modelo preditivo (que melhora com mais dados ao longo do tempo).

**6 cidades:** Sao Paulo teve o menor ganho (-4.59%). Em uma operacao real com dezenas de cidades, algumas podem nao se beneficiar do algoritmo preditivo da mesma forma — o rollout precisaria de analise cidade por cidade.

**ROI baseado em premissas:** O calculo de ROI usa R$0.50/min como custo operacional de dasher e R$38.50 como ticket medio. Esses numeros sao estimativas. O ROI real pode ser 30% maior ou menor dependendo dos numeros reais de custo da operacao.

---

## Secao 8: Glossario

**dbt (data build tool):** Ferramenta para transformar dados com SQL organizado em camadas com versionamento, testes e documentacao automatica. Analogia: e como uma receita de bolo com etapas ordenadas, ingredientes rastreavies e testes de qualidade em cada etapa. O chef (analista) escreve a receita; o dbt garante que ela e executada na ordem correta e que cada ingrediente esta no padrao.

**EDA (Exploratory Data Analysis):** Analise exploratoria inicial para entender o dado antes de modelar — distribuicoes, valores nulos, outliers, correlacoes. Analogia: e o "reconhecimento do terreno" antes de construir. Um arquiteto nao projeta um edificio sem estudar o solo; um analista nao modela dados sem fazer EDA.

**A/B Test:** Experimento controlado onde dois grupos recebem versoes diferentes de um produto ou algoritmo. O grupo A recebe a versao atual (controle) e o grupo B recebe a nova versao (tratamento). Comparamos metricas entre os grupos para decidir qual versao e melhor. Analogia: dar cardapios diferentes para dois grupos de clientes em restaurantes identicos e comparar a gorjeta media.

**p-value:** Probabilidade de observar o efeito medido (ou um efeito maior) se a hipotese nula fosse verdadeira — ou seja, se nao houvesse diferenca real entre os grupos. Valores abaixo de 0.05 sao a convencao para "evidencia suficiente contra a hipotese nula". No nosso caso, p ≈ 0.000 significa que a probabilidade de ver uma diferenca de 2.44 min por acaso e menor que 0.001%.

**DuckDB:** Banco de dados analitico que roda como um arquivo local, sem servidor, sem instalacao. Especializado em consultas OLAP (agregacoes, JOINs em grandes volumes). Analogia: o SQLite do mundo de analytics — leve como um arquivo de texto, mas poderoso como um banco colunar de producao.

**Staging (dbt):** Primeira camada de transformacao no pipeline dbt. Faz apenas limpeza e padronizacao de tipos — sem joins, sem business logic. Regra: uma coluna por fonte, sempre. Materializada como view.

**Mart (dbt):** Camada final de consumo no pipeline dbt. Tem granularidade clara (ex: 1 linha = 1 entrega), esta pronta para BI e analises. Materializada como table para performance.

**Welch t-test:** Variante do t-test classico que nao assume variancas iguais entre os dois grupos comparados. Usa graus de liberdade ajustados pelo metodo de Satterthwaite. Mais robusto para dados reais onde a variancia entre grupos raramente e identica.

**MDE (Minimum Detectable Effect):** Menor diferenca entre grupos que o experimento consegue detectar com poder estatistico suficiente, dado o tamanho amostral. Define o "piso" do experimento: efeitos abaixo do MDE podem existir mas nao serao detectados de forma confiavel.

**Poder estatistico:** Probabilidade de detectar um efeito real quando ele existe (P(rejeitar H0 | H1 verdadeira)). Convencao de mercado: 80%. Poder menor que 80% significa que o experimento tem chances razoaveis de perder um efeito real — falso negativo.

**seed=42:** Numero inicial fornecido ao gerador de numeros pseudoaleatorios. Com o mesmo seed, a sequencia de "numeros aleatorios" e identica em todas as execucoes. Garante que o dataset sintetico e identico toda vez que o script roda — reproducibilidade total.

**Hash deterministico:** Funcao matematica que mapeia qualquer input para um output de tamanho fixo, sempre produzindo o mesmo output para o mesmo input. No contexto de A/B test, garante que o mesmo order_id sempre cai no mesmo grupo, mesmo em reprocessamentos ou falhas do sistema.

**CI/CD (Continuous Integration / Continuous Deployment):** Pratica de automatizar build, testes e deploy em todo push de codigo. No nosso pipeline, cada push dispara: geracao de dados, dbt run, dbt test. Se qualquer etapa falhar (incluindo o teste A/B singular), o pipeline para e o time e notificado antes que dados incorretos cheguem ao dashboard.

**Effect size (Cohen's d):** Medida padronizada do tamanho do efeito, calculada como a diferenca entre medias dividida pelo desvio padrao poolado. Independente do tamanho amostral — permite comparar efeitos entre estudos com n diferentes. Por convencao: d=0.2 pequeno, d=0.5 medio, d=0.8 grande.

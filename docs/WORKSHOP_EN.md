# Workshop DoorDash Analytics — Facilitator Guide

**Duration:** 4 hours | **Level:** Intermediate | **Prerequisites:** Basic Python + SQL
**Repository:** https://github.com/gabriel-analytics/doordash-analytics-case
**Dashboard:** https://doordash-analytics-case-hupqbwjyucsrwzsvceqqyw.streamlit.app

---

## Before Starting — Facilitator Setup

🇧🇷 Projetor com terminal aberto na raiz do repositorio

🇺🇸 Projector with terminal open at the repository root

---

🇧🇷 Streamlit rodando localmente em http://localhost:8501

🇺🇸 Streamlit running locally at http://localhost:8501

---

🇧🇷 dbt docs servindo em http://localhost:8080

🇺🇸 dbt docs serving at http://localhost:8080

---

🇧🇷 Slides de referencia fechados — o roteiro e o terminal

🇺🇸 Reference slides closed — the script and the terminal are the guide

---

🇧🇷 Avisar: "Vamos codar ao vivo. Pode ter erro. Isso e proposital."

🇺🇸 Announce: "We will code live. There may be errors. That is intentional."

---

## MODULE 1 — The Business Problem (45 min)

[FACILITADOR - Abertura]

🇧🇷 "Antes de escrever uma linha de codigo hoje, vou te fazer uma pergunta de negocio. Apenas uma. E quero que voce pense de verdade antes de responder."

🇺🇸 [FACILITATOR - Opening] "Before we write a single line of code today, I am going to ask you a business question. Just one. And I want you to genuinely think before answering."

---

🇧🇷 Pausa de 3 segundos.

🇺🇸 Pause for 3 seconds.

---

🇧🇷 "Voce e o Head of Analytics da DoorDash Brasil. Sao 9h de segunda-feira. Seu CEO manda uma mensagem no Slack. A mensagem diz: 'O tempo medio de entrega subiu 15% no ultimo trimestre. O que esta acontecendo?' — so isso. Sem contexto adicional."

🇺🇸 "You are the Head of Analytics at DoorDash Brazil. It is 9am on a Monday. Your CEO sends a message on Slack. The message says: 'Average delivery time went up 15% last quarter. What is going on?' — that is it. No additional context."

---

🇧🇷 "O que voce faz primeiro?"

🇺🇸 "What do you do first?"

---

[TURMA - Discussao livre, 2 min]

🇧🇷 Deixar a turma responder. Nao corrigir ainda. Ouvir as respostas. As respostas tipicas vao ser: "abro o dashboard", "faco uma query no banco", "ligo para o time de operacoes". Todas estao corretas, mas incompletas.

🇺🇸 [CLASS - Open discussion, 2 min] Let the class respond. Do not correct yet. Listen to the answers. Typical answers will be: "I open the dashboard", "I run a query on the database", "I call the operations team." All of these are correct, but incomplete.

---

[FACILITADOR - Storytelling da DoorDash]

🇧🇷 "Antes de responder, deixa eu te contar quem e a DoorDash."

🇺🇸 [FACILITATOR - DoorDash Storytelling] "Before answering, let me tell you who DoorDash is."

---

🇧🇷 "A DoorDash e o maior marketplace de delivery de comida dos EUA. Mais de 35 milhoes de pedidos por mes. O modelo de negocio e simples: eles conectam clientes, restaurantes e entregadores — os dashers — e cobram uma comissao de 15% do restaurante em cima de cada pedido. Parece pouco? 15% de cada pizza, hamburguer e sushi pedido em dezenas de cidades todos os dias soma bilhoes."

🇺🇸 "DoorDash is the largest food delivery marketplace in the US. Over 35 million orders per month. The business model is simple: they connect customers, restaurants, and delivery drivers — dashers — and charge a 15% commission from the restaurant on each order. Seems small? 15% of every pizza, burger, and sushi ordered across dozens of cities every day adds up to billions."

---

🇧🇷 "Mas o produto da DoorDash nao e a comida. O produto da DoorDash e a velocidade. A promessa que eles vendem para o cliente e: 'Voce vai receber sua comida rapido, quente, e sem complicacao.' Se eles quebram essa promessa, perdem o cliente."

🇺🇸 "But DoorDash's product is not the food. DoorDash's product is speed. The promise they sell to the customer is: 'You will receive your food fast, hot, and hassle-free.' If they break that promise, they lose the customer."

---

🇧🇷 "Agora imagina que no primeiro trimestre de 2025, os dados mostram que o tempo medio de entrega subiu 15%. Nao 1%, nao 2% — 15%. Isso e o equivalente a um restaurante que sempre entregava em 35 minutos passar a entregar em 40 minutos sem nenhuma justificativa."

🇺🇸 "Now imagine that in Q1 2025, the data shows that average delivery time went up 15%. Not 1%, not 2% — 15%. That is the equivalent of a restaurant that always delivered in 35 minutes now delivering in 40 minutes with no explanation."

---

🇧🇷 "E o CEO, que nao tem um dashboard aberto na frente dele agora, e que nao sabe se e problema de algoritmo, de contratacao, de trafego ou de sazonalidade — ele manda aquela mensagem no Slack."

🇺🇸 "And the CEO, who does not have a dashboard open right now, who does not know if it is an algorithm issue, a hiring issue, a traffic issue or a seasonality issue — sends that Slack message."

---

[FACILITADOR - O impacto financeiro]

🇧🇷 "Antes de comecar a analise tecnica, precisamos entender o que '15% mais lento' significa em dinheiro. Porque se o CEO vai tomar uma decisao de investimento — seja contratar engenheiros, mudar algoritmo, ou abrir novas operacoes — ele precisa de um numero, nao de um grafico bonito."

🇺🇸 [FACILITATOR - The financial impact] "Before starting the technical analysis, we need to understand what '15% slower' means in money. Because if the CEO is going to make an investment decision — whether to hire engineers, change the algorithm, or open new operations — he needs a number, not a pretty chart."

---

🇧🇷 "Usamos uma formula simples:"

🇺🇸 "We use a simple formula:"

---

🇧🇷 Escrever no quadro ou mostrar no terminal:

🇺🇸 Write on the board or show in the terminal:

```
Delta_Revenue = Delta_Time x Cost_Per_Minute x Orders_Per_Day
              + Delta_Retention x Average_Ticket x Orders_Per_Day
```

---

🇧🇷 "Cada minuto extra que o dasher passa esperando o pedido ficar pronto custa dinheiro. Estimamos R$0.50 por minuto por entrega — entre incentivos ao dasher e custo de oportunidade. Com 333 pedidos por dia no nosso scope, 2.44 minutos a mais por entrega custam R$12.000 por mes so em custo operacional."

🇺🇸 "Every extra minute the dasher spends waiting for the order to be ready costs money. We estimate R$0.50 per minute per delivery — between dasher incentives and opportunity cost. With 333 orders per day in our scope, 2.44 extra minutes per delivery cost R$12,000 per month in operational costs alone."

---

🇧🇷 "Isso sem contar o churn de cliente. Estudos internos de delivery mostram que cada minuto adicional reduz a probabilidade de reorder em 0.3%. Em 2.44 minutos extras, isso e quase 0.7% de churn incremental por cliente. Multiplicado pelo ticket medio de R$38.50 e pela base de pedidos, comeca a ser material."

🇺🇸 "This does not count customer churn. Internal delivery studies show that each additional minute reduces the probability of a reorder by 0.3%. With 2.44 extra minutes, that is nearly 0.7% of incremental churn per customer. Multiplied by the average ticket of R$38.50 and the order base, this starts to be material."

---

🇧🇷 "Entendido o problema. Agora, como a gente resolve?"

🇺🇸 "Problem understood. Now, how do we solve it?"

---

[FACILITADOR - As 4 Hipoteses como Detetive]

🇧🇷 "Vou te mostrar como um bom analista pensa. Nao comecamos com o dado — comecamos com hipoteses. Isso e o metodo cientifico aplicado a analytics."

🇺🇸 [FACILITATOR - The 4 Hypotheses as a Detective] "I am going to show you how a good analyst thinks. We do not start with the data — we start with hypotheses. This is the scientific method applied to analytics."

---

🇧🇷 "Imagina que voce e o Sherlock Holmes dos dados. Voce chegou na cena do crime. Antes de pegar o microscopio, voce observa o ambiente e formula hipoteses. Hipoteses que voce vai tentar refutar, nao confirmar."

🇺🇸 "Imagine you are the Sherlock Holmes of data. You have arrived at the crime scene. Before picking up the microscope, you observe the environment and formulate hypotheses. Hypotheses you will try to refute, not confirm."

---

🇧🇷 "Temos 4 hipoteses aqui:"

🇺🇸 "We have 4 hypotheses here:"

---

🇧🇷 Apresentar cada uma com pausa para perguntas:

🇺🇸 Present each one with a pause for questions:

---

🇧🇷 "Hipotese 1: O algoritmo de alocacao de dashers e o problema. O sistema atual — chamamos de FIFO, First In First Out — pega o dasher mais proximo e manda pra la. Mas ele ignora quando o pedido vai ficar pronto. O dasher chega, fica esperando 10 minutos na porta do restaurante. Esse tempo nao aparece como 'atraso' em lugar nenhum, mas aparece no tempo total de entrega."

🇺🇸 "Hypothesis 1: The dasher allocation algorithm is the problem. The current system — we call it FIFO, First In First Out — picks the nearest available dasher and sends them over. But it ignores when the order will be ready. The dasher arrives and waits 10 minutes at the restaurant door. This time does not show up as 'delay' anywhere, but it appears in the total delivery time."

---

🇧🇷 "Hipotese 2: Dentro do fluxo de entrega, a etapa de atribuicao do dasher e a mais critica — nao a rota. Se o dasher errado e atribuido, cada etapa depois dele fica penalizada em cascata."

🇺🇸 "Hypothesis 2: Within the delivery flow, the dasher assignment step is the most critical — not the route. If the wrong dasher is assigned, every step after that is penalized in a cascade."

---

🇧🇷 "Hipotese 3: Se trocarmos o algoritmo FIFO por um algoritmo preditivo, conseguimos reducao de pelo menos 5% no tempo de entrega. Por que 5%? Porque abaixo de 5%, o custo de implementacao nao justifica o risco operacional de mudar um sistema critico."

🇺🇸 "Hypothesis 3: If we replace the FIFO algorithm with a predictive algorithm, we can achieve at least 5% reduction in delivery time. Why 5%? Because below 5%, the implementation cost does not justify the operational risk of changing a critical system."

---

🇧🇷 "Hipotese 4: O impacto nao e uniforme. Cidades diferentes, horarios diferentes, comportamentos diferentes. O algoritmo pode ser excelente em Curitiba e mediano em Sao Paulo — e precisamos saber isso antes de fazer rollout total."

🇺🇸 "Hypothesis 4: The impact is not uniform. Different cities, different time periods, different behaviors. The algorithm may be excellent in Curitiba and average in Sao Paulo — and we need to know that before a full rollout."

---

[EXERCICIO - 5 min]

[FACILITADOR]

🇧🇷 "Agora e sua vez. Antes de continuar, quero que voce crie a sua propria hipotese — uma quinta hipotese que eu nao listei. Pode ser relacionada ao problema de negocio, ao dado, ao algoritmo, ao comportamento do cliente, ao que voce quiser. Voce tem 5 minutos. Escreva numa folha ou no computador. Depois vamos compartilhar algumas."

🇺🇸 [EXERCISE - 5 min] [FACILITATOR] "Now it is your turn. Before we move on, I want you to create your own hypothesis — a fifth hypothesis I did not list. It can be related to the business problem, the data, the algorithm, customer behavior, whatever you like. You have 5 minutes. Write it on paper or on your computer. Then we will share a few."

---

🇧🇷 Caminhar pela sala durante os 5 minutos. Observar o que as pessoas escrevem.

🇺🇸 Walk around the room during the 5 minutes. Observe what people are writing.

---

[FACILITADOR - Fechamento do modulo]

🇧🇷 "Otimo. Vamos ouvir algumas hipoteses..."

🇺🇸 [FACILITATOR - Module closing] "Great. Let us hear some hypotheses..."

---

🇧🇷 Ouvir 3-4 hipoteses da turma. Comentar brevemente cada uma. Nao refutar — validar o raciocinio.

🇺🇸 Listen to 3-4 hypotheses from the class. Comment briefly on each one. Do not refute — validate the reasoning.

---

🇧🇷 "Excelente. Hipoteses boas sao hipoteses testageis — elas precisam ter uma variavel que voce manipula e uma metrica que voce mede. 'A satisfacao do cliente vai melhorar' nao e hipotese testavel. 'A taxa de pedidos recorrentes vai aumentar em pelo menos 2% com a mudanca X' e hipotese testavel."

🇺🇸 "Excellent. Good hypotheses are testable hypotheses — they need a variable you manipulate and a metric you measure. 'Customer satisfaction will improve' is not a testable hypothesis. 'The recurring order rate will increase by at least 2% with change X' is a testable hypothesis."

---

🇧🇷 "Modulo 2. Agora vamos ver os dados."

🇺🇸 "Module 2. Now let us look at the data."

---

## MODULE 2 — The Data (60 min)

[FACILITADOR - Introducao]

🇧🇷 "Hipoteses sao bonitas. Mas dados sao a realidade. Vamos ver o que temos."

🇺🇸 [FACILITATOR - Introduction] "Hypotheses are beautiful. But data is reality. Let us see what we have."

---

🇧🇷 "Eu vou mostrar um dataset que parece perfeito a primeira vista. Sao 10.000 pedidos de delivery, 29 colunas, periodo de janeiro a marco de 2025. Mas tem 4 problemas escondidos dentro dele. Problemas que eu coloquei intencionalmente — porque em producao voce vai encontrar exatamente esses problemas, ou variacoes deles."

🇺🇸 "I am going to show you a dataset that looks perfect at first glance. It is 10,000 delivery orders, 29 columns, covering January through March 2025. But it has 4 hidden problems inside it. Problems I put in intentionally — because in production you will encounter exactly these problems, or variations of them."

---

🇧🇷 "O desafio: quem encontrar os 4 problemas e conseguir explicar a causa raiz de cada um ganha o respeito eterno da turma. Vamos comecar."

🇺🇸 "The challenge: whoever finds all 4 problems and can explain the root cause of each one earns the eternal respect of the class. Let us begin."

---

[LIVE CODING - generate_doordash.py]

🇧🇷 Abrir o arquivo no terminal:

🇺🇸 [LIVE CODING - generate_doordash.py] Open the file in the terminal:

```bash
cat gen/data/generate_doordash.py
```

---

[FACILITADOR - Comentando o codigo enquanto mostra]

🇧🇷 "Primeiro detalhe que voce precisa notar: `seed=42`. Por que seed=42 especificamente? Nao e magica nem piada de programador — e uma convencao de reproducibilidade. Com o mesmo seed, toda vez que eu rodar esse script, eu vou gerar exatamente o mesmo dataset. Os mesmos pedidos, os mesmos clientes, os mesmos problemas. Isso e critico para que qualquer pessoa que clonar o repositorio chegue nos mesmos resultados que eu."

🇺🇸 [FACILITATOR - Commenting on the code while showing] "First detail you need to notice: `seed=42`. Why seed=42 specifically? It is not magic or a programmer joke — it is a reproducibility convention. With the same seed, every time I run this script I will generate exactly the same dataset. The same orders, the same customers, the same problems. This is critical so that anyone who clones the repository arrives at the same results as me."

---

🇧🇷 "Segundo: a distribuicao do tempo de entrega e log-normal. Por que log-normal e nao normal? Porque tempo de entrega em delivery nao segue uma curva de sino simetrica. Tem um limite inferior fisico — ninguem entrega em zero minutos. Mas nao tem limite superior pratico — um pedido pode demorar 3 horas se o sistema falhar. Distribuicao log-normal captura essa assimetria. A maioria dos pedidos concentra em torno de 35-40 minutos, mas tem uma cauda longa para a direita."

🇺🇸 "Second: the delivery time distribution is log-normal. Why log-normal and not normal? Because delivery time in food delivery does not follow a symmetric bell curve. There is a physical lower bound — nobody delivers in zero minutes. But there is no practical upper bound — an order can take 3 hours if the system fails. The log-normal distribution captures this asymmetry. Most orders cluster around 35-40 minutes, but there is a long tail to the right."

---

🇧🇷 "Terceiro: como o efeito do A/B foi injetado. Veja essa linha:"

🇺🇸 "Third: how the A/B effect was injected. Look at this line:"

---

🇧🇷 Mostrar no codigo:

🇺🇸 Show in the code:

```python
multiplicador_b = 0.94
delivery_time = base_time * (multiplicador_b if ab_group == 'B' else 1.0)
```

---

🇧🇷 "O grupo B e exatamente 6% mais rapido — matematicamente. Quando a gente fizer a analise estatistica, o resultado vai ser -6.4%, nao -6.0% exato. Por que? Porque a variancia amostral sempre adiciona ruido. Se o estimador devolvesse exatamente -6.0%, eu suspeitaria que a analise esta lendo o parametro direto em vez de estimando do dado. O fato de ser -6.4% significa que o estimador esta funcionando corretamente."

🇺🇸 "Group B is exactly 6% faster — mathematically. When we run the statistical analysis, the result will be -6.4%, not exactly -6.0%. Why? Because sampling variance always adds noise. If the estimator returned exactly -6.0%, I would suspect the analysis is reading the parameter directly instead of estimating from the data. The fact that it comes out as -6.4% means the estimator is working correctly."

---

[FACILITADOR - A cacada aos bugs]

🇧🇷 "Agora a cacada. Esses sao os 4 problemas que coloquei:"

🇺🇸 [FACILITATOR - The bug hunt] "Now the hunt. These are the 4 problems I introduced:"

---

🇧🇷 Mostrar as linhas de injecao de problemas no codigo.

🇺🇸 Show the problem injection lines in the code.

---

🇧🇷 "Problema 1: Duplicatas. 200 pedidos duplicados — 2% do dataset. Em producao, isso acontece quando o sistema de pagamento reenvia um webhook porque nao recebeu confirmacao de recebimento no tempo limite. O servico de destino ja processou o evento, mas o ACK foi perdido na rede. O evento chega de novo. O banco de dados nao tem protecao de idempotencia. Duplicata inserida."

🇺🇸 "Problem 1: Duplicates. 200 duplicated orders — 2% of the dataset. In production, this happens when the payment system resends a webhook because it did not receive confirmation within the timeout. The destination service already processed the event, but the ACK was lost in the network. The event arrives again. The database has no idempotency protection. Duplicate inserted."

---

🇧🇷 "Qual o impacto de nao detectar isso? Sua media de tempo de entrega esta errada. Seu count de pedidos esta errado. Qualquer JOIN com a tabela de clientes vai gerar o dobro de linhas para esses pedidos."

🇺🇸 "What is the impact of not detecting this? Your average delivery time is wrong. Your order count is wrong. Any JOIN with the customer table will generate double the rows for those orders."

---

🇧🇷 "Problema 2: Timestamps fora de ordem. 97 pedidos onde o timestamp de uma etapa e anterior ao da etapa anterior — o que e fisicamente impossivel. Em producao, isso e clock skew: diferentes microsservicos rodam em servidores diferentes com relogios ligeiramente dessincronizados. Diferenca de 200 milissegundos entre servidores ja causa isso quando os eventos chegam muito proximos no tempo."

🇺🇸 "Problem 2: Out-of-order timestamps. 97 orders where the timestamp of a step is earlier than the previous step — which is physically impossible. In production, this is clock skew: different microservices run on different servers with slightly desynchronized clocks. A 200 millisecond difference between servers already causes this when events arrive very close together in time."

---

🇧🇷 "Problema 3: Dasher ausente. 97 pedidos sem dasher_id. Em producao: o algoritmo de alocacao esgotou o timeout sem encontrar um dasher disponivel. O pedido fica em fila. Se voce calcular tempo de atribuicao com NULL, o resultado e NULL — e todas as agregacoes que incluem esse campo viram NULL."

🇺🇸 "Problem 3: Missing dasher. 97 orders without a dasher_id. In production: the allocation algorithm exhausted the timeout without finding an available dasher. The order sits in the queue. If you calculate assignment time with NULL, the result is NULL — and all aggregations that include that field become NULL."

---

🇧🇷 "Problema 4: Outliers acima de 120 minutos. 97 pedidos com tempo de entrega acima de 2 horas. Em producao: dasher com problema mecanico, pedido perdido no restaurante, erro de GPS. Esses registros sao tecnicamente validos — nao sao erros de sistema — mas nao representam o fluxo operacional normal."

🇺🇸 "Problem 4: Outliers above 120 minutes. 97 orders with delivery time above 2 hours. In production: dasher with a mechanical breakdown, order lost at the restaurant, GPS error. These records are technically valid — they are not system errors — but they do not represent the normal operational flow."

---

[LIVE CODING - eda_cleaning.py]

🇧🇷 Executar:

🇺🇸 [LIVE CODING - eda_cleaning.py] Run:

```bash
python gen/data/eda_cleaning.py
```

---

[FACILITADOR - Comentando enquanto o script roda]

🇧🇷 "Veja que o pipeline de limpeza nao deleta informacao — ele cria flags booleanas. has_duplicate_flag, has_timestamp_issue_flag, has_missing_dasher_flag, has_outlier_flag. Isso e critico: em vez de apagar o registro problematico, eu marco ele. O registro continua no dataset para auditorias e analises de excecao. Mas os modelos downstream filtram has_duplicate_flag = false e has_outlier_flag = false antes de calcular metricas."

🇺🇸 [FACILITATOR - Commenting while the script runs] "Notice that the cleaning pipeline does not delete information — it creates boolean flags. has_duplicate_flag, has_timestamp_issue_flag, has_missing_dasher_flag, has_outlier_flag. This is critical: instead of erasing the problematic record, I flag it. The record stays in the dataset for audits and exception analyses. But the downstream models filter has_duplicate_flag = false and has_outlier_flag = false before calculating metrics."

---

🇧🇷 "Por que nao simplesmente deletar? Porque amanha o seu gestor pode perguntar: 'Quantos pedidos tiveram problema de dasher ausente esse mes?' Se voce deletou, a resposta e: 'Nao sei.' Se voce marcou com flag, a resposta e: '97 pedidos, 1% do total, concentrados nos horarios de pico.'"

🇺🇸 "Why not simply delete? Because tomorrow your manager may ask: 'How many orders had a missing dasher issue this month?' If you deleted them, the answer is: 'I do not know.' If you flagged them, the answer is: '97 orders, 1% of the total, concentrated in peak hours.'"

---

[TURMA - Momento 'aha']

[FACILITADOR]

🇧🇷 "Antes de continuar, vou mostrar o impacto da limpeza nas metricas."

🇺🇸 [CLASS - 'Aha' moment] [FACILITATOR] "Before moving on, let me show the impact of cleaning on the metrics."

---

🇧🇷 Abrir Python interativo ou mostrar os prints do script:

🇺🇸 Open interactive Python or show the script output:

---

🇧🇷 "Media do tempo de entrega com duplicatas: veja que cai ligeiramente apos a deduplicacao. O count vai de 10.200 para 9.703. Isso e quase 500 registros que estariam distorcendo cada metrica que voce calcular."

🇺🇸 "Average delivery time with duplicates: notice it drops slightly after deduplication. The count goes from 10,200 to 9,703. That is almost 500 records that were distorting every metric you calculate."

---

🇧🇷 "Alguem aqui ja viu isso em producao? Um relatorio que dava um numero por semanas e de repente o numero mudou depois que alguem limpou o dado?"

🇺🇸 "Has anyone here seen this in production? A report that showed one number for weeks and then suddenly the number changed after someone cleaned the data?"

---

🇧🇷 Pausa para 2-3 respostas da turma.

🇺🇸 Pause for 2-3 responses from the class.

---

🇧🇷 "Exatamente. E por isso que o pipeline de limpeza precisa ser reproducivel, documentado e versionado. Nao pode ser um script que alguem rodou uma vez no notebook local e ninguem mais sabe onde esta."

🇺🇸 "Exactly. That is why the cleaning pipeline needs to be reproducible, documented, and version-controlled. It cannot be a script someone ran once in a local notebook and nobody knows where it is anymore."

---

[DISCUSSAO - 5 min]

[FACILITADOR]

🇧🇷 "Ultimo ponto desse modulo. Discussao rapida: qual desses 4 problemas voce ja encontrou no seu trabalho? E qual foi o impacto quando ele nao foi detectado a tempo?"

🇺🇸 [DISCUSSION - 5 min] [FACILITATOR] "Last point of this module. Quick discussion: which of these 4 problems have you encountered in your own work? And what was the impact when it was not detected in time?"

---

🇧🇷 Ouvir 3-4 historias. Elas vao ser memoraveis para a turma e criam conexao entre o conteudo e a realidade deles.

🇺🇸 Listen to 3-4 stories. They will be memorable for the class and create a connection between the content and their reality.

---

## MODULE 3 — Modeling with dbt (60 min)

[FACILITADOR - Abertura]

🇧🇷 "Alguem aqui ja ouviu falar de dbt?"

🇺🇸 [FACILITATOR - Opening] "Has anyone here heard of dbt?"

---

🇧🇷 Esperar por levantada de maos ou respostas.

🇺🇸 Wait for raised hands or responses.

---

🇧🇷 "Para quem conhece: obrigado. Para quem nao conhece: dbt e o padrao de mercado para transformacao de dados em analytics. Nao e um banco de dados. Nao e uma ferramenta de visualizacao. E uma camada de transformacao que fica entre a fonte de dados e o BI."

🇺🇸 "For those who know it: thank you. For those who do not: dbt is the market standard for data transformation in analytics. It is not a database. It is not a visualization tool. It is a transformation layer that sits between the data source and BI."

---

[FACILITADOR - A analogia da receita de bolo]

🇧🇷 "Vou usar uma analogia que nunca mais vai sair da sua cabeca. Imagine que voce esta fazendo um bolo."

🇺🇸 [FACILITATOR - The cake recipe analogy] "I am going to use an analogy that will stick with you forever. Imagine you are baking a cake."

---

🇧🇷 "A camada de staging e onde voce separa os ingredientes. Farinha de um lado, ovos do outro, manteiga na tigelinha. Voce lava os ovos, pesa a farinha, amolece a manteiga. Isso e staging: limpeza e padronizacao. Sem misturar ainda. Sem assar. So preparar."

🇺🇸 "The staging layer is where you separate the ingredients. Flour on one side, eggs on the other, butter in a small bowl. You wash the eggs, weigh the flour, soften the butter. That is staging: cleaning and standardization. No mixing yet. No baking. Just preparation."

---

🇧🇷 "A camada intermediate e onde voce mistura. Bate os ovos com o acucar, incorpora a farinha, adiciona o fermento. Aqui a logica de negocio comeca: calculamos duracao de cada etapa, fazemos joins, criamos colunas derivadas. E a massa do bolo — nao e o bolo final, mas ja e mais do que ingredientes separados."

🇺🇸 "The intermediate layer is where you mix. You beat the eggs with the sugar, incorporate the flour, add the baking powder. Here business logic begins: we calculate the duration of each step, do joins, create derived columns. It is the batter — not the final cake, but already more than separate ingredients."

---

🇧🇷 "A camada de marts e o bolo pronto. Pronto para servir. Granularidade clara — 1 linha por entrega, 1 linha por resultado de A/B test. O analitico de BI abre o Tableau ou o Streamlit e aponta para essa tabela. E onde ele para."

🇺🇸 "The mart layer is the finished cake. Ready to serve. Clear granularity — 1 row per delivery, 1 row per A/B test result. The BI analyst opens Tableau or Streamlit and points to that table. That is where they stop."

---

[FACILITADOR - Por que nao fazer tudo num script Python?]

🇧🇷 "Vou ser honesto sobre os trade-offs. Por que nao um script pandas que faz tudo?"

🇺🇸 [FACILITATOR - Why not just do everything in a Python script?] "I am going to be honest about the trade-offs. Why not a pandas script that does everything?"

---

🇧🇷 Esperar respostas da turma.

🇺🇸 Wait for responses from the class.

---

🇧🇷 "As respostas que geralmente ouço: 'pandas nao escala', 'SQL e mais legivel para o time', 'dbt tem testes'. Todas corretas. Mas vou adicionar uma que raramente aparece: versionamento da logica de negocio."

🇺🇸 "The answers I usually hear: 'pandas does not scale', 'SQL is more readable for the team', 'dbt has tests.' All correct. But I will add one that rarely comes up: version control of business logic."

---

🇧🇷 "Quando voce muda como calcula o tempo de entrega no seu script Python, quem sabe que houve uma mudanca? Se voce usa Git, o diff aparece — mas a descricao do que mudou e o motivo fica no commit message, que geralmente e 'fix bug' ou 'update script'. No dbt, cada modelo e um arquivo SQL independente com seu proprio historico de versoes, sua propria documentacao e seus proprios testes. A mudanca e auditavel e explicada."

🇺🇸 "When you change how you calculate delivery time in your Python script, who knows a change was made? If you use Git, the diff shows up — but the description of what changed and why lives in the commit message, which is usually 'fix bug' or 'update script.' In dbt, each model is an independent SQL file with its own version history, its own documentation, and its own tests. The change is auditable and explained."

---

[LIVE CODING - dbt pipeline completo]

🇧🇷 Executar:

🇺🇸 [LIVE CODING - complete dbt pipeline] Run:

```bash
cd dbt_doordash
dbt deps --profiles-dir .
```

---

[FACILITADOR]

🇧🇷 "dbt deps instala os pacotes. Usamos dbt_utils — um pacote da comunidade com testes genericos extras. Equivalente ao pip install para Python."

🇺🇸 [FACILITATOR] "dbt deps installs the packages. We use dbt_utils — a community package with extra generic tests. Equivalent to pip install for Python."

```bash
dbt run --profiles-dir .
```

---

[FACILITADOR - enquanto os modelos compilam e rodam]

🇧🇷 "Observem os logs. dbt esta compilando cada modelo SQL — substituindo as macros como ref() e source() pelos paths reais — e executando na sequencia correta automaticamente. Ele detecta as dependencias pelo grafo."

🇺🇸 [FACILITATOR - while the models compile and run] "Watch the logs. dbt is compiling each SQL model — replacing macros like ref() and source() with the actual paths — and executing them in the correct sequence automatically. It detects dependencies from the graph."

---

🇧🇷 "Primeiro stg_pedidos, depois int_pedidos_com_etapas que depende de stg_pedidos, depois fct_entregas que depende de int_pedidos_com_etapas, e por ultimo fct_ab_resultados que depende de fct_entregas. Tudo isso sem eu escrever um makefile ou um orquestrador — o dbt resolve o DAG sozinho."

🇺🇸 "First stg_pedidos, then int_pedidos_com_etapas which depends on stg_pedidos, then fct_entregas which depends on int_pedidos_com_etapas, and finally fct_ab_resultados which depends on fct_entregas. All of this without writing a makefile or an orchestrator — dbt resolves the DAG on its own."

---

[FACILITADOR - A provocacao dos testes]

🇧🇷 "Agora vou te fazer uma pergunta incomoda. Por que eu escrevi 29 testes se o dataset e sintetico e eu sei exatamente o que tem nele?"

🇺🇸 [FACILITATOR - The test challenge] "Now I am going to ask you an uncomfortable question. Why did I write 29 tests if the dataset is synthetic and I know exactly what is in it?"

---

🇧🇷 Pausa. Deixar a turma pensar.

🇺🇸 Pause. Let the class think.

---

🇧🇷 "A resposta que eu espero: porque os testes nao sao para mim. Sao para o proximo desenvolvedor que modificar o pipeline, para o GitHub Actions que vai rodar em cada push, e para o dia em que o dado fonte mudar sem aviso."

🇺🇸 "The answer I am looking for: because the tests are not for me. They are for the next developer who modifies the pipeline, for the GitHub Actions run on every push, and for the day the source data changes without warning."

---

🇧🇷 "Se amanha alguem adicionar uma nova cidade ao dataset sem atualizar o teste de accepted_values, o teste falha. O pipeline para. O problema e detectado antes de chegar no dashboard. Sem os testes, esse dado errado iria direto para producao e o time de produto tomaria decisoes erradas por semanas antes de alguem notar."

🇺🇸 "If tomorrow someone adds a new city to the dataset without updating the accepted_values test, the test fails. The pipeline stops. The problem is caught before it reaches the dashboard. Without the tests, that bad data would go straight to production and the product team would make wrong decisions for weeks before anyone noticed."

---

[LIVE CODING - dbt test]

🇧🇷 Executar:

🇺🇸 [LIVE CODING - dbt test] Run:

```bash
dbt test --profiles-dir .
```

---

[FACILITADOR - comentando cada categoria de teste enquanto os resultados aparecem]

🇧🇷 "8 not_null: order_id, ab_group, tempo_total_min nunca podem ser NULL nos modelos finais. Se um JOIN falhar silenciosamente e gerar NULL, esses testes capturam."

🇺🇸 [FACILITATOR - commenting on each test category as the results appear] "8 not_null: order_id, ab_group, tempo_total_min can never be NULL in the final models. If a JOIN fails silently and generates NULL, these tests catch it."

---

🇧🇷 "4 unique: order_id deve ser unico em cada camada. Se uma duplicata escorregou pela limpeza, esses testes capturam."

🇺🇸 "4 unique: order_id must be unique at each layer. If a duplicate slipped through cleaning, these tests catch it."

---

🇧🇷 "16 accepted_values: ab_group so pode ser A ou B. customer_city so pode ser uma das 6 cidades. month so pode ser Jan, Feb ou Mar. Qualquer valor corrompido e detectado imediatamente."

🇺🇸 "16 accepted_values: ab_group can only be A or B. customer_city can only be one of the 6 cities. month can only be Jan, Feb, or Mar. Any corrupted value is detected immediately."

---

🇧🇷 "E o teste mais importante: o singular customizado."

🇺🇸 "And the most important test: the custom singular test."

```bash
dbt test --select assert_grupo_b_mais_rapido --profiles-dir .
```

---

🇧🇷 "Esse teste faz uma query na fct_ab_resultados e verifica que a media do grupo B e estritamente menor que a do grupo A. Se o pipeline gerar dados onde A vence — por qualquer motivo, seja corrupcao de dado, seja bug de codigo — esse teste falha e o pipeline para."

🇺🇸 "This test queries fct_ab_resultados and verifies that the average time for group B is strictly less than for group A. If the pipeline generates data where A wins — for any reason, whether data corruption or a code bug — this test fails and the pipeline stops."

---

[LIVE CODING - dbt docs]

🇧🇷 Executar:

🇺🇸 [LIVE CODING - dbt docs] Run:

```bash
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

---

[FACILITADOR - abrindo o browser em localhost:8080]

🇧🇷 "Isso aqui e o lineage graph. Cada no e um modelo. As setas mostram as dependencias. Clica em fct_entregas."

🇺🇸 [FACILITATOR - opening the browser at localhost:8080] "This is the lineage graph. Each node is a model. The arrows show the dependencies. Click on fct_entregas."

---

🇧🇷 "Voce ve: de onde vem (stg_pedidos via int_pedidos_com_etapas), para onde vai (fct_ab_resultados), e cada coluna com a descricao que escrevi no schema.yml."

🇺🇸 "You can see: where it comes from (stg_pedidos via int_pedidos_com_etapas), where it goes (fct_ab_resultados), and each column with the description I wrote in schema.yml."

---

🇧🇷 "Isso e documentacao que se gera sozinha a cada dbt docs generate. Nao e um PDF que alguem escreveu uma vez e ficou desatualizado. E um documento vivo que reflete o estado atual do pipeline."

🇺🇸 "This is documentation that generates itself with every dbt docs generate. It is not a PDF someone wrote once and went stale. It is a living document that reflects the current state of the pipeline."

---

[TURMA - Momento de reflexao, 3 min]

[FACILITADOR]

🇧🇷 "Antes de avancar: uma pergunta honesta. No seu trabalho atual, se alguem sair de ferias amanha, o proximo analista consegue entender de onde vem cada numero no relatorio principal? Em quanto tempo? Voce acha que o dbt mudaria isso?"

🇺🇸 [CLASS - Reflection moment, 3 min] [FACILITATOR] "Before we move on: an honest question. In your current job, if someone goes on vacation tomorrow, can the next analyst figure out where every number in the main report comes from? How long would it take? Do you think dbt would change that?"

---

## MODULE 4 — The A/B Experiment (45 min)

[FACILITADOR - Abertura]

🇧🇷 "Vou te fazer uma pergunta que parece simples mas nao e: como voce sabe se uma mudanca funcionou?"

🇺🇸 [FACILITATOR - Opening] "I am going to ask you a question that seems simple but is not: how do you know if a change worked?"

---

🇧🇷 Pausa.

🇺🇸 Pause.

---

🇧🇷 "A resposta errada e: 'o numero foi para cima.' O numero pode ter ido para cima por sazonalidade, por uma campanha de marketing que aconteceu ao mesmo tempo, por um dia de sol que botou mais pessoas com vontade de pedir comida. O numero ir para cima nao prova que a sua mudanca causou isso."

🇺🇸 "The wrong answer is: 'the number went up.' The number might have gone up because of seasonality, because of a marketing campaign that happened at the same time, because of a sunny day that put more people in the mood to order food. The number going up does not prove your change caused it."

---

🇧🇷 "A resposta certa e: 'fizemos um experimento controlado onde mantivemos tudo igual exceto a variavel de interesse.' Isso e um A/B test."

🇺🇸 "The correct answer is: 'we ran a controlled experiment where we kept everything equal except the variable of interest.' That is an A/B test."

---

[FACILITADOR - A analogia do restaurante]

🇧🇷 "Imagine dois restaurantes identicos — mesmo cardapio, mesmo chefe, mesma localizacao, mesmo preco. No restaurante A, o garcom traz o vinho antes do prato. No restaurante B, o garcom traz o vinho depois do prato. Voce quer saber qual versao gera mais gorjeta."

🇺🇸 [FACILITATOR - The restaurant analogy] "Imagine two identical restaurants — same menu, same chef, same location, same prices. In restaurant A, the waiter brings the wine before the main course. In restaurant B, the waiter brings the wine after the main course. You want to know which version generates a better tip."

---

🇧🇷 "Se voce apenas observa os dois restaurantes sem controlar quem vai pra qual, pode ter vieis: talvez os clientes do restaurante A sejam mais ricos por acidente. Talvez o restaurante B tenha um garcom mais simpatico. Um A/B test controlado resolve isso: os clientes sao alocados aleatoriamente em um dos dois restaurantes."

🇺🇸 "If you just observe the two restaurants without controlling who goes where, you may have bias: maybe restaurant A's customers happen to be wealthier. Maybe restaurant B has a friendlier waiter. A controlled A/B test solves this: customers are randomly assigned to one of the two restaurants."

---

🇧🇷 "E exatamente o que fizemos com o algoritmo de delivery. 50% dos pedidos foram para o algoritmo A (FIFO), 50% para o algoritmo B (preditivo). A alocacao foi feita por hash deterministico no order_id — sempre o mesmo grupo para o mesmo pedido, sem vazamento entre grupos."

🇺🇸 "That is exactly what we did with the delivery algorithm. 50% of orders went to algorithm A (FIFO), 50% to algorithm B (predictive). The allocation was done by deterministic hash on the order_id — always the same group for the same order, with no leakage between groups."

---

[FACILITADOR - O erro mais comum]

🇧🇷 "O erro que eu vejo com mais frequencia em analises de A/B test: olhar o grafico de barras, ver que a barra do grupo B e menor, e dizer 'B e melhor, vamos fazer rollout.'"

🇺🇸 [FACILITATOR - The most common error] "The error I see most often in A/B test analyses: looking at the bar chart, seeing that group B's bar is smaller, and saying 'B is better, let us roll it out.'"

---

🇧🇷 "Isso esta errado. Por que?"

🇺🇸 "That is wrong. Why?"

---

🇧🇷 Pausa para respostas.

🇺🇸 Pause for responses.

---

🇧🇷 "Porque nao sabemos se essa diferenca e real ou se e ruido aleatorio. Imagina que voce joga uma moeda 10 vezes e cai cara 7 vezes. Voce diria que a moeda esta viciada? Nao — 7 em 10 pode acontecer por acaso com uma moeda honesta. Mas se jogar 1.000 vezes e cair cara 700, ai sim voce comecar a suspeitar de vicio."

🇺🇸 "Because we do not know if that difference is real or random noise. Imagine you flip a coin 10 times and heads comes up 7 times. Would you say the coin is rigged? No — 7 in 10 can happen by chance with a fair coin. But if you flip 1,000 times and heads comes up 700 times, then you start to suspect the coin is biased."

---

🇧🇷 "O p-value formaliza essa intuicao. Ele responde: 'Se os dois algoritmos fossem identicos (nenhuma diferenca real), qual seria a probabilidade de ver uma diferenca tao grande quanto a que observamos, so pelo acaso da variancia?'"

🇺🇸 "The p-value formalizes that intuition. It answers: 'If the two algorithms were identical (no real difference), what would be the probability of seeing a difference as large as the one we observed, purely by sampling variance?'"

---

🇧🇷 "No nosso caso, p ≈ 0.000. A chance de ver essa diferenca por acaso e menor que 1 em 1 milhao."

🇺🇸 "In our case, p ≈ 0.000. The chance of seeing this difference by accident is less than 1 in 1 million."

---

[LIVE CODING - analise estatistica no Python]

🇧🇷 Abrir Python interativo e mostrar:

🇺🇸 [LIVE CODING - statistical analysis in Python] Open interactive Python and show:

```python
import pandas as pd
from scipy import stats

df = pd.read_csv('gen/data/doordash_clean.csv')
grupo_a = df[df['ab_group'] == 'A']['delivery_duration_minutes'].dropna()
grupo_b = df[df['ab_group'] == 'B']['delivery_duration_minutes'].dropna()

# Welch t-test
t_stat, p_value = stats.ttest_ind(grupo_a, grupo_b, equal_var=False)
print(f"t = {t_stat:.4f}")
print(f"p-value = {p_value:.6f}")

# IC 95%
delta = grupo_b.mean() - grupo_a.mean()
se = (grupo_a.var()/len(grupo_a) + grupo_b.var()/len(grupo_b)) ** 0.5
ic_lower = delta - 1.96 * se
ic_upper = delta + 1.96 * se
print(f"Delta: {delta:.2f} min")
print(f"95% CI: [{ic_lower:.2f}, {ic_upper:.2f}]")
```

---

[FACILITADOR - Revelacao dos resultados]

🇧🇷 "Olha esse p-value. 0.000000. Seis casas decimais de zeros."

🇺🇸 [FACILITATOR - Results reveal] "Look at this p-value. 0.000000. Six decimal places of zeros."

---

🇧🇷 "Isso significa: a probabilidade de ver uma diferenca de 2.44 minutos por puro acaso, assumindo que os algoritmos sao identicos, e menor que 0.0001%."

🇺🇸 "This means: the probability of seeing a 2.44-minute difference by pure chance, assuming the algorithms are identical, is less than 0.0001%."

---

🇧🇷 "t = 14.0. Para ter nocao: t > 2 ja e significativo com alpha = 0.05. t = 14 e um sinal extremamente forte."

🇺🇸 "t = 14.0. For reference: t > 2 is already significant at alpha = 0.05. t = 14 is an extremely strong signal."

---

🇧🇷 "IC 95%: [-2.71, -2.17]. O intervalo nao inclui zero. Isso confirma que o efeito e real, e nos diz o range: no cenario pessimista, B e 2.17 minutos mais rapido. No cenario otimista, 2.71 minutos mais rapido."

🇺🇸 "95% CI: [-2.71, -2.17]. The interval does not include zero. This confirms the effect is real, and tells us the range: in the pessimistic scenario, B is 2.17 minutes faster. In the optimistic scenario, 2.71 minutes faster."

---

[DISCUSSAO - O debate central, 10 min]

[FACILITADOR]

🇧🇷 "Agora, o debate mais importante do workshop. Tenho p < 0.001, IC 95% que nao inclui zero, efeito de -6.4%. Isso significa que devo adotar o algoritmo B imediatamente?"

🇺🇸 [DISCUSSION - The central debate, 10 min] [FACILITATOR] "Now, the most important debate of the workshop. I have p < 0.001, a 95% CI that does not include zero, and an effect of -6.4%. Does this mean I should adopt algorithm B immediately?"

---

🇧🇷 Esperar respostas. Provavelmente vai dividir a sala.

🇺🇸 Wait for responses. The class will likely be divided.

---

🇧🇷 "A resposta certa e: depende. E depende de tres dimensoes diferentes de significancia."

🇺🇸 "The correct answer is: it depends. And it depends on three different dimensions of significance."

---

🇧🇷 "Significancia estatistica: p < 0.001. Confirmada."

🇺🇸 "Statistical significance: p < 0.001. Confirmed."

---

🇧🇷 "Significancia pratica: 2.44 minutos em 38 minutos e 6.4%. Em um produto de delivery, isso e relevante. Mas se fosse 0.1 minuto, seria estatisticamente significativo com n=10.000 e praticamante irrelevante."

🇺🇸 "Practical significance: 2.44 minutes out of 38 is 6.4%. In a delivery product, this is relevant. But if it were 0.1 minutes, it would be statistically significant with n=10,000 and practically irrelevant."

---

🇧🇷 "Significancia economica: ROI de 274% no horizonte de 12 meses. Isso justifica o custo de implementacao de 3 meses de engenharia? A resposta e um 'sim' claro."

🇺🇸 "Economic significance: 274% ROI over 12 months. Does this justify the implementation cost of 3 months of engineering? The answer is a clear 'yes.'"

---

🇧🇷 "Mas ha uma quarta dimensao que a analise estatistica nao captura: risco operacional. Mudar o algoritmo de um sistema que processa milhoes de pedidos por mes e uma decisao critica. Um bug no algoritmo preditivo pode gerar mais atrasos do que o que estamos tentando resolver. Por isso o rollout gradual — 25%, 50%, 100% — com guardrails de monitoramento."

🇺🇸 "But there is a fourth dimension that statistical analysis does not capture: operational risk. Changing the algorithm of a system that processes millions of orders per month is a critical decision. A bug in the predictive algorithm can generate more delays than what we are trying to solve. That is why the gradual rollout — 25%, 50%, 100% — with monitoring guardrails."

---

## MODULE 5 — The Dashboard (30 min)

[LIVE CODING - iniciar o Streamlit]

🇧🇷 Executar:

🇺🇸 [LIVE CODING - start Streamlit] Run:

```bash
streamlit run streamlit_app.py
```

---

🇧🇷 Abrir no browser em http://localhost:8501.

🇺🇸 Open in the browser at http://localhost:8501.

---

[FACILITADOR - Tour pela Visao Geral]

🇧🇷 "Primeira pagina: Visao Geral. Imagine que voce tem 30 segundos para apresentar a situacao para o CEO. O que voce conta?"

🇺🇸 [FACILITATOR - Overview Tour] "First page: Overview. Imagine you have 30 seconds to present the situation to the CEO. What do you say?"

---

🇧🇷 Mostrar os KPIs no topo: total de pedidos, tempo medio, taxa de cancelamento.

🇺🇸 Show the KPIs at the top: total orders, average time, cancellation rate.

---

🇧🇷 "Tres numeros. So tres. Depois o grafico de tendencia mensal."

🇺🇸 "Three numbers. Just three. Then the monthly trend chart."

---

🇧🇷 "Olha esse grafico. Duas linhas, dois eixos Y. Quem sabe por que dois eixos?"

🇺🇸 "Look at this chart. Two lines, two Y axes. Does anyone know why two axes?"

---

🇧🇷 Esperar resposta.

🇺🇸 Wait for a response.

---

🇧🇷 "Porque o volume de pedidos (3.000-4.000) e a taxa de cancelamento (0-15%) sao escalas completamente diferentes. Se eu colocar no mesmo eixo, uma das series vira uma linha reta no fundo do grafico, invisivel. Dual-axis resolve isso."

🇺🇸 "Because order volume (3,000-4,000) and cancellation rate (0-15%) are completely different scales. If I put them on the same axis, one of the series becomes a flat line at the bottom of the chart, invisible. Dual-axis solves that."

---

🇧🇷 "E o sinal mais importante aqui: cancelamentos em Janeiro eram 4.9%. Em Fevereiro, 8.5%. Em Marco, 12%. Isso e uma tendencia que o CEO precisa ver, independente do A/B test."

🇺🇸 "And the most important signal here: cancellations in January were 4.9%. In February, 8.5%. In March, 12.0%. That is a trend the CEO needs to see, independent of the A/B test."

---

[FACILITADOR - Tour pelo A/B Test]

🇧🇷 "Segunda pagina: Resultado do A/B Test. A pergunta central: B foi mesmo mais rapido que A?"

🇺🇸 [FACILITATOR - A/B Test Tour] "Second page: A/B Test Result. The central question: was B actually faster than A?"

---

🇧🇷 Mostrar o boxplot.

🇺🇸 Show the boxplot.

---

🇧🇷 "Por que boxplot e nao barra de media? Alguem sabe?"

🇺🇸 "Why a boxplot and not a bar chart of averages? Does anyone know?"

---

🇧🇷 Esperar resposta.

🇺🇸 Wait for a response.

---

🇧🇷 "Barra de media esconde a distribuicao. A media pode ser identica em dois grupos com distribuicoes completamente diferentes: um grupo compacto e um grupo com muita variancia. O boxplot mostra mediana, IQR (a caixa — onde esta 50% dos dados), whiskers (1.5x IQR) e outliers individuais como pontos. Com um boxplot, voce ve em 5 segundos o que uma barra de media esconde."

🇺🇸 "A bar chart of averages hides the distribution. The mean can be identical in two groups with completely different distributions: one compact group and one with high variance. The boxplot shows the median, IQR (the box — where 50% of the data lives), whiskers (1.5x IQR), and individual outliers as points. With a boxplot you see in 5 seconds what a bar chart of averages hides."

---

🇧🇷 "Veja os outliers do grupo A: tem pontos acima de 60, 70, 80 minutos. Sao as entregas problematicas que passaram pelos filtros. O grupo B tem menos outliers — o algoritmo preditivo tambem reduz a cauda de entregas ruins."

🇺🇸 "Look at the outliers in group A: there are points above 60, 70, 80 minutes. Those are the problematic deliveries that passed through the filters. Group B has fewer outliers — the predictive algorithm also reduces the tail of bad deliveries."

---

🇧🇷 "Agora, os inputs no sidebar. Muda a cidade para Porto Alegre."

🇺🇸 "Now, the inputs in the sidebar. Change the city to Porto Alegre."

---

🇧🇷 Mudar o filtro.

🇺🇸 Change the filter.

---

🇧🇷 "Delta de -7.86%. Muda para Sao Paulo."

🇺🇸 "Delta of -7.86%. Change it to Sao Paulo."

---

🇧🇷 Mudar o filtro.

🇺🇸 Change the filter.

---

🇧🇷 "Delta de -4.59%. O algoritmo B vence em todas as cidades, mas o ganho e diferente. Isso nos diz que para Sao Paulo pode valer a pena tunar o algoritmo especificamente para alta densidade."

🇺🇸 "Delta of -4.59%. Algorithm B wins in every city, but the gain is different. This tells us that for Sao Paulo it may be worth tuning the algorithm specifically for high density environments."

---

[FACILITADOR - Tour pela Analise de Etapas]

🇧🇷 "Terceira pagina: Analise por Etapa. Essa e a pagina que responde a hipotese H2 — qual etapa do fluxo de entrega e a mais impactada pelo algoritmo."

🇺🇸 [FACILITATOR - Stage Analysis Tour] "Third page: Stage Analysis. This is the page that answers hypothesis H2 — which step of the delivery flow is most impacted by the algorithm."

---

🇧🇷 Mostrar o waterfall.

🇺🇸 Show the waterfall chart.

---

🇧🇷 "O waterfall mostra a composicao aditiva do tempo total. Cada barra e uma etapa. A soma de todas e o tempo total de entrega."

🇺🇸 "The waterfall shows the additive composition of the total time. Each bar is a step. The sum of all of them is the total delivery time."

---

🇧🇷 "A etapa de Rota domina: 17.30 minutos, 43% do tempo total. E tambem a etapa com maior ganho do algoritmo B: -1.15 minutos, -6.4%."

🇺🇸 "The Route step dominates: 17.30 minutes, 43% of total time. It is also the step with the greatest gain from algorithm B: -1.15 minutes, -6.4%."

---

🇧🇷 "Faz sentido. O algoritmo preditivo programa o dasher para chegar no restaurante exatamente quando o pedido esta pronto. Sem espera. Ele parte direto para a entrega com a rota otimizada — sem a pressa de compensar o tempo perdido esperando."

🇺🇸 "This makes sense. The predictive algorithm schedules the dasher to arrive at the restaurant exactly when the order is ready. No waiting. They leave directly for the delivery with the optimized route — without the rush to compensate for time lost waiting."

---

[FACILITADOR - Tour por Impacto Financeiro]

🇧🇷 "Quarta pagina: Impacto Financeiro. Aqui a turma pode mexer."

🇺🇸 [FACILITATOR - Financial Impact Tour] "Fourth page: Financial Impact. Here the class can interact."

---

🇧🇷 Deixar a turma mudar os sliders.

🇺🇸 Let the class change the sliders.

---

🇧🇷 "Muda o custo por minuto. Muda o numero de pedidos por dia. O ROI muda em tempo real."

🇺🇸 "Change the cost per minute. Change the number of orders per day. The ROI changes in real time."

---

🇧🇷 "Por que isso importa? Porque quando voce apresenta um ROI de 274% para um CEO, a primeira coisa que ele faz e questionar as premissas: 'Mas esse R$0.50 por minuto e real? Isso inclui o custo do algoritmo em producao?' Com inputs interativos, ele pode ajustar as premissas dele e ver o resultado. O numero que sai dos seus inputs dele e muito mais convincente do que o numero que voce calculou sozinho."

🇺🇸 "Why does this matter? Because when you present a 274% ROI to a CEO, the first thing they do is question the assumptions: 'But is this R$0.50 per minute real? Does it include the cost of running the algorithm in production?' With interactive inputs, they can adjust their own assumptions and see the result. The number that comes out of their own inputs is far more convincing than the number you calculated alone."

---

[FACILITADOR - A pergunta final do modulo]

🇧🇷 "Como voce apresentaria esse dashboard para um CEO que nao sabe o que e p-value e que nunca ouviu falar de Welch t-test?"

🇺🇸 [FACILITATOR - Final module question] "How would you present this dashboard to a CEO who does not know what a p-value is and has never heard of the Welch t-test?"

---

🇧🇷 Pausa para respostas.

🇺🇸 Pause for responses.

---

🇧🇷 "A traducao que eu usaria: 'Testamos dois algoritmos em condicoes identicas. O algoritmo novo foi mais rapido em todas as 6 cidades e todos os 5 horarios testados. A probabilidade de isso ser coincidencia e menor que 1 em 1 milhao. Com base no custo operacional atual, o ROI em 12 meses e de 274%. Recomendo rollout gradual com monitoramento semanal.'"

🇺🇸 "The translation I would use: 'We tested two algorithms under identical conditions. The new algorithm was faster in all 6 cities and all 5 time periods tested. The probability that this is a coincidence is less than 1 in 1 million. Based on current operational costs, the 12-month ROI is 274%. I recommend a gradual rollout with weekly monitoring.'"

---

🇧🇷 "Sem p-value. Sem t-statistic. Mas a rigidez estatistica por baixo e que garante que voce pode fazer essa afirmacao com confianca."

🇺🇸 "No p-value. No t-statistic. But the statistical rigor underneath is what guarantees you can make that statement with confidence."

---

## CLOSING (20 min)

[FACILITADOR - Reflexao]

🇧🇷 "Vou te dar 60 segundos para pensar — silencio mesmo, sem conversa. O que voce aprendeu hoje que voce nao sabia antes? Pode ser tecnico, pode ser metodologico, pode ser uma perspectiva nova sobre um problema que voce ja tinha."

🇺🇸 [FACILITATOR - Reflection] "I am going to give you 60 seconds to think — real silence, no talking. What did you learn today that you did not know before? It can be technical, methodological, or a new perspective on a problem you already had."

---

🇧🇷 Ficar em silencio por 60 segundos.

🇺🇸 Stay silent for 60 seconds.

---

[FACILITADOR - Roleplay: A Decisao Final]

🇧🇷 "Agora voce e o Head of Analytics da DoorDash. E segunda de manha. Voce tem 5 minutos de reuniao com o CEO. Qual e a sua recomendacao?"

🇺🇸 [FACILITATOR - Roleplay: The Final Decision] "Now you are the Head of Analytics at DoorDash. It is Monday morning. You have a 5-minute meeting with the CEO. What is your recommendation?"

---

🇧🇷 Esperar 2-3 voluntarios responderem.

🇺🇸 Wait for 2-3 volunteers to respond.

---

🇧🇷 Corrigir gentilmente:

🇺🇸 Correct gently:

---

🇧🇷 - Se a recomendacao for "rollout imediato": "Rollout de quanto? Para todas as cidades ao mesmo tempo? Sem monitoramento? Em sistemas criticos, rollout gradual e obrigatorio."

🇺🇸 - If the recommendation is "immediate rollout": "Rollout to what percentage? To all cities at once? Without monitoring? In critical systems, gradual rollout is mandatory."

---

🇧🇷 - Se a recomendacao for "precisamos de mais testes": "Os dados ja sao suficientes para uma decisao — p < 0.001, n > 4.000, IC 95% robusto. Pedir mais dados pode ser procrastinacao disfarcada de rigor."

🇺🇸 - If the recommendation is "we need more tests": "The data is already sufficient for a decision — p < 0.001, n > 4,000, robust 95% CI. Asking for more data can be procrastination disguised as rigor."

---

🇧🇷 - Se a recomendacao for "rollout gradual com guardrails": "Exatamente. Voce foi aprovado."

🇺🇸 - If the recommendation is "gradual rollout with guardrails": "Exactly. You passed."

---

[FACILITADOR - O Plano de Rollout]

🇧🇷 "O plano que eu recomendo — e que esta na documentacao:"

🇺🇸 [FACILITATOR - The Rollout Plan] "The plan I recommend — which is in the documentation:"

---

🇧🇷 "Semana 1: 25% do trafego. Monitore tres coisas: taxa de cancelamento (alerta se ultrapassar 12%), dasher_score medio (alerta se cair mais de 5%), e tempo de atribuicao (alerta se ultrapassar 5 minutos). Se qualquer alerta disparar, volta para 0% e investiga."

🇺🇸 "Week 1: 25% of traffic. Monitor three things: cancellation rate (alert if it exceeds 12%), average dasher_score (alert if it drops more than 5%), and assignment time (alert if it exceeds 5 minutes). If any alert fires, roll back to 0% and investigate."

---

🇧🇷 "Semana 2: 50%. Valide que o ganho de -6.4% persiste fora do ambiente controlado do experimento. O ambiente de producao tem variaveis que o experimento nao capturou."

🇺🇸 "Week 2: 50%. Validate that the -6.4% gain persists outside the controlled experiment environment. Production has variables the experiment did not capture."

---

🇧🇷 "Semana 3: 100%. Mantenha monitoramento por 30 dias adicionais. Depois de 30 dias, compare o impacto financeiro real com o projetado."

🇺🇸 "Week 3: 100%. Maintain monitoring for 30 additional days. After 30 days, compare the actual financial impact with the projection."

---

[FACILITADOR - Como adaptar esse case para o seu trabalho]

🇧🇷 "Uma pergunta que eu recebi no ultimo workshop: 'Isso funciona para o meu setor? Eu trabalho com varejo, nao delivery.'"

🇺🇸 [FACILITATOR - How to adapt this case to your own work] "A question I received in the last workshop: 'Does this work for my sector? I work in retail, not delivery.'"

---

🇧🇷 "A resposta e: o framework funciona para qualquer problema de negocio que tenha uma metrica mensuravel, uma alavanca que voce pode manipular e um grupo de controle viavel."

🇺🇸 "The answer is: the framework works for any business problem that has a measurable metric, a lever you can manipulate, and a viable control group."

---

🇧🇷 "No varejo: A/B test de layout de produto na home. Metrica: taxa de clique. Alavanca: posicao e design do card."

🇺🇸 "In retail: A/B test of product layout on the homepage. Metric: click-through rate. Lever: card position and design."

---

🇧🇷 "Em banco: A/B test de mensagem de cobranca. Metrica: taxa de pagamento em dia. Alavanca: tom da mensagem (formal vs amigavel)."

🇺🇸 "In banking: A/B test of a payment reminder message. Metric: on-time payment rate. Lever: message tone (formal vs. friendly)."

---

🇧🇷 "Em RH: A/B test de processo de onboarding. Metrica: retencao em 90 dias. Alavanca: quantidade de checkpoints no primeiro mes."

🇺🇸 "In HR: A/B test of the onboarding process. Metric: 90-day retention. Lever: number of check-in touchpoints in the first month."

---

🇧🇷 "O codigo e o dataset mudam. O raciocinio e identico."

🇺🇸 "The code and the dataset change. The reasoning is identical."

---

[FACILITADOR - Recursos para continuar]

🇧🇷 "Tres recursos que eu recomendo para continuar:"

🇺🇸 [FACILITATOR - Resources to continue] "Three resources I recommend to keep going:"

---

🇧🇷 "Primeiro: a documentacao do dbt em docs.getdbt.com. A secao de 'best practices' e particularmente boa para entender as convencoes de nomenclatura e estrutura de projeto."

🇺🇸 "First: the dbt documentation at docs.getdbt.com. The 'best practices' section is particularly good for understanding naming conventions and project structure."

---

🇧🇷 "Segundo: o livro 'Trustworthy Online Controlled Experiments' de Ron Kohavi, Diane Tang e Ya Xu. E o livro definitivo de A/B testing escrito por pessoas que construiram sistemas de experimentacao na Microsoft, Google e LinkedIn. Pesado, mas indispensavel."

🇺🇸 "Second: the book 'Trustworthy Online Controlled Experiments' by Ron Kohavi, Diane Tang, and Ya Xu. It is the definitive A/B testing book, written by people who built experimentation systems at Microsoft, Google, and LinkedIn. Dense, but indispensable."

---

🇧🇷 "Terceiro: o repositorio desse case. Cada arquivo tem comentarios explicando o raciocinio. O README tem o passo a passo completo para rodar localmente. Clone, modifique, quebre e conserte — a melhor forma de aprender."

🇺🇸 "Third: the repository for this case. Every file has comments explaining the reasoning. The README has the complete step-by-step to run locally. Clone it, modify it, break it, and fix it — that is the best way to learn."

---

[FACILITADOR - Q&A estruturado, 10 min]

🇧🇷 "Agora o Q&A. Mas vou estruturar de forma diferente: nao quero perguntas sobre 'como faco X no Python.' Para isso voce tem a documentacao e o Google. Quero perguntas sobre decisoes: 'Por que voce escolheu X em vez de Y?' e 'Em que situacao voce nao usaria essa abordagem?'"

🇺🇸 [FACILITATOR - Structured Q&A, 10 min] "Now the Q&A. But I will structure it differently: I do not want questions about 'how do I do X in Python.' For that you have the documentation and Google. I want questions about decisions: 'Why did you choose X instead of Y?' and 'In what situation would you not use this approach?'"

---

🇧🇷 Responder 4-5 perguntas.

🇺🇸 Answer 4-5 questions.

---

[FACILITADOR - Encerramento]

🇧🇷 "Ultimo pensamento. A coisa mais importante que voce pode levar desse workshop nao e nenhuma ferramenta especifica. Nao e dbt, nao e DuckDB, nao e Streamlit."

🇺🇸 [FACILITATOR - Closing] "One last thought. The most important thing you can take away from this workshop is not any specific tool. Not dbt, not DuckDB, not Streamlit."

---

🇧🇷 "E a disciplina de comecar com o problema de negocio. Formular hipoteses antes de abrir o dado. Quantificar o impacto financeiro antes de recomendar uma solucao. E comunicar os resultados em linguagem que o CEO entende, sem sacrificar o rigor estatistico por baixo."

🇺🇸 "It is the discipline of starting with the business problem. Formulating hypotheses before opening the data. Quantifying the financial impact before recommending a solution. And communicating results in language the CEO understands, without sacrificing the statistical rigor underneath."

---

🇧🇷 "Ferramentas vao mudar. Esse raciocinio nao muda."

🇺🇸 "Tools will change. This way of thinking does not."

---

🇧🇷 "Obrigado."

🇺🇸 "Thank you."

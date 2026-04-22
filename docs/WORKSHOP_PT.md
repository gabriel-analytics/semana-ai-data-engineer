# Workshop DoorDash Analytics — Roteiro do Facilitador

**Duracao:** 4 horas | **Nivel:** Intermediario | **Pre-requisito:** Python basico + SQL
**Repositorio:** https://github.com/gabriel-analytics/doordash-analytics-case
**Dashboard:** https://doordash-analytics-case-hupqbwjyucsrwzsvceqqyw.streamlit.app

---

## Antes de Comecar — Setup do Facilitador

- Projetor com terminal aberto na raiz do repositorio
- Streamlit rodando localmente em http://localhost:8501
- dbt docs servindo em http://localhost:8080
- Slides de referencia fechados — o roteiro e o terminal
- Avisar: "Vamos codar ao vivo. Pode ter erro. Isso e proposital."

---

## MODULO 1 — O Problema de Negocio (45 min)

[FACILITADOR - Abertura]

"Antes de escrever uma linha de codigo hoje, vou te fazer uma pergunta de negocio. Apenas uma. E quero que voce pense de verdade antes de responder."

Pausa de 3 segundos.

"Voce e o Head of Analytics da DoorDash Brasil. Sao 9h de segunda-feira. Seu CEO manda uma mensagem no Slack. A mensagem diz: 'O tempo medio de entrega subiu 15% no ultimo trimestre. O que esta acontecendo?' — so isso. Sem contexto adicional."

"O que voce faz primeiro?"

---

[TURMA - Discussao livre, 2 min]

Deixar a turma responder. Nao corrigir ainda. Ouvir as respostas. As respostas tipicas vao ser: "abro o dashboard", "faco uma query no banco", "ligo para o time de operacoes". Todas estao corretas, mas incompletas.

---

[FACILITADOR - Storytelling da DoorDash]

"Antes de responder, deixa eu te contar quem e a DoorDash."

"A DoorDash e o maior marketplace de delivery de comida dos EUA. Mais de 35 milhoes de pedidos por mes. O modelo de negocio e simples: eles conectam clientes, restaurantes e entregadores — os dashers — e cobram uma comissao de 15% do restaurante em cima de cada pedido. Parece pouco? 15% de cada pizza, hamburguer e sushi pedido em dezenas de cidades todos os dias soma bilhoes."

"Mas o produto da DoorDash nao e a comida. O produto da DoorDash e a velocidade. A promessa que eles vendem para o cliente e: 'Voce vai receber sua comida rapido, quente, e sem complicacao.' Se eles quebram essa promessa, perdem o cliente."

"Agora imagina que no primeiro trimestre de 2025, os dados mostram que o tempo medio de entrega subiu 15%. Nao 1%, nao 2% — 15%. Isso e o equivalente a um restaurante que sempre entregava em 35 minutos passar a entregar em 40 minutos sem nenhuma justificativa."

"E o CEO, que nao tem um dashboard aberto na frente dele agora, e que nao sabe se e problema de algoritmo, de contratacao, de trafego ou de sazonalidade — ele manda aquela mensagem no Slack."

---

[FACILITADOR - O impacto financeiro]

"Antes de comecar a analise tecnica, precisamos entender o que '15% mais lento' significa em dinheiro. Porque se o CEO vai tomar uma decisao de investimento — seja contratar engenheiros, mudar algoritmo, ou abrir novas operacoes — ele precisa de um numero, nao de um grafico bonito."

"Usamos uma formula simples:"

Escrever no quadro ou mostrar no terminal:

```
Delta_Receita = Delta_Tempo x Custo_Minuto x Pedidos_Dia
              + Delta_Retencao x Ticket_Medio x Pedidos_Dia
```

"Cada minuto extra que o dasher passa esperando o pedido ficar pronto custa dinheiro. Estimamos R$0.50 por minuto por entrega — entre incentivos ao dasher e custo de oportunidade. Com 333 pedidos por dia no nosso scope, 2.44 minutos a mais por entrega custam R$12.000 por mes so em custo operacional."

"Isso sem contar o churn de cliente. Estudos internos de delivery mostram que cada minuto adicional reduz a probabilidade de reorder em 0.3%. Em 2.44 minutos extras, isso e quase 0.7% de churn incremental por cliente. Multiplicado pelo ticket medio de R$38.50 e pela base de pedidos, comeca a ser material."

"Entendido o problema. Agora, como a gente resolve?"

---

[FACILITADOR - As 4 Hipoteses como Detetive]

"Vou te mostrar como um bom analista pensa. Nao comecamos com o dado — comecamos com hipoteses. Isso e o metodo cientifico aplicado a analytics."

"Imagina que voce e o Sherlock Holmes dos dados. Voce chegou na cena do crime. Antes de pegar o microscopio, voce observa o ambiente e formula hipoteses. Hipoteses que voce vai tentar refutar, nao confirmar."

"Temos 4 hipoteses aqui:"

Apresentar cada uma com pausa para perguntas:

"Hipotese 1: O algoritmo de alocacao de dashers e o problema. O sistema atual — chamamos de FIFO, First In First Out — pega o dasher mais proximo e manda pra la. Mas ele ignora quando o pedido vai ficar pronto. O dasher chega, fica esperando 10 minutos na porta do restaurante. Esse tempo nao aparece como 'atraso' em lugar nenhum, mas aparece no tempo total de entrega."

"Hipotese 2: Dentro do fluxo de entrega, a etapa de atribuicao do dasher e a mais critica — nao a rota. Se o dasher errado e atribuido, cada etapa depois dele fica penalizada em cascata."

"Hipotese 3: Se trocarmos o algoritmo FIFO por um algoritmo preditivo, conseguimos reducao de pelo menos 5% no tempo de entrega. Por que 5%? Porque abaixo de 5%, o custo de implementacao nao justifica o risco operacional de mudar um sistema critico."

"Hipotese 4: O impacto nao e uniforme. Cidades diferentes, horarios diferentes, comportamentos diferentes. O algoritmo pode ser excelente em Curitiba e mediano em Sao Paulo — e precisamos saber isso antes de fazer rollout total."

---

[EXERCICIO - 5 min]

[FACILITADOR]

"Agora e sua vez. Antes de continuar, quero que voce crie a sua propria hipotese — uma quinta hipotese que eu nao listei. Pode ser relacionada ao problema de negocio, ao dado, ao algoritmo, ao comportamento do cliente, ao que voce quiser. Voce tem 5 minutos. Escreva numa folha ou no computador. Depois vamos compartilhar algumas."

Caminhar pela sala durante os 5 minutos. Observar o que as pessoas escrevem.

[FACILITADOR - Fechamento do modulo]

"Otimo. Vamos ouvir algumas hipoteses..."

Ouvir 3-4 hipoteses da turma. Comentar brevemente cada uma. Nao refutar — validar o raciocinio.

"Excelente. Hipoteses boas sao hipoteses testageis — elas precisam ter uma variavel que voce manipula e uma metrica que voce mede. 'A satisfacao do cliente vai melhorar' nao e hipotese testavel. 'A taxa de pedidos recorrentes vai aumentar em pelo menos 2% com a mudanca X' e hipotese testavel."

"Modulo 2. Agora vamos ver os dados."

---

## MODULO 2 — Os Dados (60 min)

[FACILITADOR - Introducao]

"Hipoteses sao bonitas. Mas dados sao a realidade. Vamos ver o que temos."

"Eu vou mostrar um dataset que parece perfeito a primeira vista. Sao 10.000 pedidos de delivery, 29 colunas, periodo de janeiro a marco de 2025. Mas tem 4 problemas escondidos dentro dele. Problemas que eu coloquei intencionalmente — porque em producao voce vai encontrar exatamente esses problemas, ou variacoes deles."

"O desafio: quem encontrar os 4 problemas e conseguir explicar a causa raiz de cada um ganha o respeito eterno da turma. Vamos comecar."

---

[LIVE CODING - generate_doordash.py]

Abrir o arquivo no terminal:

```bash
cat gen/data/generate_doordash.py
```

[FACILITADOR - Comentando o codigo enquanto mostra]

"Primeiro detalhe que voce precisa notar: `seed=42`. Por que seed=42 especificamente? Nao e magica nem piada de programador — e uma convencao de reproducibilidade. Com o mesmo seed, toda vez que eu rodar esse script, eu vou gerar exatamente o mesmo dataset. Os mesmos pedidos, os mesmos clientes, os mesmos problemas. Isso e critico para que qualquer pessoa que clonar o repositorio chegue nos mesmos resultados que eu."

"Segundo: a distribuicao do tempo de entrega e log-normal. Por que log-normal e nao normal? Porque tempo de entrega em delivery nao segue uma curva de sino simetrica. Tem um limite inferior fisico — ninguem entrega em zero minutos. Mas nao tem limite superior pratico — um pedido pode demorar 3 horas se o sistema falhar. Distribuicao log-normal captura essa assimetria. A maioria dos pedidos concentra em torno de 35-40 minutos, mas tem uma cauda longa para a direita."

"Terceiro: como o efeito do A/B foi injetado. Veja essa linha:"

Mostrar no codigo:

```python
multiplicador_b = 0.94
delivery_time = base_time * (multiplicador_b if ab_group == 'B' else 1.0)
```

"O grupo B e exatamente 6% mais rapido — matematicamente. Quando a gente fizer a analise estatistica, o resultado vai ser -6.4%, nao -6.0% exato. Por que? Porque a variancia amostral sempre adiciona ruido. Se o estimador devolvesse exatamente -6.0%, eu suspeitaria que a analise esta lendo o parametro direto em vez de estimando do dado. O fato de ser -6.4% significa que o estimador esta funcionando corretamente."

---

[FACILITADOR - A cacada aos bugs]

"Agora a cacada. Esses sao os 4 problemas que coloquei:"

Mostrar as linhas de injecao de problemas no codigo.

"Problema 1: Duplicatas. 200 pedidos duplicados — 2% do dataset. Em producao, isso acontece quando o sistema de pagamento reenvia um webhook porque nao recebeu confirmacao de recebimento no tempo limite. O servico de destino ja processou o evento, mas o ACK foi perdido na rede. O evento chega de novo. O banco de dados nao tem protecao de idempotencia. Duplicata inserida."

"Qual o impacto de nao detectar isso? Sua media de tempo de entrega esta errada. Seu count de pedidos esta errado. Qualquer JOIN com a tabela de clientes vai gerar o dobro de linhas para esses pedidos."

"Problema 2: Timestamps fora de ordem. 97 pedidos onde o timestamp de uma etapa e anterior ao da etapa anterior — o que e fisicamente impossivel. Em producao, isso e clock skew: diferentes microsservicos rodam em servidores diferentes com relogios ligeiramente dessincronizados. Diferenca de 200 milissegundos entre servidores ja causa isso quando os eventos chegam muito proximos no tempo."

"Problema 3: Dasher ausente. 97 pedidos sem dasher_id. Em producao: o algoritmo de alocacao esgotou o timeout sem encontrar um dasher disponivel. O pedido fica em fila. Se voce calcular tempo de atribuicao com NULL, o resultado e NULL — e todas as agregacoes que incluem esse campo viram NULL."

"Problema 4: Outliers acima de 120 minutos. 97 pedidos com tempo de entrega acima de 2 horas. Em producao: dasher com problema mecanico, pedido perdido no restaurante, erro de GPS. Esses registros sao tecnicamente validos — nao sao erros de sistema — mas nao representam o fluxo operacional normal."

---

[LIVE CODING - eda_cleaning.py]

```bash
python gen/data/eda_cleaning.py
```

[FACILITADOR - Comentando enquanto o script roda]

"Veja que o pipeline de limpeza nao deleta informacao — ele cria flags booleanas. has_duplicate_flag, has_timestamp_issue_flag, has_missing_dasher_flag, has_outlier_flag. Isso e critico: em vez de apagar o registro problematico, eu marco ele. O registro continua no dataset para auditorias e analises de excecao. Mas os modelos downstream filtram has_duplicate_flag = false e has_outlier_flag = false antes de calcular metricas."

"Por que nao simplesmente deletar? Porque amanha o seu gestor pode perguntar: 'Quantos pedidos tiveram problema de dasher ausente esse mes?' Se voce deletou, a resposta e: 'Nao sei.' Se voce marcou com flag, a resposta e: '97 pedidos, 1% do total, concentrados nos horarios de pico.'"

---

[TURMA - Momento 'aha']

[FACILITADOR]

"Antes de continuar, vou mostrar o impacto da limpeza nas metricas."

Abrir Python interativo ou mostrar os prints do script:

"Media do tempo de entrega com duplicatas: veja que cai ligeiramente apos a deduplicacao. O count vai de 10.200 para 9.703. Isso e quase 500 registros que estariam distorcendo cada metrica que voce calcular."

"Alguem aqui ja viu isso em producao? Um relatorio que dava um numero por semanas e de repente o numero mudou depois que alguem limpou o dado?"

Pausa para 2-3 respostas da turma.

"Exatamente. E por isso que o pipeline de limpeza precisa ser reproducivel, documentado e versionado. Nao pode ser um script que alguem rodou uma vez no notebook local e ninguem mais sabe onde esta."

---

[DISCUSSAO - 5 min]

[FACILITADOR]

"Ultimo ponto desse modulo. Discussao rapida: qual desses 4 problemas voce ja encontrou no seu trabalho? E qual foi o impacto quando ele nao foi detectado a tempo?"

Ouvir 3-4 historias. Elas vao ser memoraveis para a turma e criam conexao entre o conteudo e a realidade deles.

---

## MODULO 3 — Modelagem com dbt (60 min)

[FACILITADOR - Abertura]

"Alguem aqui ja ouviu falar de dbt?"

Esperar por levantada de maos ou respostas.

"Para quem conhece: obrigado. Para quem nao conhece: dbt e o padrao de mercado para transformacao de dados em analytics. Nao e um banco de dados. Nao e uma ferramenta de visualizacao. E uma camada de transformacao que fica entre a fonte de dados e o BI."

---

[FACILITADOR - A analogia da receita de bolo]

"Vou usar uma analogia que nunca mais vai sair da sua cabeca. Imagine que voce esta fazendo um bolo."

"A camada de staging e onde voce separa os ingredientes. Farinha de um lado, ovos do outro, manteiga na tigelinha. Voce lava os ovos, pesa a farinha, amolece a manteiga. Isso e staging: limpeza e padronizacao. Sem misturar ainda. Sem assar. So preparar."

"A camada intermediate e onde voce mistura. Bate os ovos com o acucar, incorpora a farinha, adiciona o fermento. Aqui a logica de negocio comeca: calculamos duracao de cada etapa, fazemos joins, criamos colunas derivadas. E a massa do bolo — nao e o bolo final, mas ja e mais do que ingredientes separados."

"A camada de marts e o bolo pronto. Pronto para servir. Granularidade clara — 1 linha por entrega, 1 linha por resultado de A/B test. O analitico de BI abre o Tableau ou o Streamlit e aponta para essa tabela. E onde ele para."

---

[FACILITADOR - Por que nao fazer tudo num script Python?]

"Vou ser honesto sobre os trade-offs. Por que nao um script pandas que faz tudo?"

Esperar respostas da turma.

"As respostas que geralmente ouço: 'pandas nao escala', 'SQL e mais legivel para o time', 'dbt tem testes'. Todas corretas. Mas vou adicionar uma que raramente aparece: versionamento da logica de negocio."

"Quando voce muda como calcula o tempo de entrega no seu script Python, quem sabe que houve uma mudanca? Se voce usa Git, o diff aparece — mas a descricao do que mudou e o motivo fica no commit message, que geralmente e 'fix bug' ou 'update script'. No dbt, cada modelo e um arquivo SQL independente com seu proprio historico de versoes, sua propria documentacao e seus proprios testes. A mudanca e auditavel e explicada."

---

[LIVE CODING - dbt pipeline completo]

```bash
cd dbt_doordash
dbt deps --profiles-dir .
```

[FACILITADOR]

"dbt deps instala os pacotes. Usamos dbt_utils — um pacote da comunidade com testes genericos extras. Equivalente ao pip install para Python."

```bash
dbt run --profiles-dir .
```

[FACILITADOR - enquanto os modelos compilam e rodam]

"Observem os logs. dbt esta compilando cada modelo SQL — substituindo as macros como ref() e source() pelos paths reais — e executando na sequencia correta automaticamente. Ele detecta as dependencias pelo grafo."

"Primeiro stg_pedidos, depois int_pedidos_com_etapas que depende de stg_pedidos, depois fct_entregas que depende de int_pedidos_com_etapas, e por ultimo fct_ab_resultados que depende de fct_entregas. Tudo isso sem eu escrever um makefile ou um orquestrador — o dbt resolve o DAG sozinho."

---

[FACILITADOR - A provocacao dos testes]

"Agora vou te fazer uma pergunta incomoda. Por que eu escrevi 29 testes se o dataset e sintetico e eu sei exatamente o que tem nele?"

Pausa. Deixar a turma pensar.

"A resposta que eu espero: porque os testes nao sao para mim. Sao para o proximo desenvolvedor que modificar o pipeline, para o GitHub Actions que vai rodar em cada push, e para o dia em que o dado fonte mudar sem aviso."

"Se amanha alguem adicionar uma nova cidade ao dataset sem atualizar o teste de accepted_values, o teste falha. O pipeline para. O problema e detectado antes de chegar no dashboard. Sem os testes, esse dado errado iria direto para producao e o time de produto tomaria decisoes erradas por semanas antes de alguem notar."

---

[LIVE CODING - dbt test]

```bash
dbt test --profiles-dir .
```

[FACILITADOR - comentando cada categoria de teste enquanto os resultados aparecem]

"8 not_null: order_id, ab_group, tempo_total_min nunca podem ser NULL nos modelos finais. Se um JOIN falhar silenciosamente e gerar NULL, esses testes capturam."

"4 unique: order_id deve ser unico em cada camada. Se uma duplicata escorregou pela limpeza, esses testes capturam."

"16 accepted_values: ab_group so pode ser A ou B. customer_city so pode ser uma das 6 cidades. month so pode ser Jan, Feb ou Mar. Qualquer valor corrompido e detectado imediatamente."

"E o teste mais importante: o singular customizado."

```bash
dbt test --select assert_grupo_b_mais_rapido --profiles-dir .
```

"Esse teste faz uma query na fct_ab_resultados e verifica que a media do grupo B e estritamente menor que a do grupo A. Se o pipeline gerar dados onde A vence — por qualquer motivo, seja corrupcao de dado, seja bug de codigo — esse teste falha e o pipeline para."

---

[LIVE CODING - dbt docs]

```bash
dbt docs generate --profiles-dir .
dbt docs serve --profiles-dir .
```

[FACILITADOR - abrindo o browser em localhost:8080]

"Isso aqui e o lineage graph. Cada no e um modelo. As setas mostram as dependencias. Clica em fct_entregas."

"Voce ve: de onde vem (stg_pedidos via int_pedidos_com_etapas), para onde vai (fct_ab_resultados), e cada coluna com a descricao que escrevi no schema.yml."

"Isso e documentacao que se gera sozinha a cada dbt docs generate. Nao e um PDF que alguem escreveu uma vez e ficou desatualizado. E um documento vivo que reflete o estado atual do pipeline."

---

[TURMA - Momento de reflexao, 3 min]

[FACILITADOR]

"Antes de avancar: uma pergunta honesta. No seu trabalho atual, se alguem sair de ferias amanha, o proximo analista consegue entender de onde vem cada numero no relatorio principal? Em quanto tempo? Voce acha que o dbt mudaria isso?"

---

## MODULO 4 — O Experimento A/B (45 min)

[FACILITADOR - Abertura]

"Vou te fazer uma pergunta que parece simples mas nao e: como voce sabe se uma mudanca funcionou?"

Pausa.

"A resposta errada e: 'o numero foi para cima.' O numero pode ter ido para cima por sazonalidade, por uma campanha de marketing que aconteceu ao mesmo tempo, por um dia de sol que botou mais pessoas com vontade de pedir comida. O numero ir para cima nao prova que a sua mudanca causou isso."

"A resposta certa e: 'fizemos um experimento controlado onde mantivemos tudo igual exceto a variavel de interesse.' Isso e um A/B test."

---

[FACILITADOR - A analogia do restaurante]

"Imagine dois restaurantes identicos — mesmo cardapio, mesmo chefe, mesma localizacao, mesmo preco. No restaurante A, o garcom traz o vinho antes do prato. No restaurante B, o garcom traz o vinho depois do prato. Voce quer saber qual versao gera mais gorjeta."

"Se voce apenas observa os dois restaurantes sem controlar quem vai pra qual, pode ter vieis: talvez os clientes do restaurante A sejam mais ricos por acidente. Talvez o restaurante B tenha um garcom mais simpatico. Um A/B test controlado resolve isso: os clientes sao alocados aleatoriamente em um dos dois restaurantes."

"E exatamente o que fizemos com o algoritmo de delivery. 50% dos pedidos foram para o algoritmo A (FIFO), 50% para o algoritmo B (preditivo). A alocacao foi feita por hash deterministico no order_id — sempre o mesmo grupo para o mesmo pedido, sem vazamento entre grupos."

---

[FACILITADOR - O erro mais comum]

"O erro que eu vejo com mais frequencia em analises de A/B test: olhar o grafico de barras, ver que a barra do grupo B e menor, e dizer 'B e melhor, vamos fazer rollout.'"

"Isso esta errado. Por que?"

Pausa para respostas.

"Porque nao sabemos se essa diferenca e real ou se e ruido aleatorio. Imagina que voce joga uma moeda 10 vezes e cai cara 7 vezes. Voce diria que a moeda esta viciada? Nao — 7 em 10 pode acontecer por acaso com uma moeda honesta. Mas se jogar 1.000 vezes e cair cara 700, ai sim voce comecar a suspeitar de vicio."

"O p-value formaliza essa intuicao. Ele responde: 'Se os dois algoritmos fossem identicos (nenhuma diferenca real), qual seria a probabilidade de ver uma diferenca tao grande quanto a que observamos, so pelo acaso da variancia?'"

"No nosso caso, p ≈ 0.000. A chance de ver essa diferenca por acaso e menor que 1 em 1 milhao."

---

[LIVE CODING - analise estatistica no Python]

```bash
python gen/data/eda_cleaning.py
```

Ou abrir Python interativo e mostrar:

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
print(f"IC 95%: [{ic_lower:.2f}, {ic_upper:.2f}]")
```

---

[FACILITADOR - Revelacao dos resultados]

"Olha esse p-value. 0.000000. Seis casas decimais de zeros."

"Isso significa: a probabilidade de ver uma diferenca de 2.44 minutos por puro acaso, assumindo que os algoritmos sao identicos, e menor que 0.0001%."

"t = 14.0. Para ter nocao: t > 2 ja e significativo com alpha = 0.05. t = 14 e um sinal extremamente forte."

"IC 95%: [-2.71, -2.17]. O intervalo nao inclui zero. Isso confirma que o efeito e real, e nos diz o range: no cenario pessimista, B e 2.17 minutos mais rapido. No cenario otimista, 2.71 minutos mais rapido."

---

[DISCUSSAO - O debate central, 10 min]

[FACILITADOR]

"Agora, o debate mais importante do workshop. Tenho p < 0.001, IC 95% que nao inclui zero, efeito de -6.4%. Isso significa que devo adotar o algoritmo B imediatamente?"

Esperar respostas. Provavelmente vai dividir a sala.

"A resposta certa e: depende. E depende de tres dimensoes diferentes de significancia."

"Significancia estatistica: p < 0.001. Confirmada."

"Significancia pratica: 2.44 minutos em 38 minutos e 6.4%. Em um produto de delivery, isso e relevante. Mas se fosse 0.1 minuto, seria estatisticamente significativo com n=10.000 e praticamante irrelevante."

"Significancia economica: ROI de 274% no horizonte de 12 meses. Isso justifica o custo de implementacao de 3 meses de engenharia? A resposta e um 'sim' claro."

"Mas ha uma quarta dimensao que a analise estatistica nao captura: risco operacional. Mudar o algoritmo de um sistema que processa milhoes de pedidos por mes e uma decisao critica. Um bug no algoritmo preditivo pode gerar mais atrasos do que o que estamos tentando resolver. Por isso o rollout gradual — 25%, 50%, 100% — com guardrails de monitoramento."

---

## MODULO 5 — O Dashboard (30 min)

[LIVE CODING - iniciar o Streamlit]

```bash
streamlit run streamlit_app.py
```

Abrir no browser em http://localhost:8501.

[FACILITADOR - Tour pela Visao Geral]

"Primeira pagina: Visao Geral. Imagine que voce tem 30 segundos para apresentar a situacao para o CEO. O que voce conta?"

Mostrar os KPIs no topo: total de pedidos, tempo medio, taxa de cancelamento.

"Tres numeros. So tres. Depois o grafico de tendencia mensal."

"Olha esse grafico. Duas linhas, dois eixos Y. Quem sabe por que dois eixos?"

Esperar resposta.

"Porque o volume de pedidos (3.000-4.000) e a taxa de cancelamento (0-15%) sao escalas completamente diferentes. Se eu colocar no mesmo eixo, uma das series vira uma linha reta no fundo do grafico, invisivel. Dual-axis resolve isso."

"E o sinal mais importante aqui: cancelamentos em Janeiro eram 4.9%. Em Fevereiro, 8.5%. Em Marco, 12%. Isso e uma tendencia que o CEO precisa ver, independente do A/B test."

---

[FACILITADOR - Tour pelo A/B Test]

"Segunda pagina: Resultado do A/B Test. A pergunta central: B foi mesmo mais rapido que A?"

Mostrar o boxplot.

"Por que boxplot e nao barra de media? Alguem sabe?"

Esperar resposta.

"Barra de media esconde a distribuicao. A media pode ser identica em dois grupos com distribuicoes completamente diferentes: um grupo compacto e um grupo com muita variancia. O boxplot mostra mediana, IQR (a caixa — onde esta 50% dos dados), whiskers (1.5x IQR) e outliers individuais como pontos. Com um boxplot, voce ve em 5 segundos o que uma barra de media esconde."

"Veja os outliers do grupo A: tem pontos acima de 60, 70, 80 minutos. Sao as entregas problematicas que passaram pelos filtros. O grupo B tem menos outliers — o algoritmo preditivo tambem reduz a cauda de entregas ruins."

"Agora, os inputs no sidebar. Muda a cidade para Porto Alegre."

Mudar o filtro.

"Delta de -7.86%. Muda para Sao Paulo."

Mudar o filtro.

"Delta de -4.59%. O algoritmo B vence em todas as cidades, mas o ganho e diferente. Isso nos diz que para Sao Paulo pode valer a pena tunar o algoritmo especificamente para alta densidade."

---

[FACILITADOR - Tour pela Analise de Etapas]

"Terceira pagina: Analise por Etapa. Essa e a pagina que responde a hipotese H2 — qual etapa do fluxo de entrega e a mais impactada pelo algoritmo."

Mostrar o waterfall.

"O waterfall mostra a composicao aditiva do tempo total. Cada barra e uma etapa. A soma de todas e o tempo total de entrega."

"A etapa de Rota domina: 17.30 minutos, 43% do tempo total. E tambem a etapa com maior ganho do algoritmo B: -1.15 minutos, -6.4%."

"Faz sentido. O algoritmo preditivo programa o dasher para chegar no restaurante exatamente quando o pedido esta pronto. Sem espera. Ele parte direto para a entrega com a rota otimizada — sem a pressa de compensar o tempo perdido esperando."

---

[FACILITADOR - Tour pelo Impacto Financeiro]

"Quarta pagina: Impacto Financeiro. Aqui a turma pode mexer."

Deixar a turma mudar os sliders.

"Muda o custo por minuto. Muda o numero de pedidos por dia. O ROI muda em tempo real."

"Por que isso importa? Porque quando voce apresenta um ROI de 274% para um CEO, a primeira coisa que ele faz e questionar as premissas: 'Mas esse R$0.50 por minuto e real? Isso inclui o custo do algoritmo em producao?' Com inputs interativos, ele pode ajustar as premissas dele e ver o resultado. O numero que sai dos seus inputs dele e muito mais convincente do que o numero que voce calculou sozinho."

---

[FACILITADOR - A pergunta final do modulo]

"Como voce apresentaria esse dashboard para um CEO que nao sabe o que e p-value e que nunca ouviu falar de Welch t-test?"

Pausa para respostas.

"A traducao que eu usaria: 'Testamos dois algoritmos em condicoes identicas. O algoritmo novo foi mais rapido em todas as 6 cidades e todos os 5 horarios testados. A probabilidade de isso ser coincidencia e menor que 1 em 1 milhao. Com base no custo operacional atual, o ROI em 12 meses e de 274%. Recomendo rollout gradual com monitoramento semanal.'"

"Sem p-value. Sem t-statistic. Mas a rigidez estatistica por baixo e que garante que voce pode fazer essa afirmacao com confianca."

---

## ENCERRAMENTO (20 min)

[FACILITADOR - Reflexao]

"Vou te dar 60 segundos para pensar — silencio mesmo, sem conversa. O que voce aprendeu hoje que voce nao sabia antes? Pode ser tecnico, pode ser metodologico, pode ser uma perspectiva nova sobre um problema que voce ja tinha."

Ficar em silencio por 60 segundos.

---

[FACILITADOR - Roleplay: A Decisao Final]

"Agora voce e o Head of Analytics da DoorDash. E segunda de manha. Voce tem 5 minutos de reuniao com o CEO. Qual e a sua recomendacao?"

Esperar 2-3 voluntarios responderem.

Corrigir gentilmente:
- Se a recomendacao for "rollout imediato": "Rollout de quanto? Para todas as cidades ao mesmo tempo? Sem monitoramento? Em sistemas criticos, rollout gradual e obrigatorio."
- Se a recomendacao for "precisamos de mais testes": "Os dados ja sao suficientes para uma decisao — p < 0.001, n > 4.000, IC 95% robusto. Pedir mais dados pode ser procrastinacao disfarcada de rigor."
- Se a recomendacao for "rollout gradual com guardrails": "Exatamente. Voce foi aprovado."

---

[FACILITADOR - O Plano de Rollout]

"O plano que eu recomendo — e que esta na documentacao:"

"Semana 1: 25% do trafego. Monitore tres coisas: taxa de cancelamento (alerta se ultrapassar 12%), dasher_score medio (alerta se cair mais de 5%), e tempo de atribuicao (alerta se ultrapassar 5 minutos). Se qualquer alerta disparar, volta para 0% e investiga."

"Semana 2: 50%. Valide que o ganho de -6.4% persiste fora do ambiente controlado do experimento. O ambiente de producao tem variaveis que o experimento nao capturou."

"Semana 3: 100%. Mantenha monitoramento por 30 dias adicionais. Depois de 30 dias, compare o impacto financeiro real com o projetado."

---

[FACILITADOR - Como adaptar esse case para o seu trabalho]

"Uma pergunta que eu recebi no ultimo workshop: 'Isso funciona para o meu setor? Eu trabalho com varejo, nao delivery.'"

"A resposta e: o framework funciona para qualquer problema de negocio que tenha uma metrica mensuravel, uma alavanca que voce pode manipular e um grupo de controle viavel."

"No varejo: A/B test de layout de produto na home. Metrica: taxa de clique. Alavanca: posicao e design do card."

"Em banco: A/B test de mensagem de cobranca. Metrica: taxa de pagamento em dia. Alavanca: tom da mensagem (formal vs amigavel)."

"Em RH: A/B test de processo de onboarding. Metrica: retencao em 90 dias. Alavanca: quantidade de checkpoints no primeiro mes."

"O codigo e o dataset mudam. O raciocinio e identico."

---

[FACILITADOR - Recursos para continuar]

"Tres recursos que eu recomendo para continuar:"

"Primeiro: a documentacao do dbt em docs.getdbt.com. A secao de 'best practices' e particularmente boa para entender as convencoes de nomenclatura e estrutura de projeto."

"Segundo: o livro 'Trustworthy Online Controlled Experiments' de Ron Kohavi, Diane Tang e Ya Xu. E o livro definitivo de A/B testing escrito por pessoas que construiram sistemas de experimentacao na Microsoft, Google e LinkedIn. Pesado, mas indispensavel."

"Terceiro: o repositorio desse case. Cada arquivo tem comentarios explicando o raciocinio. O README tem o passo a passo completo para rodar localmente. Clone, modifique, quebre e conserte — a melhor forma de aprender."

---

[FACILITADOR - Q&A estruturado, 10 min]

"Agora o Q&A. Mas vou estruturar de forma diferente: nao quero perguntas sobre 'como faco X no Python.' Para isso voce tem a documentacao e o Google. Quero perguntas sobre decisoes: 'Por que voce escolheu X em vez de Y?' e 'Em que situacao voce nao usaria essa abordagem?'"

Responder 4-5 perguntas.

---

[FACILITADOR - Encerramento]

"Ultimo pensamento. A coisa mais importante que voce pode levar desse workshop nao e nenhuma ferramenta especifica. Nao e dbt, nao e DuckDB, nao e Streamlit."

"E a disciplina de comecar com o problema de negocio. Formular hipoteses antes de abrir o dado. Quantificar o impacto financeiro antes de recomendar uma solucao. E comunicar os resultados em linguagem que o CEO entende, sem sacrificar o rigor estatistico por baixo."

"Ferramentas vao mudar. Esse raciocinio nao muda."

"Obrigado."

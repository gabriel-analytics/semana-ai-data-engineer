"""
pdf_to_obsidian_v2.py
=====================
Converte PDFs de livros técnicos em notas Zettelkasten no Obsidian.
Detecta capítulos automaticamente e cria UMA NOTA POR CAPÍTULO.

Para livros sem índice claro, usa divisão por blocos de páginas.

USO:
    # Instalar dependências
    pip install anthropic pymupdf

    # Configurar API key
    $env:ANTHROPIC_API_KEY = "sk-ant-..."

    # Rodar
    python pdf_to_obsidian_v2.py

CUSTO ESTIMADO:
    ~$0.02 a $0.05 por capítulo com claude-haiku-4-5 (mais barato)
    ~$0.10 a $0.30 por capítulo com claude-sonnet-4-6 (melhor qualidade)
"""

import os
import re
import json
import time
from pathlib import Path
from dataclasses import dataclass
import anthropic
import fitz  # PyMuPDF

# ─────────────────────────────────────────────
# ⚙️  CONFIG
# ─────────────────────────────────────────────
CONFIG = {
    # Pasta raiz dos seus PDFs
    "pdf_root": r"C:\Users\lineg\OneDrive\Documentos\CURSOS\CursosGabriel\DSA\LIVROS\04_data_modeling_dbt",

    # Vault Obsidian
    "vault_root": r"C:\Users\lineg\OneDrive\Documentos\ObsidianVault",

    # Modelo — haiku é mais barato, sonnet é melhor
    "model": "claude-haiku-4-5-20251001",  # barato: ~$0.02/capítulo
    # Comente o Sonnet e ative o Haiku
    #"model": "claude-sonnet-4-6",            # melhor: ~$0.15/capítulo

    # Máximo de caracteres por capítulo enviado à API (~30k tokens)
    "max_chars_per_chapter": 40000,

    # Pausa entre chamadas (segundos)
    "sleep_between": 2,

    # Arquivo de progresso (não reprocessa o que já foi feito)
    "progress_file": "obsidian_progress.json",

    # Padrões para detectar início de capítulo no texto
    "chapter_patterns": [
        r"^(Capítulo|Chapter|CAPÍTULO|CHAPTER)\s+\d+",
        r"^\d+\.\s+[A-ZÁÉÍÓÚÂÊÎÔÛÃÕÇ][a-záéíóúâêîôûãõç]",
        r"^(Parte|Part|PARTE|PART)\s+(I|II|III|IV|V|\d+)",
        r"^#{1,2}\s+",  # Markdown headers
    ],

    # Se não detectar capítulos, divide por blocos de N páginas
    "pages_per_block": 20,

    # Domínios para mapear pasta → subpasta do vault
    "domain_mapping": {
        "machine learning": "books/05_machine_learning",
        "deep learning": "books/05_machine_learning",
        "sql": "books/01_sql_analytics",
        "sql with dbt": "books/01_sql_analytics/AnalyticsEngineeringWithSQLAndDBT",
        "airflow": "books/03_orquestracao",
        "airbyte": "books/05_engenharia_dbt",
        "dbt": "books/05_engenharia_dbt",
        "snowflake": "books/04_plataforma_dados",
        "bigquery": "books/04_plataforma_dados",
        "databricks": "books/04_plataforma_dados",
        "terraform": "books/02_infraestrutura",
        "power bi": "books/07_visualizacao",
        "python": "books/01_fundacao",
        "estatistica": "books/06_statistics_math",
        "estatística": "books/06_statistics_math",
        "inferencia": "books/06_statistics_math",
        "probabilidade": "books/06_statistics_math",
        "mineracao": "books/09_data_mining",
        "mineração": "books/09_data_mining",
        "analytics": "books/10_business_analytics",
        "business": "books/10_business_analytics",
        "data science": "books/05_machine_learning",
        "iac": "books/02_infraestrutura",
    },
}

# ─────────────────────────────────────────────
# 📝 PROMPTS
# ─────────────────────────────────────────────

PROMPT_DETECTAR_CAPITULOS = """Você vai receber o índice ou primeiras páginas de um livro técnico sobre dados.

Extraia a lista de capítulos no formato JSON:
{{
  "titulo_livro": "...",
  "capitulos": [
    {{"numero": 1, "titulo": "...", "pagina_inicio": 10}},
    {{"numero": 2, "titulo": "...", "pagina_inicio": 35}}
  ]
}}

Se não conseguir detectar capítulos claros, retorne:
{{"titulo_livro": "...", "capitulos": []}}

Responda APENAS com o JSON, sem texto adicional.

CONTEÚDO:
{conteudo}"""

PROMPT_NOTA_CAPITULO = """Você é um especialista em criação de notas Zettelkasten para um vault Obsidian sobre dados, engenharia de dados, analytics e machine learning.

Crie uma nota Zettelkasten completa em Português do Brasil para o capítulo abaixo.

REGRAS:
- Use formato Markdown compatível com Obsidian
- Use [[links internos]] para conectar com outros conceitos (ex: [[dbt]], [[Star Schema]], [[Teste A/B]])
- Use tags: #dominio/subdomain (ex: #dados/modelagem, #ml/supervisionado)
- Seja DENSO em informação — capture o máximo de valor do capítulo
- Inclua exemplos de código quando o capítulo tiver (SQL, Python, etc.)
- Foco em: conceitos-chave, como funciona, quando usar, armadilhas comuns

ESTRUTURA OBRIGATÓRIA:
```
# [Título do Capítulo]

**Livro:** [[Nome do Livro]]
**Capítulo:** X de Y
**Tags:** #tag1 #tag2

## 💡 Ideia Central
[1-2 frases resumindo o conceito principal]

## 📚 Conceitos-chave
[Lista dos principais conceitos com explicação breve]

## 🔧 Como funciona
[Explicação técnica com exemplos]

## 💻 Código/Exemplos
[Código relevante do capítulo, se houver]

## ⚠️ Armadilhas e Boas Práticas
[O que evitar e o que fazer]

## 🔗 Conectado a
[Links para conceitos relacionados no vault]

## 📖 Fonte
[Nome do livro, capítulo, páginas]
```

LIVRO: {titulo_livro}
CAPÍTULO: {titulo_capitulo} (Capítulo {num_capitulo})
PÁGINAS: {paginas}

CONTEÚDO DO CAPÍTULO:
{conteudo}"""


# ─────────────────────────────────────────────
# 🏗️ ESTRUTURAS DE DADOS
# ─────────────────────────────────────────────

@dataclass
class Capitulo:
    numero: int
    titulo: str
    pagina_inicio: int
    pagina_fim: int
    texto: str


# ─────────────────────────────────────────────
# 🔧 FUNÇÕES AUXILIARES
# ─────────────────────────────────────────────

def load_progress(path: str) -> dict:
    if Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_progress(path: str, progress: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)


def sanitize(name: str) -> str:
    """Remove caracteres inválidos para nomes de arquivo."""
    invalid = r'\/:*?"<>|'
    for c in invalid:
        name = name.replace(c, "-")
    return name.strip()[:100]


def get_vault_subfolder(pdf_path: Path) -> str:
    """Mapeia PDF para subpasta do vault baseado no conteúdo do caminho."""
    path_lower = str(pdf_path).lower()
    for keyword, folder in CONFIG["domain_mapping"].items():
        if keyword in path_lower:
            return folder
    return "books/outros"


def extrair_texto_paginas(doc: fitz.Document, inicio: int, fim: int) -> str:
    """Extrai texto de um range de páginas."""
    textos = []
    for i in range(inicio, min(fim, len(doc))):
        page = doc[i]
        texto = page.get_text("text")
        if texto.strip():
            textos.append(texto)
    return "\n\n".join(textos)


def detectar_capitulos_por_regex(doc: fitz.Document) -> list[dict]:
    """
    Tenta detectar capítulos usando padrões regex no texto.
    Retorna lista de dicts com numero, titulo, pagina_inicio.
    """
    capitulos = []
    patterns = [re.compile(p, re.MULTILINE | re.IGNORECASE)
                for p in CONFIG["chapter_patterns"]]

    for page_num in range(len(doc)):
        page = doc[page_num]
        texto = page.get_text("text")

        for line in texto.split("\n"):
            line = line.strip()
            if not line or len(line) < 3:
                continue

            for pattern in patterns:
                if pattern.match(line):
                    # Tenta extrair número do capítulo
                    num_match = re.search(r"\d+", line)
                    num = int(num_match.group()) if num_match else len(capitulos) + 1

                    # Evita duplicatas da mesma página
                    if capitulos and capitulos[-1]["pagina_inicio"] == page_num:
                        continue

                    capitulos.append({
                        "numero": num,
                        "titulo": line[:80],
                        "pagina_inicio": page_num
                    })
                    break

    return capitulos


def detectar_capitulos_via_api(client: anthropic.Anthropic,
                                doc: fitz.Document,
                                titulo_livro: str) -> list[dict]:
    """
    Usa a API do Claude para detectar capítulos a partir do índice.
    """
    # Pega as primeiras 10 páginas (geralmente tem o índice)
    texto_inicio = extrair_texto_paginas(doc, 0, 10)
    if len(texto_inicio) > 8000:
        texto_inicio = texto_inicio[:8000]

    prompt = PROMPT_DETECTAR_CAPITULOS.format(conteudo=texto_inicio)

    try:
        response = client.messages.create(
            model=CONFIG["model"],
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        texto = response.content[0].text.strip()

        # Limpa possível markdown
        texto = re.sub(r"```json\s*", "", texto)
        texto = re.sub(r"```\s*", "", texto)

        data = json.loads(texto)
        return data.get("capitulos", [])

    except Exception as e:
        print(f"  ⚠️  Erro ao detectar capítulos via API: {e}")
        return []


def dividir_em_blocos(doc: fitz.Document, pages_per_block: int) -> list[Capitulo]:
    """
    Fallback: divide o PDF em blocos fixos de páginas quando não
    consegue detectar capítulos.
    """
    total = len(doc)
    capitulos = []
    num = 1

    for inicio in range(0, total, pages_per_block):
        fim = min(inicio + pages_per_block, total)
        texto = extrair_texto_paginas(doc, inicio, fim)

        capitulos.append(Capitulo(
            numero=num,
            titulo=f"Bloco {num} (páginas {inicio+1}-{fim})",
            pagina_inicio=inicio,
            pagina_fim=fim,
            texto=texto
        ))
        num += 1

    return capitulos


def construir_capitulos(doc: fitz.Document,
                         client: anthropic.Anthropic,
                         titulo_livro: str) -> list[Capitulo]:
    """
    Tenta detectar capítulos em ordem de qualidade:
    1. Via API (melhor)
    2. Via regex (médio)
    3. Por blocos fixos (fallback)
    """
    total_paginas = len(doc)
    capitulos_raw = []

    # Tentativa 1: API
    print("   🔍 Tentando detectar capítulos via API...")
    caps_api = detectar_capitulos_via_api(client, doc, titulo_livro)
    if len(caps_api) >= 2:
        print(f"   ✅ {len(caps_api)} capítulos detectados via API")
        capitulos_raw = caps_api
    else:
        # Tentativa 2: Regex
        print("   🔍 Tentando detectar capítulos via regex...")
        caps_regex = detectar_capitulos_por_regex(doc)
        if len(caps_regex) >= 2:
            print(f"   ✅ {len(caps_regex)} capítulos detectados via regex")
            capitulos_raw = caps_regex
        else:
            # Fallback: blocos fixos
            print(f"   ⚠️  Sem capítulos detectados. Dividindo em blocos de {CONFIG['pages_per_block']} páginas")
            return dividir_em_blocos(doc, CONFIG["pages_per_block"])

    # Constrói objetos Capitulo com texto
    capitulos = []
    for i, cap in enumerate(capitulos_raw):
        inicio = cap.get("pagina_inicio", 0)
        fim = capitulos_raw[i+1]["pagina_inicio"] if i+1 < len(capitulos_raw) else total_paginas

        texto = extrair_texto_paginas(doc, inicio, fim)

        # Limita tamanho para não explodir contexto
        if len(texto) > CONFIG["max_chars_per_chapter"]:
            texto = texto[:CONFIG["max_chars_per_chapter"]] + "\n\n[... texto truncado ...]"

        capitulos.append(Capitulo(
            numero=cap.get("numero", i+1),
            titulo=cap.get("titulo", f"Capítulo {i+1}"),
            pagina_inicio=inicio,
            pagina_fim=fim,
            texto=texto
        ))

    return capitulos


def gerar_nota_capitulo(client: anthropic.Anthropic,
                         capitulo: Capitulo,
                         titulo_livro: str,
                         total_caps: int) -> str:
    """Chama Claude para gerar a nota Zettelkasten do capítulo."""
    prompt = PROMPT_NOTA_CAPITULO.format(
        titulo_livro=titulo_livro,
        titulo_capitulo=capitulo.titulo,
        num_capitulo=capitulo.numero,
        paginas=f"{capitulo.pagina_inicio+1}-{capitulo.pagina_fim}",
        conteudo=capitulo.texto
    )

    response = client.messages.create(
        model=CONFIG["model"],
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text


def salvar_nota(conteudo: str,
                vault_root: Path,
                subfolder: str,
                titulo_livro: str,
                capitulo: Capitulo) -> Path:
    """Salva a nota no vault Obsidian."""
    livro_folder = vault_root / subfolder / sanitize(titulo_livro)
    livro_folder.mkdir(parents=True, exist_ok=True)

    # Nome do arquivo: 01-titulo-do-capitulo.md
    nome = f"{capitulo.numero:02d}-{sanitize(capitulo.titulo)}.md"
    nota_path = livro_folder / nome

    # Header de metadados
    header = f"""---
livro: "{titulo_livro}"
capitulo: {capitulo.numero}
titulo_capitulo: "{capitulo.titulo}"
paginas: "{capitulo.pagina_inicio+1}-{capitulo.pagina_fim}"
gerado_em: "{time.strftime('%Y-%m-%d')}"
tipo: capitulo
---

"""
    with open(nota_path, "w", encoding="utf-8") as f:
        f.write(header + conteudo)

    return nota_path


def criar_indice_livro(vault_root: Path,
                        subfolder: str,
                        titulo_livro: str,
                        capitulos: list[Capitulo],
                        pdf_path: Path) -> Path:
    """Cria uma nota índice do livro que linka para todos os capítulos."""
    livro_folder = vault_root / subfolder / sanitize(titulo_livro)
    indice_path = livro_folder / "00-INDICE.md"

    links = "\n".join([
        f"- [[{capitulo.numero:02d}-{sanitize(capitulo.titulo)}|Cap {capitulo.numero}: {capitulo.titulo}]]"
        for capitulo in capitulos
    ])

    conteudo = f"""---
tipo: indice-livro
titulo: "{titulo_livro}"
total_capitulos: {len(capitulos)}
gerado_em: "{time.strftime('%Y-%m-%d')}"
---

# 📚 {titulo_livro}

**Arquivo original:** `{pdf_path.name}`
**Total de capítulos:** {len(capitulos)}
**Localização:** `{pdf_path.parent.name}`

## Capítulos

{links}

## Tags relacionadas
> Adicione as tags relevantes do domínio desse livro
"""

    with open(indice_path, "w", encoding="utf-8") as f:
        f.write(conteudo)

    return indice_path


# ─────────────────────────────────────────────
# 🚀 PROCESSAMENTO PRINCIPAL
# ─────────────────────────────────────────────

def processar_pdf(client: anthropic.Anthropic,
                   pdf_path: Path,
                   vault_root: Path,
                   progress: dict) -> int:
    """
    Processa um PDF completo, gerando uma nota por capítulo.
    Retorna o número de capítulos processados.
    """
    pdf_key = str(pdf_path)
    titulo_livro = pdf_path.stem.replace("-", " ").replace("_", " ").title()

    print(f"\n{'='*60}")
    print(f"📚 Livro: {titulo_livro}")
    print(f"   Arquivo: {pdf_path.name}")

    # Verifica se já foi totalmente processado
    if progress.get(pdf_key, {}).get("status") == "completo":
        print(f"   ⏭️  Já processado completamente, pulando")
        return 0

    # Abre o PDF
    try:
        doc = fitz.open(str(pdf_path))
        print(f"   Páginas: {len(doc)}")
    except Exception as e:
        print(f"   ❌ Erro ao abrir PDF: {e}")
        return 0

    # Detecta capítulos
    subfolder = get_vault_subfolder(pdf_path)
    capitulos = construir_capitulos(doc, client, titulo_livro)
    print(f"   📑 {len(capitulos)} seções para processar")

    if not capitulos:
        print(f"   ⚠️  Nenhuma seção detectada, pulando")
        doc.close()
        return 0

    # Cria índice do livro
    criar_indice_livro(vault_root, subfolder, titulo_livro, capitulos, pdf_path)

    # Inicializa progresso do livro
    if pdf_key not in progress:
        progress[pdf_key] = {
            "titulo": titulo_livro,
            "total_capitulos": len(capitulos),
            "processados": [],
            "status": "em_progresso"
        }

    processados = 0

    for capitulo in capitulos:
        cap_key = f"cap_{capitulo.numero}"

        # Pula capítulos já processados
        if cap_key in progress[pdf_key].get("processados", []):
            print(f"   ⏭️  Cap {capitulo.numero} já processado")
            continue

        if not capitulo.texto.strip():
            print(f"   ⚠️  Cap {capitulo.numero} sem texto, pulando")
            continue

        print(f"\n   📄 Cap {capitulo.numero}: {capitulo.titulo[:50]}")
        print(f"      Páginas {capitulo.pagina_inicio+1}-{capitulo.pagina_fim} | {len(capitulo.texto):,} chars")

        # Gera nota via API
        try:
            print(f"      🤖 Gerando nota...")
            nota = gerar_nota_capitulo(client, capitulo, titulo_livro, len(capitulos))
            nota_path = salvar_nota(nota, vault_root, subfolder, titulo_livro, capitulo)
            print(f"      ✅ Salvo: {nota_path.name}")

            progress[pdf_key]["processados"].append(cap_key)
            processados += 1
            save_progress(CONFIG["progress_file"], progress)

        except Exception as e:
            print(f"      ❌ Erro: {e}")
            continue

        time.sleep(CONFIG["sleep_between"])

    # Marca como completo se todos foram processados
    if len(progress[pdf_key]["processados"]) >= len(capitulos):
        progress[pdf_key]["status"] = "completo"
        save_progress(CONFIG["progress_file"], progress)

    doc.close()
    return processados


def main():
    print("=" * 60)
    print("🧠 PDF → Obsidian Zettelkasten (v2 — Por Capítulo)")
    print("=" * 60)

    # Verifica API key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("\n❌ ANTHROPIC_API_KEY não encontrada!")
        print("   Configure com: $env:ANTHROPIC_API_KEY='sk-ant-...'")
        print("   Obtenha em: https://console.anthropic.com/")
        return

    client = anthropic.Anthropic(api_key=api_key)
    pdf_root = Path(CONFIG["pdf_root"])
    vault_root = Path(CONFIG["vault_root"])

    if not pdf_root.exists():
        print(f"\n❌ Pasta não encontrada: {pdf_root}")
        return

    vault_root.mkdir(parents=True, exist_ok=True)
    progress = load_progress(CONFIG["progress_file"])

    # Encontra PDFs
    pdfs = sorted(pdf_root.rglob("*.pdf"))
    pendentes = [p for p in pdfs
                 if progress.get(str(p), {}).get("status") != "completo"]

    print(f"\n📊 Status:")
    print(f"   PDFs encontrados:  {len(pdfs)}")
    print(f"   Já completos:      {len(pdfs) - len(pendentes)}")
    print(f"   Pendentes:         {len(pendentes)}")
    print(f"   Vault:             {vault_root}")

    if not pendentes:
        print("\n✅ Todos os PDFs já foram processados!")
        return

    # Estima custo
    print(f"\n💰 Estimativa de custo:")
    print(f"   ~10-20 capítulos por livro × {len(pendentes)} livros")
    print(f"   ~$0.15/capítulo (Sonnet) ou ~$0.02/capítulo (Haiku)")
    print(f"   Total estimado: ${len(pendentes) * 15 * 0.05:.0f}-${len(pendentes) * 20 * 0.15:.0f}")

    confirma = input("\nContinuar? [s/N]: ").strip().lower()
    if confirma not in ["s", "sim", "y", "yes"]:
        print("Cancelado.")
        return

    total_notas = 0

    for i, pdf_path in enumerate(pendentes, 1):
        print(f"\n[{i}/{len(pendentes)}]")
        notas = processar_pdf(client, pdf_path, vault_root, progress)
        total_notas += notas

    print(f"\n{'='*60}")
    print(f"✅ Concluído!")
    print(f"   Total de notas criadas: {total_notas}")
    print(f"   Vault: {vault_root}")
    print(f"   Progresso salvo em: {CONFIG['progress_file']}")
    print("=" * 60)


if __name__ == "__main__":
    main()

# Fluxo: Criar RDA a partir do Contexto da Conversa

Use este fluxo quando o usuário quer capturar uma decisão já discutida na conversa atual ou presente em um documento fornecido.

**Pré-requisito:** Leia `references/decisoes-arquiteturais.md` antes de executar este fluxo.

---

## Passo 1 — Extrair informações da decisão

Analise o contexto disponível (histórico da conversa, documento fornecido) e extraia:

| Campo | O que procurar |
|---|---|
| **Título** | Uma frase nominal curta que descreva a decisão |
| **Contexto** | Forças, motivações, restrições e problemas que levaram à decisão |
| **Decisão** | O que foi escolhido/decidido |
| **Consequências** | Impactos positivos, negativos e trade-offs mencionados |
| **Autores** | Quem participou ou propôs a decisão (se identificável) |
| **Status** | `proposta` ou `aceita` (inferir pelo tom da conversa) |

Se alguma informação essencial — especialmente Contexto, Decisão ou Consequências — não puder ser inferida com clareza, pergunte ao usuário antes de continuar. Não invente informações.

---

## Passo 2 — Determinar o local de armazenamento

Siga as diretrizes "Onde gravar ou localizar RDAs" do `SKILL.md` para determinar `$RDA_DIR`. Se o diretório não existir, crie-o no Passo 7 antes de gravar o arquivo.

---

## Passo 3 — Determinar o próximo número

```bash
NUM=$(python3 scripts/next_rda_number.py "$RDA_DIR")
```

O script lista os arquivos existentes e retorna o próximo número com 4 dígitos (ex: `0003`). Retorna `0001` se o diretório não existir ou estiver vazio.

---

## Passo 4 — Gerar o nome do arquivo

```bash
FILENAME=$(python3 scripts/rda_filename.py "$NUM" "<título da decisão>")
# Resultado: RDA-0003-adocao-do-postgresql-para-persistencia-de-dados
```

O arquivo final será: `$RDA_DIR/$FILENAME.md`

---

## Passo 5 — Preencher o template

Use o template em `assets/template-rda.md` como base. Substitua todos os placeholders com as informações extraídas.

- Use a **data atual** para o campo `data`
- Se não for possível identificar autores, deixe a lista com um item vazio ou pergunte ao usuário

---

## Passo 6 — Apresentar o rascunho para revisão

Exiba o conteúdo completo da RDA gerada e solicite revisão:

> "Esse rascunho captura corretamente a decisão? Deseja ajustar alguma seção antes de gravar?"

Aguarde confirmação ou correções antes de prosseguir. Incorpore os ajustes solicitados.

---

## Passo 7 — Gravar o arquivo

Após aprovação do usuário, salve o arquivo no caminho `$RDA_DIR/$FILENAME.md` (o diretório já foi criado pelo script no Passo 2). Confirme ao usuário o caminho completo do arquivo criado.

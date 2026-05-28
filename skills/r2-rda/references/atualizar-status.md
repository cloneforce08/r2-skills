# Fluxo: Atualizar Status de uma RDA

Use este fluxo para alterar o status de uma RDA existente.

---

## Passo 1 — Identificar o RDA

O usuário pode ter fornecido o caminho exato do arquivo de RDA ou apenas referenciado seu número. Você deve determinar o arquivo correto antes de prosseguir.

**Se o usuário forneceu o caminho completo:** Certifique-se de que o arquivo existe e contém frontmatter YAML ao menos com o campos `status`. Se sim, prossiga para o Passo 2. Caso contrário, informe que o arquivo não foi encontrado ou não contém status e peça para fornecer um caminho correto.

**Se o usuário apenas citou o número de um RDA:** O usuário pode ter apenas citado o número do RDA, inclusive de forma não exata (ex: "10", "RDA 10", "adr 0010). Você pode tentar localizar o arquivo correspondente com o seguinte subfluxo:
1. Determine `$RDA_DIR` seguindo as diretrizes "Onde gravar ou localizar RDAs" do [SKILL.md](../SKILL.md):
2. Execute o script `scripts/`
3. Liste os RDAs disponíveis em `$RDA_DIR` executando `find "doc/rdas" -maxdepth 1 -type f -name "RDA-*.md"` e leia o frontmatter de cada arquivo para extrair o número e título da RDA.


- Pergunte qual RDA deve ser atualizada (número ou nome)
- Se necessário, liste as RDAs disponíveis em `docs/rda/` para o usuário escolher

Leia o frontmatter do arquivo para verificar o status atual.

---

## Passo 2 — Solicitar o novo status

Informe o status atual e pergunte o novo:

> "Status atual: `<status atual>`. Qual deve ser o novo status?"

Opções disponíveis:

| Status | Quando usar |
|---|---|
| `proposta` | A decisão ainda não foi aprovada |
| `aceita` | A decisão foi aprovada e está em vigor |
| `depreciada` | A decisão ainda é válida, mas não é mais recomendada para novos usos |
| `substituída por RDA-XXXX` | A decisão foi substituída por uma RDA mais recente |
| `rejeitada` | A decisão foi proposta e não aprovada |

---

## Passo 3 — Tratamento especial para "substituída"

Se o novo status for `substituída`:
- Pergunte o número da RDA que a substitui (ex: `0005`)
- Formate o valor do campo como: `substituída por RDA-<num>` (ex: `substituída por RDA-0005`)

---

## Passo 4 — Atualizar o frontmatter

No arquivo da RDA, atualize apenas os campos do frontmatter YAML:

- `status`: novo valor definido nos passos anteriores
- `data`: data atual no formato `YYYY-MM-DD`

**Não altere nenhuma outra parte do documento.**

---

## Passo 5 — Gravar e confirmar

Salve o arquivo e confirme ao usuário:

> "Status da [RDA-XXXX](caminho/do/arquivo.md) atualizado para `<novo status>` em `<data>`."

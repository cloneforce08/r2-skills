# Fluxo: Adequar RDA Existente ao Template

Use este fluxo quando existe uma RDA em formato diferente do template padrão que precisa ser padronizada.

**Pré-requisito:** Leia `references/decisoes-arquiteturais.md` antes de executar este fluxo.

---

## Passo 1 — Identificar a RDA a ser adequada

Se o usuário não especificou o arquivo:
- Pergunte qual RDA deve ser adequada (número, nome ou caminho)
- Ou liste as RDAs existentes em `docs/rda/` para o usuário escolher

Leia o conteúdo completo do arquivo identificado.

---

## Passo 2 — Mapear o conteúdo para o template

Identifique no documento existente as informações correspondentes a cada campo do template:

| Campo do template | O que procurar no documento |
|---|---|
| `status` | Qualquer menção a status, estado, situação, aprovação da decisão |
| `data` | Data de criação, aprovação, publicação ou última atualização |
| `autores` | Autores, responsáveis, proponentes, "escrito por", "decisão de" |
| **Contexto** | Motivação, background, problema, situação, forças em jogo, "por quê" |
| **Decisão** | O que foi decidido, solução escolhida, "optamos por", "vamos usar" |
| **Consequências** | Impactos, trade-offs, vantagens, desvantagens, riscos, "como resultado" |

**Para campos não encontrados:**
- `status`: use `aceita` se a RDA parece estar em vigor; caso contrário, pergunte ao usuário
- `data`: use a data de criação do arquivo se disponível; caso contrário, use a data atual e informe ao usuário
- `autores`: deixe vazio ou pergunte ao usuário
- Seções ausentes (Contexto, Decisão, Consequências): informe ao usuário que a informação não foi encontrada e pergunte como prosseguir

---

## Passo 3 — Verificar numeração e nome do arquivo

- Se o arquivo já segue o padrão `RDA-XXXX-slug.md`, mantenha o número; prossiga para verificar apenas o slug
- Se o arquivo não tem número, determine `$RDA_DIR` seguindo as diretrizes "Onde gravar ou localizar RDAs" do `SKILL.md` e obtenha o próximo número:
  ```bash
  NUM=$(python3 scripts/next_rda_number.py "$RDA_DIR")
  ```
- Se o slug precisar ser corrigido ou gerado, use o script:
  ```bash
  FILENAME=$(python3 scripts/rda_filename.py "$NUM" "<título da RDA>")
  ```

---

## Passo 4 — Gerar a versão adequada

Preencha o template `assets/template-rda.md` com o conteúdo mapeado. Preserve ao máximo o texto original — o objetivo é reestruturar, não reescrever.

Se alguma seção precisar ser criada do zero (informação ausente no original), sinalizar claramente com um comentário como `<!-- TODO: preencher -->` para o usuário revisar.

---

## Passo 5 — Apresentar o resultado para revisão

Exiba a RDA adequada e destaque as principais mudanças:

- Seções adicionadas, reorganizadas ou renomeadas
- Informações inferidas (não extraídas diretamente do original)
- Campos deixados em branco ou marcados como TODO

Solicite confirmação antes de gravar:

> "Esse resultado está correto? Posso substituir o arquivo original?"

---

## Passo 6 — Gravar

Após aprovação do usuário:

- **Se o nome do arquivo não mudou:** substitua o conteúdo do arquivo original
- **Se o nome do arquivo mudou:** crie o novo arquivo e informe ao usuário que o arquivo original pode ser removido manualmente (não exclua automaticamente)

Confirme ao usuário o caminho completo do arquivo salvo.

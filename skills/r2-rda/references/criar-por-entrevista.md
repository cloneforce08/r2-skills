# Fluxo: Criar RDA por Entrevista

Use este fluxo quando o usuário quer ser guiado passo a passo para registrar uma decisão arquitetural que ainda não está documentada.

**Pré-requisito:** Leia `references/decisoes-arquiteturais.md` antes de executar este fluxo.

---

## Passo 1 — Conduzir a entrevista

Faça as perguntas **em sequência**, aguardando e processando a resposta de cada uma antes de avançar. Não faça todas as perguntas de uma vez.

### Pergunta 1 — Título

> "Qual é o título desta decisão? Use uma frase nominal curta que descreva o que foi decidido.
>
> Exemplo: 'Adoção do Redis para Cache de Sessão', 'Migração para Arquitetura de Microsserviços'."

### Pergunta 2 — Contexto

> "Qual é o contexto que motivou esta decisão? Descreva os problemas, restrições, requisitos e forças em jogo que tornaram essa decisão necessária.
>
> Dica: seja factual e neutro — o objetivo é descrever a situação, não justificar a escolha."

### Pergunta 3 — Decisão

> "O que foi decidido? Descreva a decisão de forma direta, usando voz ativa.
>
> Exemplo: 'Adotaremos o Redis como solução de cache...', 'Utilizaremos PostgreSQL como banco de dados principal...'"

### Pergunta 4 — Consequências

> "Quais são as consequências desta decisão? Liste tanto os benefícios quanto os trade-offs, riscos e impactos negativos.
>
> Lembre-se: consequências honestas — incluindo as negativas — tornam o documento mais valioso para quem vier depois."

### Pergunta 5 — Status

> "Qual é o status desta decisão?"

Opções:
- `proposta` — elaborada, mas ainda não aprovada
- `aceita` — aprovada e em vigor
- `depreciada` — ainda aplicável, mas não mais recomendada
- `rejeitada` — proposta e não aprovada

### Pergunta 6 — Autores

> "Quem são os autores ou proponentes desta decisão? (Pode informar nomes completos, usernames ou deixar em branco)"

---

## Passo 2 — Determinar o local de armazenamento

Siga as diretrizes "Onde gravar ou localizar RDAs" do `SKILL.md` para determinar `$RDA_DIR`. Informe ao usuário o diretório onde a RDA será salva antes de prosseguir. Se o diretório não existir, crie-o no Passo 6.

---

## Passo 3 — Determinar o próximo número

```bash
NUM=$(python3 scripts/next_rda_number.py "$RDA_DIR")
```

Informe ao usuário qual será o número da nova RDA antes de iniciar as perguntas.

---

## Passo 4 — Gerar o rascunho

Preencha o template em `assets/template-rda.md` com as respostas coletadas:

- Use a **data atual** para o campo `data`
- Se autores não foram informados, omita a lista ou use um placeholder

---

## Passo 5 — Apresentar o rascunho para revisão

Exiba o conteúdo completo da RDA e solicite confirmação:

> "Aqui está o rascunho da RDA-XXXX. Alguma seção precisa de ajuste antes de gravar?"

Incorpore as correções solicitadas antes de prosseguir.

---

## Passo 6 — Gravar o arquivo

Após aprovação:

1. Gere o nome do arquivo com o script:
   ```bash
   FILENAME=$(python3 scripts/rda_filename.py "$NUM" "<título coletado na entrevista>")
   ```
2. Salve o arquivo em `$RDA_DIR/$FILENAME.md` (o diretório já foi criado no Passo 1)

Confirme ao usuário o caminho completo do arquivo criado.

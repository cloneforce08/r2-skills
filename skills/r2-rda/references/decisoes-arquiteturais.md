# Princípios e Regras para Registros de Decisão de Arquitetura (RDAs)

## O que é uma RDA

Uma RDA (Registro de Decisão de Arquitetura) é um documento curto que captura uma decisão arquiteturalmente significativa, incluindo o contexto que motivou a decisão e suas consequências.

O objetivo é preservar o raciocínio por trás de decisões importantes para que futuros membros da equipe entendam não apenas o que foi decidido, mas por quê. Sem esse registro, quem chega depois só tem duas opções ruins: aceitar cegamente ou reverter sem entender — ambas prejudicam o projeto.

## O que merece uma RDA

Documente decisões que afetam:

- A **estrutura** do sistema (padrões arquiteturais, organização de módulos, decomposição em serviços)
- **Características não-funcionais** (desempenho, segurança, escalabilidade, disponibilidade, observabilidade)
- **Dependências** (escolha de bibliotecas, frameworks, serviços externos, bancos de dados)
- **Interfaces** (APIs, contratos entre sistemas, protocolos de comunicação, formatos de dados)
- **Técnicas de construção** (linguagens, paradigmas, ferramentas de build/deploy/infraestrutura)

Não documente decisões de implementação rotineiras ou facilmente reversíveis sem impacto sistêmico.

## Estrutura de uma RDA

### Frontmatter YAML

```yaml
---
status: <status>
data: <YYYY-MM-DD>
autores:
  - Nome do Autor
---
```

**`status`** — Estado atual da decisão. Valores possíveis:

| Valor | Significado |
|---|---|
| `proposta` | Elaborada, mas ainda aguardando aprovação dos stakeholders |
| `aceita` | Aprovada e em vigor |
| `depreciada` | Ainda aplicável, mas não mais recomendada para novos usos |
| `substituída por RDA-XXXX` | Substituída por outra RDA — informar o número completo (ex: `substituída por RDA-0005`) |
| `rejeitada` | Proposta e não aprovada |

**`data`** — Data em que o status atual foi definido, no formato `YYYY-MM-DD`. Atualizar sempre que o status mudar.

**`autores`** — Lista dos autores ou proponentes da decisão.

### Título

Formato: `# RDA-XXXX: Título em Frase Nominal`

O título deve ser uma frase nominal curta e descritiva que permita identificar a decisão sem ler o documento inteiro. Não ultrapasse 70 caracteres.

- Bom: `RDA-0003: Adoção do PostgreSQL para Persistência de Dados`
- Ruim: `RDA-0003: Banco de Dados`

### Seção: Contexto

Descreve as forças em jogo que tornaram a decisão necessária: tecnológicas, políticas, sociais, organizacionais e técnicas. Essas forças frequentemente estão em tensão entre si.

Use linguagem **factual e neutra em valores** — apenas descreva a realidade, sem indicar preferências ou justificar a decisão. A justificativa fica na seção Decisão.

Exemplos de forças a mencionar:
- Requisitos e restrições do negócio
- Limitações ou capacidades técnicas existentes
- Restrições de equipe, conhecimento ou prazo
- Decisões anteriores que criam dependências

### Seção: Decisão

Descreve a resposta escolhida para as forças descritas no Contexto. Use **voz ativa** com construções como "Adotaremos...", "Utilizaremos...", "Optamos por...".

Seja direto e preciso sobre o que foi decidido. Pode incluir brevemente as alternativas consideradas e a justificativa da escolha, especialmente quando a decisão não for óbvia.

### Seção: Consequências

Lista todos os resultados da decisão — positivos, negativos e neutros. **Não omita trade-offs ou consequências negativas.** Uma decisão pode ter impactos bons e ruins simultaneamente; ambos afetam a equipe no futuro.

As consequências de uma RDA frequentemente se tornam o contexto de RDAs futuras — são a "continuação da conversa" com quem vier depois.

## Estilo de escrita

- Escreva como se estivesse conversando com um desenvolvedor futuro que não participou da decisão
- Use **frases completas** organizadas em parágrafos
- Bullets são aceitáveis para estilo visual, mas não como substituto para frases completas
- Tamanho ideal: 1 a 2 páginas
- Idioma: português brasileiro


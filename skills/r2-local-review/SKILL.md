---
name: r2-local-review
description: >-
  Realiza revisão técnica detalhada de código — análise de qualidade, arquitetura,
  boas práticas, desempenho e programação defensiva. Use este skill sempre que o
  usuário pedir para revisar, analisar, auditar ou verificar a qualidade de um
  arquivo, conjunto de arquivos, ou escopo de código (ex: "revisa esse arquivo",
  "analisa o que está no stage do git", "dá uma olhada nesse componente"). Use
  também quando o usuário mencionar "code review", "revisão de código", "verificar
  implementação" ou pedir feedback técnico sobre código existente. IMPORTANTE: este
  skill é para revisão de arquivos/código, NÃO para revisar pull requests ou issues
  do GitHub — para isso, use o fluxo de revisão de PR.
argument-hint: O que você gostaria que eu revisasse?
---

# Revisão de Código

Este skill guia uma revisão técnica aprofundada de código, cobrindo desde decisões
de arquitetura até detalhes de implementação.

---

## Antes de começar: confirme o escopo

**Se o usuário não especificou explicitamente o que deve ser revisado**, pergunte
antes de prosseguir. Exemplos de escopo válido:

- Um ou mais arquivos: `"revisa src/services/auth.service.ts"`
- Mudanças no stage do git: `"revisa o que está no git staging"`
- Um diretório ou módulo: `"revisa tudo em src/components/checkout/"`
- Um diff ou trecho colado diretamente no chat

Não inicie a análise enquanto o escopo não estiver claro.

Se o escopo exceder aproximadamente 500 linhas ou 10 arquivos, informe isso ao
usuário e proponha uma estratégia de revisão focada (ex: pontos de entrada,
apenas arquivos alterados, ou módulos de maior risco) antes de prosseguir.

---

## Fluxo de Análise

### Fase 1 — Entender o contexto

Antes de qualquer julgamento, entenda o que está sendo revisado:

- Quantos arquivos foram criados/modificados?
- Qual é a natureza da mudança: nova feature, bug fix, refatoramento, migração?
- Qual o objetivo principal da implementação?
- Há considerações especiais (performance crítica, integração externa, restrições de
  compatibilidade)?

Se precisar de contexto adicional para entender a intenção por trás do código, leia
arquivos relacionados (testes, tipos, interfaces, serviços consumidos).

### Fase 2 — Análise de alto nível

Avalie a abordagem antes de mergulhar nos detalhes:

**Arquitetura e design**
- A solução escolhida faz sentido para o problema?
- É consistente com os padrões do restante do codebase?
- Existe uma abordagem mais simples que resolveria o mesmo problema?
- O código está na camada certa (lógica de negócio em service, não em component, etc.)?

**Organização**
- Separação de responsabilidades está clara?
- As abstrações criadas se justificam, ou adicionam complexidade desnecessária?
- A estrutura de arquivos/diretórios faz sentido?

### Fase 3 — Análise detalhada do código

Vá linha a linha nas partes relevantes:

- Conformidade com boas práticas da linguagem/framework
- Tratamento de erros: casos de falha cobertos? Erros silenciados indevidamente?
- Tipagem: uso correto de tipos? Uso de `any` onde poderia ser específico?
- Legibilidade: nomes descritivos, lógica compreensível sem comentários excessivos?
- Duplicação: código repetido que poderia ser extraído?

### Fase 4 — Programação defensiva (aplique quando houver entradas externas)

Use esta fase quando o código lidar com entrada de usuário, dados de API externa,
arquivos, variáveis de ambiente, filas, webhooks ou qualquer dado não confiável:

- Inputs são validados antes de serem usados?
- Tipos e ranges são verificados onde necessário?
- Casos de borda (null, undefined, array vazio, zero) são tratados?
- Erros de rede/API têm fallback adequado?

### Fase 5 — Análise de desempenho (aplique quando houver impacto potencial)

Use esta fase quando houver loops sobre coleções, consultas a banco, renderização
de listas, processamento de grandes volumes, chamadas repetidas a serviços, ou
outras operações potencialmente custosas:

- O algoritmo é adequado para a escala esperada?
- Há loops desnecessários ou nested loops evitáveis?
- Operações custosas são repetidas onde poderiam ser cacheadas?
- Observables ou Promises são gerenciados corretamente (sem leaks)?

### Fase 6 — Documentação vs implementação (aplique quando houver documentação)

Use esta fase quando o escopo incluir comentários inline, JSDoc/TSDoc, README,
documentação de módulo ou qualquer texto explicativo sobre o comportamento:

- Os comentários descrevem o *porquê*, não o *o quê* óbvio?
- A documentação (JSDoc/TSDoc) reflete o comportamento real?
- Há comentários desatualizados ou enganosos?

---

## Formato do output

Use **sempre** este template. Omita seções que não se aplicam (ex: sem incidentes de
desempenho? não inclua essa seção). Escreva em português.

```
# Revisão de Código

## Contexto
- **Arquivos revisados**: [lista]
- **Tipo de mudança**: [Feature | Fix | Refatoramento | Migração | Outro]
- **Objetivo**: [breve descrição do que a implementação pretende fazer]
- **Limitações de contexto**: [se linguagem/framework for incomum ou sem boas
  práticas verificáveis, declare isso explicitamente e limite os incidentes a
  observações agnósticas (lógica, tratamento de erros, nomes, clareza)]

---

## Resumo Executivo

[2 a 4 frases resumindo a qualidade geral: o que foi bem feito, onde estão os
principais problemas, e se o código está pronto para merge ou precisa de ajustes.]

**Resultado geral**: [✅ Aprovado | ⚠️ Aprovado com ressalvas | ❌ Reprovado]
**Incidentes**: [X crítico(s) · Y alto(s) · Z médio(s) · W baixo(s)]

---

## Análise

### Alto Nível
[Observações sobre arquitetura, design e organização. Se tudo estiver bem, diga isso
brevemente em vez de forçar críticas.]

### Código
[Observações sobre a implementação em si: tipagem, lógica, tratamento de erros,
legibilidade. Não repita incidentes já listados abaixo — aqui é o espaço para
observações gerais ou padrões que aparecem em múltiplos lugares.]

---

## Incidentes

[Liste cada incidente no formato abaixo. Agrupe por severidade, do mais grave ao
menos grave. Não inclua seções de severidade vazias.]

Cada incidente recebe um **identificador único** formado por uma letra de severidade
e um número sequencial de 4 dígitos, reiniciando em 0001 para cada nível dentro da
mesma revisão:

| Severidade | Letra | Exemplo |
|------------|-------|---------|
| CRÍTICO    | `c`   | `c0001` |
| ALTO       | `a`   | `a0001` |
| MÉDIO      | `m`   | `m0001` |
| BAIXO      | `b`   | `b0001` |
| SUGESTÃO   | `s`   | `s0001` |

O identificador vai no cabeçalho do incidente, entre o emoji e o título, para
facilitar referências futuras (ex: "veja c0001", "corrigido a0002").

### 🔴 CRÍTICO `c0001` — [Título]
**Localização**: `caminho/arquivo.ts:42`
**Problema**: [descrição clara do problema e seu impacto]
**Sugestão**: [como corrigir, idealmente com código de exemplo]

---

### 🟠 ALTO `a0001` — [Título]
**Localização**: `...`
**Problema**: ...
**Sugestão**: ...

---

### 🟡 MÉDIO `m0001` — [Título]
**Localização**: `...`
**Problema**: ...
**Sugestão**: ...

---

### 🔵 BAIXO `b0001` — [Título]
**Localização**: `...`
**Problema**: ...
**Sugestão**: ...

---

### 💡 SUGESTÃO `s0001` — [Título]
**Localização**: `...`
**Observação**: [melhoria opcional, sem impacto negativo se não implementada]

---

## Pontos Positivos

[O que foi feito bem. Sempre inclua esta seção — feedback equilibrado é mais útil do
que só apontar problemas.]
```

---

## Guia de severidade

Use estes critérios para classificar cada incidente:

| Nível | Quando usar |
|-------|-------------|
| 🔴 CRÍTICO | Vulnerabilidades de segurança, corrupção de dados, crashes garantidos, perda de dados |
| 🟠 ALTO | Comportamento incorreto, erro não tratado que quebra funcionalidade, memory leak grave |
| 🟡 MÉDIO | Código que funciona mas tem problemas de qualidade, manutenibilidade ou padrões |
| 🔵 BAIXO | Estilo, nomenclatura, pequenas melhorias que não afetam comportamento |
| 💡 SUGESTÃO | Melhorias opcionais, alternativas mais idiomáticas, não há problema em ignorar |

O **Resultado geral** deve refletir:
- ❌ **Reprovado**: há pelo menos um incidente CRÍTICO
- ⚠️ **Aprovado com ressalvas**: há pelo menos um incidente ALTO, ou 3 ou mais
  incidentes MÉDIO
- ✅ **Aprovado**: sem incidentes CRÍTICO/ALTO e com no máximo 2 incidentes MÉDIO
  (qualquer quantidade de BAIXO/SUGESTÃO)

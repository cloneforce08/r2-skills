---
name: r2-doc-code
description: Produz e revisa documentação técnica de código fonte TypeScript/Angular com JSDoc/TSDoc. USE QUANDO outro skill ou agente precisar documentar código, adicionar JSDoc/TSDoc, revisar ou melhorar documentação existente, padronizar comentários de API, ou gerar documentação de contrato para funções, classes, tipos, interfaces, serviços ou componentes. Também use quando houver código sem documentação que precisa ser coberto, ou quando a documentação existente estiver desatualizada em relação à implementação.
argument-hint: Quais arquivos/símbolos documentar?
---

# Documentação Técnica de Código

Skill para produção e revisão de documentação JSDoc/TSDoc. Projetado para ser
invocado por outros skills ou agentes — não é acionado diretamente pelo usuário.

## Entradas

| Entrada                             | Obrigatória | Default                           |
| ----------------------------------- | ----------- | --------------------------------- |
| Escopo (arquivos, pastas, símbolos) | Não         | Arquivo aberto e focado no editor |

## Restrição de escopo

Este skill documenta código — ele não altera implementação. Se durante a
execução for identificada divergência entre código e documentação, corrija
apenas a documentação e sinalize a possível inconsistência no resumo final.

## Regra de idioma

Toda documentação nova deve ser escrita em **português**.

Exceção única: ao editar documentação já existente que esteja em **inglês**,
manter inglês para consistência daquele bloco. Esta exceção não se aplica a
documentação nova — apenas à edição de blocos pré-existentes.

---

## Fluxo de execução

Execute os passos abaixo **em ordem, sem pular nenhum**. Cada passo tem uma
condição de saída — só avance quando ela for satisfeita.

### Passo 1 — Resolver escopo

Determinar quais símbolos serão documentados.

**Ações:**

1. Se o escopo foi fornecido explicitamente: usar como está.
2. Se não: usar o arquivo aberto e focado no editor.
3. Listar todos os símbolos exportados/públicos do escopo.
4. Ordenar por prioridade: API pública > pontos de integração > regras de
   negócio > código complexo > utilitários.

**Condição de saída:** Lista ordenada de símbolos a documentar está definida.

### Passo 2 — Classificar e filtrar símbolos

Para cada símbolo da lista, determinar tipo e nível de documentação necessário.

**Tabela de classificação:**

| Tipo              | Foco da documentação                                          |
| ----------------- | ------------------------------------------------------------- |
| Função/método     | Contrato: parâmetros, retorno, exceções, efeitos colaterais   |
| Classe/componente | Responsabilidade, ciclo de vida, invariantes                  |
| Tipo/interface    | Semântica dos campos, restrições, exemplos de valores válidos |
| Módulo/arquivo    | Contexto arquitetural, dependências, propósito                |

**Regras de filtragem:**

- Símbolo público trivial (getter simples, re-export): **pular** — não
  documentar para evitar ruído.
- Símbolo privado trivial: **pular**.
- Símbolo privado não-trivial: **documentar como `@internal`** — veja critérios
  abaixo.
- Símbolo público não-trivial: **documentar**.
- **Tipo derivado/alias** (`type Foo = Exclude<...>`, mapped types triviais,
  re-exports de tipo): documentar em **no máximo 1 linha** de descrição — a
  estrutura do tipo já carrega sua semântica. Não usar `@remarks` nem exemplos.

**Critérios para documentar membros privados com `@internal`:**

Um membro privado merece `@internal` se qualquer resposta abaixo for _sim_:

- Acessa recurso externo (storage, DOM, API, cache)?
- Tem lazy initialization, efeitos colaterais ou lógica não-óbvia?
- Um mantenedor que leia o código pela primeira vez ficaria com dúvidas sobre o
  que faz?

Se a resposta for _não_ para todas: pular.

**Condição de saída:** Cada símbolo tem tipo e decisão (documentar / pular /
@internal) definidos.

### Passo 3 — Coletar evidências

Para **cada símbolo que será documentado**, coletar evidências antes de escrever
qualquer coisa.

**Ações:**

1. Ler a assinatura completa (parâmetros, tipos de retorno, overloads).
2. Ler o corpo da implementação para identificar: validações, throws, efeitos
   colaterais, chamadas externas.
3. Verificar se existem testes que demonstrem comportamento esperado.
4. Se existir documentação prévia, ler e avaliar se ainda reflete o código
   atual. Registrar uma das decisões:
   - **Mantido** — documentação está correta e completa, nada a alterar.
   - **Aprimorado** — estava correta mas incompleta; melhorias incrementais
     serão aplicadas.
   - **Reescrito** — estava incorreta ou desatualizada em relação à
     implementação atual.

Essa decisão deve aparecer na coluna `Ação` da tabela de cobertura do resumo
final.

A documentação deve descrever **comportamento real observado**, não intenção
presumida. Se o comportamento for ambíguo e não puder ser confirmado: registrar
como dúvida no resumo final e não documentar inferências.

**Condição de saída:** Para cada símbolo, evidências estão coletadas e o
comportamento real é conhecido (ou marcado como ambíguo).

### Passo 4 — Escrever documentação

Agora escrever os comentários JSDoc/TSDoc seguindo estas regras.

**Princípio central:** documentar o **contrato** (o que faz, pré-condições,
pós-condições, limites) — não a implementação interna.

**Idioma:** aplicar a regra de idioma definida acima. Se existir documentação
prévia em inglês, manter inglês nesse bloco. Documentação nova: português.

**Formato por tag:**

- `@param` — Descrição clara e concisa do parâmetro. Se tipos de union/variações
  alterarem o comportamento, manter a descrição do `@param` curta e detalhar em
  `@remarks`.
- `@returns` — O que é retornado e em quais condições. Mesma regra: se complexo,
  detalhar em `@remarks`.
- `@throws` — Cada exceção possível e sua condição.
- `@example` — Incluir quando houver ambiguidade de uso ou quando o contrato não
  for óbvio pela assinatura.
- `@remarks` — Detalhes adicionais: variações de comportamento por parâmetro,
  interações com estado externo, limitações conhecidas.
- `@privateRemarks` — Reservado para: workarounds, justificativas de hacks,
  decisões de design internas, débitos técnicos. Visível apenas para
  mantenedores.
- `@deprecated` — Quando aplicável, indicar alternativa.
- `@see` — Referências a símbolos ou recursos relacionados.
- `@defaultValue` — Quando o parâmetro tem valor padrão não óbvio.

**Regras de consistência:**

- Não duplicar informação já evidente no tipo TypeScript. O objetivo das tags é
  descrever o **papel semântico** do parâmetro/retorno, não repetir o tipo.
  Exemplos:

  ```
  // ❌ ERRADO — repete o que o tipo já diz
  @param data - Dados do tipo unknown a validar
  @returns Retorna valor do tipo O

  // ✅ CERTO — foco no papel, não no tipo
  @param data - Entrada a ser validada pelo schema
  @returns Dado validado e coagido conforme o schema
  ```

- Manter tempo verbal consistente (preferir imperativo ou indicativo presente).
- Manter terminologia consistente dentro do mesmo módulo.

**Condição de saída:** Todos os símbolos marcados para documentação têm
comentários JSDoc/TSDoc escritos.

### Passo 5 — Revisar qualidade

Verificar cada comentário escrito contra esta checklist:

- [ ] **Precisão**: o comentário reflete o código atual?
- [ ] **Idioma**: regra de idioma foi seguida? (português para novo, manter
      inglês se editando existente em inglês)
- [ ] **Completude**: exceções, efeitos colaterais e casos limite estão
      cobertos?
- [ ] **Clareza**: linguagem objetiva, sem ambiguidade?
- [ ] **Utilidade**: responde perguntas reais de quem usa/mantém o código?
- [ ] **Sem redundância**: não repete o que o tipo já expressa?
- [ ] **Tags corretas**: `@param`, `@returns`, `@throws` estão presentes quando
      aplicáveis?
- [ ] **@privateRemarks**: usado corretamente (apenas para detalhes internos de
      manutenção)?

Se algum item falhar, corrigir antes de prosseguir.

**Condição de saída:** Todos os itens da checklist passam para todos os símbolos
documentados.

### Passo 6 — Validar e entregar

**Ações:**

1. Se houver linter disponível: verificar e corrigir erros **apenas de
   documentação** (não alterar código).
2. Confirmar que a regra de idioma foi seguida em toda documentação produzida.
3. Produzir o resumo de saída (formato abaixo).

**Condição de saída:** Resumo entregue.

---

## Formato da saída

Entregar **exatamente** estas três seções:

### 1. Cobertura

Tabela de símbolos processados. A coluna `Ação` deve usar um destes valores:
`Documentado` · `Aprimorado` · `Reescrito` · `Mantido` · `Pulado (trivial)` ·
`Pulado (@internal não-aplicável)`

```
| Símbolo | Tipo | Ação | Notas |
|---------|------|------|-------|
| nomeFuncao | Função | Documentado | — |
| outroSimbolo | Tipo | Pulado (trivial) | Re-export simples |
| docsExistentes | Método | Mantido | Documentação correta e completa |
| docsParciais | Classe | Aprimorado | Adicionado @throws e @example |
```

### 2. Dúvidas e riscos

Lista de comportamentos ambíguos encontrados, divergências entre código e
documentação existente, ou possíveis bugs identificados durante a análise. Se
não houver nenhum, informar explicitamente.

### 3. Pendências

Símbolos que ficaram fora do escopo ou não puderam ser documentados por falta de
evidência.

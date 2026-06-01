---
name: r2-test-unit
description: >-
  Guia a criacao, avaliação e melhoria de testes unitarios de forma consistente,
  com regras comuns para qualquer stack e regras especificas consultadas por
  tecnologia.
argument-hint: O que você quer testar?
---

## Objetivo

Produzir testes unitarios legiveis, confiaveis e focados no contrato publico do codigo, sem
acoplamento a detalhes internos de implementacao.

## Fundamentos (agnosticos)

### Escopo do que testar

- Testar interface publica (metodos, funcoes, propriedades expostas)
- Validar comportamento observavel: entradas, saidas, erros, efeitos visiveis
- Cobrir cenarios principais e casos de borda (nulo, vazio, zero, limites, entradas invalidas)
- Incluir formas de uso distintas quando houver variacoes de entrada/assinatura

Evitar:

- Testar detalhes internos ou estrutura privada/protegida
- Testar getters/setters triviais sem regra de negocio
- Acoplar o teste a ordem interna de chamadas sem necessidade comportamental

### Estrutura e organizacao

- Organizar por comportamento/metodo com blocos de agrupamento (ex.: suites aninhadas quando fizer
  sentido)
- Usar nomes descritivos orientados a comportamento esperado
- Aplicar padrao AAA em cada caso:
  - Arrange: prepara dados, doubles e estado
  - Act: executa a acao
  - Assert: valida o resultado
- Quando Act e Assert forem naturalmente combinados (ex.: validacao de excecao/rejeicao), sinalizar
  isso explicitamente

### Isolamento e qualidade

- Preferir instanciacao real quando simples e barata
- Usar mocks/stubs somente para isolar dependencias externas relevantes
- Manter cada teste focado em um comportamento
- Evitar duplicacao excessiva de setup (extrair setup compartilhado quando apropriado)

### Idioma padrao

- O idioma padrao para descricoes e comentarios de teste e portugues brasileiro.
- So usar outro idioma se houver instrucao explicita do usuario ou instrucao de contexto do projeto
  (ex.: AGENTS.md) definindo outro padrao.

## Deteccao da tecnologia e referencia obrigatoria

Antes de fazer qualquer coisa, detectar a tecnologia pelo tipo/extensao do arquivo alvo (arquivo a
ser testado).

Mapeamento atual:

- Arquivos Java (`.java`): usar JUnit com instruções específicas em
  [`references/junit.md`](references/junit.md).
- Arquivos JavaScript/TypeScript (`.js`, `.jsx`, `.ts`, `.tsx`): usar Vitest com instruções
  específicas em [`references/vitest.md`](references/vitest.md).

**IMPORTANTE**: A leitura do arquivo de referencia da tecnologia detectada e imprescindivel antes de
propor, criar ou alterar qualquer teste.

**IMPORTANTE**: Se o tipo de arquivo nao estiver mapeado, solicitar confirmacao da tecnologia e
somente prosseguir apos definir uma referencia aplicavel.

## Workflow recomendado

1. Identificar unidade sob teste e contrato publico
2. Detectar tecnologia e carregar referencia correspondente
3. Listar cenarios: sucesso, erro, borda
4. Escrever testes com AAA e organizacao por comportamento
5. Aplicar regras especificas da tecnologia selecionada
6. Revisar legibilidade, isolamento e cobertura dos cenarios essenciais

## Checklist de revisao para testes ruins ou instáveis (flaky)

Use ao revisar testes que falham de forma intermitente, sao dificeis de manter
ou geram baixa confianca.

### Dependencias de estado externo ou compartilhado

- [ ] O teste depende de estado global mutavel entre testes?
- [ ] Banco de dados, filesystem, rede ou clock real sao usados sem controle?
- [ ] A ordem de execucao dos testes importa para o resultado?

### Acoplamento a detalhes internos

- [ ] O teste verifica estrutura interna (campos privados, ordem de chamadas)?
- [ ] Mudancas de implementacao sem alteracao de comportamento quebram o teste?

### Asserções frageis

- [ ] Assercoes dependem de formato de mensagem exato sujeito a mudanca?
- [ ] Assercoes de colecoes assumem ordenacao sem garantia de ordem?
- [ ] Comparacoes de floats/timestamps sem tolerancia adequada?

### Setup e teardown

- [ ] Estado criado e limpo apos cada teste?
- [ ] Mocks/stubs sao resetados entre os casos?
- [ ] Recursos (conexoes, timers, observers) sao devidamente encerrados?

### Foco e escopo

- [ ] O teste cobre mais de um comportamento independente (deveria ser dividido)?
- [ ] O nome do teste descreve com precisao o que e validado?
- [ ] O teste ainda reflete o comportamento atual do codigo ou ficou obsoleto?

## Checklist de conclusao

- [ ] Tecnologia detectada e referencia correta aplicada
- [ ] Testes focados na interface publica
- [ ] Casos principais e de borda cobertos
- [ ] AAA consistente em todos os casos
- [ ] Dependencias externas isoladas quando necessario
- [ ] Sem validacoes acopladas a detalhes internos desnecessarios
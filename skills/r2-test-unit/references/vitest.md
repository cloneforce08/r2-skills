# Referencia Vitest

Guia de convencoes especificas para testes unitarios em projetos JavaScript/TypeScript.

## Framework e sintaxe

- Usar Vitest como framework de execucao de testes
- Estruturar suites com `describe` e casos com `it`/`test`
- Preferir `expect` do Vitest para assercoes

## Imports do Vitest

Detectar se o projeto usa modo globals:

1. Pedido explicito na solicitacao (ex.: "sem imports do vitest")
2. Contexto da sessao indicando globals
3. Configuracao fixa do workspace/projeto (ex.: `globals: true`)

Se globals estiver ativo:

- Nao importar de `vitest`
- Importar apenas o modulo sob teste

Se globals nao estiver ativo:

- Importar explicitamente de `vitest` apenas o que for usado
- Exemplo comum: `describe`, `it`, `expect`, `vi`, hooks

## Mocks e doubles

- Usar `vi.fn()` para funcoes mockadas
- Usar `vi.spyOn()` quando precisar observar comportamento de dependencia real
- Evitar dependencias externas reais em unit tests

## Assincrono e erros

- Para promessas, usar `await` no Act
- Para validacao de erro async, usar `await expect(...).rejects`
- Nesses casos, pode combinar bloco `Act & Assert`

## Organizacao recomendada

- Bloco raiz com nome da funcao/classe sob teste
- Blocos internos por metodo ou categoria de comportamento
- Setup compartilhado em `beforeEach` quando reduzir duplicacao

## Antipadroes a evitar

- Misturar convencoes de outros frameworks de teste no mesmo arquivo
- Acoplar assercoes a detalhes internos sem valor de contrato
- Ignorar cenarios de borda (nulo, vazio, zero, invalido)

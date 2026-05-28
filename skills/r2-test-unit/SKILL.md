---
name: r2-test-unit
description: >-
  Cria ou atualiza testes unitários com Vitest. Use este skill sempre que o
  usuário quiser escrever, criar, atualizar ou melhorar testes unitários em
  arquivos .spec.ts ou .test.ts, ou mencionar Vitest, testes de unidade, cobertura
  de testes, casos de teste, ou queira adicionar testes a uma função, classe,
  serviço ou módulo TypeScript. Use também quando o usuário pedir para "testar"
  código, "cobrir" código com testes, ou "garantir que X funciona".
argument-hint: O que gostaria de testar?
---

# Testes Unitários com Vitest

Este skill guia a criação e atualização de testes unitários com Vitest, seguindo
boas práticas de qualidade, organização e legibilidade.

---

## Princípios fundamentais

### O que testar

Teste a **interface pública** do módulo ou classe — o contrato exposto para quem usa o código:

- Métodos e propriedades **públicos** (nunca privados ou protegidos)
- **Comportamento observável**: o que entra, o que sai, o que é emitido, o que é
  lançado — não como o código chega lá internamente
- **Diferentes formas de uso**: se uma função aceita overloads, strings, arrays ou
  objetos, cubra cada forma de chamada separadamente
- **Casos de borda**: valores nulos, vazios, zero, limites, entradas inválidas

Evite testar:
- Detalhes de implementação (estrutura interna, ordem de chamadas privadas)
- Dependências externas diretamente — use mocks/stubs para isolá-las
- Membros privados/protegidos — se sentir necessidade, é sinal de que a API pública está mal estruturada

### Idioma

Todos os comentários no código de teste, todas as descrições de `describe` e
`it`/`test`, e todos os comentários inline devem ser escritos **em português**.

---

## Estrutura dos testes

### Organização com `describe` aninhados

Nunca coloque todos os testes em uma lista plana. Agrupe-os em blocos `describe`
aninhados para criar uma hierarquia clara:

```
describe('NomeDaClasse ou nomeDaFunção')
  describe('método ou comportamento principal')
    it('faz X quando Y')
    it('lança erro quando Z')
  describe('outro método ou cenário')
    it('retorna W quando ...')
```

O bloco raiz usa o nome do módulo, classe ou função que está sendo testada. Os
blocos internos agrupam por método, estado inicial relevante ou categoria de
comportamento.

### Metodologia AAA: Arrange → Act → Assert

Cada caso de teste (`it`/`test`) deve seguir esta estrutura, marcada por
comentários no código:

```typescript
it('descrição em português do que deve acontecer', () => {
  // Arrange — prepara dados, instâncias, mocks
  const entrada = 'valor';
  const instancia = new MinhaClasse();

  // Act — executa a ação que está sendo testada
  const resultado = instancia.metodo(entrada);

  // Assert — verifica os resultados esperados
  expect(resultado).toBe('valor esperado');
});
```

Os comentários `// Arrange`, `// Act` e `// Assert` são obrigatórios e devem
aparecer mesmo que uma das seções seja de uma única linha. Isso torna a intenção
de cada parte do teste explícita para quem lê.

Para testes assíncronos, o mesmo padrão se aplica:

```typescript
it('resolve com o valor correto', async () => {
  // Arrange
  const servico = new MeuServico();

  // Act
  const resultado = await servico.buscar(42);

  // Assert
  expect(resultado).toEqual({ id: 42, nome: 'Exemplo' });
});
```

---

## Importações

### Detectar modo globals

Antes de escrever qualquer import do Vitest, verifique se o projeto usa **Vitest
no modo globals**. Nesse modo, utilitários como `describe`, `it`, `test`,
`expect`, `vi`, `beforeEach`, `afterEach`, `beforeAll` e `afterAll` já estão
disponíveis no ambiente — importá-los seria redundante e incorreto.

Detecte o modo globals pelos seguintes sinais (em ordem de prioridade):

1. **Instrução explícita na solicitação atual**: o usuário pediu "sem imports do
   vitest", "usando globals", ou algo equivalente.
2. **Contexto anterior da sessão**: o usuário mencionou antes, na mesma sessão,
   que o projeto usa globals.
3. **Instruções fixas do projeto**: o `CLAUDE.md` ou `AGENTS.md` ou outra instrução
   de workspace menciona que o Vitest está configurado com globals (ex: "configura
   o Vitest para utilizar globals", "no need to import", `globals: true`).

### Quando globals estiver ativo

**Não importe nada do pacote `vitest`.** Importe apenas o código que está sendo
testado:

```typescript
import { minhaFuncao } from './minha-funcao';
```

Os utilitários de teste já estão disponíveis globalmente — use-os diretamente.

### Quando globals NÃO estiver configurado (padrão)

Importe **explicitamente** do pacote `vitest`. Inclua apenas o que for realmente
usado no arquivo:

```typescript
import { describe, it, expect, vi, beforeEach, afterEach, beforeAll, afterAll } from 'vitest';
```

---

## Exemplos de padrões comuns

> Os exemplos abaixo incluem imports explícitos do Vitest (modo sem globals). Em
> projetos com globals habilitado, omita as linhas `import { ... } from 'vitest'`.

### Função pura com múltiplos tipos de entrada (overloads)

```typescript
import { describe, it, expect } from 'vitest';
import { formatar } from './formatar';

describe('formatar', () => {
  describe('quando recebe uma string', () => {
    it('retorna a string formatada em maiúsculas', () => {
      // Arrange
      const entrada = 'olá mundo';

      // Act
      const resultado = formatar(entrada);

      // Assert
      expect(resultado).toBe('OLÁ MUNDO');
    });
  });

  describe('quando recebe um número', () => {
    it('retorna o número como string formatada', () => {
      // Arrange
      const entrada = 1234.5;

      // Act
      const resultado = formatar(entrada);

      // Assert
      expect(resultado).toBe('1.234,50');
    });
  });

  describe('casos de borda', () => {
    it('retorna string vazia para entrada nula', () => {
      // Arrange
      const entrada = null;

      // Act
      const resultado = formatar(entrada);

      // Assert
      expect(resultado).toBe('');
    });
  });
});
```

### Classe com dependências (usando mock)

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { PedidoService } from './pedido.service';
import { RepositorioPedido } from './repositorio-pedido';

describe('PedidoService', () => {
  let service: PedidoService;
  let repositorioMock: ReturnType<typeof vi.mocked<RepositorioPedido>>;

  beforeEach(() => {
    // Arrange — configuração compartilhada entre testes do grupo
    repositorioMock = {
      buscar: vi.fn(),
      salvar: vi.fn(),
    } as unknown as ReturnType<typeof vi.mocked<RepositorioPedido>>;
    service = new PedidoService(repositorioMock);
  });

  describe('buscarPorId', () => {
    it('retorna o pedido quando encontrado', async () => {
      // Arrange
      const pedidoEsperado = { id: 1, total: 99.9 };
      repositorioMock.buscar.mockResolvedValue(pedidoEsperado);

      // Act
      const resultado = await service.buscarPorId(1);

      // Assert
      expect(resultado).toEqual(pedidoEsperado);
    });

    it('lança erro quando pedido não é encontrado', async () => {
      // Arrange
      repositorioMock.buscar.mockResolvedValue(null);

      // Act & Assert — combinados quando o Assert depende diretamente do Act
      await expect(service.buscarPorId(999)).rejects.toThrow('Pedido não encontrado');
    });
  });

  describe('calcularTotal', () => {
    it('soma os itens corretamente', () => {
      // Arrange
      const itens = [{ preco: 10 }, { preco: 20 }, { preco: 5 }];

      // Act
      const total = service.calcularTotal(itens);

      // Assert
      expect(total).toBe(35);
    });
  });
});
```

### Exceção ao comentário `// Act` e `// Assert`

Quando o Act é um `expect(...).rejects` ou `.resolves`, os dois passos se fundem
naturalmente. Nesse caso, use um comentário único `// Act & Assert` para deixar
claro que é uma fusão intencional, não um descuido.

---

## Checklist ao criar ou revisar testes

- [ ] Importações corretas conforme o modo de configuração: se globals estiver ativo, nenhuma importação do pacote `vitest`; caso contrário, todas as importações vêm de `vitest`
- [ ] Todos os `describe` e `it`/`test` têm descrições em português
- [ ] Todos os comentários inline são em português
- [ ] Cada teste segue a estrutura AAA com comentários marcados
- [ ] Testes de métodos/funcionalidades diferentes estão em `describe` separados
- [ ] Nenhum membro privado é acessado diretamente nos testes
- [ ] Diferentes overloads e tipos de entrada estão cobertos
- [ ] Casos de borda (null, vazio, zero, inválido) estão testados
- [ ] Mocks são criados com `vi.fn()` ou `vi.spyOn()`, nunca dependências reais

---

## Dicas adicionais

- **Nomes de testes descrevem comportamento**, não código. Prefira "retorna vazio
  quando a lista está vazia" a "testa getItems com array vazio".
- **Um assert por conceito**: um teste pode ter múltiplos `expect`, mas todos
  devem verificar aspectos do mesmo resultado ou comportamento. Se estiver tentado
  a testar duas coisas independentes, divida em dois testes.
- **Setup compartilhado vai em `beforeEach`**: se vários testes do mesmo grupo
  precisam da mesma instância ou estado inicial, inicialize em `beforeEach` em
  vez de repetir em cada teste — mas mantenha o comentário `// Arrange` quando
  houver configuração específica do teste além do setup compartilhado.

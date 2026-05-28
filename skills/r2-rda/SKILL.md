---
name: r2-rda
description: >-
  Cria, padroniza e altera status de RDA (Registro Decisão de Arquitetura), também conhecido como ADR (Architecture Decision Record). Use quando o usuário pedir para criar ou documentar uma decisão arquitetural (ex: "crie um RDA para..." ou "registre uma decisão arquitetural sobre..."); quando pedir para padronizar ou formatar um RDA existente (ex: "padronize a decisão 0001" ou "formate a RDA 0004"); quando pedir para atualizar o status de um RDA (ex: "aprove o RDA-0001" ou "altere o status da RDA 0001 para rejetado).
disable-model-invocation: true
metadata:
  internal: true
---

# Registro de Decisão de Arquitetura

## Detectando intenção

Apenas as seguintes ações são cobertas por esta skill:

| #   | Ação                         | Usar para                                                                        |
| --- | ---------------------------- | -------------------------------------------------------------------------------- |
| 1   | **Criar RDA por contexto**   | Capturar uma decisão já discutida na conversa ou presente em documento fornecido |
| 2   | **Criar RDA por entrevista** | Guiar o usuário passo a passo para registrar uma nova decisão                    |
| 3   | **Adequar RDA ao template**  | Padronizar uma RDA existente em formato diferente do template                    |
| 4   | **Atualizar status**         | Alterar o status de uma RDA existente (ex: `proposta` → `aceita`)                |

Tente inferir a ação desejada pelo usuário a partir de expressões como "crie um RDA para...", "registre uma decisão arquitetural sobre...", "padronize a decisão 0001", "formate a RDA 0004", "aprove o RDA-0001", "altere o status da RDA 0001 para rejeitado", etc. Há inúmeras variações possíveis dessas expressões, então use o contexto para inferir a ação. Você provavelmente conseguirá fazê-lo. Se não conseguir com confiança, entretanto, pergunte ao usuário qual ação ele deseja executar, listando as opções disponíveis.

Caso o usuário queira que execute uma ação que não esteja entre as 4 listadas, informe que essa skill é especializada apenas nessas ações e pergunte se ele gostaria de executar uma delas.

OBS: O termo ADR equivale a RDA. Ambos significam Registro de Decisão de Arquitetura, apenas em idiomas diferentes.

## Como executar cada ação

Antes de executar as ações 1, 2 ou 3, utilize uma ferramenta de leitura de arquivo para obter o conteúdo completo de [references/decisoes-arquiteturais.md](./references/decisoes-arquiteturais.md) para ter os princípios e regras de escrita de um RDA para entender como fazê-lo.

Em seguida, carregue e entenda também o conteúdo completo do arquivo de referência da ação escolhida e siga o fluxo contido nele:

| #   | Ação                 | Arquivo de referência                                                      |
| --- | -------------------- | -------------------------------------------------------------------------- |
| 1   | Criar por contexto   | [references/criar-por-contexto.md](./references/criar-por-contexto.md)     |
| 2   | Criar por entrevista | [references/criar-por-entrevista.md](./references/criar-por-entrevista.md) |
| 3   | Adequar ao template  | [references/adequar-ao-template.md](./references/adequar-ao-template.md)   |
| 4   | Atualizar status     | [references/atualizar-status.md](./references/atualizar-status.md)         |

## Template

O template padrão de RDA está em [assets/template-rda.md](./assets/template-rda.md). Siga-o estritamente: não omita seções, não adicione seções extras e preserve os nomes dos campos exatamente como definidos.

## Ciclo de vida

RDAs **nunca são excluídos**. Quando uma decisão é revertida ou substituída:

1. O RDA original recebe `status: substituída por RDA-XXXX`
2. Um novo RDA documenta a nova decisão

Isso preserva o histórico de raciocínio do projeto. O RDA antigo ainda é relevante — ela mostra o que *foi* a decisão, mesmo que não seja mais.

## Convenções gerais

### Onde gravar ou localizar RDAs

**Passo 1 — Identificar o tipo de repositório**

1. Verifique se existe `nx.json` na raiz do repositório (`find . -maxdepth 1 -type f -name nx.json`).
    - **SE existir:** tipo = **Nx**. Consulte [references/nx.md](./references/nx.md) quando necessário.
    - **SENÃO:** vá para 1.2.
2. Verifique se existe `pom.xml` com `<modules>` na raiz do repositório (`grep "<modules>" pom.xml`).
    - **SE existir:** tipo = **Maven**. Consulte [references/maven.md](./references/maven.md) quando necessário.
    - **SENÃO:** tipo = **repositório simples**.

**Passo 2 — Determinar o diretório do projeto (`<project_dir>`)**

1. **SE** tipo = repositório simples:
    - `<project_dir>` = raiz do repositório.
2. **SE** tipo = Nx ou Maven:
    - Tente identificar o projeto pelo contexto da conversa, arquivos mencionados ou estrutura visível.
    - **SE não conseguir com exatidão:** consulte o arquivo de referência do orquestrador (Nx/Maven).
    - **SE ainda não conseguir:** pergunte ao usuário qual o caminho exato do projeto a ser utilizado.

**Passo 3 — Localizar ou criar o diretório de RDAs (`<rda_dir>`)**

1. Execute:
    ```bash
    find "<project_dir>" -maxdepth 2 -type d \
        -regextype posix-extended -regex '.*/docs?/(rda|adr)s?' \
        -print -quit
    ```
2. **SE** o comando retornar um diretório:
    - `<rda_dir>` = diretório retornado.
    - Informe ao usuário o diretório identificado.
3. **SENÃO** (nenhum diretório encontrado):
    - Crie `"<project_dir>/docs/rda"` executando `mkdir -p "<project_dir>/docs/rda"`
    - `<rda_dir>` = `<project_dir>/docs/rda`.
    - Informe ao usuário que esse será o diretório de RDAs do projeto.

### Numeração

- Sequencial por projeto, sempre com 4 dígitos (ex: `0001`, `0002`...)
- Utilize o script [scripts/next_rda_number.py](./scripts/next_rda_number.py) para calcular o próximo número disponível
  - Execute com `python3 "<skill_dir>/scripts/next_rda_number.py" "<rda_dir>"`

### Nome do arquivo

- Formato: `RDA-<num>-<slug>.md` (ex: `RDA-0003-adocao-do-redis-para-cache.md`)
- Utilize o script [scripts/rda_filename.py](./scripts/rda_filename.py) para gerar o nome do arquivo a partir do número e do título da decisão
  - Execute com `python3 "<skill_dir>/scripts/rda_filename.py" "<rda_num>" "<rda_title>"`

## Scripts auxiliares

Os scripts em [scripts/](./scripts/) auxiliam algumas tarefas determinísticas. Se um script terminar com código de saída diferente de zero e você não conseguir resolver o identificar ou resolver o problema, informe o erro ao usuário e pergunte como prosseguir.

### Script para calcular o próximo número de RDA

Retorna o próximo número de RDA disponível no diretório.

**Script:** [scripts/next_rda_number.py](./scripts/next_rda_number.py)

**Instruções de uso**:

```
Uso:
    python3 next_rda_number.py "<rda_dir>"

Parâmetros:
    <rda_dir>   Caminho do diretório onde os arquivos de RDA
                estão localizados (ex: "/home/dev/project/docs/rda")

Stdout quando sucesso:
    Número do próximo RDA, zero-padded (ex: "0001", "0042")

Stderr quando erro:
    Mensagem de erro indicando o motivo da falha

Códigos de saída:
    0  Sucesso
    1  Parâmetros incorretos
    2  <rda_dir> não existe, não é um diretório, ou não está acessível
    3  Erro de acesso a diretório ou arquivo
    4  Próximo número de RDA ultrapassaria o limite de 9999
```

### Script para calcular o nome do arquivo de um RDA

Gera o nome de arquivo para um RDA a partir do número e do título.

**Script:** [scripts/rda_filename.py](./scripts/rda_filename.py)

**Instruções de uso**:

```
Uso:
    python3 rda_filename.py "<rda_num>" "<rda_title>"

Parâmetros:
    <rda_num>   Número da decisão (ex: "0003")
    <rda_title> Título da decisão (ex: "Adoção do Redis para Cache")

Stdout quando sucesso:
    Nome do arquivo do RDA (ex: "RDA-0003-adocao-do-redis-para-cache.md")

Stderr quando erro:
    Mensagem de erro indicando o motivo da falha

Códigos de saída:
    0  Sucesso
    1  Parâmetros incorretos
    2  <rda_num> inválido
    3  <rda_title> não produz um slug válido

Regra de tamanho:
    O nome completo do arquivo é limitado a 100 caracteres.
    O script trunca automaticamente apenas o slug do título para respeitar esse limite.
```

### Script para encontrar um RDA por seu número

Encontra o arquivo de um RDA por seu número no diretório fornecido.

**Script:** [scripts/find_rda_by_number.py](./scripts/find_rda_by_number.py)

**Instruções de uso**:

```
Uso:
    python3 find_rda_by_number.py "<rda_num>" "<rda_dir>"

Parâmetros:
    <rda_num>   Número do RDA a ser encontrado (ex: "0003" ou "rda 3")
    <rda_dir>   Caminho do diretório onde os arquivos de RDAs
                estão localizados (ex: "/home/dev/project/docs/rda")

Stdout quando sucesso:
    Caminho absoluto do arquivo de RDA correspondente ao número informado
    (ex: "/home/dev/project/docs/rda/RDA-0003-adocao-do-redis-para-cache.md")

Stderr quando erro:
    Mensagem de erro indicando o motivo da falha

Códigos de saída:
    0  Sucesso
    1  Parâmetros incorretos
    2  Não foi possível extrair um número de RDA de <rda_num>
    3  <rda_dir> não existe, não é um diretório, ou não está acessível
    4  Erro de acesso do diretório ou arquivo
    5  RDA não encontrado
    6  Múltiplos arquivos de RDA encontrados para o número especificado
```

### Script para obter o nome do autor

Obtém o nome do autor a partir do ambiente.

**Script:** [scripts/get_author.sh](./scripts/get_author.sh)

**Instruções de uso**:

```
Uso:
    bash get_author.sh "<rda_dir>"

Parâmetros:
    <rda_dir>   Caminho absoluto do diretório onde os arquivos de RDA
                estão localizados (ex: "/home/dev/project/docs/rda")

Stdout quando sucesso:
    O nome do autor (ex: "João Silva")

Stderr quando erro:
    Mensagem de erro indicando o motivo da falha

Códigos de saída:
    0  Sucesso
    1  rda_dir não informado
    2  rda_dir não é um diretório válido
    3  Git não disponível
    4  Não foi possível obter o nome do autor
```
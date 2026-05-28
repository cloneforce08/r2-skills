## Deteção do diretório de um projeto em monorepos Nx

### Passo 1: Descobrindo todos os projetos

Execute o comando `npx nx show projects` na raiz do repositório para obter a lista de projetos. Desta lista, de acordo com o contexto da conversa, identifique qual é o projeto pertinente para o qual a RDA deve ser criada ou atualizada.

Se não consguir identificar, apresente a lista de projetos ao usuário e pergunte qual deles utilizar.

OBS: Se existirem até 9 projetos e você tiver disponível uma ferramenta para questionar o usuário apresentando opções, use-a. Caso contrário, apresente uma lista numerada em formato de texto com todos os projetos e peça para o usuário digitar o número relativo ao projeto desejado.

Referenciaremos o nome exato do projeto identificado como `{project_name}`.

### Passo 2: Descobrindo o diretório do projeto

Uma vez identificado o nome exato do projeto:

1. Determine a disponibilidade do utilitário `jq` ou `yq` para processar JSON executando `which jq || which yq`.
   1. Se retornar o caminho de um dos utilitários (referenciaremos como `utility_path`), execute `nx show project {project_name} --json | {utility_path} '.root'` para obter o caminho do diretório do projeto relativo à raíz do repositório.
   2. Se retornar código de saída diferente de zero, execute `nx show project {project_name} --json` e extraia o valor do campo `root` manualmente do JSON retornado.
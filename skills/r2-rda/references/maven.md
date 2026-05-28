## Deteção do diretório de um projeto em monorepos Maven

Execute o comando `grep -Poz '<modules>\K(?s).*?(?=</modules>)' pom.xml | tr '\0' '\n'` na raiz do repositório para obter a lista de paths de projetos (módulos) contidos em tags `<module>`. Dessa lista, de acordo com o contexto da conversa, identifique qual é o projeto pertinente para o qual a RDA deve ser criada ou atualizada.

Se não consguir identificar, apresente a lista de paths de projetos ao usuário e pergunte qual deles utilizar.

OBS: Se existirem até 9 projetos e você tiver disponível uma ferramenta para questionar o usuário apresentando opções, use-a. Caso contrário, apresente uma lista numerada em formato de texto com todos os paths de projetos e peça para o usuário digitar o número relativo ao projeto desejado.

#!/usr/bin/env bash
set -euo pipefail

# Obtém o nome do autor a partir do ambiente.
# 
# Uso:
#     bash get_author.sh "<rda_dir>"
# 
# Parâmetros:
#     <rda_dir>   Caminho absoluto do diretório onde os arquivos de RDA
#                 estão localizados (ex: "/home/dev/project/docs/rda")
# 
# Stdout quando sucesso:
#     O nome do autor (ex: "João Silva")
#
# Stderr quando erro:
#     Mensagem de erro indicando o motivo da falha
# 
# Códigos de saída:
#     0  Sucesso
#     1  rda_dir não informado
#     2  rda_dir não é um diretório válido
#     3  Git não disponível
#     4  Não foi possível obter o nome do autor

REPO_DIR=${1:-}

if [[ "$REPO_DIR" == "" ]]; then
  echo "Uso: $0 \"<rda_dir>\"" >&2
  return 1
fi

if [[ ! -d "$REPO_DIR" ]]; then
  echo "rda_dir não é um diretório válido: '$REPO_DIR'" >&2
  return 2
fi

# Sem git disponível, desiste cedo
if ! command -v git >/dev/null 2>&1; then
  echo "Git não disponível" >&2
  return 3
fi

cd "$REPO_DIR"

AUTHOR=$(git config user.name || true)

if [[ -n "$AUTHOR" ]]; then
  echo "$AUTHOR"
  return 0
fi

# TODO: Tentar obter o sistema operacional

echo "Não foi possível obter o nome do autor" >&2
return 4

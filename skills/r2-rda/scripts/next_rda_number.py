#!/usr/bin/env python3

"""Retorna o próximo número de RDA disponível no diretório.

Uso:
    python next_rda_number.py "<rda_dir>"

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
"""

import sys
from enum import Enum
from pathlib import Path
from _utils import (
    RDA_FILE_PATTERN,
    RDA_NUM_MAX,
    parse_rda_num,
    is_directory_valid_and_accessible,
    RdaNumRangeError,
)

__FILENAME__ = Path(__file__).name


class ErrorCode(Enum):
    INCORRECT_PARAMS = 1
    RDA_DIR_INVALID = 2
    ACCESS_ERROR = 3
    RDA_NUM_RANGE_OVERFLOW = 4


def main() -> None:
    args = sys.argv[1:]

    if len(args) != 1:
        print("Erro: número incorreto de parâmetros", file=sys.stderr)
        print(f'Uso: {__FILENAME__} "<rda_dir>"', file=sys.stderr)
        sys.exit(ErrorCode.INCORRECT_PARAMS.value)

    rda_dir = args[0].strip()
    if len(rda_dir) == 0:
        print("Erro: <rda_dir> vazio ou não informado", file=sys.stderr)
        sys.exit(ErrorCode.INCORRECT_PARAMS.value)

    rda_dir = Path(rda_dir)
    if is_directory_valid_and_accessible(rda_dir) is False:
        print(
            f"Erro: O caminho não é um diretório válido ou não está acessível: '{rda_dir}'",
            file=sys.stderr,
        )
        sys.exit(ErrorCode.RDA_DIR_INVALID.value)

    try:
        print(_get_next_rda_number(rda_dir))
    except OSError as ex:
        print(f"Erro: Acesso não permitido: {ex}", file=sys.stderr)
        sys.exit(ErrorCode.ACCESS_ERROR.value)
    except RdaNumRangeError as ex:
        print(
            f"Erro: Próximo número de RDA ultrapassaria o limite de {RDA_NUM_MAX}",
            file=sys.stderr,
        )
        sys.exit(ErrorCode.RDA_NUM_RANGE_OVERFLOW.value)


def _get_next_rda_number(rda_dir: Path) -> str:
    """Retorna o próximo número de RDA disponível no diretório.

    Analisa os arquivos de RDAs existentes e retorna o maior número
    encontrado + 1, formatado com 4 dígitos.

    Caso não encontre nenhum arquivo de RDA, retorna '0001'.

    Args:
        rda_dir (Path): O diretório onde os arquivos de RDA estão localizados.

    Returns:
        str: O próximo número de RDA disponível, formatado como string de 4 dígitos.

    Raises:
        OSError: Se houver falha de acesso ou leitura do diretório ou de seus arquivos.
        RdaNumRangeError: Se o próximo número de RDA ultrapassar o limite de 9999.
    """
    max_num = 0

    for entry in rda_dir.iterdir():
        if not entry.is_file():
            continue

        match = RDA_FILE_PATTERN.match(entry.name)

        if match:
            num = int(match.group(1))
            if num > max_num:
                max_num = num

    return parse_rda_num(max_num + 1)


if __name__ == "__main__":
    main()

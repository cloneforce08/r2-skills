#!/usr/bin/env python3

"""Encontra o arquivo de um RDA por seu número no diretório fornecido.

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
    4  Erro de acesso a diretório ou arquivo
    5  RDA não encontrado
    6  Múltiplos arquivos de RDA encontrados para o número especificado
"""

import re
import sys
from pathlib import Path
from enum import Enum
from _utils import (
    RDA_FILE_PATTERN,
    RdaNumRangeError,
    parse_rda_num,
    is_directory_valid_and_accessible,
)

__FILENAME__ = Path(__file__).name


class ErrorCode(Enum):
    INCORRECT_PARAMS = 1
    CANT_EXTRACT_RDA_NUM = 2
    RDA_DIR_INVALID = 3
    ACCESS_ERROR = 4
    RDA_NOT_FOUND = 5
    MULTIPLE_RDAS_FOUND = 6


def main() -> None:
    args = sys.argv[1:]

    if len(args) != 2:
        print("Erro: número incorreto de parâmetros", file=sys.stderr)
        print(f'Uso: {__FILENAME__} "<rda_num>" "<rda_dir>"', file=sys.stderr)
        sys.exit(ErrorCode.INCORRECT_PARAMS.value)

    rda_num = args[0].strip()
    if len(rda_num) == 0:
        print("Erro: <rda_num> vazio ou não informado", file=sys.stderr)
        sys.exit(ErrorCode.INCORRECT_PARAMS.value)

    rda_dir = args[1].strip()
    if len(rda_dir) == 0:
        print("Erro: <rda_dir> vazio ou não informado", file=sys.stderr)
        sys.exit(ErrorCode.INCORRECT_PARAMS.value)

    # --- Tratando rda_num
    try:
        rda_num = _extract_rda_num_from_argument(rda_num)
    except (RdaNumRangeError, MultipleRdaNumCandidatesError) as ex:
        print(
            f"Erro: Não foi possível extrair um número de RDA de '{args[0]}': {ex}",
            file=sys.stderr,
        )
        sys.exit(ErrorCode.CANT_EXTRACT_RDA_NUM.value)
    if rda_num is None:
        print(
            f"Erro: Não foi possível extrair um número de RDA de '{args[0]}'",
            file=sys.stderr,
        )
        sys.exit(ErrorCode.CANT_EXTRACT_RDA_NUM.value)

    # --- Tratando rda_dir
    rda_dir = Path(rda_dir)
    if is_directory_valid_and_accessible(rda_dir) is False:
        print(
            f"Erro: O caminho não é um diretório válido ou não está acessível: '{rda_dir}'",
            file=sys.stderr,
        )
        sys.exit(ErrorCode.RDA_DIR_INVALID.value)

    try:
        rda_path = _find_rda_by_number(rda_num, rda_dir)
    except MultipleRdaFilesFoundError as ex:
        print(f"Erro: {ex}", file=sys.stderr)
        sys.exit(ErrorCode.MULTIPLE_RDAS_FOUND.value)
    except OSError as ex:
        print(f"Erro: Acesso não permitido: {ex}", file=sys.stderr)
        sys.exit(ErrorCode.ACCESS_ERROR.value)

    if rda_path is None:
        print(
            f"Erro: RDA com número '{rda_num}' não encontrado em '{rda_dir}'",
            file=sys.stderr,
        )
        sys.exit(ErrorCode.RDA_NOT_FOUND.value)

    print(rda_path)


class MultipleRdaFilesFoundError(Exception):
    """Exceção para indicar que múltiplos arquivos de RDA foram encontrados para um número específico."""

    def __init__(self, rda_num: str, file_paths: list[str]):
        super().__init__(
            f"Múltiplos arquivos encontrados para RDA {rda_num}: {file_paths}"
        )
        self.rda_num = rda_num
        self.file_paths = file_paths


class MultipleRdaNumCandidatesError(Exception):
    """Exceção para indicar que múltiplos candidatos a número de RDA foram encontrados na string de entrada."""

    def __init__(self, input_str: str, candidates: list[str]):
        super().__init__(
            f"Múltiplos candidatos a número de RDA encontrados em '{input_str}': {candidates}"
        )
        self.input_str = input_str
        self.candidates = candidates


def _extract_rda_num_from_argument(rda_num: str) -> str | None:
    """Tenta extrair um número de RDA da string informada.

    Args:
        rda_num (str): A string da qual tentar extrair o número de RDA.

    Returns:
        str | None: O número de RDA formatado como string de 4 dígitos,
        ou None se não for possível extrair um número válido.

    Raises:
        RdaNumRangeError: Se número de RDA extraído estiver fora do range permitido.
        MultipleRdaNumCandidatesError: Se múltiplos candidatos a número de RDA forem encontrados na string de entrada.
    """
    matches = re.findall(r"\d+", rda_num)

    if len(matches) == 1:
        return parse_rda_num(int(matches[0]))
    elif len(matches) > 1:
        raise MultipleRdaNumCandidatesError(rda_num, matches)

    return None


def _find_rda_by_number(rda_num: str, rda_dir: Path) -> str | None:
    """Encontra um RDA por seu número no diretório fornecido.

    Args:
        rda_num (str): O número do RDA a ser encontrado, formatado como string de 4 dígitos.
        rda_dir (Path): O diretório onde os arquivos de RDA estão localizados.

    Returns:
        str | None: O caminho absoluto do arquivo de RDA correspondente,
                    ou None se nenhum arquivo com esse número for encontrado.

    Raises:
        OSError: Se houver falha de acesso ou leitura do diretório ou de seus arquivos.
        MultipleRdaFilesFoundError: Se múltiplos arquivos de RDA forem encontrados para o número especificado.
    """
    matches: list[str] = []

    for entry in rda_dir.iterdir():
        if not entry.is_file():
            continue

        match = RDA_FILE_PATTERN.match(entry.name)

        if match and match.group(1) == rda_num:
            matches.append(str(entry.resolve()))
            if len(matches) > 1:
                break

    if len(matches) > 1:
        raise MultipleRdaFilesFoundError(rda_num, matches)

    return matches[0] if matches else None


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Gera o nome de arquivo para um RDA a partir do número e do título.

Uso:
    python rda_filename.py "<rda_num>" "<rda_title>"

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
"""

import re
import sys
import unicodedata
from enum import Enum
from pathlib import Path
from _utils import RdaNumRangeError, parse_rda_num

MAX_FILENAME_LENGTH = 100

__FILENAME__ = Path(__file__).name


class ErrorCode(Enum):
    INCORRECT_PARAMS = 1
    INVALID_RDA_NUM = 2
    INVALID_TITLE_SLUG = 3


def main() -> None:
    args = sys.argv[1:]

    if len(args) != 2:
        print("Erro: número incorreto de parâmetros", file=sys.stderr)
        print(f'Uso: {__FILENAME__} "<rda_num>" "<rda_title>"', file=sys.stderr)
        sys.exit(ErrorCode.INCORRECT_PARAMS.value)

    rda_num = args[0].strip()
    if len(rda_num) == 0:
        print("Erro: <rda_num> vazio ou não informado", file=sys.stderr)
        sys.exit(ErrorCode.INCORRECT_PARAMS.value)

    rda_title = args[1].strip()
    if len(rda_title) == 0:
        print("Erro: <rda_title> vazio ou não informado", file=sys.stderr)
        sys.exit(ErrorCode.INCORRECT_PARAMS.value)

    # --- Tratando rda_num
    try:
        rda_num = parse_rda_num(int(rda_num))
    except (RdaNumRangeError, ValueError) as ex:
        print(
            f"Erro: '{rda_num}' não é um número de RDA válido: {ex}",
            file=sys.stderr,
        )
        sys.exit(ErrorCode.INVALID_RDA_NUM.value)

    # --- Criando o slug
    title_slug = _slugify_title(rda_title)
    if len(title_slug) == 0:
        print(
            f"Erro: O título '{rda_title}' não produz um slug válido: '{title_slug}'",
            file=sys.stderr,
        )
        sys.exit(ErrorCode.INVALID_TITLE_SLUG.value)

    # Garantindo que o nome do arquivo completo não ultrapasse o limite, truncando apenas o slug do título
    fixed_part = f"RDA-{rda_num}-.md"
    max_slug_length = MAX_FILENAME_LENGTH - len(fixed_part)
    if len(title_slug) > max_slug_length:
        title_slug = title_slug[:max_slug_length].rstrip("-")
    assert len(title_slug) > 0, "O slug do título não pode ser vazio após truncamento"

    print(f"RDA-{rda_num}-{title_slug}.md")


def _slugify_title(title: str) -> str:
    """Converte um título em slug para uso em nomes de arquivo.

    Aplica as seguintes transformações:
    1. Normaliza para NFD e remove marcas de diacríticos (acentos, cedilha etc.)
    2. Converte para minúsculas
    3. Substitui por hífen caracteres que não sejam a-z, 0-9 ou hífen
    4. Colapsa múltiplos hífens consecutivos em um único
    5. Remove hífens no início e no fim

    Args:
        title (str): O título a ser convertido

    Returns:
        str: O slug resultante
    """
    # NFD decompõe caracteres acentuados em base + marca combinante
    nfd = unicodedata.normalize("NFD", title)

    # Remove as marcas combinantes (diacríticos)
    without_diacritics = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    lower = without_diacritics.lower()
    cleaned = re.sub(r"[^a-z0-9-]", "-", lower)
    collapsed = re.sub(r"-{2,}", "-", cleaned)

    return collapsed.strip("-")


if __name__ == "__main__":
    main()

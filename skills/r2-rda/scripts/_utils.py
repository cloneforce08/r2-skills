from pathlib import Path
import re

# Padrão para localizar arquivos de RDA, com captura do número de RDA
# É mais permissivo em relação ao case para permitir encontrar arquivos
# levemente fora do padrão.
RDA_FILE_PATTERN = re.compile(r"^RDA-(\d{4})-[a-zA-Z0-9-]+\.md$", re.IGNORECASE)

RDA_NUM_MIN = 1
RDA_NUM_MAX = 9999


def is_valid_rda_num(num: int) -> bool:
    """Verifica se um número de RDA é válido (entre RDA_NUM_MIN e RDA_NUM_MAX).

    Args:
        num (int): O número de RDA a ser verificado.

    Returns:
        bool: True se o número for válido, False caso contrário.
    """
    return RDA_NUM_MIN <= num <= RDA_NUM_MAX


def parse_rda_num(num: int | str) -> str:
    """Formata um número de RDA como uma string de 4 dígitos com zeros à esquerda.

    Args:
        num (int | str): O número de RDA a ser formatado, como inteiro ou string numérica.

    Returns:
        str: Uma string representando o número de RDA formatado.

    Raises:
        RdaNumRangeError: Se o número estiver fora do range permitido.
        ValueError: Se o valor fornecido não for um número inteiro válido.
    """

    if isinstance(num, str):
        if not re.match(r"^\d+$", num):
            raise ValueError(f"Valor '{num}' não é um número inteiro válido.")
        num = int(num)

    if is_valid_rda_num(num):
        return f"{num:04d}"

    raise RdaNumRangeError(num)


def is_directory_valid_and_accessible(path: Path) -> bool:
    """Verifica se o caminho é um diretório válido e acessível.

    Args:
        path (Path): O caminho a ser verificado.

    Returns:
        bool: True se o caminho é um diretório válido e acessível, False caso contrário.
    """
    try:
        if not path.exists() or not path.is_dir():
            return False

        next(path.iterdir(), None)

        return True
    except OSError:
        return False


class RdaNumRangeError(ValueError):
    """Exceção para indicar que um número de RDA está fora do range permitido."""

    def __init__(self, num: int):
        super().__init__(
            f"Número de RDA deve estar entre {RDA_NUM_MIN} e {RDA_NUM_MAX}, mas recebeu {num}"
        )

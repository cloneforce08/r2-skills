#!/usr/bin/env python3
"""Testes da API pública do script find_rda_by_number.py.

Estes testes executam o script via subprocess, focando no comportamento
observável (stdout, stderr, exit code) sem acoplar a implementação interna.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "find_rda_by_number.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


class TestSucesso(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _create_rda(self, name: str) -> Path:
        path = self.tmpdir / name
        path.touch()
        return path

    def test_encontra_por_numero_exato(self):
        expected = self._create_rda("RDA-0003-adocao-do-redis.md")
        result = _run("0003", str(self.tmpdir))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), str(expected.resolve()))

    def test_encontra_por_numero_curto(self):
        expected = self._create_rda("RDA-0003-adocao-do-redis.md")
        result = _run("3", str(self.tmpdir))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), str(expected.resolve()))

    def test_encontra_por_texto_com_numero(self):
        expected = self._create_rda("RDA-0003-adocao-do-redis.md")
        result = _run("rda 3", str(self.tmpdir))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), str(expected.resolve()))

    def test_stdout_e_caminho_absoluto(self):
        self._create_rda("RDA-0005-kafka-como-broker.md")
        result = _run("5", str(self.tmpdir))
        self.assertEqual(result.returncode, 0)
        self.assertTrue(Path(result.stdout.strip()).is_absolute())

    def test_stderr_vazio_no_sucesso(self):
        self._create_rda("RDA-0010-migracao-para-k8s.md")
        result = _run("10", str(self.tmpdir))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stderr, "")

    def test_ignora_arquivos_sem_padrao_rda(self):
        expected = self._create_rda("RDA-0007-uso-de-graphql.md")
        self._create_rda("README.md")
        self._create_rda("notes.txt")
        result = _run("7", str(self.tmpdir))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), str(expected.resolve()))

    def test_encontra_rda_com_numero_minimo(self):
        expected = self._create_rda("RDA-0001-primeiro-rda.md")
        result = _run("1", str(self.tmpdir))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), str(expected.resolve()))

    def test_encontra_rda_com_numero_maximo(self):
        expected = self._create_rda("RDA-9999-ultimo-rda.md")
        result = _run("9999", str(self.tmpdir))
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), str(expected.resolve()))


class TestErros(unittest.TestCase):
    def setUp(self):
        self.tmpdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def _create_rda(self, name: str) -> Path:
        path = self.tmpdir / name
        path.touch()
        return path

    # --- exit code 1: parâmetros incorretos ---

    def test_sem_argumentos(self):
        result = _run()
        self.assertEqual(result.returncode, 1)

    def test_apenas_um_argumento(self):
        result = _run("0003")
        self.assertEqual(result.returncode, 1)

    def test_tres_argumentos(self):
        result = _run("0003", str(self.tmpdir), "extra")
        self.assertEqual(result.returncode, 1)

    def test_rda_num_vazio(self):
        result = _run("", str(self.tmpdir))
        self.assertEqual(result.returncode, 1)

    def test_rda_num_apenas_espacos(self):
        result = _run("   ", str(self.tmpdir))
        self.assertEqual(result.returncode, 1)

    def test_rda_dir_vazio(self):
        result = _run("0003", "")
        self.assertEqual(result.returncode, 1)

    # --- exit code 2: não foi possível extrair número de RDA ---

    def test_rda_num_sem_digitos(self):
        result = _run("abc", str(self.tmpdir))
        self.assertEqual(result.returncode, 2)

    def test_rda_num_multiplos_grupos_de_digitos(self):
        result = _run("1 2", str(self.tmpdir))
        self.assertEqual(result.returncode, 2)

    def test_rda_num_zero_fora_do_range(self):
        result = _run("0", str(self.tmpdir))
        self.assertEqual(result.returncode, 2)

    def test_rda_num_acima_do_range(self):
        result = _run("10000", str(self.tmpdir))
        self.assertEqual(result.returncode, 2)

    # --- exit code 3: rda_dir inválido ---

    def test_rda_dir_inexistente(self):
        result = _run("0003", "/caminho/que/nao/existe/abc123")
        self.assertEqual(result.returncode, 3)

    def test_rda_dir_e_arquivo(self):
        arquivo = self.tmpdir / "nao-e-diretorio.md"
        arquivo.touch()
        result = _run("0003", str(arquivo))
        self.assertEqual(result.returncode, 3)

    @unittest.skipIf(os.getuid() == 0, "chmod não tem efeito como root")
    def test_rda_dir_sem_permissao(self):
        os.chmod(self.tmpdir, 0o000)
        try:
            result = _run("0003", str(self.tmpdir))
            self.assertEqual(result.returncode, 3)
        finally:
            os.chmod(self.tmpdir, 0o755)

    # --- exit code 4: Erro de acesso ---

    # Dificil testar esta condicao, pois envolveria ela acontecer
    # após a primeira validação (do argumento).

    # --- exit code 5: RDA não encontrado ---

    def test_rda_nao_encontrado_em_diretorio_vazio(self):
        result = _run("0003", str(self.tmpdir))
        self.assertEqual(result.returncode, 5)

    def test_rda_nao_encontrado_entre_outros_rdas(self):
        (self.tmpdir / "RDA-0001-primeiro.md").touch()
        (self.tmpdir / "RDA-0002-segundo.md").touch()
        result = _run("0099", str(self.tmpdir))
        self.assertEqual(result.returncode, 5)

    # --- exit code 6: múltiplos arquivos encontrados ---

    def test_multiplos_rdas_com_mesmo_numero(self):
        (self.tmpdir / "RDA-0003-nome-a.md").touch()
        (self.tmpdir / "RDA-0003-nome-b.md").touch()
        result = _run("0003", str(self.tmpdir))
        self.assertEqual(result.returncode, 6)

    # --- verificações de stderr/stdout ---

    def test_stderr_contem_mensagem_de_erro(self):
        result = _run("abc", str(self.tmpdir))
        self.assertIn("Erro:", result.stderr)

    def test_stdout_vazio_em_erro(self):
        result = _run("abc", str(self.tmpdir))
        self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()

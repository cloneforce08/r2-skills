#!/usr/bin/env python3
"""Testes da API pública do script next_rda_number.py.

Estes testes executam o script via subprocess, focando no comportamento
observável (stdout, stderr, exit code) sem acoplar a implementação interna.
"""

import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "next_rda_number.py"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )


class TestSucesso(unittest.TestCase):

    def test_diretorio_vazio_retorna_0001(self):
        with tempfile.TemporaryDirectory() as tmp:
            r = _run(tmp)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stdout.strip(), "0001")
            self.assertEqual(r.stderr, "")

    def test_retorna_proximo_numero_mais_alto(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "RDA-0001-primeiro.md").write_text("", encoding="utf-8")
            (base / "RDA-0042-resposta.md").write_text("", encoding="utf-8")
            (base / "README.md").write_text("nao conta", encoding="utf-8")
            (base / "subdir").mkdir()

            r = _run(tmp)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stdout.strip(), "0043")
            self.assertEqual(r.stderr, "")

    def test_case_insensitive_no_prefixo_rda(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "rda-0007-minusculo.md").write_text("", encoding="utf-8")

            r = _run(tmp)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stdout.strip(), "0008")

    def test_ignora_arquivos_fora_do_padrao(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "RDA-12-curto.md").write_text("", encoding="utf-8")
            (base / "RDA-000A-invalido.md").write_text("", encoding="utf-8")
            (base / "RDA-0011-valido.md").write_text("", encoding="utf-8")

            r = _run(tmp)
            self.assertEqual(r.returncode, 0)
            self.assertEqual(r.stdout.strip(), "0012")


class TestErros(unittest.TestCase):

    def test_sem_argumentos(self):
        r = _run()
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "")
        self.assertIn("número incorreto de parâmetros", r.stderr)
        self.assertIn("Uso", r.stderr)

    def test_argumento_a_mais(self):
        r = _run("/tmp", "extra")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "")
        self.assertIn("número incorreto de parâmetros", r.stderr)

    def test_caminho_inexistente(self):
        with tempfile.TemporaryDirectory() as tmp:
            inexistente = str(Path(tmp) / "nao-existe")
            r = _run(inexistente)
            self.assertEqual(r.returncode, 2)
            self.assertEqual(r.stdout, "")
            self.assertIn("não é um diretório válido", r.stderr)

    def test_caminho_e_arquivo(self):
        with tempfile.TemporaryDirectory() as tmp:
            arquivo = Path(tmp) / "arquivo.txt"
            arquivo.write_text("x", encoding="utf-8")
            r = _run(str(arquivo))
            self.assertEqual(r.returncode, 2)
            self.assertEqual(r.stdout, "")
            self.assertIn("não é um diretório válido", r.stderr)

    def test_overflow_quando_ja_existe_9999(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "RDA-9999-maximo.md").write_text("", encoding="utf-8")

            r = _run(tmp)
            self.assertEqual(r.returncode, 4)
            self.assertEqual(r.stdout, "")
            self.assertIn("ultrapassa o limite de 9999", r.stderr)

    def test_erro_de_acesso_leitura_no_diretorio(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            (base / "RDA-0001-primeiro.md").write_text("", encoding="utf-8")

            original_mode = stat.S_IMODE(base.stat().st_mode)
            try:
                base.chmod(0)
                r = _run(tmp)
            finally:
                base.chmod(original_mode)

            if r.returncode == 0:
                self.skipTest("Ambiente permite leitura mesmo sem permissões (possível execução privilegiada)")

            self.assertEqual(r.returncode, 3)
            self.assertEqual(r.stdout, "")
            self.assertIn("Erro de acesso/leitura", r.stderr)


if __name__ == "__main__":
    unittest.main()

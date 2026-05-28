#!/usr/bin/env python3
"""Testes da API pública do script rda_filename.py.

Estes testes executam o script via subprocess, focando no comportamento
observável (stdout, stderr, exit code) sem acoplar a implementação interna.
"""

import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "rda_filename.py"

def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
    )

class TestSucesso(unittest.TestCase):
    
    def test_numero_com_leading_zeros(self):
        r = _run("0003", "Adoção do Redis para Cache")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "RDA-0003-adocao-do-redis-para-cache.md")
        self.assertEqual(r.stderr, "")

    def test_numero_sem_leading_zeros(self):
        r = _run("3", "Adoção do Redis para Cache")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "RDA-0003-adocao-do-redis-para-cache.md")

    def test_numero_um_digito(self):
        r = _run("1", "Primeira Decisão")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "RDA-0001-primeira-decisao.md")

    def test_numero_quatro_digitos(self):
        r = _run("9999", "Decisão Final")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "RDA-9999-decisao-final.md")

    def test_remove_acentos(self):
        r = _run("1", "Criação de APIs RESTful")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "RDA-0001-criacao-de-apis-restful.md")

    def test_remove_cedilha(self):
        r = _run("2", "Integração com Sistemas Legados")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "RDA-0002-integracao-com-sistemas-legados.md")

    def test_maiusculas_para_minusculas(self):
        r = _run("1", "Migrar para TypeScript")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "RDA-0001-migrar-para-typescript.md")

    def test_caracteres_especiais_substituidos(self):
        r = _run("1", "API v2.0 (nova versão)")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "RDA-0001-api-v2-0-nova-versao.md")

    def test_colapso_hifens_multiplos(self):
        r = _run("1", "A & B — C/D")
        self.assertEqual(r.returncode, 0)
        slug = r.stdout.strip()
        self.assertNotIn("--", slug)
        self.assertTrue(slug.startswith("RDA-0001-a-b-c-d.md"))

    def test_titulo_uma_palavra(self):
        r = _run("1", "Deploy")
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.strip(), "RDA-0001-deploy.md")

    def _slug(self, stdout: str) -> str:
        return stdout.strip().replace("RDA-0001-", "").replace(".md", "")

    def test_titulo_muito_longo_truncado_para_limite_de_nome_completo(self):
        titulo = "a" * 500
        r = _run("1", titulo)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(len(r.stdout.strip()), 100)

    def test_truncamento_remove_hifen_final(self):
        r = _run("1", ("a" * 242) + " b")
        self.assertEqual(r.returncode, 0)
        slug = self._slug(r.stdout)
        self.assertLessEqual(len(r.stdout.strip()), 100)
        self.assertFalse(slug.endswith("-"))


class TestErros(unittest.TestCase):

    def test_sem_argumentos(self):
        r = _run()
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "")
        self.assertIn("Uso", r.stderr)

    def test_apenas_um_argumento(self):
        r = _run("0001")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "")

    def test_numero_zero(self):
        r = _run("0", "teste")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(r.stdout, "")

    def test_numero_string_nao_numerica(self):
        r = _run("abc", "teste")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(r.stdout, "")

    def test_numero_cinco_digitos(self):
        r = _run("12345", "teste")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(r.stdout, "")

    def test_numero_negativo(self):
        r = _run("-1", "teste")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(r.stdout, "")

    def test_numero_float(self):
        r = _run("1.5", "teste")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(r.stdout, "")

    def test_numero_vazio(self):
        r = _run("", "teste")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "")

    def test_titulo_so_caracteres_especiais(self):
        r = _run("1", "!!!")
        self.assertEqual(r.returncode, 3)
        self.assertEqual(r.stdout, "")

    def test_titulo_so_emojis(self):
        r = _run("1", "🚀🔥")
        self.assertEqual(r.returncode, 3)
        self.assertEqual(r.stdout, "")

    def test_titulo_so_espacos(self):
        r = _run("1", "   ")
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "")

    def test_mensagem_erro_numero_invalido(self):
        r = _run("0", "teste")
        self.assertIn("número", r.stderr.lower())

    def test_mensagem_erro_slug_invalido(self):
        r = _run("1", "!!!")
        self.assertIn("slug", r.stderr.lower())


if __name__ == "__main__":
    unittest.main()

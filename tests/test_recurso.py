"""Pruebas del recurso (R5). Ejecutar desde la raíz del repositorio:

    python -m unittest discover -s tests -v      # o: python -m pytest tests -q

Requieren spaCy, medspaCy y el modelo es_core_news_md (o sm). Solo usan frases sintéticas.
"""
import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

with contextlib.redirect_stdout(io.StringIO()):
    from cli import build_pipeline  # noqa: E402
    from escribe.default_nlp import check_order, make_nlp  # noqa: E402
import manifiesto_lexico as ML  # noqa: E402

MANIFEST = json.loads(ML.MANIFEST.read_text(encoding="utf-8"))


def n_rules(nlp_obj):
    return len(nlp_obj.get_pipe("medspacy_target_matcher").rules)


def quiet_build(profile, **kw):
    with contextlib.redirect_stdout(io.StringIO()):
        return build_pipeline(profile, verbose=False, **kw)


class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.core = quiet_build("core")
        cls.core_n_antes = n_rules(cls.core)
        cls.py = quiet_build("py")
        cls.co = quiet_build("co")

    # R1: orden
    def test_orden_matcher_antes_de_context(self):
        for name, obj in (("co", self.co), ("core", self.core), ("py", self.py)):
            names = obj.pipe_names
            self.assertLess(names.index("medspacy_target_matcher"), names.index("medspacy_context"), name)

    def test_check_order_detecta_orden_invalido(self):
        bad = make_nlp()
        bad.remove_pipe("medspacy_target_matcher")
        bad.add_pipe("medspacy_target_matcher")  # al final, como en la versión anterior
        with self.assertRaises(RuntimeError):
            check_order(bad)

    # R2: perfiles independientes y conteos
    def test_perfiles_son_objetos_distintos(self):
        self.assertIsNot(self.core, self.py)
        self.assertIsNot(self.core, self.co)

    def test_core_no_cambia_al_construir_py(self):
        self.assertEqual(n_rules(self.core), self.core_n_antes)

    def test_reglas_cargadas_igual_a_declaradas(self):
        for prof, obj in (("co", self.co), ("core", self.core), ("py", self.py)):
            self.assertEqual(n_rules(obj), MANIFEST["perfiles"][prof]["reglas_declaradas"], prof)

    # Las dos APIs cargan en el mismo orden (antes select_concepts usaba un set y el desempate
    # entre categorías superpuestas variaba con PYTHONHASHSEED)
    def test_select_concepts_igual_a_build_pipeline(self):
        from escribe.default_nlp import select_concepts
        with contextlib.redirect_stdout(io.StringIO()):
            sel = select_concepts(make_nlp(), json_dir=str(ROOT / "escribe/patterns/Concept_CO"),
                                  concepts=("Ansiedad", "Depresion", "Contexto"), reset=True, verbose=False)
        for frase in ("Paciente refiere sin energía.", "Paciente refiere alteraciones psicomotoras.", "Niega ansiedad."):
            a = [(e.text, e.label_, e._.is_negated) for e in sel(frase).ents]
            b = [(e.text, e.label_, e._.is_negated) for e in self.co(frase).ents]
            self.assertEqual(a, b, frase)

    # Regresión de ConText (frases de la auditoría del 07/10/2026)
    def test_context_regresion(self):
        casos = [("Niega ansiedad.", "is_negated"), ("Antecedentes de ansiedad.", "is_historical"),
                 ("Madre con ansiedad.", "is_family")]
        for obj in (self.core, self.py):
            for frase, attr in casos:
                ents = [e for e in obj(frase).ents if e.label_ == "Ansiedad"]
                self.assertTrue(ents, frase)
                self.assertTrue(getattr(ents[0]._, attr), f"{frase}: {attr}")
        ents = [e for e in self.py("Paciente bajoneado.").ents]
        self.assertEqual([(e.label_, e._.is_negated) for e in ents], [("Animodeprimido", False)])


class TestLexico(unittest.TestCase):
    # R3: unicidad dentro de cada carpeta (Core y PY). CO es la base histórica: se conserva tal cual
    # y se fijan sus 3 repeticiones conocidas para detectar cualquier cambio.
    def test_sin_reglas_repetidas(self):
        for layer in ("Concept_Core", "Concept_PY"):
            self.assertEqual(ML.duplicados(layer), {}, layer)

    def test_co_conserva_sus_repeticiones_historicas(self):
        conocidas = {("Ansiedad", "Compulsiones|LIT:toc"), ("Ansiedad", "Obsesiones|LIT:toc"),
                     ("Depresion", 'SueoHipersomnio|[{"LOWER": {"IN": ["hipersomnia", "hipersomnio"]}}]')}
        self.assertEqual(set(ML.duplicados("Concept_CO")), conocidas)

    # R3: conceptos compartidos entre Ansiedad/ y Depresion/ sincronizados
    def test_conceptos_compartidos_sincronizados(self):
        for layer in ML.LAYERS:
            self.assertEqual(ML.compartidos_desincronizados(layer), [], layer)

    # R5: manifiesto congelado
    def test_manifiesto_coincide(self):
        self.assertEqual(ML.verificar(), [])

    def test_reglas_tienen_categoria(self):
        for layer in ML.LAYERS:
            for _, p in ML.json_files(layer):
                for r in ML.rules_of(p):
                    self.assertIn("category", r, p.name)


if __name__ == "__main__":
    unittest.main()

"""Pruebas unitarias puras del motor NIST (modulo critico #4 del E2,
seccion 2.6). Cubre el calculo de madurez (RF-15) y la integridad del
catalogo de preguntas (RF-14: 25 preguntas, 5 por funcion)."""

from app.models.nist_assessment import NistFunction
from app.services.nist_engine import QUESTION_CATALOG, average_score, maturity_percent


def test_average_score_empty_list_is_none():
    assert average_score([]) is None


def test_average_score_single_value():
    assert average_score([4]) == 4.0


def test_average_score_computes_mean():
    assert average_score([1, 2, 3, 4, 5]) == 3.0


def test_maturity_percent_empty_list_is_none():
    assert maturity_percent([]) is None


def test_maturity_percent_max_score_is_100():
    assert maturity_percent([5, 5, 5]) == 100.0


def test_maturity_percent_min_score_is_20_percent():
    assert maturity_percent([1, 1, 1]) == 20.0


def test_maturity_percent_rounds_to_one_decimal():
    # promedio = 10/3 = 3.3333... -> (3.3333/5)*100 = 66.666... -> 66.7
    assert maturity_percent([3, 3, 4]) == 66.7


def test_maturity_percent_unanswered_questions_excluded_by_caller():
    # El motor recibe solo las puntuaciones ya respondidas (los None se
    # filtran antes de llamar, tal como hace el router de NIST); con una
    # sola respuesta de 3 el porcentaje debe ser el de esa unica respuesta.
    assert maturity_percent([3]) == 60.0


def test_question_catalog_has_25_questions():
    assert len(QUESTION_CATALOG) == 25


def test_question_catalog_has_5_questions_per_function():
    for function in NistFunction:
        count = sum(1 for q in QUESTION_CATALOG if q["function"] == function)
        assert count == 5, f"{function} tiene {count} preguntas, se esperaban 5"


def test_question_catalog_codes_are_unique():
    codes = [q["code"] for q in QUESTION_CATALOG]
    assert len(codes) == len(set(codes))

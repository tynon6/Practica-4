"""Practica 1: operaciones sobre cadenas y lenguajes."""
import pytest

from lenguajes import (LIMITE_CADENAS, cerradura_kleene, cerradura_positiva, normalizar_alfabeto,
                       numero_cadenas, potencia, prefijos, reflexion, subcadenas, sufijos)


def test_cadena_vacia():
    assert prefijos("") == [""]
    assert sufijos("") == [""]
    assert subcadenas("") == [""]


def test_prefijos_sufijos_longitud_uno():
    assert prefijos("a") == ["", "a"]
    assert sufijos("a") == ["a", ""]


def test_numero_de_prefijos_y_subcadenas():
    w = "abcd"
    assert len(prefijos(w)) == len(w) + 1
    assert len(subcadenas(w)) == len(w) * (len(w) + 1) // 2 + 1  # todos distintos + lambda
    assert len(subcadenas("aaa")) == 4  # λ, a, aa, aaa


def test_alfabeto_de_un_simbolo():
    assert cerradura_kleene("a", 3) == ["", "a", "aa", "aaa"]
    assert cerradura_positiva("a", 3) == ["a", "aa", "aaa"]


def test_kleene_contra_positiva_longitud_cero():
    assert cerradura_kleene("ab", 0) == [""]
    assert cerradura_positiva("ab", 0) == []


def test_conteo_y_limite():
    assert len(cerradura_kleene("ab", 3)) == numero_cadenas(2, 3) == 15
    with pytest.raises(ValueError):
        cerradura_kleene("abc", 12)  # 797 161 > 200 000
    assert numero_cadenas(2, 16) < LIMITE_CADENAS < numero_cadenas(2, 17)


def test_otras_operaciones():
    assert potencia("ab", 0) == ""
    assert potencia("ab", 2) == "abab"
    assert reflexion("abc") == "cba"
    assert normalizar_alfabeto("b,a,a") == ["a", "b"]

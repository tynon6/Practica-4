"""Practica 4, Ejercicio 4: congruencia entre el automata y re.fullmatch.

Para cada validador se generan al menos 500 cadenas (ver
validadores.generar_casos) y se exige que el AFD minimo obtenido de la
expresion y re.fullmatch con la expresion escrita a mano coincidan en todas.
"""
import re

import pytest

import validadores as V

CLAVES = list(V.VALIDADORES)


@pytest.mark.parametrize("clave", CLAVES)
def test_congruencia_afd_contra_re(clave):
    v = V.VALIDADORES[clave]
    casos = V.generar_casos(clave)
    assert len(casos) >= 500
    discrepancias = [c for c in casos if v.valida(c) != v.valida_re(c)]
    assert discrepancias == []
    validas = sum(v.valida_re(c) for c in casos)
    assert validas >= 100 and len(casos) - validas >= 100  # ambos tipos bien representados


@pytest.mark.parametrize("clave", CLAVES)
def test_traduccion_automatica_coincide(clave):
    automatica = re.compile(V.traduccion_automatica(clave))
    v = V.VALIDADORES[clave]
    for c in V.generar_casos(clave):
        assert (automatica.fullmatch(c) is not None) == v.valida(c)


@pytest.mark.parametrize("clave", CLAVES)
def test_ejemplos_documentados(clave):
    v = V.VALIDADORES[clave]
    assert all(v.valida(c) for c in v.validos)
    assert not any(v.valida(c) for c in v.invalidos)


def test_minimizacion_reduce_estados():
    for clave in CLAVES:
        p = V.construir(clave)
        assert len(p.minimo.estados) <= len(p.afd.estados) + 1  # +1 por el posible estado trampa

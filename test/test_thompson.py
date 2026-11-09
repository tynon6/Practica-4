"""Practica 4, Ejercicio 2: de expresion regular a AFD minimo.

Para cada caso de casos/practica4/ejercicios_er.json se comprueba que los
cuatro automatas (AFN-λ, AFN, AFD y AFD minimo) aceptan exactamente las mismas
cadenas que re.fullmatch con la traduccion de la expresion, sobre todas las
cadenas del alfabeto hasta LONGITUD.
"""
import json
import re
from pathlib import Path

import pytest

import conversiones as cv
import expresiones as er
from thompson import pipeline

RAIZ = Path(__file__).resolve().parent.parent
DATOS = json.loads((RAIZ / "casos/practica4/ejercicios_er.json").read_text(encoding="utf-8"))
CASOS = [c for c in DATOS["casos"] if c.get("expresion")]
LONGITUD = 8  # con |Σ| = 2 son 511 cadenas, suficiente para recorrer cada ciclo de los AFD minimos


@pytest.mark.parametrize("caso", CASOS, ids=[f"L{c['lista']}-{c['ejercicio']}" for c in CASOS])
def test_caso_de_la_lista(caso):
    p = pipeline(caso["expresion"], DATOS.get("clases") or None, set(caso["alfabeto"]))
    patron = re.compile(er.a_python(p.arbol))
    for w in cv.todas_las_cadenas(caso["alfabeto"], LONGITUD):
        esperado = patron.fullmatch(w) is not None
        assert p.thompson.afn_lambda.acepta(w) == esperado, w
        assert p.afn.acepta(w) == esperado, w
        assert p.acepta(w) == esperado, w
    for w in caso["aceptadas"]:
        assert p.acepta(w), w
    for w in caso["rechazadas"]:
        assert not p.acepta(w), w
    assert len(p.minimo.estados) <= len(cv.completar(p.afd).estados)


def test_pasos_de_thompson():
    p = pipeline("(a+b)*abb")
    reglas = [paso.regla.split(":")[0] for paso in p.thompson.pasos]
    assert reglas.count("Caso basico") == 5
    assert "Union" in reglas and "Cerradura" in reglas and "Concatenacion" in reglas
    for paso in p.thompson.pasos:      # cada parcial: un inicial y un final
        assert len(paso.automata.finales) == 1
    assert len(p.minimo.estados) == 4  # el clasico AFD minimo de (a+b)*abb


def test_lenguaje_vacio_y_lambda():
    assert not pipeline("∅", alfabeto={"a"}).acepta("")
    assert pipeline("λ", alfabeto={"a"}).acepta("")
    assert not pipeline("λ", alfabeto={"a"}).acepta("a")

"""Practica 4, Ejercicio 3: de AFD a expresion regular por eliminacion de estados."""
import random

import pytest

import conversiones as cv
from automata import Automata
from eliminacion_estados import a_expresion, eliminar_estados
from thompson import pipeline


def afd_aleatorio(rng, n):
    estados = [f"q{i}" for i in range(n)]
    a = Automata(estados, ["a", "b"], "q0", {q for q in estados if rng.random() < 0.4} or {"q0"})
    for q in estados:
        for s in "ab":
            a.agregar_transicion(q, s, rng.choice(estados))
    return a


@pytest.mark.parametrize("semilla", range(15))
def test_ida_y_vuelta(semilla):
    """AFD -> ER -> AFD minimo debe ser equivalente al original."""
    rng = random.Random(semilla)
    original = afd_aleatorio(rng, rng.randint(1, 5))
    expresion = a_expresion(original)
    reconstruido = pipeline(expresion, alfabeto={"a", "b"}).minimo
    iguales, detalle, contraejemplo = cv.equivalentes(original, reconstruido)
    assert iguales, (expresion, detalle, contraejemplo)


def test_detecta_no_determinismo(afn_termina_ab):
    with pytest.raises(ValueError, match="estado 0"):
        eliminar_estados(afn_termina_ab)


def test_pasos(afd_pares_a):
    expr, pasos = eliminar_estados(afd_pares_a)
    assert len(pasos) == len(afd_pares_a.estados) + 1
    assert pasos[-1].estados == ["I", "F"]

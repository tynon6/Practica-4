"""Practicas 2 y 3: simulacion, cerradura lambda y la cadena de conversiones."""

import conversiones as cv
from automata import Automata

LONGITUD = 7  # 2^0 + ... + 2^7 = 255 cadenas: cubre todos los ciclos de estos automatas


def test_afd_acepta_y_rechaza(afd_pares_a):
    assert afd_pares_a.simular_afd("abab")[0]
    assert not afd_pares_a.simular_afd("ab")[0]
    assert afd_pares_a.simular_afd("")[0]


def test_afnd_lambda_requiere_cerradura(afn_lambda_anexo):
    assert cv.cerradura_lambda(afn_lambda_anexo, "q0") == {"q0", "q1"}
    aceptada, pasos = cv.simular_afn(afn_lambda_anexo, "bb")
    assert aceptada  # solo se acepta gracias a la transicion lambda q0 -> q1
    assert pasos[-1]["despues"] == {"q0", "q1"}


def test_tipo_y_determinismo(afd_pares_a, afn_termina_ab):
    assert afd_pares_a.tipo() == "AFD"
    assert afn_termina_ab.tipo() == "AFND-lambda"
    assert afn_termina_ab.motivo_no_determinista() == ("0", "")


def test_cadena_completa_preserva_el_lenguaje(afn_termina_ab):
    afn, reg = cv.eliminar_lambda(afn_termina_ab)
    assert not afn.tiene_lambda()
    afd, tabla = cv.subconjuntos(afn)
    assert afd.es_determinista()
    minimo, reg_min = cv.minimizar(afd)
    assert len(minimo.estados) <= len(cv.completar(afd).estados)
    for w in cv.todas_las_cadenas("ab", LONGITUD):
        esperado = w.endswith("ab")
        assert afn_termina_ab.acepta(w) == afn.acepta(w) == afd.acepta(w) == minimo.acepta(w) == esperado


def test_minimizacion_conocida():
    # Seis estados que en realidad distinguen solo "termina en a" (minimo: 2 estados).
    a = Automata(list("ABCDEF"), ["a", "b"], "A", {"B", "D", "F"})
    for o, s, d in [("A", "a", "B"), ("A", "b", "C"), ("B", "a", "D"), ("B", "b", "C"),
                    ("C", "a", "F"), ("C", "b", "E"), ("D", "a", "B"), ("D", "b", "E"),
                    ("E", "a", "F"), ("E", "b", "C"), ("F", "a", "D"), ("F", "b", "C")]:
        a.agregar_transicion(o, s, d)
    minimo, reg = cv.minimizar(a)
    assert len(minimo.estados) == 2
    assert reg["rondas"][0]


def test_equivalencia(afd_pares_a):
    otro = Automata(["x", "y", "z"], ["a", "b"], "x", {"x", "z"},
                    {("x", "a"): {"y"}, ("x", "b"): {"z"}, ("y", "a"): {"z"}, ("y", "b"): {"y"},
                     ("z", "a"): {"y"}, ("z", "b"): {"x"}})
    iguales, _, _ = cv.equivalentes(afd_pares_a, otro)
    assert iguales
    distinto = afd_pares_a.copia()
    distinto.finales = {"i"}
    iguales, _, contraejemplo = cv.equivalentes(afd_pares_a, distinto)
    assert not iguales and contraejemplo == ""


def test_validacion_por_lote(afd_pares_a):
    res = cv.validar_lote(afd_pares_a, ["", "a", "aa"])
    assert res == [("", True), ("a", False), ("aa", True)]

"""Practica 4, Ejercicio 2: analisis de expresiones con la notacion del curso."""
import pytest

import expresiones as er


@pytest.mark.parametrize("texto, esperado", [
    ("a+bc*", "a + bc*"),          # * > concatenacion > +
    ("(a+b)c", "(a + b)c"),
    ("((a))", "a"),
    ("a**", "a**"),
    ("λ+∅", "λ + ∅"),
    ("[D][D]", "[D][D]"),
    ("\\+52", "\\+52"),
])
def test_precedencia_y_reimpresion(texto, esperado):
    assert er.a_texto(er.analizar(texto)) == esperado


def test_arbol_respeta_precedencia():
    arbol = er.analizar("a+bc*")
    assert isinstance(arbol, er.Union)
    assert isinstance(arbol.der, er.Concat)
    assert isinstance(arbol.der.der, er.Estrella)


@pytest.mark.parametrize("texto, posicion", [
    ("", 0),          # vacia
    ("+a", 0),        # + sin operando izquierdo
    ("a+", 2),        # falta operando al final
    ("*a", 0),        # * sin operando
    ("(a+b", 0),      # parentesis sin cerrar: se senala el '('
    ("a+b)", 3),      # ')' sin abrir
    ("()", 0),        # parentesis vacios
    ("a+(+b)", 3),    # + sin operando dentro del parentesis
    ("[X]a", 0),      # clase no declarada
    ("ab\\", 2),      # escape al final
])
def test_errores_con_posicion(texto, posicion):
    with pytest.raises(er.ErrorExpresion) as info:
        er.analizar(texto)
    assert info.value.posicion == posicion
    assert "^" in info.value.señalar()


def test_clases_declaradas():
    clases = er.leer_clases("V = a + e + i + o + u\nH = 0-9a-f")
    assert clases["V"] == "aeiou"
    assert len(clases["H"]) == 16
    arbol = er.analizar("[V]*", clases)
    assert arbol.simbolos() == set("aeiou")


def test_leyes_de_los_constructores():
    a = er.Simbolo("a")
    assert er.union(a, er.Vacio()) == a
    assert er.concat(a, er.Lambda()) == a
    assert er.concat(a, er.Vacio()) == er.Vacio()
    assert er.estrella(er.Vacio()) == er.Lambda()
    assert er.estrella(er.estrella(a)) == er.estrella(a)

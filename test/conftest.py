"""Automatas de uso comun en varias pruebas."""
import pytest

from automata import Automata


@pytest.fixture
def afd_pares_a():
    """AFD sobre {a,b}: numero par de a."""
    return Automata(["p", "i"], ["a", "b"], "p", {"p"},
                    {("p", "a"): {"i"}, ("p", "b"): {"p"}, ("i", "a"): {"p"}, ("i", "b"): {"i"}})


@pytest.fixture
def afn_lambda_anexo():
    """El AFND-lambda del Anexo 3 de la Practica 2."""
    return Automata(["q0", "q1"], ["a", "b"], "q0", {"q1"},
                    {("q0", "a"): {"q1"}, ("q0", "b"): {"q0"}, ("q0", ""): {"q1"}})


@pytest.fixture
def afn_termina_ab():
    """AFN-lambda: (a+b)*ab, con una transicion lambda superflua."""
    a = Automata(["0", "1", "2", "3"], ["a", "b"], "0", {"3"})
    for o, s, d in [("0", "a", "0"), ("0", "b", "0"), ("0", "", "1"),
                    ("1", "a", "2"), ("2", "b", "3")]:
        a.agregar_transicion(o, s, d)
    return a

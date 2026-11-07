"""De expresion regular a automata (Practica 4, Ejercicio 2).

Primera parte del teorema de Kleene: para toda expresion regular r existe un
AFN-lambda que reconoce L(r). La demostracion es constructiva y es la que se
programa aqui (construccion de Thompson):

    casos basicos   ∅ : q0   q1 (sin transiciones)      λ : q0 -λ-> q1
                    a : q0 -a-> q1
    union  r + s    nuevo inicio -λ-> inicios de r y s; finales de r y s -λ-> nuevo final
    concat rs       final de r -λ-> inicio de s
    cerradura r*    nuevo inicio -λ-> inicio de r y -λ-> nuevo final;
                    final de r -λ-> inicio de r y -λ-> nuevo final

Cada automata parcial tiene exactamente un estado inicial y uno final, y se
guarda en `pasos` para mostrarse en la interfaz.

Despues, `pipeline` aplica los algoritmos de la Practica 3:
AFN-lambda -> AFN -> AFD (subconjuntos) -> AFD minimo.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import conversiones as cv
import expresiones as er
from automata import LAMBDA, Automata


@dataclass
class Fragmento:
    inicio: str
    fin: str
    estados: list[str]
    transiciones: list[tuple[str, str, str]]


@dataclass
class Paso:
    subexpresion: str
    regla: str
    automata: Automata


@dataclass
class ResultadoThompson:
    arbol: er.Nodo
    afn_lambda: Automata
    pasos: list[Paso] = field(default_factory=list)


class _Constructor:
    def __init__(self, alfabeto: set[str]):
        self.contador = 0
        self.alfabeto = alfabeto
        self.pasos: list[Paso] = []

    def nuevo(self) -> str:
        q = f"q{self.contador}"
        self.contador += 1
        return q

    def registrar(self, nodo: er.Nodo, regla: str, f: Fragmento) -> Fragmento:
        a = Automata(list(f.estados), sorted(self.alfabeto), f.inicio, {f.fin}, {})
        for o, s, d in f.transiciones:
            a.agregar_transicion(o, s, d)
        a.alfabeto = sorted(self.alfabeto)
        self.pasos.append(Paso(er.a_texto(nodo), regla, a))
        return f

    def construir(self, n: er.Nodo) -> Fragmento:
        if isinstance(n, er.Simbolo):
            i, f = self.nuevo(), self.nuevo()
            return self.registrar(n, f"Caso basico: un simbolo '{n.c}'.",
                                  Fragmento(i, f, [i, f], [(i, n.c, f)]))
        if isinstance(n, er.Clase):
            # Abreviatura de c1 + c2 + ... + ck: se arma directamente con
            # dos estados y una transicion por simbolo (mismo lenguaje).
            i, f = self.nuevo(), self.nuevo()
            trs = [(i, c, f) for c in sorted(n.caracteres)]
            return self.registrar(n, f"Clase [{n.nombre}]: union de {len(trs)} casos basicos.",
                                  Fragmento(i, f, [i, f], trs))
        if isinstance(n, er.Lambda):
            i, f = self.nuevo(), self.nuevo()
            return self.registrar(n, "Caso basico: λ.", Fragmento(i, f, [i, f], [(i, LAMBDA, f)]))
        if isinstance(n, er.Vacio):
            i, f = self.nuevo(), self.nuevo()
            return self.registrar(n, "Caso basico: ∅ (sin transiciones).", Fragmento(i, f, [i, f], []))
        if isinstance(n, er.Union):
            a, b = self.construir(n.izq), self.construir(n.der)
            i, f = self.nuevo(), self.nuevo()
            trs = a.transiciones + b.transiciones + [
                (i, LAMBDA, a.inicio), (i, LAMBDA, b.inicio), (a.fin, LAMBDA, f), (b.fin, LAMBDA, f)]
            return self.registrar(n, "Union: nuevo inicial y nuevo final unidos con λ.",
                                  Fragmento(i, f, [i] + a.estados + b.estados + [f], trs))
        if isinstance(n, er.Concat):
            a, b = self.construir(n.izq), self.construir(n.der)
            trs = a.transiciones + b.transiciones + [(a.fin, LAMBDA, b.inicio)]
            return self.registrar(n, "Concatenacion: el final del primero va con λ al inicio del segundo.",
                                  Fragmento(a.inicio, b.fin, a.estados + b.estados, trs))
        if isinstance(n, er.Estrella):
            a = self.construir(n.r)
            i, f = self.nuevo(), self.nuevo()
            trs = a.transiciones + [(i, LAMBDA, a.inicio), (i, LAMBDA, f),
                                    (a.fin, LAMBDA, a.inicio), (a.fin, LAMBDA, f)]
            return self.registrar(n, "Cerradura: λ para saltar el automata y λ para repetirlo.",
                                  Fragmento(i, f, [i] + a.estados + [f], trs))
        raise TypeError(n)


def thompson(arbol: er.Nodo, alfabeto: set[str] | None = None) -> ResultadoThompson:
    alfabeto = set(alfabeto or ()) | arbol.simbolos()
    c = _Constructor(alfabeto)
    c.construir(arbol)
    return ResultadoThompson(arbol, c.pasos[-1].automata.copia("AFN-λ"), c.pasos)


@dataclass
class Pipeline:
    expresion: str
    arbol: er.Nodo
    thompson: ResultadoThompson
    afn: Automata
    registro_lambda: dict
    afd: Automata
    tabla_subconjuntos: list[dict]
    minimo: Automata
    registro_minimo: dict

    def acepta(self, cadena: str) -> bool:
        """Valida con el AFD minimo. Un simbolo fuera del alfabeto se rechaza."""
        if any(c not in self.minimo.alfabeto for c in cadena):
            return False
        return self.minimo.simular_afd(cadena)[0]

    def resumen(self) -> list[tuple[str, int, int]]:
        """(etapa, estados, transiciones) de cada automata de la cadena."""
        return [("AFN-λ (Thompson)", len(self.thompson.afn_lambda.estados),
                 self.thompson.afn_lambda.numero_transiciones()),
                ("AFN sin λ", len(self.afn.estados), self.afn.numero_transiciones()),
                ("AFD (subconjuntos)", len(self.afd.estados), self.afd.numero_transiciones()),
                ("AFD minimo", len(self.minimo.estados), self.minimo.numero_transiciones())]


def pipeline(expresion: str, clases: dict[str, str] | None = None,
             alfabeto: set[str] | None = None) -> Pipeline:
    """Expresion (texto) -> arbol -> AFN-λ -> AFN -> AFD -> AFD minimo."""
    arbol = er.analizar(expresion, clases)
    t = thompson(arbol, alfabeto)
    afn, reg_l = cv.eliminar_lambda(t.afn_lambda)
    afn, _ = cv.eliminar_inaccesibles(afn)
    afn.nombre = "AFN sin λ"
    afd, tabla = cv.subconjuntos(afn)
    afd.nombre = "AFD"
    minimo, reg_m = cv.minimizar(afd)
    minimo.nombre = "AFD minimo"
    return Pipeline(expresion, arbol, t, afn, reg_l, afd, tabla, minimo, reg_m)

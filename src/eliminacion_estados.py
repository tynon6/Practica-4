"""De automata a expresion regular (Practica 4, Ejercicio 3).

Segunda parte del teorema de Kleene, por el metodo de eliminacion de estados:

1. Se verifica que el automata sea un AFD (si no, se informa estado y simbolo).
2. Se construye el automata generalizado (AFG): un nuevo inicial `I` con λ
   hacia el inicial original y un nuevo final `F` al que llegan con λ todos
   los de aceptacion. Las etiquetas de las aristas son expresiones regulares.
3. Se elimina un estado k a la vez. Para cada par (i, j) con i -> k -> j:
        R(i,j) := R(i,j) + R(i,k) R(k,k)* R(k,j)
4. Al final queda solo I -> F y su etiqueta es la expresion buscada.

Las etiquetas se manejan como arboles de `expresiones`, cuyos constructores
aplican las leyes r+∅=r, rλ=r, r∅=∅, ∅*=λ, (r*)*=r*, con lo que la
expresion resultante sale ya parcialmente simplificada.
"""

from __future__ import annotations

from dataclasses import dataclass

import expresiones as er
from automata import LAMBDA, LAMBDA_VISIBLE, Automata

INICIO, FIN = "I", "F"


@dataclass
class PasoEliminacion:
    eliminado: str | None
    aristas: dict[tuple[str, str], er.Nodo]
    estados: list[str]

    def tabla(self) -> list[tuple[str, str, str]]:
        return [(i, j, er.a_texto(r)) for (i, j), r in self.aristas.items()]


def verificar_afd(automata: Automata) -> None:
    motivo = automata.motivo_no_determinista()
    if motivo:
        estado, simbolo = motivo
        if simbolo == LAMBDA:
            raise ValueError(f"No es determinista: el estado {estado} tiene una transicion {LAMBDA_VISIBLE}.")
        destinos = ", ".join(sorted(automata.destinos(estado, simbolo)))
        raise ValueError(f"No es determinista: desde el estado {estado} con el simbolo "
                         f"'{simbolo}' hay varios destinos ({destinos}).")


def automata_generalizado(automata: Automata) -> tuple[list[str], dict[tuple[str, str], er.Nodo]]:
    inicio, fin = INICIO, FIN
    while inicio in automata.estados:
        inicio += "'"
    while fin in automata.estados:
        fin += "'"
    aristas: dict[tuple[str, str], er.Nodo] = {(inicio, automata.inicial): er.Lambda()}
    for (o, s), destinos in automata.transiciones.items():
        etiqueta = er.Lambda() if s == LAMBDA else er.Simbolo(s)
        for d in destinos:
            aristas[(o, d)] = er.union(aristas.get((o, d), er.Vacio()), etiqueta)
    for q in automata.finales:
        aristas[(q, fin)] = er.union(aristas.get((q, fin), er.Vacio()), er.Lambda())
    return [inicio] + list(automata.estados) + [fin], aristas


def eliminar_estados(automata: Automata, orden: list[str] | None = None,
                     exigir_afd: bool = True) -> tuple[er.Nodo, list[PasoEliminacion]]:
    """Devuelve (expresion, pasos). `orden` fija el orden de eliminacion."""
    if exigir_afd:
        verificar_afd(automata)
    estados, aristas = automata_generalizado(automata)
    inicio, fin = estados[0], estados[-1]
    pendientes = list(orden) if orden else list(automata.estados)
    pasos = [PasoEliminacion(None, dict(aristas), list(estados))]
    for k in pendientes:
        bucle = aristas.get((k, k), er.Vacio())
        entradas = [(i, r) for (i, j), r in aristas.items() if j == k and i != k]
        salidas = [(j, r) for (i, j), r in aristas.items() if i == k and j != k]
        for i, rik in entradas:
            for j, rkj in salidas:
                atajo = er.concat(er.concat(rik, er.estrella(bucle)), rkj)
                aristas[(i, j)] = er.union(aristas.get((i, j), er.Vacio()), atajo)
        aristas = {(i, j): r for (i, j), r in aristas.items()
                   if i != k and j != k and not isinstance(r, er.Vacio)}
        estados.remove(k)
        pasos.append(PasoEliminacion(k, dict(aristas), list(estados)))
    return aristas.get((inicio, fin), er.Vacio()), pasos


def a_expresion(automata: Automata) -> str:
    return er.a_texto(eliminar_estados(automata)[0])

"""Conversión de un AFD a expresión regular mediante eliminación de estados."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Automata:
    estados: tuple[str, ...]
    alfabeto: tuple[str, ...]
    inicial: str
    finales: frozenset[str]
    transiciones: dict[tuple[str, str], frozenset[str]]


@dataclass(frozen=True)
class Expresion:
    tipo: str
    valor: str = ""
    partes: tuple[Expresion, ...] = ()


EPSILON = Expresion("epsilon")


def leer_jff(ruta: str | Path) -> Automata:
    """Lee estados y transiciones de un archivo .jff de JFLAP."""
    try:
        raiz = ET.parse(ruta).getroot()
    except (ET.ParseError, OSError) as error:
        raise ValueError(f"No se pudo leer el archivo .jff: {error}") from error
    elemento = raiz.find("automaton")
    if elemento is None:
        raise ValueError("El archivo no contiene un autómata de JFLAP.")

    estados: list[str] = []
    ids: dict[str, str] = {}
    iniciales: list[str] = []
    finales: set[str] = set()
    for estado in elemento.findall("state"):
        identificador = estado.get("id")
        nombre = estado.get("name")
        if identificador is None or nombre is None:
            raise ValueError("Hay un estado sin identificador o nombre.")
        estados.append(nombre)
        ids[identificador] = nombre
        if estado.find("initial") is not None:
            iniciales.append(nombre)
        if estado.find("final") is not None:
            finales.add(nombre)
    if len(iniciales) != 1:
        raise ValueError("El autómata debe tener exactamente un estado inicial.")

    transiciones: dict[tuple[str, str], set[str]] = {}
    alfabeto: list[str] = []
    for transicion in elemento.findall("transition"):
        origen_id = transicion.findtext("from", "")
        destino_id = transicion.findtext("to", "")
        if origen_id not in ids or destino_id not in ids:
            raise ValueError("Una transición apunta a un estado inexistente.")
        simbolo = (transicion.findtext("read") or "").strip()
        origen, destino = ids[origen_id], ids[destino_id]
        transiciones.setdefault((origen, simbolo), set()).add(destino)
        if simbolo and simbolo not in alfabeto:
            alfabeto.append(simbolo)
    return Automata(
        tuple(estados), tuple(alfabeto), iniciales[0], frozenset(finales),
        {par: frozenset(destinos) for par, destinos in transiciones.items()},
    )


def revisar_determinismo(automata: Automata) -> list[str]:
    """Devuelve los conflictos que impiden que el archivo represente un AFD."""
    problemas = []
    for (estado, simbolo), destinos in sorted(automata.transiciones.items()):
        if not simbolo:
            problemas.append(f"El estado {estado} tiene una transición λ.")
        if len(destinos) > 1:
            lectura = simbolo or "λ"
            problemas.append(
                f"El estado {estado}, con el símbolo {lectura}, tiene varios destinos: "
                f"{', '.join(sorted(destinos))}."
            )
    return problemas


def _unir(*expresiones: Expresion | None) -> Expresion | None:
    elementos: list[Expresion] = []
    for expresion in expresiones:
        if expresion is None:
            continue
        elementos.extend(expresion.partes if expresion.tipo == "union" else (expresion,))
    unicos = list(dict.fromkeys(elementos))
    if not unicos:
        return None
    if len(unicos) == 1:
        return unicos[0]
    return Expresion("union", partes=tuple(unicos))


def _concatenar(*expresiones: Expresion | None) -> Expresion | None:
    elementos: list[Expresion] = []
    for expresion in expresiones:
        if expresion is None:
            return None
        if expresion.tipo == "epsilon":
            continue
        elementos.extend(expresion.partes if expresion.tipo == "concat" else (expresion,))
    if not elementos:
        return EPSILON
    if len(elementos) == 1:
        return elementos[0]
    return Expresion("concat", partes=tuple(elementos))


def _estrella(expresion: Expresion | None) -> Expresion:
    if expresion is None or expresion.tipo == "epsilon":
        return EPSILON
    if expresion.tipo == "star":
        return expresion
    return Expresion("star", partes=(expresion,))


def _mostrar(expresion: Expresion | None, nivel: int = 0) -> str:
    if expresion is None:
        return "∅"
    if expresion.tipo == "epsilon":
        return "λ"
    if expresion.tipo == "simbolo":
        return expresion.valor
    if expresion.tipo == "union":
        prioridad = 1
        texto = " + ".join(_mostrar(parte, prioridad) for parte in expresion.partes)
    elif expresion.tipo == "concat":
        prioridad = 2
        texto = "".join(_mostrar(parte, prioridad) for parte in expresion.partes)
    else:
        prioridad = 3
        texto = _mostrar(expresion.partes[0], prioridad) + "*"
    return f"({texto})" if prioridad < nivel else texto


@dataclass(frozen=True)
class Paso:
    titulo: str
    estados: tuple[str, ...]
    matriz: tuple[tuple[str, ...], ...]


def convertir(automata: Automata) -> tuple[list[Paso], str]:
    """Calcula una expresión y conserva la matriz tras cada eliminación."""
    problemas = revisar_determinismo(automata)
    if problemas:
        raise ValueError("\n".join(problemas))

    inicio, fin = "⟨inicio⟩", "⟨fin⟩"
    estados = [inicio, *automata.estados, fin]
    arcos: dict[tuple[str, str], Expresion | None] = {}

    def agregar(origen: str, destino: str, expresion: Expresion | None) -> None:
        if expresion is not None:
            par = (origen, destino)
            arcos[par] = _unir(arcos.get(par), expresion)

    agregar(inicio, automata.inicial, EPSILON)
    for (origen, simbolo), destinos in automata.transiciones.items():
        for destino in destinos:
            agregar(origen, destino, Expresion("simbolo", valor=simbolo))
    for estado in automata.finales:
        agregar(estado, fin, EPSILON)

    pasos: list[Paso] = []

    def guardar(titulo: str, actuales: list[str]) -> None:
        matriz = tuple(
            tuple(_mostrar(arcos.get((origen, destino))) for destino in actuales)
            for origen in actuales
        )
        pasos.append(Paso(titulo, tuple(actuales), matriz))

    guardar("Autómata generalizado inicial", estados)
    for quitar in automata.estados:
        restantes = [estado for estado in estados if estado != quitar]
        bucle = _estrella(arcos.get((quitar, quitar)))
        for origen in restantes:
            hacia_quitar = arcos.get((origen, quitar))
            if hacia_quitar is None:
                continue
            for destino in restantes:
                desde_quitar = arcos.get((quitar, destino))
                if desde_quitar is None:
                    continue
                camino = _concatenar(hacia_quitar, bucle, desde_quitar)
                agregar(origen, destino, camino)
        for par in list(arcos):
            if quitar in par:
                del arcos[par]
        estados = restantes
        guardar(f"Se eliminó el estado {quitar}", estados)

    resultado = _mostrar(arcos.get((inicio, fin)))
    return pasos, resultado

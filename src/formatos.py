"""Lectura y escritura de automatas en .jff (JFLAP), .json y .xml (Practica 2).

Convencion: la transicion lambda se escribe como cadena vacia en los tres
formatos (<read/> en .jff, "" en .json y lee="" en .xml), igual que JFLAP.
Este modulo no depende de Flet.
"""

from __future__ import annotations

import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

from automata import LAMBDA, Automata


class ErrorFormato(ValueError):
    pass


# ------------------------------------------------------------------------ .jff
def leer_jff_texto(texto: str, nombre: str = "") -> Automata:
    try:
        raiz = ET.fromstring(texto.strip())
    except ET.ParseError as e:
        raise ErrorFormato(f"El archivo .jff no es XML valido: {e}") from e
    tipo = raiz.findtext("type", default="fa").strip()
    if tipo != "fa":
        raise ErrorFormato(f"Solo se admiten automatas finitos (type=fa); el archivo es '{tipo}'.")
    nodo = raiz.find("automaton")
    if nodo is None:
        nodo = raiz  # JFLAP 6 guarda los estados directamente bajo <structure>
    ids, estados, finales, inicial = {}, [], set(), None
    for e in nodo.iter("state"):
        id_ = e.get("id")
        nom = e.get("name") or f"q{id_}"
        ids[id_] = nom
        estados.append(nom)
        if e.find("initial") is not None:
            inicial = nom
        if e.find("final") is not None:
            finales.add(nom)
    if not estados:
        raise ErrorFormato("El archivo no contiene estados.")
    if inicial is None:
        raise ErrorFormato("El archivo no declara estado inicial (<initial/>).")
    automata = Automata(estados, [], inicial, finales, {}, nombre)
    auxiliares = 0
    for t in nodo.iter("transition"):
        try:
            origen, destino = ids[t.findtext("from").strip()], ids[t.findtext("to").strip()]
        except (KeyError, AttributeError) as e:
            raise ErrorFormato("Una transicion hace referencia a un estado inexistente.") from e
        lee = t.findtext("read") or ""
        if len(lee) <= 1:
            automata.agregar_transicion(origen, lee, destino)
        else:
            # JFLAP admite cadenas en las transiciones: se expanden en una
            # cadena de estados auxiliares, lo que preserva el lenguaje.
            actual = origen
            for i, simbolo in enumerate(lee):
                if i == len(lee) - 1:
                    siguiente = destino
                else:
                    siguiente = f"_aux{auxiliares}"
                    auxiliares += 1
                automata.agregar_transicion(actual, simbolo, siguiente)
                actual = siguiente
    return automata


def posiciones(automata: Automata, ancho: float = 600, alto: float = 400) -> dict[str, tuple[float, float]]:
    """Coloca los estados en circulo (para exportar a JFLAP y para dibujar)."""
    n = len(automata.estados)
    if n == 1:
        return {automata.estados[0]: (ancho / 2, alto / 2)}
    radio = min(ancho, alto) / 2 - 50
    cx, cy = ancho / 2, alto / 2
    return {q: (cx + radio * math.cos(math.pi + 2 * math.pi * i / n),
                cy + radio * math.sin(math.pi + 2 * math.pi * i / n))
            for i, q in enumerate(automata.estados)}


def escribir_jff_texto(automata: Automata) -> str:
    escala = max(600, 90 * len(automata.estados))
    pos = posiciones(automata, escala, escala * 0.7)
    raiz = ET.Element("structure")
    ET.SubElement(raiz, "type").text = "fa"
    nodo = ET.SubElement(raiz, "automaton")
    ids = {q: str(i) for i, q in enumerate(automata.estados)}
    for q in automata.estados:
        e = ET.SubElement(nodo, "state", id=ids[q], name=q)
        ET.SubElement(e, "x").text = f"{pos[q][0]:.1f}"
        ET.SubElement(e, "y").text = f"{pos[q][1]:.1f}"
        if q == automata.inicial:
            ET.SubElement(e, "initial")
        if q in automata.finales:
            ET.SubElement(e, "final")
    for o, s, d in automata.lista_transiciones():
        t = ET.SubElement(nodo, "transition")
        ET.SubElement(t, "from").text = ids[o]
        ET.SubElement(t, "to").text = ids[d]
        lee = ET.SubElement(t, "read")
        if s != LAMBDA:
            lee.text = s
    ET.indent(raiz, space="  ")
    return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + ET.tostring(raiz, encoding="unicode") + "\n"


# ----------------------------------------------------------------------- .json
def a_diccionario(automata: Automata) -> dict:
    agrupadas = []
    for (o, s), ds in sorted(automata.transiciones.items(),
                             key=lambda kv: (automata.estados.index(kv[0][0]), kv[0][1])):
        agrupadas.append({"desde": o, "lee": s,
                          "hacia": sorted(ds, key=automata.estados.index)})
    return {"tipo": automata.tipo(), "alfabeto": list(automata.alfabeto),
            "estados": list(automata.estados), "inicial": automata.inicial,
            "aceptacion": [q for q in automata.estados if q in automata.finales],
            "transiciones": agrupadas}


def leer_json_texto(texto: str, nombre: str = "") -> Automata:
    try:
        datos = json.loads(texto)
        automata = Automata(datos["estados"], datos.get("alfabeto", []), datos["inicial"],
                            set(datos.get("aceptacion", [])), {}, nombre)
        for t in datos.get("transiciones", []):
            hacia = t["hacia"] if isinstance(t["hacia"], list) else [t["hacia"]]
            for d in hacia:
                automata.agregar_transicion(t["desde"], t.get("lee", ""), d)
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise ErrorFormato(f"El archivo .json no tiene el esquema esperado: {e}") from e
    return automata


def escribir_json_texto(automata: Automata) -> str:
    return json.dumps(a_diccionario(automata), ensure_ascii=False, indent=2) + "\n"


# ------------------------------------------------------------------------ .xml
def leer_xml_texto(texto: str, nombre: str = "") -> Automata:
    try:
        raiz = ET.fromstring(texto.strip())
    except ET.ParseError as e:
        raise ErrorFormato(f"El archivo .xml no es valido: {e}") from e
    if raiz.tag != "automata":
        raise ErrorFormato("La raiz del .xml debe ser <automata>.")
    alfabeto = [s.text or "" for s in raiz.iter("simbolo")]
    estados, inicial, finales = [], None, set()
    for e in raiz.iter("estado"):
        nom = e.get("nombre")
        estados.append(nom)
        if e.get("inicial") == "true":
            inicial = nom
        if e.get("aceptacion") == "true":
            finales.add(nom)
    if inicial is None:
        raise ErrorFormato("Ningun estado tiene inicial=\"true\".")
    automata = Automata(estados, alfabeto, inicial, finales, {}, nombre)
    for t in raiz.iter("transicion"):
        automata.agregar_transicion(t.get("desde"), t.get("lee", ""), t.get("hacia"))
    return automata


def escribir_xml_texto(automata: Automata) -> str:
    raiz = ET.Element("automata", tipo=automata.tipo())
    alf = ET.SubElement(raiz, "alfabeto")
    for s in automata.alfabeto:
        ET.SubElement(alf, "simbolo").text = s
    est = ET.SubElement(raiz, "estados")
    for q in automata.estados:
        atributos = {"nombre": q}
        if q == automata.inicial:
            atributos["inicial"] = "true"
        if q in automata.finales:
            atributos["aceptacion"] = "true"
        ET.SubElement(est, "estado", atributos)
    trs = ET.SubElement(raiz, "transiciones")
    for o, s, d in automata.lista_transiciones():
        ET.SubElement(trs, "transicion", desde=o, lee=s, hacia=d)
    ET.indent(raiz, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(raiz, encoding="unicode") + "\n"


# --------------------------------------------------------------- por extension
LECTORES = {".jff": leer_jff_texto, ".json": leer_json_texto, ".xml": leer_xml_texto}
ESCRITORES = {".jff": escribir_jff_texto, ".json": escribir_json_texto, ".xml": escribir_xml_texto}


def detectar_formato(texto: str) -> str:
    t = texto.lstrip()
    if t.startswith("{"):
        return ".json"
    return ".jff" if "<structure" in t else ".xml"


def leer_texto(texto: str, extension: str | None = None, nombre: str = "") -> Automata:
    extension = extension or detectar_formato(texto)
    if extension not in LECTORES:
        raise ErrorFormato(f"Extension no admitida: {extension}. Use .jff, .json o .xml.")
    return LECTORES[extension](texto, nombre)


def leer_archivo(ruta) -> Automata:
    ruta = Path(ruta)
    if not ruta.exists():
        raise ErrorFormato(f"No existe el archivo {ruta}.")
    return leer_texto(ruta.read_text(encoding="utf-8"), ruta.suffix.lower(), ruta.stem)


def escribir_archivo(automata: Automata, ruta) -> Path:
    ruta = Path(ruta)
    if ruta.suffix.lower() not in ESCRITORES:
        raise ErrorFormato(f"Extension no admitida: {ruta.suffix}.")
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(ESCRITORES[ruta.suffix.lower()](automata), encoding="utf-8")
    return ruta

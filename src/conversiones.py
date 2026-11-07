"""Algoritmos de la Practica 3, programados en Python puro.

    AFN-lambda --eliminar_lambda--> AFN --subconjuntos--> AFD --minimizar--> AFD minimo

Cada funcion devuelve, ademas del automata resultante, un registro de pasos
que la interfaz muestra paso a paso. Nada de este modulo depende de Flet.
"""

from __future__ import annotations

from collections import deque
from itertools import product

from automata import LAMBDA, LAMBDA_VISIBLE, Automata

TRAMPA = "∅"


# ------------------------------------------------------------- cerradura lambda
def cerradura_lambda(automata: Automata, estados) -> frozenset[str]:
    """Conjunto de estados alcanzables desde `estados` usando solo transiciones lambda."""
    if isinstance(estados, str):
        estados = {estados}
    resultado = set(estados)
    pila = list(estados)
    while pila:
        q = pila.pop()
        for d in automata.destinos(q, LAMBDA):
            if d not in resultado:
                resultado.add(d)
                pila.append(d)
    return frozenset(resultado)


def cerraduras(automata: Automata) -> dict[str, frozenset[str]]:
    return {q: cerradura_lambda(automata, q) for q in automata.estados}


def mover(automata: Automata, estados, simbolo: str) -> set[str]:
    resultado = set()
    for q in estados:
        resultado |= automata.destinos(q, simbolo)
    return resultado


def formato_conjunto(estados) -> str:
    return "{" + ", ".join(sorted(estados)) + "}" if estados else "∅"


# ----------------------------------------------------- simulacion directa AFN-λ
def simular_afn(automata: Automata, cadena: str) -> tuple[bool, list[dict]]:
    """Simulacion directa (sin convertir) de un AFN o AFN-lambda.

    Cada paso registra los estados activos antes de leer el simbolo, los que
    se alcanzan al leerlo (mover) y los que quedan tras aplicar la cerradura.
    """
    activos = cerradura_lambda(automata, automata.inicial)
    pasos = [{"simbolo": None, "antes": frozenset({automata.inicial}),
              "mover": frozenset({automata.inicial}), "despues": activos}]
    for simbolo in cadena:
        movidos = frozenset(mover(automata, activos, simbolo))
        nuevos = cerradura_lambda(automata, movidos)
        pasos.append({"simbolo": simbolo, "antes": activos, "mover": movidos, "despues": nuevos})
        activos = nuevos
    return bool(activos & automata.finales), pasos


def validar_lote(automata: Automata, cadenas: list[str]) -> list[tuple[str, bool]]:
    """Practica 3, 2.5: valida varias cadenas (una por linea en el archivo)."""
    return [(c, simular_afn(automata, c)[0]) for c in cadenas]


def informe_lote(resultados: list[tuple[str, bool]]) -> str:
    lineas = [f"{(c if c else LAMBDA_VISIBLE):<40} {'ACEPTADA' if ok else 'RECHAZADA'}"
              for c, ok in resultados]
    aceptadas = sum(ok for _, ok in resultados)
    lineas.append(f"\nTotal: {len(resultados)}  aceptadas: {aceptadas}  "
                  f"rechazadas: {len(resultados) - aceptadas}")
    return "\n".join(lineas)


# ------------------------------------------------- eliminacion de transiciones λ
def eliminar_lambda(automata: Automata) -> tuple[Automata, dict]:
    """AFN-lambda -> AFN sin lambda que reconoce el mismo lenguaje.

    delta'(q, a) = cerradura( mover( cerradura(q), a ) )
    F' = { q : cerradura(q) contiene algun estado de F }
    """
    cl = cerraduras(automata)
    nuevo = Automata(list(automata.estados), automata.alfabeto, automata.inicial,
                     set(), {}, (automata.nombre + " sin λ").strip())
    añadidas = []
    for q in automata.estados:
        for a in automata.alfabeto:
            destinos = set(cerradura_lambda(automata, mover(automata, cl[q], a)))
            for d in sorted(destinos):
                nuevo.agregar_transicion(q, a, d)
                if d not in automata.destinos(q, a):
                    añadidas.append((q, a, d))
    nuevas_finales = []
    for q in automata.estados:
        if cl[q] & automata.finales:
            nuevo.finales.add(q)
            if q not in automata.finales:
                nuevas_finales.append(q)
    eliminadas = [(o, d) for (o, s), ds in automata.transiciones.items() if s == LAMBDA for d in ds]
    registro = {"cerraduras": cl, "añadidas": añadidas, "nuevas_finales": nuevas_finales,
                "lambda_eliminadas": eliminadas}
    return nuevo, registro


# ---------------------------------------------------- construccion de subconjuntos
def subconjuntos(automata: Automata, prefijo: str = "S") -> tuple[Automata, list[dict]]:
    """AFN (con o sin lambda) -> AFD. Solo se construyen subconjuntos alcanzables.

    La tabla devuelta tiene una fila por subconjunto en el orden en que se
    generan: {"nombre", "conjunto", "transiciones": {a: nombre}, "aceptacion"}.
    El subconjunto vacio, si aparece, se convierte en un estado trampa.
    """
    inicial = cerradura_lambda(automata, automata.inicial)
    nombres = {inicial: f"{prefijo}0"}
    cola = deque([inicial])
    tabla = []
    afd = Automata([nombres[inicial]], automata.alfabeto, nombres[inicial], set(), {},
                   (automata.nombre + " AFD").strip())
    while cola:
        conjunto = cola.popleft()
        fila = {"nombre": nombres[conjunto], "conjunto": conjunto, "transiciones": {},
                "aceptacion": bool(conjunto & automata.finales)}
        for a in automata.alfabeto:
            destino = cerradura_lambda(automata, mover(automata, conjunto, a))
            if destino not in nombres:
                nombres[destino] = f"{prefijo}{len(nombres)}"
                cola.append(destino)
            afd.agregar_transicion(nombres[conjunto], a, nombres[destino])
            fila["transiciones"][a] = nombres[destino]
        if fila["aceptacion"]:
            afd.finales.add(nombres[conjunto])
        tabla.append(fila)
    afd.composicion = {n: c for c, n in nombres.items()}  # type: ignore[attr-defined]
    return afd, tabla


# ------------------------------------------------------------------ minimizacion
def eliminar_inaccesibles(automata: Automata) -> tuple[Automata, list[str]]:
    alcanzables = {automata.inicial}
    pila = [automata.inicial]
    while pila:
        q = pila.pop()
        for a in [LAMBDA] + automata.alfabeto:
            for d in automata.destinos(q, a):
                if d not in alcanzables:
                    alcanzables.add(d)
                    pila.append(d)
    quitados = [q for q in automata.estados if q not in alcanzables]
    nuevo = Automata([q for q in automata.estados if q in alcanzables], automata.alfabeto,
                     automata.inicial, automata.finales & alcanzables,
                     {(o, s): ds for (o, s), ds in automata.transiciones.items() if o in alcanzables},
                     automata.nombre)
    return nuevo, quitados


def completar(automata: Automata, trampa: str = TRAMPA) -> Automata:
    """Agrega un estado trampa explicito si a algun par (q, a) le falta transicion."""
    if not automata.es_determinista():
        raise ValueError("Solo se completa un AFD.")
    if automata.es_completo():
        return automata.copia()
    nuevo = automata.copia()
    while trampa in nuevo.estados:
        trampa += "'"
    nuevo.estados.append(trampa)
    for q in nuevo.estados:
        for a in nuevo.alfabeto:
            if not nuevo.destinos(q, a):
                nuevo.transiciones[(q, a)] = {trampa}
    return nuevo


def minimizar(automata: Automata, prefijo: str = "M") -> tuple[Automata, dict]:
    """AFD -> AFD minimo por refinamiento de particiones (algoritmo de Moore).

    Pasos: 1) quitar inaccesibles; 2) completar con trampa; 3) partir en
    {F, Q-F} y refinar mientras dos estados de un bloque vayan, con algun
    simbolo, a bloques distintos. Se registran las particiones de cada ronda.
    """
    if not automata.es_determinista():
        raise ValueError("La minimizacion requiere un AFD; aplique antes subconjuntos.")
    accesible, quitados = eliminar_inaccesibles(automata)
    completo = completar(accesible)
    finales = [q for q in completo.estados if q in completo.finales]
    no_finales = [q for q in completo.estados if q not in completo.finales]
    particion = [b for b in (finales, no_finales) if b]
    rondas = [[list(b) for b in particion]]
    while True:
        bloque_de = {q: i for i, b in enumerate(particion) for q in b}
        nueva = []
        for bloque in particion:
            grupos: dict[tuple, list[str]] = {}
            for q in bloque:
                firma = tuple(bloque_de[next(iter(completo.destinos(q, a)))]
                              for a in completo.alfabeto)
                grupos.setdefault(firma, []).append(q)
            nueva.extend(grupos.values())
        if len(nueva) == len(particion):
            break
        particion = nueva
        rondas.append([list(b) for b in particion])

    # Ordenar bloques: el del inicial primero, luego por aparicion BFS.
    bloque_de = {q: i for i, b in enumerate(particion) for q in b}
    orden, cola, vistos = [], deque([bloque_de[completo.inicial]]), {bloque_de[completo.inicial]}
    while cola:
        b = cola.popleft()
        orden.append(b)
        representante = particion[b][0]
        for a in completo.alfabeto:
            d = bloque_de[next(iter(completo.destinos(representante, a)))]
            if d not in vistos:
                vistos.add(d)
                cola.append(d)
    nombre = {b: f"{prefijo}{i}" for i, b in enumerate(orden)}
    minimo = Automata([nombre[b] for b in orden], completo.alfabeto,
                      nombre[bloque_de[completo.inicial]], set(), {},
                      (automata.nombre + " minimo").strip())
    for b in orden:
        representante = particion[b][0]
        if representante in completo.finales:
            minimo.finales.add(nombre[b])
        for a in completo.alfabeto:
            d = bloque_de[next(iter(completo.destinos(representante, a)))]
            minimo.transiciones[(nombre[b], a)] = {nombre[d]}
    minimo.composicion = {nombre[b]: frozenset(particion[b]) for b in orden}  # type: ignore[attr-defined]
    registro = {"inaccesibles": quitados, "trampa_agregada": len(completo.estados) > len(accesible.estados),
                "rondas": rondas, "estados_antes": len(automata.estados),
                "estados_despues": len(minimo.estados)}
    return minimo, registro


def sin_trampa(automata: Automata) -> Automata:
    """Quita los estados desde los que no se alcanza ninguno de aceptacion (para dibujar)."""
    vivos = set(automata.finales)
    cambio = True
    while cambio:
        cambio = False
        for (o, s), ds in automata.transiciones.items():
            if o not in vivos and ds & vivos:
                vivos.add(o)
                cambio = True
    if automata.inicial not in vivos:
        vivos.add(automata.inicial)
    return Automata([q for q in automata.estados if q in vivos], automata.alfabeto,
                    automata.inicial, automata.finales & vivos,
                    {(o, s): ds & vivos for (o, s), ds in automata.transiciones.items()
                     if o in vivos and ds & vivos}, automata.nombre)


# ---------------------------------------------------------------- equivalencia
def a_afd_minimo(automata: Automata) -> Automata:
    """Cualquier automata -> AFD minimo, pasando por toda la cadena de la Practica 3."""
    afd = automata if automata.es_determinista() else subconjuntos(automata)[0]
    return minimizar(afd)[0]


def isomorfos(a: Automata, b: Automata) -> tuple[bool, dict[str, str] | str]:
    """Decide si dos AFD completos coinciden salvo el nombre de los estados."""
    if set(a.alfabeto) != set(b.alfabeto):
        return False, "Los alfabetos son distintos."
    if len(a.estados) != len(b.estados):
        return False, f"Numero de estados distinto: {len(a.estados)} contra {len(b.estados)}."
    mapa = {a.inicial: b.inicial}
    cola = deque([a.inicial])
    while cola:
        p = cola.popleft()
        q = mapa[p]
        if (p in a.finales) != (q in b.finales):
            return False, f"{p} y {q} se corresponden pero difieren en aceptacion."
        for s in a.alfabeto:
            dp, dq = a.destinos(p, s), b.destinos(q, s)
            if len(dp) != 1 or len(dq) != 1:
                return False, "Alguno de los automatas no es un AFD completo."
            dp, dq = next(iter(dp)), next(iter(dq))
            if dp in mapa:
                if mapa[dp] != dq:
                    return False, f"Con '{s}' desde {p}/{q} se llega a estados no correspondientes."
            else:
                mapa[dp] = dq
                cola.append(dp)
    return True, mapa


def igualar_alfabetos(a: Automata, b: Automata) -> tuple[Automata, Automata]:
    union = sorted(set(a.alfabeto) | set(b.alfabeto))
    a2, b2 = a.copia(), b.copia()
    a2.alfabeto, b2.alfabeto = union, list(union)
    return a2, b2


def equivalentes(a: Automata, b: Automata) -> tuple[bool, str, str | None]:
    """Prueba de equivalencia de la Practica 3: compara los AFD minimos.

    Devuelve (equivalentes, explicacion, contraejemplo). El contraejemplo se
    busca con un recorrido BFS del producto, de modo que es el mas corto.
    """
    a, b = igualar_alfabetos(a, b)
    ma, mb = a_afd_minimo(a), a_afd_minimo(b)
    iguales, detalle = isomorfos(ma, mb)
    if iguales:
        return True, f"Los AFD minimos tienen {len(ma.estados)} estados y son isomorfos.", None
    contraejemplo = contraejemplo_mas_corto(ma, mb)
    return False, str(detalle), contraejemplo


def contraejemplo_mas_corto(a: Automata, b: Automata) -> str | None:
    """Cadena mas corta aceptada por exactamente uno de dos AFD completos."""
    inicio = (a.inicial, b.inicial)
    padre = {inicio: None}
    cola = deque([inicio])
    while cola:
        p, q = cola.popleft()
        if (p in a.finales) != (q in b.finales):
            camino = []
            nodo = (p, q)
            while padre[nodo] is not None:
                nodo, s = padre[nodo]
                camino.append(s)
            return "".join(reversed(camino))
        for s in a.alfabeto:
            sig = (next(iter(a.destinos(p, s))), next(iter(b.destinos(q, s))))
            if sig not in padre:
                padre[sig] = ((p, q), s)
                cola.append(sig)
    return None


def todas_las_cadenas(alfabeto, n: int):
    """Genera todas las cadenas de longitud 0..n (para las pruebas exhaustivas)."""
    for longitud in range(n + 1):
        for t in product(sorted(alfabeto), repeat=longitud):
            yield "".join(t)

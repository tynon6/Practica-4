"""Modelo de automata finito (Practicas 2 y 3).

Una sola clase representa AFD, AFN y AFN-lambda. La funcion de transicion se
guarda como un diccionario {(estado, simbolo): {destinos}}; el simbolo "" es
la transicion lambda. Un AFD es simplemente un automata sin transiciones
lambda y con a lo mas un destino por par (estado, simbolo). Si falta un par,
se entiende que la transicion va a un estado trampa implicito.

Este modulo no depende de Flet.
"""

from __future__ import annotations

from dataclasses import dataclass, field

LAMBDA = ""          # simbolo interno de la transicion lambda
LAMBDA_VISIBLE = "λ"


@dataclass
class Automata:
    estados: list[str]
    alfabeto: list[str]
    inicial: str
    finales: set[str]
    transiciones: dict[tuple[str, str], set[str]] = field(default_factory=dict)
    nombre: str = ""

    # ------------------------------------------------------------ construccion
    def __post_init__(self):
        self.estados = list(dict.fromkeys(self.estados))
        self.alfabeto = sorted(dict.fromkeys(s for s in self.alfabeto if s != LAMBDA))
        self.finales = set(self.finales)
        self.transiciones = {k: set(v) for k, v in self.transiciones.items() if v}

    def agregar_transicion(self, origen: str, simbolo: str, destino: str) -> None:
        if origen not in self.estados:
            self.estados.append(origen)
        if destino not in self.estados:
            self.estados.append(destino)
        if simbolo != LAMBDA and simbolo not in self.alfabeto:
            self.alfabeto = sorted(set(self.alfabeto) | {simbolo})
        self.transiciones.setdefault((origen, simbolo), set()).add(destino)

    def copia(self, nombre: str | None = None) -> "Automata":
        return Automata(
            list(self.estados), list(self.alfabeto), self.inicial, set(self.finales),
            {k: set(v) for k, v in self.transiciones.items()},
            self.nombre if nombre is None else nombre,
        )

    # --------------------------------------------------------------- consultas
    def destinos(self, estado: str, simbolo: str) -> set[str]:
        return self.transiciones.get((estado, simbolo), set())

    def tiene_lambda(self) -> bool:
        return any(s == LAMBDA for (_, s) in self.transiciones)

    def es_determinista(self) -> bool:
        return self.motivo_no_determinista() is None

    def motivo_no_determinista(self) -> tuple[str, str] | None:
        """Devuelve (estado, simbolo) del primer conflicto, o None si es AFD.

        El simbolo "" indica una transicion lambda.
        """
        for estado in self.estados:
            for simbolo in [LAMBDA] + self.alfabeto:
                destinos = self.destinos(estado, simbolo)
                if simbolo == LAMBDA and destinos:
                    return estado, LAMBDA
                if len(destinos) > 1:
                    return estado, simbolo
        return None

    def tipo(self) -> str:
        if self.tiene_lambda():
            return "AFND-lambda"
        return "AFD" if self.es_determinista() else "AFND"

    def es_completo(self) -> bool:
        return all(len(self.destinos(q, a)) == 1 for q in self.estados for a in self.alfabeto)

    def numero_transiciones(self) -> int:
        return sum(len(v) for v in self.transiciones.values())

    def lista_transiciones(self) -> list[tuple[str, str, str]]:
        """Transiciones como (origen, simbolo, destino), en orden estable."""
        orden = {q: i for i, q in enumerate(self.estados)}
        filas = [(o, s, d) for (o, s), ds in self.transiciones.items() for d in ds]
        return sorted(filas, key=lambda t: (orden.get(t[0], 0), t[1], orden.get(t[2], 0)))

    def validar(self) -> list[str]:
        """Errores de definicion de la quintupla (lista vacia si es correcta)."""
        errores = []
        if not self.estados:
            errores.append("El conjunto de estados es vacio.")
        if self.inicial not in self.estados:
            errores.append(f"El estado inicial '{self.inicial}' no pertenece a Q.")
        for f in self.finales:
            if f not in self.estados:
                errores.append(f"El estado de aceptacion '{f}' no pertenece a Q.")
        for (o, s), ds in self.transiciones.items():
            if o not in self.estados:
                errores.append(f"Transicion desde un estado desconocido: '{o}'.")
            if s != LAMBDA and s not in self.alfabeto:
                errores.append(f"El simbolo '{s}' no pertenece al alfabeto.")
            for d in ds:
                if d not in self.estados:
                    errores.append(f"Transicion hacia un estado desconocido: '{d}'.")
        return errores

    # --------------------------------------------------------------- simulacion
    def simular_afd(self, cadena: str) -> tuple[bool, list[dict]]:
        """Simula un AFD y devuelve (aceptada, traza).

        Cada paso de la traza es {"estado", "simbolo", "siguiente"}. Si falta
        una transicion, el automata cae en el estado trampa implicito.
        """
        if not self.es_determinista():
            estado, simbolo = self.motivo_no_determinista()
            raise ValueError(
                f"El automata no es determinista: estado {estado}, simbolo "
                f"{simbolo or LAMBDA_VISIBLE}. Use la simulacion de AFN."
            )
        actual = self.inicial
        traza = []
        for simbolo in cadena:
            destinos = self.destinos(actual, simbolo) if actual is not None else set()
            siguiente = next(iter(destinos)) if destinos else None
            traza.append({"estado": actual, "simbolo": simbolo, "siguiente": siguiente})
            actual = siguiente
            if actual is None:
                break
        aceptada = actual is not None and actual in self.finales and len(traza) == len(cadena)
        return aceptada, traza

    def acepta(self, cadena: str) -> bool:
        """Aceptacion para cualquier tipo de automata (via simulacion directa)."""
        from conversiones import simular_afn
        return simular_afn(self, cadena)[0]

    def __str__(self) -> str:
        return (f"Automata {self.nombre or ''} ({self.tipo()}): "
                f"{len(self.estados)} estados, {len(self.alfabeto)} simbolos, "
                f"{self.numero_transiciones()} transiciones")


def renombrar(automata: Automata, prefijo: str = "q") -> tuple[Automata, dict[str, str]]:
    """Renombra los estados como q0, q1, ... en orden BFS desde el inicial."""
    orden = []
    pendientes = [automata.inicial]
    vistos = {automata.inicial}
    while pendientes:
        q = pendientes.pop(0)
        orden.append(q)
        for a in [LAMBDA] + automata.alfabeto:
            for d in sorted(automata.destinos(q, a)):
                if d not in vistos:
                    vistos.add(d)
                    pendientes.append(d)
    orden += [q for q in automata.estados if q not in vistos]
    mapa = {q: f"{prefijo}{i}" for i, q in enumerate(orden)}
    nuevo = Automata(
        [mapa[q] for q in orden], automata.alfabeto, mapa[automata.inicial],
        {mapa[f] for f in automata.finales},
        {(mapa[o], s): {mapa[d] for d in ds} for (o, s), ds in automata.transiciones.items()},
        automata.nombre,
    )
    return nuevo, mapa


def tabla_transiciones(automata: Automata) -> tuple[list[str], list[list[str]]]:
    """Encabezados y filas de la tabla de transiciones, lista para mostrarse.

    El estado inicial se marca con '→' y los de aceptacion con '*'.
    """
    simbolos = list(automata.alfabeto)
    if automata.tiene_lambda():
        simbolos.append(LAMBDA)
    encabezados = ["δ"] + [s if s != LAMBDA else LAMBDA_VISIBLE for s in simbolos]
    filas = []
    for q in automata.estados:
        marca = ("→" if q == automata.inicial else "") + ("*" if q in automata.finales else "")
        fila = [f"{marca}{q}"]
        for s in simbolos:
            ds = automata.destinos(q, s)
            if not ds:
                fila.append("—")
            elif len(ds) == 1 and not automata.tiene_lambda() and automata.es_determinista():
                fila.append(next(iter(ds)))
            else:
                fila.append("{" + ", ".join(sorted(ds)) + "}")
        filas.append(fila)
    return encabezados, filas


def resumir_simbolos(simbolos) -> str:
    """Compacta una lista de simbolos para etiquetas: 'a-z, 0-9, @'."""
    simbolos = sorted(set(simbolos), key=lambda s: (len(s), s))
    if len(simbolos) <= 4:
        return ",".join(s if s != LAMBDA else LAMBDA_VISIBLE for s in simbolos)
    unitarios = sorted(s for s in simbolos if len(s) == 1)
    otros = [s for s in simbolos if len(s) != 1]
    partes = []
    i = 0
    while i < len(unitarios):
        j = i
        while j + 1 < len(unitarios) and ord(unitarios[j + 1]) == ord(unitarios[j]) + 1:
            j += 1
        if j - i >= 2:
            partes.append(f"{unitarios[i]}-{unitarios[j]}")
        else:
            partes.extend(unitarios[i:j + 1])
        i = j + 1
    partes += [s if s != LAMBDA else LAMBDA_VISIBLE for s in otros]
    return ",".join(partes)

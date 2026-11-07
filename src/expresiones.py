"""Expresiones regulares con la notacion del curso (Practica 4, Ejercicio 2).

Notacion aceptada
-----------------
    a          un simbolo del alfabeto (cualquier caracter que no sea operador)
    λ          la palabra vacia            ∅   el lenguaje vacio
    r + s      union                       rs  concatenacion (yuxtaposicion)
    r*         cerradura de Kleene         (r) agrupacion
    [D]        clase de simbolos declarada (abreviatura, p. ej. D = 0+1+...+9)
    \\c        el caracter c tomado literalmente (\\+, \\*, \\(, \\), \\[, \\λ, \\␣)

Precedencia: * (mas alta) > concatenacion > + (mas baja). Los espacios se
ignoran, salvo que se escapen con '\\ '.

Gramatica (descenso recursivo):
    union    ::= concat ( '+' concat )*
    concat   ::= cerradura cerradura*
    cerradura::= atomo '*'*
    atomo    ::= SIMBOLO | 'λ' | '∅' | '(' union ')' | '[' NOMBRE ']' | '\\' c

El modulo no depende de Flet.
"""

from __future__ import annotations

import random
import re
import string
from dataclasses import dataclass

LAMBDA_CAR = "λ"
VACIO_CAR = "∅"
OPERADORES = set("+*()[]\\")
ESPECIALES = OPERADORES | {LAMBDA_CAR, VACIO_CAR, "ε"}

# Clases predefinidas; el usuario puede pasar las suyas al analizador.
CLASES_PREDEFINIDAS: dict[str, str] = {
    "D": string.digits,                       # 0 + 1 + ... + 9
    "P": "123456789",                         # digito positivo
    "m": string.ascii_lowercase,              # a + b + ... + z
    "M": string.ascii_uppercase,              # A + B + ... + Z
    "L": string.ascii_letters,                # letras
    "A": string.ascii_letters + string.digits,  # alfanumericos
}


class ErrorExpresion(ValueError):
    """Expresion mal formada; `posicion` es el indice (base 0) del error."""

    def __init__(self, mensaje: str, posicion: int, expresion: str = ""):
        super().__init__(f"Posicion {posicion + 1}: {mensaje}")
        self.mensaje = mensaje
        self.posicion = posicion
        self.expresion = expresion

    def señalar(self) -> str:
        """La expresion con un acento circunflejo bajo el error."""
        return f"{self.expresion}\n{' ' * self.posicion}^"


# ------------------------------------------------------------------------- AST
class Nodo:
    precedencia = 3

    def simbolos(self) -> set[str]:
        raise NotImplementedError


@dataclass(frozen=True)
class Simbolo(Nodo):
    c: str

    def simbolos(self):
        return {self.c}


@dataclass(frozen=True)
class Clase(Nodo):
    nombre: str
    caracteres: frozenset

    def simbolos(self):
        return set(self.caracteres)


@dataclass(frozen=True)
class Lambda(Nodo):
    def simbolos(self):
        return set()


@dataclass(frozen=True)
class Vacio(Nodo):
    def simbolos(self):
        return set()


@dataclass(frozen=True)
class Union(Nodo):
    izq: Nodo
    der: Nodo
    precedencia = 1

    def simbolos(self):
        return self.izq.simbolos() | self.der.simbolos()


@dataclass(frozen=True)
class Concat(Nodo):
    izq: Nodo
    der: Nodo
    precedencia = 2

    def simbolos(self):
        return self.izq.simbolos() | self.der.simbolos()


@dataclass(frozen=True)
class Estrella(Nodo):
    r: Nodo
    precedencia = 3

    def simbolos(self):
        return self.r.simbolos()


# ------------------------------------------------- constructores que simplifican
def union(a: Nodo, b: Nodo) -> Nodo:
    """r + ∅ = r, r + r = r (leyes de identidad e idempotencia de la union)."""
    if isinstance(a, Vacio):
        return b
    if isinstance(b, Vacio):
        return a
    if a == b:
        return a
    return Union(a, b)


def concat(a: Nodo, b: Nodo) -> Nodo:
    """r∅ = ∅r = ∅ (anulador), rλ = λr = r (identidad de la concatenacion)."""
    if isinstance(a, Vacio) or isinstance(b, Vacio):
        return Vacio()
    if isinstance(a, Lambda):
        return b
    if isinstance(b, Lambda):
        return a
    return Concat(a, b)


def estrella(a: Nodo) -> Nodo:
    """∅* = λ* = λ y (r*)* = r*."""
    if isinstance(a, (Vacio, Lambda)):
        return Lambda()
    if isinstance(a, Estrella):
        return a
    return Estrella(a)


# --------------------------------------------------------------------- analisis
class _Analizador:
    def __init__(self, texto: str, clases: dict[str, str]):
        self.texto = texto
        self.clases = clases
        self.tokens = self._tokenizar()
        self.i = 0

    def _tokenizar(self) -> list[tuple[str, str, int]]:
        """Tokens (tipo, valor, posicion). Tipos: SIM, LAM, VAC, CLASE, y los operadores."""
        tokens, i, t = [], 0, self.texto
        while i < len(t):
            c = t[i]
            if c.isspace():
                i += 1
            elif c == "\\":
                if i + 1 >= len(t):
                    raise ErrorExpresion("'\\' al final de la expresion; falta el caracter a escapar.", i, t)
                tokens.append(("SIM", t[i + 1], i))
                i += 2
            elif c == "[":
                cierre = t.find("]", i)
                if cierre == -1:
                    raise ErrorExpresion("falta ']' para cerrar la clase de simbolos.", i, t)
                nombre = t[i + 1:cierre].strip()
                if not nombre:
                    raise ErrorExpresion("clase de simbolos sin nombre: '[]'.", i, t)
                if nombre not in self.clases:
                    disponibles = ", ".join(sorted(self.clases))
                    raise ErrorExpresion(f"la clase [{nombre}] no esta declarada (disponibles: {disponibles}).", i, t)
                tokens.append(("CLASE", nombre, i))
                i = cierre + 1
            elif c == "]":
                raise ErrorExpresion("']' sin '[' que la abra.", i, t)
            elif c in "+*()":
                tokens.append((c, c, i))
                i += 1
            elif c in (LAMBDA_CAR, "ε"):
                tokens.append(("LAM", c, i))
                i += 1
            elif c == VACIO_CAR:
                tokens.append(("VAC", c, i))
                i += 1
            else:
                tokens.append(("SIM", c, i))
                i += 1
        return tokens

    def _actual(self):
        return self.tokens[self.i] if self.i < len(self.tokens) else ("FIN", "", len(self.texto))

    def analizar(self) -> Nodo:
        if not self.tokens:
            raise ErrorExpresion("la expresion esta vacia (use λ para la palabra vacia).", 0, self.texto)
        arbol = self._union()
        tipo, _, pos = self._actual()
        if tipo == ")":
            raise ErrorExpresion("')' sin '(' que la abra.", pos, self.texto)
        if tipo != "FIN":
            raise ErrorExpresion(f"simbolo inesperado '{self._actual()[1]}'.", pos, self.texto)
        return arbol

    def _union(self) -> Nodo:
        izq = self._concat()
        while self._actual()[0] == "+":
            self.i += 1
            izq = Union(izq, self._concat())
        return izq

    def _inicia_atomo(self) -> bool:
        return self._actual()[0] in ("SIM", "LAM", "VAC", "CLASE", "(")

    def _concat(self) -> Nodo:
        if not self._inicia_atomo():
            tipo, valor, pos = self._actual()
            if tipo == "FIN":
                raise ErrorExpresion("se esperaba un operando al final de la expresion.", pos, self.texto)
            if tipo == "*":
                raise ErrorExpresion("'*' sin operando a su izquierda.", pos, self.texto)
            if tipo == "+":
                raise ErrorExpresion("'+' sin operando a su izquierda.", pos, self.texto)
            if tipo == ")":
                raise ErrorExpresion("se esperaba un operando antes de ')'.", pos, self.texto)
            raise ErrorExpresion(f"simbolo inesperado '{valor}'.", pos, self.texto)
        izq = self._cerradura()
        while self._inicia_atomo():
            izq = Concat(izq, self._cerradura())
        return izq

    def _cerradura(self) -> Nodo:
        r = self._atomo()
        while self._actual()[0] == "*":
            self.i += 1
            r = Estrella(r)
        return r

    def _atomo(self) -> Nodo:
        tipo, valor, pos = self._actual()
        self.i += 1
        if tipo == "SIM":
            return Simbolo(valor)
        if tipo == "LAM":
            return Lambda()
        if tipo == "VAC":
            return Vacio()
        if tipo == "CLASE":
            return Clase(valor, frozenset(self.clases[valor]))
        if tipo == "(":
            if self._actual()[0] == ")":
                raise ErrorExpresion("parentesis vacios '()'; use λ para la palabra vacia.", pos, self.texto)
            r = self._union()
            if self._actual()[0] != ")":
                raise ErrorExpresion("falta ')' para cerrar el parentesis abierto aqui.", pos, self.texto)
            self.i += 1
            return r
        raise ErrorExpresion(f"simbolo inesperado '{valor}'.", pos, self.texto)  # pragma: no cover


def analizar(texto: str, clases: dict[str, str] | None = None) -> Nodo:
    """Convierte el texto en un arbol sintactico o lanza ErrorExpresion."""
    todas = dict(CLASES_PREDEFINIDAS)
    if clases:
        todas.update(clases)
    return _Analizador(texto, todas).analizar()


def leer_clases(texto: str) -> dict[str, str]:
    """Lee declaraciones 'N = a + b + c' (una por linea) o 'N = a-z0-9' (rangos)."""
    clases = {}
    for n, linea in enumerate(texto.splitlines(), start=1):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        if "=" not in linea:
            raise ValueError(f"Linea {n}: se esperaba 'NOMBRE = simbolos'.")
        nombre, cuerpo = (p.strip() for p in linea.split("=", 1))
        if "+" in cuerpo:
            simbolos = [s.strip() for s in cuerpo.split("+") if s.strip()]
        else:
            simbolos = []
            i = 0
            while i < len(cuerpo):
                if i + 2 < len(cuerpo) and cuerpo[i + 1] == "-":
                    simbolos += [chr(c) for c in range(ord(cuerpo[i]), ord(cuerpo[i + 2]) + 1)]
                    i += 3
                else:
                    if not cuerpo[i].isspace():
                        simbolos.append(cuerpo[i])
                    i += 1
        if not nombre or not simbolos:
            raise ValueError(f"Linea {n}: la clase debe tener nombre y al menos un simbolo.")
        clases[nombre] = "".join(dict.fromkeys(simbolos))
    return clases


# ------------------------------------------------------------------ impresion
def _sim_texto(c: str) -> str:
    return "\\" + c if c in ESPECIALES or c.isspace() else c


def a_texto(n: Nodo) -> str:
    """Escribe el arbol con la notacion del curso usando los parentesis minimos."""
    if isinstance(n, Simbolo):
        return _sim_texto(n.c)
    if isinstance(n, Clase):
        return f"[{n.nombre}]"
    if isinstance(n, Lambda):
        return LAMBDA_CAR
    if isinstance(n, Vacio):
        return VACIO_CAR
    if isinstance(n, Estrella):
        interior = a_texto(n.r)
        return (interior if n.r.precedencia >= 3 else f"({interior})") + "*"
    if isinstance(n, Concat):
        partes = []
        for h in (n.izq, n.der):
            t = a_texto(h)
            partes.append(t if h.precedencia >= 2 else f"({t})")
        return "".join(partes)
    if isinstance(n, Union):
        return f"{a_texto(n.izq)} + {a_texto(n.der)}"
    raise TypeError(n)


def subexpresiones(n: Nodo) -> list[Nodo]:
    """Nodos en postorden: el orden en que la construccion de Thompson los arma."""
    if isinstance(n, (Union, Concat)):
        return subexpresiones(n.izq) + subexpresiones(n.der) + [n]
    if isinstance(n, Estrella):
        return subexpresiones(n.r) + [n]
    return [n]


def tamaño(n: Nodo) -> int:
    return len(subexpresiones(n))


# ------------------------------------------------------- traduccion al modulo re
def _clase_re(caracteres) -> str:
    return "[" + "".join(re.escape(c) if c in "\\]^-[" else c for c in sorted(caracteres)) + "]"


def a_python(n: Nodo) -> str:
    """Traduccion automatica a la sintaxis de re (para usar con re.fullmatch)."""
    if isinstance(n, Simbolo):
        return re.escape(n.c)
    if isinstance(n, Clase):
        return _clase_re(n.caracteres)
    if isinstance(n, Lambda):
        return "(?:)"
    if isinstance(n, Vacio):
        return "(?!)"
    if isinstance(n, Estrella):
        return f"(?:{a_python(n.r)})*"
    if isinstance(n, Concat):
        return a_python(n.izq) + a_python(n.der)
    if isinstance(n, Union):
        return f"(?:{a_python(n.izq)}|{a_python(n.der)})"
    raise TypeError(n)


# ------------------------------------------------ generacion de cadenas del lenguaje
def generar_cadena(n: Nodo, rng: random.Random, max_rep: int = 3) -> str | None:
    """Deriva una cadena aleatoria del lenguaje de `n` recorriendo el arbol.

    Union: elige una rama al azar; estrella: repite de 0 a max_rep veces;
    clase: elige un caracter. Devuelve None si el lenguaje es vacio.
    Es independiente del automata, por eso sirve para probar la congruencia.
    """
    if isinstance(n, Simbolo):
        return n.c
    if isinstance(n, Clase):
        return rng.choice(sorted(n.caracteres))
    if isinstance(n, Lambda):
        return ""
    if isinstance(n, Vacio):
        return None
    if isinstance(n, Union):
        ramas = [n.izq, n.der]
        rng.shuffle(ramas)
        for r in ramas:
            c = generar_cadena(r, rng, max_rep)
            if c is not None:
                return c
        return None
    if isinstance(n, Concat):
        a = generar_cadena(n.izq, rng, max_rep)
        b = generar_cadena(n.der, rng, max_rep) if a is not None else None
        return None if b is None else a + b
    if isinstance(n, Estrella):
        partes = []
        for _ in range(rng.randint(0, max_rep)):
            c = generar_cadena(n.r, rng, max_rep)
            if c is None:
                break
            partes.append(c)
        return "".join(partes)
    raise TypeError(n)

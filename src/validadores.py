"""Validadores construidos con expresiones regulares (Practica 4, Ejercicio 4).

Cada validador se define con:
  * la expresion en la notacion del curso (la que analiza `expresiones`),
  * las clases de simbolos que usa (abreviaturas declaradas),
  * una expresion equivalente escrita a mano para el modulo `re`,
  * el estandar consultado y los casos que la expresion deja fuera.

El automata se obtiene con `thompson.pipeline`, es decir, con la cadena
completa ER -> AFN-λ -> AFN -> AFD -> AFD minimo, y la validacion se hace
con el AFD minimo. Este modulo no depende de Flet.
"""

from __future__ import annotations

import random
import re
import string
from dataclasses import dataclass, field
from functools import lru_cache

import expresiones as er
from thompson import Pipeline, pipeline

ALFANUM = string.ascii_letters + string.digits

CLASES = {
    "D": string.digits,                      # 0 + 1 + ... + 9
    "P": "123456789",                        # digito distinto de cero
    "L": string.ascii_letters,               # letras ASCII
    "A": ALFANUM,                            # letras y digitos
    "H": ALFANUM + "-",                      # caracteres de una etiqueta de dominio
    "W": ALFANUM + "_%+-",                   # parte local de un correo (sin punto)
    "R": ALFANUM + "-._~%",                  # caracteres de un segmento de ruta URL
}

ETIQUETA = "([A] + [A][H]*[A])"            # etiqueta de dominio: no empieza ni termina en '-'
DOMINIO = f"({ETIQUETA}.)({ETIQUETA}.)*[L][L][L]*"
DIA = "(0[P] + (1 + 2)[D] + 3(0 + 1))"
MES = "(0[P] + 1(0 + 1 + 2))"
SEP = "(\\  + - + λ)"                       # espacio, guion o nada


@dataclass(frozen=True)
class Validador:
    clave: str
    nombre: str
    descripcion: str
    expresion: str
    regex_python: str
    estandar: str
    limitaciones: str
    validos: tuple[str, ...] = field(default_factory=tuple)
    invalidos: tuple[str, ...] = field(default_factory=tuple)

    def clases_usadas(self) -> dict[str, str]:
        return {k: v for k, v in CLASES.items() if f"[{k}]" in self.expresion}

    def automata(self) -> Pipeline:
        return construir(self.clave)

    def valida(self, texto: str) -> bool:
        return self.automata().acepta(texto)

    def valida_re(self, texto: str) -> bool:
        return re.fullmatch(self.regex_python, texto) is not None


VALIDADORES: dict[str, Validador] = {}


def _registrar(v: Validador) -> None:
    VALIDADORES[v.clave] = v


_registrar(Validador(
    clave="correo",
    nombre="Correo electronico",
    descripcion="parte-local@dominio.tld; la parte local admite letras, digitos y _ % + -, "
                "con puntos solo entre caracteres; el dominio tiene una o mas etiquetas y un TLD de 2+ letras.",
    expresion=f"[W]([W] + .[W])* @ {DOMINIO}",
    regex_python=r"[A-Za-z0-9_%+-]+(?:\.[A-Za-z0-9_%+-]+)*@"
                 r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}",
    estandar="RFC 5321 (SMTP), sec. 4.1.2, y RFC 5322, sec. 3.4.1 (addr-spec).",
    limitaciones="Quedan fuera direcciones validas segun el RFC 5322 como las de parte local entre "
                 "comillas (\"juan perez\"@x.mx), los caracteres ! # $ & ' * / = ? ^ ` { | } ~, los "
                 "dominios literales IP (usuario@[192.168.0.1]) y los nombres internacionalizados (ñ, acentos). "
                 "Se aceptan algunas invalidas, p. ej. etiquetas de mas de 63 caracteres o direcciones de mas de 254.",
    validos=("saul.hernandez@ipn.mx", "a@b.co", "juan_perez+tc@alumno.ipn.mx", "x-1@mi-dominio.com"),
    invalidos=("saul@ipn", ".saul@ipn.mx", "saul..h@ipn.mx", "saul@-ipn.mx", "saul@ipn.m", "saul ipn.mx"),
))

_registrar(Validador(
    clave="telefono",
    nombre="Telefono (formato nacional, Mexico)",
    descripcion="10 digitos, agrupados 2-4-4 (lada de 2 digitos) o 3-3-4 (lada de 3), separados por "
                "espacio, guion o nada; opcionalmente precedidos de +52.",
    expresion=f"(\\+52(\\  + λ) + λ)([D][D]{SEP}[D][D][D][D]{SEP}[D][D][D][D] + "
              f"[D][D][D]{SEP}[D][D][D]{SEP}[D][D][D][D])",
    regex_python=r"(?:\+52 ?)?(?:[0-9]{2}[ -]?[0-9]{4}[ -]?[0-9]{4}|[0-9]{3}[ -]?[0-9]{3}[ -]?[0-9]{4})",
    estandar="Plan Tecnico Fundamental de Numeracion del IFT (marcacion de 10 digitos, vigente desde el 3 de agosto de 2019).",
    limitaciones="No verifica que la lada exista ni que el numero este asignado; acepta separadores mezclados "
                 "(55 1234-5678). Quedan fuera los formatos con parentesis ((55) 1234 5678), el prefijo 01 "
                 "o 044 ya eliminados, y los numeros internacionales distintos de +52.",
    validos=("5512345678", "55 1234 5678", "771-123-4567", "+52 55 1234 5678", "+527711234567"),
    invalidos=("551234567", "55123456789", "(55) 1234 5678", "+1 555 123 4567", "55_1234_5678"),
))

_registrar(Validador(
    clave="fecha",
    nombre="Fecha (dd/mm/aaaa o aaaa-mm-dd)",
    descripcion="Dia 01-31 y mes 01-12, en formato dd/mm/aaaa (uso en Mexico) o aaaa-mm-dd (ISO 8601).",
    expresion=f"{DIA}/{MES}/[D][D][D][D] + [D][D][D][D]-{MES}-{DIA}",
    regex_python=r"(?:0[1-9]|[12][0-9]|3[01])/(?:0[1-9]|1[0-2])/[0-9]{4}"
                 r"|[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])",
    estandar="ISO 8601-1:2019, formato extendido de fecha de calendario (aaaa-mm-dd).",
    limitaciones="No relaciona el dia con el mes: acepta 31/02/2026 y 29/02/2025. Comprobar los dias de cada "
                 "mes es regular pero alarga mucho la expresion, y los años bisiestos solo pueden "
                 "aproximarse con un lenguaje finito. Quedan fuera fechas sin ceros (6/11/2026) y años de 2 digitos.",
    validos=("06/11/2026", "2026-11-06", "31/12/1999", "01/01/0001"),
    invalidos=("6/11/2026", "32/01/2026", "15/13/2026", "2026/11/06", "2026-11-6", "00/10/2026"),
))

_registrar(Validador(
    clave="url",
    nombre="URL (http y https)",
    descripcion="http:// o https://, un nombre de dominio con TLD, un puerto opcional y segmentos de ruta.",
    expresion=f"http(s + λ)://{DOMINIO}(:[P][D]* + λ)(/[R]*)*",
    regex_python=r"https?://(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}"
                 r"(?::[1-9][0-9]*)?(?:/[A-Za-z0-9._~%-]*)*",
    estandar="RFC 3986 (sintaxis generica de URI), sec. 3, y RFC 1123, sec. 2.1 (nombres de host).",
    limitaciones="Quedan fuera otros esquemas (ftp, mailto), direcciones IP, localhost, credenciales "
                 "(usuario@host), consulta (?q=1) y fragmento (#seccion). No limita el puerto a 65535.",
    validos=("https://www.escom.ipn.mx", "http://ipn.mx/", "https://a.b.co:8550/practica4/README.md"),
    invalidos=("ftp://ipn.mx", "https://ipn", "https//ipn.mx", "https://ipn.mx:0", "http://-ipn.mx"),
))


@lru_cache(maxsize=None)
def construir(clave: str) -> Pipeline:
    v = VALIDADORES[clave]
    return pipeline(v.expresion, CLASES)


def traduccion_automatica(clave: str) -> str:
    """La traduccion mecanica del arbol a sintaxis de re (ver expresiones.a_python)."""
    v = VALIDADORES[clave]
    return er.a_python(er.analizar(v.expresion, CLASES))


# --------------------------------------------------------------- casos de prueba
RUIDO = " #!ñ()/:.@-_+"


def mutar(cadena: str, simbolos: str, rng: random.Random) -> str:
    """Aplica una mutacion al azar: insertar, borrar, sustituir, duplicar o truncar."""
    if not cadena:
        return rng.choice(simbolos)
    i = rng.randrange(len(cadena))
    opcion = rng.randrange(5)
    if opcion == 0:
        return cadena[:i] + rng.choice(simbolos) + cadena[i:]
    if opcion == 1:
        return cadena[:i] + cadena[i + 1:]
    if opcion == 2:
        return cadena[:i] + rng.choice(simbolos) + cadena[i + 1:]
    if opcion == 3:
        return cadena[:i] + cadena[i] + cadena[i:]
    return cadena[:i]


def generar_casos(clave: str, total: int = 600, semilla: int = 2026) -> list[str]:
    """Conjunto de prueba reproducible para un validador.

    Procedimiento (se describe en docs/practica4/04-validadores.md):
      1. Los ejemplos validos e invalidos escritos a mano.
      2. Cadenas derivadas al azar del arbol de la expresion (pertenecen al
         lenguaje por construccion, sin usar el automata).
      3. Cada derivada se muta una o dos veces (insertar, borrar, sustituir,
         duplicar, truncar) con simbolos del alfabeto y de ruido; la mayoria
         de las mutantes queda fuera del lenguaje.
      4. Cadenas aleatorias sobre el alfabeto y el ruido.
    Se usa una semilla fija para que el conjunto sea el mismo en cada ejecucion.
    """
    v = VALIDADORES[clave]
    rng = random.Random(f"{semilla}-{clave}")
    arbol = er.analizar(v.expresion, CLASES)
    alfabeto = "".join(sorted(arbol.simbolos()))
    simbolos = alfabeto + RUIDO
    casos = list(v.validos) + list(v.invalidos) + ["", " "]
    derivadas = []
    while len(derivadas) < total * 2 // 5:
        derivadas.append(er.generar_cadena(arbol, rng))
    casos += derivadas
    for d in derivadas:
        m = mutar(d, simbolos, rng)
        if rng.random() < 0.3:
            m = mutar(m, simbolos, rng)
        casos.append(m)
    while len(casos) < total:
        casos.append("".join(rng.choice(simbolos) for _ in range(rng.randint(1, 25))))
    return list(dict.fromkeys(casos))

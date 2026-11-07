"""Operaciones basicas sobre cadenas y lenguajes (Practica 1).

Funciones puras: no dependen de Flet ni de ningun otro modulo del
proyecto, por lo que se prueban directamente con pytest.

Convencion adoptada: la cadena vacia (lambda) se representa con "" y
SI figura entre los prefijos, los sufijos y las subcadenas, porque
lambda es prefijo, sufijo y subcadena de toda cadena (w = lambda w = w lambda).
"""

from itertools import product

LAMBDA = "λ"
LIMITE_CADENAS = 200_000


def prefijos(w: str) -> list[str]:
    """Los |w| + 1 prefijos de w, del mas corto (lambda) al mas largo (w)."""
    return [w[:i] for i in range(len(w) + 1)]


def sufijos(w: str) -> list[str]:
    """Los |w| + 1 sufijos de w, del mas largo (w) al mas corto (lambda)."""
    return [w[i:] for i in range(len(w) + 1)]


def subcadenas(w: str) -> list[str]:
    """Subcadenas distintas de w, ordenadas por longitud y luego por aparicion.

    Como maximo hay n(n+1)/2 + 1 subcadenas distintas (contando lambda);
    el maximo se alcanza cuando todos los simbolos de w son distintos.
    """
    vistas: dict[str, None] = {"": None}
    for longitud in range(1, len(w) + 1):
        for i in range(len(w) - longitud + 1):
            vistas.setdefault(w[i:i + longitud], None)
    return list(vistas)


def concatenar(u: str, v: str) -> str:
    return u + v


def potencia(w: str, n: int) -> str:
    """w^n; por definicion w^0 = lambda."""
    if n < 0:
        raise ValueError("La potencia debe ser un entero no negativo.")
    return w * n


def reflexion(w: str) -> str:
    """w^R, la cadena escrita al reves."""
    return w[::-1]


def normalizar_alfabeto(alfabeto) -> list[str]:
    """Acepta 'a,b', 'ab', 'a b' o un iterable; devuelve simbolos unicos ordenados."""
    if isinstance(alfabeto, str):
        texto = alfabeto.strip()
        if "," in texto:
            simbolos = [s.strip() for s in texto.split(",")]
        elif " " in texto:
            simbolos = texto.split()
        else:
            simbolos = list(texto)
    else:
        simbolos = list(alfabeto)
    simbolos = [s for s in simbolos if s != ""]
    if not simbolos:
        raise ValueError("El alfabeto no puede ser vacio.")
    return sorted(dict.fromkeys(simbolos))


def numero_cadenas(k: int, n: int, positiva: bool = False) -> int:
    """Cuantas cadenas de longitud 0..n (o 1..n) hay sobre un alfabeto de k simbolos."""
    inicio = 1 if positiva else 0
    return sum(k ** i for i in range(inicio, n + 1))


def _cerradura(alfabeto, n: int, positiva: bool) -> list[str]:
    simbolos = normalizar_alfabeto(alfabeto)
    if n < 0:
        raise ValueError("La longitud maxima debe ser un entero no negativo.")
    total = numero_cadenas(len(simbolos), n, positiva)
    if total > LIMITE_CADENAS:
        raise ValueError(
            f"La combinacion generaria {total:,} cadenas y el limite es "
            f"{LIMITE_CADENAS:,}. Reduzca el alfabeto o la longitud maxima."
        )
    resultado = []
    for longitud in range(1 if positiva else 0, n + 1):
        resultado.extend("".join(t) for t in product(simbolos, repeat=longitud))
    return resultado


def cerradura_kleene(alfabeto, n: int) -> list[str]:
    """Sigma* truncada a longitud n: Sigma^0 U Sigma^1 U ... U Sigma^n."""
    return _cerradura(alfabeto, n, positiva=False)


def cerradura_positiva(alfabeto, n: int) -> list[str]:
    """Sigma+ truncada a longitud n: Sigma^1 U ... U Sigma^n (sin lambda)."""
    return _cerradura(alfabeto, n, positiva=True)


def mostrar(w: str) -> str:
    """Representacion para pantalla: la cadena vacia se muestra como lambda."""
    return LAMBDA if w == "" else w

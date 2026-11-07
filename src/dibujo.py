"""Dibujo de automatas sobre un lienzo de Flet (parte de la interfaz).

Es el unico modulo, ademas de app.py, que importa Flet. Recibe un Automata
(o un automata generalizado con etiquetas de texto) y devuelve un control.
"""

from __future__ import annotations

import math

import flet as ft
import flet.canvas as cv

from automata import LAMBDA, Automata, resumir_simbolos

RADIO = 20
MAX_ESTADOS = 40


def _posiciones(estados: list[str], ancho: float, alto: float) -> dict[str, tuple[float, float]]:
    n = len(estados)
    if n == 1:
        return {estados[0]: (ancho / 2, alto / 2)}
    if n <= 12:
        rx, ry = ancho / 2 - 60, alto / 2 - 50
        return {q: (ancho / 2 + rx * math.cos(math.pi + 2 * math.pi * i / n),
                    alto / 2 + ry * math.sin(math.pi + 2 * math.pi * i / n))
                for i, q in enumerate(estados)}
    # Muchos estados: rejilla en zigzag (se leen mejor que en circulo).
    columnas = math.ceil(math.sqrt(n * 1.6))
    filas = math.ceil(n / columnas)
    dx = (ancho - 80) / max(columnas - 1, 1)
    dy = (alto - 80) / max(filas - 1, 1)
    return {q: (40 + dx * (i % columnas), 40 + dy * (i // columnas) + (12 if (i % columnas) % 2 else 0))
            for i, q in enumerate(estados)}


def _orden_bfs(automata: Automata) -> list[str]:
    """Estados en orden de recorrido desde el inicial: el dibujo se lee de izquierda a derecha."""
    orden, cola, vistos = [], [automata.inicial], {automata.inicial}
    while cola:
        q = cola.pop(0)
        orden.append(q)
        for a in [LAMBDA] + automata.alfabeto:
            for d in sorted(automata.destinos(q, a)):
                if d not in vistos:
                    vistos.add(d)
                    cola.append(d)
    return orden + [q for q in automata.estados if q not in vistos]


def _punta(x, y, angulo, color) -> cv.Path:
    largo, abertura = 10, 0.45
    return cv.Path([
        cv.Path.MoveTo(x, y),
        cv.Path.LineTo(x - largo * math.cos(angulo - abertura), y - largo * math.sin(angulo - abertura)),
        cv.Path.LineTo(x - largo * math.cos(angulo + abertura), y - largo * math.sin(angulo + abertura)),
        cv.Path.Close(),
    ], paint=ft.Paint(color=color, style=ft.PaintingStyle.FILL))


def dibujar(automata: Automata | None = None, *, estados: list[str] | None = None,
            inicial: str | None = None, finales: set[str] | None = None,
            etiquetas: dict[tuple[str, str], str] | None = None,
            resaltados: set[str] | None = None, ancho: int = 640, alto: int = 420) -> ft.Control:
    """Devuelve un control con el diagrama.

    Se puede pasar un Automata, o bien estados/inicial/finales/etiquetas para
    dibujar un automata generalizado cuyas aristas llevan expresiones.
    """
    if automata is not None:
        estados = _orden_bfs(automata)
        inicial = automata.inicial
        finales = set(automata.finales)
        agrupadas: dict[tuple[str, str], list[str]] = {}
        for (o, s), ds in automata.transiciones.items():
            for d in ds:
                agrupadas.setdefault((o, d), []).append(s)
        etiquetas = {k: resumir_simbolos(v) for k, v in agrupadas.items()}
    estados = estados or []
    finales = finales or set()
    etiquetas = etiquetas or {}
    resaltados = resaltados or set()

    if not estados:
        return ft.Text("Sin automata cargado.", italic=True)
    if len(estados) > MAX_ESTADOS:
        return ft.Text(f"El automata tiene {len(estados)} estados; es demasiado grande para "
                       f"dibujarse con claridad. Consulte la tabla de transiciones.", italic=True)

    linea = ft.Colors.ON_SURFACE
    acento = ft.Colors.PRIMARY
    pos = _posiciones(estados, ancho, alto)
    formas: list = []
    estilo = ft.TextStyle(size=11, color=linea)
    estilo_etq = ft.TextStyle(size=11, color=ft.Colors.TERTIARY, weight=ft.FontWeight.BOLD)

    for (o, d), texto in etiquetas.items():
        if o not in pos or d not in pos:
            continue
        texto = texto if len(texto) <= 28 else texto[:26] + "…"
        x1, y1 = pos[o]
        x2, y2 = pos[d]
        pintura = ft.Paint(color=linea, stroke_width=1.4, style=ft.PaintingStyle.STROKE)
        if o == d:  # bucle encima del estado
            formas.append(cv.Arc(x1 - 12, y1 - RADIO - 22, 24, 28, math.pi * 0.85, math.pi * 1.3, paint=pintura))
            formas.append(_punta(x1 + 10, y1 - RADIO + 2, math.pi * 0.42, linea))
            formas.append(cv.Text(x1, y1 - RADIO - 32, texto, style=estilo_etq, alignment=ft.Alignment.CENTER))
            continue
        dx, dy = x2 - x1, y2 - y1
        distancia = math.hypot(dx, dy) or 1
        nx, ny = -dy / distancia, dx / distancia
        curva = 28 if (d, o) in etiquetas else 0
        cx, cy = (x1 + x2) / 2 + nx * curva, (y1 + y2) / 2 + ny * curva
        # recortar en el borde de los circulos
        a1 = math.atan2(cy - y1, cx - x1)
        a2 = math.atan2(y2 - cy, x2 - cx)
        sx, sy = x1 + RADIO * math.cos(a1), y1 + RADIO * math.sin(a1)
        ex, ey = x2 - RADIO * math.cos(a2), y2 - RADIO * math.sin(a2)
        formas.append(cv.Path([cv.Path.MoveTo(sx, sy), cv.Path.QuadraticTo(cx, cy, ex, ey)], paint=pintura))
        formas.append(_punta(ex, ey, a2, linea))
        formas.append(cv.Text((sx + 2 * cx + ex) / 4 + nx * 8, (sy + 2 * cy + ey) / 4 + ny * 8, texto,
                              style=estilo_etq, alignment=ft.Alignment.CENTER))

    for q in estados:
        x, y = pos[q]
        relleno = ft.Colors.with_opacity(0.85, acento) if q in resaltados else ft.Colors.SURFACE
        formas.append(cv.Circle(x, y, RADIO, ft.Paint(color=relleno, style=ft.PaintingStyle.FILL)))
        formas.append(cv.Circle(x, y, RADIO, ft.Paint(color=acento, stroke_width=2, style=ft.PaintingStyle.STROKE)))
        if q in finales:
            formas.append(cv.Circle(x, y, RADIO - 4, ft.Paint(color=acento, stroke_width=1.5,
                                                              style=ft.PaintingStyle.STROKE)))
        if q == inicial:
            formas.append(cv.Line(x - RADIO - 26, y, x - RADIO - 2, y, ft.Paint(color=linea, stroke_width=2)))
            formas.append(_punta(x - RADIO - 1, y, 0, linea))
        nombre = q if len(q) <= 5 else q[:4] + "…"
        color = ft.Colors.ON_PRIMARY if q in resaltados else linea
        formas.append(cv.Text(x, y, nombre, style=ft.TextStyle(size=11, color=color, weight=ft.FontWeight.BOLD),
                              alignment=ft.Alignment.CENTER))

    return ft.Container(cv.Canvas(formas, width=ancho, height=alto), width=ancho, height=alto,
                        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT), border_radius=8)

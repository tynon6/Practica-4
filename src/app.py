"""Interfaz grafica del software de Teoria de la Computacion (Practicas 1 a 4).

Esta es la unica capa que depende de Flet (junto con dibujo.py). Toda la
logica vive en los modulos del nucleo y se prueba sin abrir la interfaz:

    lenguajes.py           Practica 1   operaciones sobre cadenas y lenguajes
    automata.py            Practica 2   modelo y simulacion de AFD/AFN/AFN-λ
    formatos.py            Practica 2   .jff, .json, .xml
    conversiones.py        Practica 3   cerradura λ, eliminar λ, subconjuntos, minimizar
    expresiones.py         Practica 4   analisis de expresiones regulares
    thompson.py            Practica 4   ER -> AFN-λ -> AFD minimo   (Ejercicio 2)
    eliminacion_estados.py Practica 4   AFD -> ER                   (Ejercicio 3)
    validadores.py         Practica 4   validadores                 (Ejercicio 4)

Ejecucion:
    python src/app.py                  ventana de escritorio (requiere flet[all])
    FLET_FORCE_WEB_SERVER=true python src/app.py   servidor web en el puerto 8550
    docker compose up py312            dentro del contenedor (abrir http://localhost:8550)

Los archivos se leen de las carpetas del repositorio y se guardan en salidas/,
de modo que funciona igual en escritorio, en el navegador y en el contenedor.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import flet as ft

sys.path.insert(0, str(Path(__file__).resolve().parent))

import conversiones as cv  # noqa: E402
import eliminacion_estados as elim  # noqa: E402
import expresiones as er  # noqa: E402
import formatos as fm  # noqa: E402
import lenguajes as lg  # noqa: E402
import validadores as val  # noqa: E402
from automata import LAMBDA, LAMBDA_VISIBLE, Automata, tabla_transiciones  # noqa: E402
from dibujo import dibujar  # noqa: E402
from thompson import pipeline  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
SALIDAS = RAIZ / "salidas"
MONO = "monospace"


# =============================================================== utilidades UI
def texto_salida(lineas: int = 12) -> ft.TextField:
    return ft.TextField(multiline=True, read_only=True, min_lines=lineas, max_lines=lineas,
                        text_style=ft.TextStyle(font_family=MONO, size=13), expand=True)


def tabla(encabezados: list[str], filas: list[list[str]]) -> ft.Control:
    if not filas:
        return ft.Text("—")
    columnas = [ft.DataColumn(ft.Text(h, weight=ft.FontWeight.BOLD)) for h in encabezados]
    renglones = []
    for f in filas:
        renglones.append(ft.DataRow([ft.DataCell(ft.Text(str(c), font_family=MONO, selectable=True)) for c in f]))
    return ft.Row([ft.DataTable(columns=columnas, rows=renglones, column_spacing=18,
                                heading_row_height=36, data_row_min_height=30, data_row_max_height=34)],
                  scroll=ft.ScrollMode.AUTO)


def tabla_automata(a: Automata) -> ft.Control:
    encabezados, filas = tabla_transiciones(a)
    return tabla(encabezados, filas)


def guardar(nombre: str, contenido: str) -> Path:
    SALIDAS.mkdir(exist_ok=True)
    ruta = SALIDAS / nombre
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(contenido, encoding="utf-8")
    return ruta


def ruta_relativa(ruta: Path) -> str:
    try:
        return str(ruta.relative_to(RAIZ))
    except ValueError:
        return str(ruta)


def archivos_automata() -> list[str]:
    encontrados = []
    for carpeta in ("automatas", "salidas", "casos"):
        base = RAIZ / carpeta
        if base.exists():
            for ext in ("*.jff", "*.json", "*.xml"):
                encontrados += [ruta_relativa(p) for p in base.rglob(ext)
                                if p.name != "ejercicios_er.json"]
    return sorted(encontrados)


def boton(texto, al_pulsar, icono=None, principal=False):
    clase = ft.FilledButton if principal else ft.OutlinedButton
    return clase(texto, icon=icono, on_click=al_pulsar)


def seccion(titulo: str, controles: list, abierta: bool = False) -> ft.ExpansionTile:
    return ft.ExpansionTile(title=ft.Text(titulo, weight=ft.FontWeight.W_600), controls=controles,
                            expanded=abierta, controls_padding=ft.Padding.only(left=12, right=12, bottom=12),
                            expanded_cross_axis_alignment=ft.CrossAxisAlignment.START)


def describir_clase(nombre: str, simbolos: str) -> str:
    """'D = 0 + 1 + ... + 9' para clases cortas; para las largas, la lista de simbolos."""
    escapados = [("\\" + c) if c in er.ESPECIALES or c.isspace() else c for c in simbolos]
    if len(simbolos) <= 12:
        return f"{nombre} = " + " + ".join(escapados)
    return f"{nombre} = " + "".join(escapados) + f"   ({len(simbolos)} simbolos)"


def mostrar(c: str) -> str:
    return LAMBDA_VISIBLE if c == "" else c


def conjunto(s) -> str:
    return cv.formato_conjunto(s)


class App:
    def __init__(self, page: ft.Page):
        self.page = page
        page.title = "Teoria de la Computacion — Software interactivo"
        page.theme_mode = ft.ThemeMode.SYSTEM
        page.theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
        page.dark_theme = ft.Theme(color_scheme_seed=ft.Colors.INDIGO)
        page.padding = 0
        self.vistas = [
            ("Lenguajes", ft.Icons.TEXT_FIELDS, self.vista_lenguajes),
            ("Automatas", ft.Icons.ACCOUNT_TREE, self.vista_automatas),
            ("ER a automata", ft.Icons.ARROW_FORWARD, self.vista_er_automata),
            ("Automata a ER", ft.Icons.ARROW_BACK, self.vista_automata_er),
            ("Validadores", ft.Icons.VERIFIED, self.vista_validadores),
        ]
        self.construidas: dict[int, ft.Control] = {}
        self.contenido = ft.Container(expand=True, padding=16)
        self.riel = ft.NavigationRail(
            selected_index=0, label_type=ft.NavigationRailLabelType.ALL, min_width=96,
            destinations=[ft.NavigationRailDestination(icon=i, label=t) for t, i, _ in self.vistas],
            on_change=lambda e: self.ir(e.control.selected_index))
        page.add(ft.Row([self.riel, ft.VerticalDivider(width=1), self.contenido], expand=True))
        # estado compartido de la seccion de automatas
        self.actual: Automata | None = None
        self.historial: list[Automata] = []
        self.ir(0)

    # ------------------------------------------------------------- navegacion
    def ir(self, indice: int):
        if indice not in self.construidas:
            self.construidas[indice] = self.vistas[indice][2]()
        self.riel.selected_index = indice
        self.contenido.content = self.construidas[indice]
        self.page.update()

    def aviso(self, mensaje: str, error: bool = False):
        self.page.show_dialog(ft.SnackBar(
            ft.Text(mensaje, color=ft.Colors.ON_ERROR_CONTAINER if error else None),
            bgcolor=ft.Colors.ERROR_CONTAINER if error else None, duration=5000))

    def encabezado(self, titulo: str, subtitulo: str) -> ft.Control:
        return ft.Column([ft.Text(titulo, size=24, weight=ft.FontWeight.BOLD),
                          ft.Text(subtitulo, color=ft.Colors.ON_SURFACE_VARIANT)], spacing=2)

    # ================================================== 1. LENGUAJES (Practica 1)
    def vista_lenguajes(self) -> ft.Control:
        cadena = ft.TextField(label="Cadena w", hint_text="por ejemplo: abc", width=320)
        alfabeto = ft.TextField(label="Alfabeto Σ", hint_text="a,b  o  ab", width=200)
        longitud = ft.TextField(label="Longitud maxima n", value="3", width=160,
                                keyboard_type=ft.KeyboardType.NUMBER)
        salida = texto_salida(18)
        resumen = ft.Text()
        ultimo = {"nombre": "resultado", "lineas": []}

        def publicar(nombre: str, elementos: list[str], nota: str):
            ultimo["nombre"], ultimo["lineas"] = nombre, elementos
            salida.value = "\n".join(lg.mostrar(x) for x in elementos)
            resumen.value = f"{nota}  —  {len(elementos)} elementos"
            self.page.update()

        def operacion_cadena(nombre, funcion):
            def manejar(_):
                w = cadena.value or ""
                publicar(nombre, funcion(w), f"{nombre} de w = {lg.mostrar(w)} (|w| = {len(w)})")
            return manejar

        def operacion_cerradura(nombre, funcion):
            def manejar(_):
                try:
                    n = int(longitud.value)
                    publicar(nombre, funcion(alfabeto.value or "", n),
                             f"{nombre} con Σ = {{{', '.join(lg.normalizar_alfabeto(alfabeto.value or ''))}}}, n = {n}")
                except ValueError as e:
                    self.aviso(str(e), error=True)
            return manejar

        def exportar(_):
            if not ultimo["lineas"]:
                self.aviso("Primero calcule algun resultado.", error=True)
                return
            ruta = guardar(f"lenguajes/{ultimo['nombre'].lower().replace(' ', '_')}.txt",
                           resumen.value + "\n\n" + (salida.value or "") + "\n")
            self.aviso(f"Guardado en {ruta_relativa(ruta)}")

        return ft.Column([
            self.encabezado("Operaciones sobre cadenas y lenguajes", "Practica 1 · Ejercicio 5"),
            ft.Text("Convencion: λ (cadena vacia) figura entre los prefijos, los sufijos y las subcadenas."),
            ft.Row([cadena, boton("Prefijos", operacion_cadena("Prefijos", lg.prefijos)),
                    boton("Sufijos", operacion_cadena("Sufijos", lg.sufijos)),
                    boton("Subcadenas", operacion_cadena("Subcadenas", lg.subcadenas))], wrap=True),
            ft.Row([alfabeto, longitud, boton("Σ* (Kleene)", operacion_cerradura("Cerradura de Kleene", lg.cerradura_kleene)),
                    boton("Σ+ (positiva)", operacion_cerradura("Cerradura positiva", lg.cerradura_positiva))], wrap=True),
            ft.Text(f"Limite: {lg.LIMITE_CADENAS:,} cadenas (el total crece como |Σ|ⁿ).", size=12,
                    color=ft.Colors.ON_SURFACE_VARIANT),
            resumen, salida,
            boton("Guardar en archivo de texto", exportar, ft.Icons.SAVE),
        ], scroll=ft.ScrollMode.AUTO, spacing=12, expand=True)

    # ================================================ 2. AUTOMATAS (Practicas 2 y 3)
    def vista_automatas(self) -> ft.Control:
        info = ft.Text(selectable=True)
        vista_tabla = ft.Container()
        vista_dibujo = ft.Container()
        registro = texto_salida(14)

        def refrescar(resaltados: set[str] | None = None, mensaje: str | None = None):
            a = self.actual
            if a is None:
                info.value = "Cargue o defina un automata."
                vista_tabla.content = None
                vista_dibujo.content = dibujar(None)
            else:
                errores = a.validar()
                info.value = (f"{a.nombre or 'Automata'} · {a.tipo()} · {len(a.estados)} estados · "
                              f"Σ = {{{', '.join(a.alfabeto)}}} · inicial {a.inicial} · "
                              f"F = {conjunto(a.finales)}" + (f"\n⚠ {'; '.join(errores)}" if errores else ""))
                vista_tabla.content = tabla_automata(a)
                vista_dibujo.content = dibujar(a, resaltados=resaltados)
                estado_lambda.options = [ft.DropdownOption(q) for q in a.estados]
            if mensaje is not None:
                registro.value = mensaje
            self.page.update()

        def establecer(a: Automata, mensaje: str, guardar_historial: bool = True):
            if guardar_historial and self.actual is not None:
                self.historial.append(self.actual)
            self.actual = a
            refrescar(mensaje=mensaje)

        self.establecer_automata = establecer  # lo usan otras secciones

        # ---- cargar
        lista = ft.Dropdown(label="Archivo del repositorio", width=420, enable_filter=True, editable=True,
                            options=[ft.DropdownOption(r) for r in archivos_automata()])
        pegado = ft.TextField(label="…o pegue aqui el contenido .jff / .json / .xml", multiline=True,
                              min_lines=3, max_lines=6, text_style=ft.TextStyle(font_family=MONO, size=12))

        def recargar_lista(_=None):
            lista.options = [ft.DropdownOption(r) for r in archivos_automata()]
            self.page.update()

        def cargar_archivo(_):
            if not lista.value:
                self.aviso("Elija un archivo.", error=True)
                return
            try:
                a = fm.leer_archivo(RAIZ / lista.value)
                establecer(a, f"Cargado {lista.value}: {a}")
            except (fm.ErrorFormato, OSError) as e:
                self.aviso(str(e), error=True)

        def cargar_texto(_):
            try:
                a = fm.leer_texto(pegado.value or "", nombre="pegado")
                establecer(a, f"Cargado desde texto: {a}")
            except fm.ErrorFormato as e:
                self.aviso(str(e), error=True)

        # ---- definicion manual con tabla interactiva
        m_alfabeto = ft.TextField(label="Alfabeto (separado por comas)", value="a,b", width=220)
        m_estados = ft.TextField(label="Estados", value="q0,q1,q2", width=220)
        m_inicial = ft.TextField(label="Inicial", value="q0", width=100)
        m_finales = ft.TextField(label="Aceptacion", value="q2", width=140)
        m_lambda = ft.Checkbox(label="Columna λ", value=False)
        rejilla = ft.Column()
        celdas: dict[tuple[str, str], ft.TextField] = {}

        def separar(texto):
            return [x.strip() for x in (texto or "").split(",") if x.strip()]

        def generar_rejilla(_=None):
            celdas.clear()
            simbolos = separar(m_alfabeto.value) + ([LAMBDA] if m_lambda.value else [])
            filas = [ft.Row([ft.Text("δ", width=70, weight=ft.FontWeight.BOLD)] +
                            [ft.Text(mostrar(s), width=90, weight=ft.FontWeight.BOLD) for s in simbolos])]
            previo = self.actual
            for q in separar(m_estados.value):
                fila = [ft.Text(q, width=70, font_family=MONO)]
                for s in simbolos:
                    valor = ""
                    if previo and q in previo.estados:
                        valor = ",".join(sorted(previo.destinos(q, s)))
                    campo = ft.TextField(value=valor, width=90, dense=True, hint_text="—",
                                         text_style=ft.TextStyle(font_family=MONO, size=12))
                    celdas[(q, s)] = campo
                    fila.append(campo)
                filas.append(ft.Row(fila))
            rejilla.controls = filas + [ft.Text("Cada celda admite varios destinos separados por comas "
                                                "(automata no determinista).", size=12)]
            self.page.update()

        def aplicar_definicion(_):
            estados = separar(m_estados.value)
            a = Automata(estados, separar(m_alfabeto.value), (m_inicial.value or "").strip(),
                         set(separar(m_finales.value)), {}, "manual")
            for (q, s), campo in celdas.items():
                for d in separar(campo.value):
                    a.agregar_transicion(q, s, d)
            errores = a.validar()
            if errores:
                self.aviso("; ".join(errores), error=True)
                return
            establecer(a, f"Definido manualmente: {a}")

        def editar_actual(_):
            if self.actual is None:
                return
            a = self.actual
            m_alfabeto.value = ",".join(a.alfabeto)
            m_estados.value = ",".join(a.estados)
            m_inicial.value = a.inicial
            m_finales.value = ",".join(q for q in a.estados if q in a.finales)
            m_lambda.value = a.tiene_lambda()
            generar_rejilla()

        # ---- simulacion
        cadena = ft.TextField(label="Cadena", width=260)
        traza: list[dict] = []
        paso = {"i": 0}
        texto_paso = ft.Text(font_family=MONO, selectable=True)

        def validar(_):
            if self.actual is None:
                return
            w = cadena.value or ""
            ok, pasos = cv.simular_afn(self.actual, w)
            lineas = [f"Cadena: {mostrar(w)}  →  {'ACEPTADA' if ok else 'RECHAZADA'}", ""]
            if self.actual.es_determinista():
                _, tr = self.actual.simular_afd(w)
                for t in tr:
                    lineas.append(f"δ({t['estado']}, {t['simbolo']}) = {t['siguiente'] or '∅ (sin transicion)'}")
            else:
                for p in pasos:
                    if p["simbolo"] is None:
                        lineas.append(f"inicio: cerradura λ({self.actual.inicial}) = {conjunto(p['despues'])}")
                    else:
                        lineas.append(f"lee {p['simbolo']}: {conjunto(p['antes'])} → mover {conjunto(p['mover'])}"
                                      f" → cerradura λ {conjunto(p['despues'])}")
            refrescar(mensaje="\n".join(lineas))

        def iniciar_paso(_):
            if self.actual is None:
                return
            traza.clear()
            traza.extend(cv.simular_afn(self.actual, cadena.value or "")[1])
            paso["i"] = 0
            mostrar_paso()

        def mostrar_paso():
            if not traza:
                return
            p = traza[paso["i"]]
            w = cadena.value or ""
            leido = w[:paso["i"]]
            if p["simbolo"] is None:
                texto_paso.value = f"Paso 0/{len(w)} · estados activos tras la cerradura λ: {conjunto(p['despues'])}"
            else:
                texto_paso.value = (f"Paso {paso['i']}/{len(w)} · leido: {leido} · resta: {w[paso['i']:] or LAMBDA_VISIBLE}\n"
                                    f"antes {conjunto(p['antes'])} --{p['simbolo']}--> {conjunto(p['mover'])}"
                                    f"  · tras cerradura λ: {conjunto(p['despues'])}")
            if paso["i"] == len(traza) - 1:
                ok = bool(p["despues"] & self.actual.finales)
                texto_paso.value += f"\nFin: {'ACEPTADA' if ok else 'RECHAZADA'}"
            refrescar(resaltados=set(p["despues"]))

        def mover_paso(delta):
            def manejar(_):
                if traza:
                    paso["i"] = max(0, min(len(traza) - 1, paso["i"] + delta))
                    mostrar_paso()
            return manejar

        # ---- cerradura lambda
        estado_lambda = ft.Dropdown(label="Estado", width=160)

        def ver_cerradura(_):
            if self.actual is None or not estado_lambda.value:
                return
            cl = cv.cerradura_lambda(self.actual, estado_lambda.value)
            refrescar(resaltados=set(cl), mensaje=f"cerradura λ({estado_lambda.value}) = {conjunto(cl)}")

        def todas_cerraduras(_):
            if self.actual is None:
                return
            lineas = [f"cerradura λ({q}) = {conjunto(c)}" for q, c in cv.cerraduras(self.actual).items()]
            refrescar(mensaje="\n".join(lineas))

        # ---- conversiones (Practica 3)
        def convertir_lambda(_):
            if self.actual is None:
                return
            nuevo, reg = cv.eliminar_lambda(self.actual)
            lineas = ["ELIMINACION DE TRANSICIONES λ", "δ'(q,a) = cerradura λ(mover(cerradura λ(q), a))", ""]
            lineas += [f"cerradura λ({q}) = {conjunto(c)}" for q, c in reg["cerraduras"].items()]
            lineas += ["", "Transiciones λ eliminadas: " + (", ".join(f"{o}→{d}" for o, d in reg["lambda_eliminadas"]) or "ninguna"),
                       "Transiciones añadidas:"]
            lineas += [f"  δ'({o}, {s}) ∋ {d}" for o, s, d in reg["añadidas"]] or ["  ninguna"]
            lineas += ["Nuevos estados de aceptacion: " + (", ".join(reg["nuevas_finales"]) or "ninguno")]
            establecer(nuevo, "\n".join(lineas))

        def convertir_subconjuntos(_):
            if self.actual is None:
                return
            nuevo, tbl = cv.subconjuntos(self.actual)
            lineas = ["CONSTRUCCION DE SUBCONJUNTOS (solo los alcanzables, en orden de generacion)", ""]
            for f in tbl:
                trs = "  ".join(f"{a}→{d}" for a, d in f["transiciones"].items())
                marca = "  * aceptacion: contiene un estado final" if f["aceptacion"] else ""
                lineas.append(f"{f['nombre']} = {conjunto(f['conjunto'])}:  {trs}{marca}")
            establecer(nuevo, "\n".join(lineas))

        def convertir_minimo(_):
            if self.actual is None:
                return
            try:
                nuevo, reg = cv.minimizar(self.actual)
            except ValueError as e:
                self.aviso(str(e), error=True)
                return
            lineas = ["MINIMIZACION POR REFINAMIENTO DE PARTICIONES",
                      "Inaccesibles eliminados: " + (", ".join(reg["inaccesibles"]) or "ninguno"),
                      "Estado trampa agregado: " + ("si" if reg["trampa_agregada"] else "no"), ""]
            for i, ronda in enumerate(reg["rondas"]):
                lineas.append(f"Ronda {i}: " + "  ".join(conjunto(b) for b in ronda))
            lineas += ["", f"Estados: {reg['estados_antes']} → {reg['estados_despues']}"]
            lineas += [f"{n} = {conjunto(c)}" for n, c in nuevo.composicion.items()]
            establecer(nuevo, "\n".join(lineas))

        def deshacer(_):
            if self.historial:
                self.actual = self.historial.pop()
                refrescar(mensaje="Se restauro el automata anterior.")

        # ---- equivalencia
        otro = ft.Dropdown(label="Segundo automata", width=420, enable_filter=True, editable=True,
                           options=[ft.DropdownOption(r) for r in archivos_automata()])

        def comparar(_):
            if self.actual is None or not otro.value:
                return
            try:
                b = fm.leer_archivo(RAIZ / otro.value)
            except fm.ErrorFormato as e:
                self.aviso(str(e), error=True)
                return
            iguales, detalle, contra = cv.equivalentes(self.actual, b)
            texto = ("EQUIVALENTES. " if iguales else "NO equivalentes. ") + detalle
            if contra is not None:
                texto += f"\nCadena mas corta que los distingue: {mostrar(contra)}"
            refrescar(mensaje=texto)

        # ---- validacion por lote
        lote = ft.TextField(label="Cadenas (una por linea) o ruta de un .txt del repositorio", multiline=True,
                            min_lines=3, max_lines=6)

        def validar_lote(_):
            if self.actual is None:
                return
            texto = lote.value or ""
            posible = RAIZ / texto.strip()
            if "\n" not in texto.strip() and texto.strip().endswith(".txt") and posible.exists():
                texto = posible.read_text(encoding="utf-8")
            cadenas = ["" if c.strip() in (LAMBDA_VISIBLE, "λ") else c.rstrip("\r")
                       for c in texto.splitlines() if c.strip()]
            informe = cv.informe_lote(cv.validar_lote(self.actual, cadenas))
            ruta = guardar(f"lote_{datetime.now():%Y%m%d_%H%M%S}.txt", informe + "\n")
            refrescar(mensaje=informe + f"\n\nInforme guardado en {ruta_relativa(ruta)}")

        # ---- exportacion
        nombre_exp = ft.TextField(label="Nombre base", value="automata", width=200)

        def exportar(_):
            if self.actual is None:
                return
            rutas = [fm.escribir_archivo(self.actual, SALIDAS / f"{nombre_exp.value or 'automata'}{ext}")
                     for ext in (".jff", ".json", ".xml")]
            recargar_lista()
            self.aviso("Exportado: " + ", ".join(ruta_relativa(r) for r in rutas))

        controles = ft.Column([
            seccion("Cargar", [ft.Row([lista, ft.IconButton(ft.Icons.REFRESH, on_click=recargar_lista,
                                                            tooltip="Volver a buscar archivos")]),
                               boton("Cargar archivo", cargar_archivo, ft.Icons.FOLDER_OPEN, True),
                               pegado, boton("Cargar texto", cargar_texto)], abierta=True),
            seccion("Definir con tabla interactiva", [
                ft.Row([m_alfabeto, m_estados], wrap=True), ft.Row([m_inicial, m_finales, m_lambda], wrap=True),
                ft.Row([boton("Generar tabla", generar_rejilla), boton("Editar el actual", editar_actual),
                        boton("Aplicar", aplicar_definicion, principal=True)], wrap=True),
                ft.Row([rejilla], scroll=ft.ScrollMode.AUTO)]),
            seccion("Simular cadenas", [
                ft.Row([cadena, boton("Validar", validar, principal=True)], wrap=True),
                ft.Row([boton("Paso a paso", iniciar_paso), ft.IconButton(ft.Icons.CHEVRON_LEFT, on_click=mover_paso(-1)),
                        ft.IconButton(ft.Icons.CHEVRON_RIGHT, on_click=mover_paso(1))]),
                texto_paso]),
            seccion("Cerradura λ", [ft.Row([estado_lambda, boton("Ver", ver_cerradura),
                                            boton("Todas", todas_cerraduras)], wrap=True)]),
            seccion("Convertir (Practica 3)", [
                ft.Text("Cada paso reemplaza al automata actual; use Deshacer para regresar.", size=12),
                ft.Row([boton("1. Eliminar λ", convertir_lambda), boton("2. Subconjuntos", convertir_subconjuntos),
                        boton("3. Minimizar", convertir_minimo), boton("Deshacer", deshacer, ft.Icons.UNDO)], wrap=True)]),
            seccion("Equivalencia de automatas", [otro, boton("Comparar con el actual", comparar)]),
            seccion("Validar varias cadenas", [lote, boton("Validar y guardar informe", validar_lote)]),
            seccion("Exportar", [ft.Row([nombre_exp, boton("Guardar .jff, .json y .xml", exportar, ft.Icons.SAVE)])]),
        ], scroll=ft.ScrollMode.AUTO, width=520, spacing=0)

        panel = ft.Column([info, vista_dibujo, vista_tabla, ft.Text("Registro", weight=ft.FontWeight.BOLD), registro],
                          scroll=ft.ScrollMode.AUTO, expand=True, spacing=10)
        refrescar()
        return ft.Column([
            self.encabezado("Simulador de automatas finitos", "Practicas 2 y 3 · AFD, AFN, AFN-λ y conversiones"),
            ft.Row([controles, ft.VerticalDivider(width=1), panel], expand=True,
                   vertical_alignment=ft.CrossAxisAlignment.START),
        ], expand=True)

    # ============================================ 3. ER -> AUTOMATA (P4, Ejercicio 2)
    def vista_er_automata(self) -> ft.Control:
        datos = json.loads((RAIZ / "casos/practica4/ejercicios_er.json").read_text(encoding="utf-8"))
        casos = [c for c in datos["casos"] if c.get("expresion")]
        expresion = ft.TextField(label="Expresion regular (notacion del curso)", value="(a + b)*abb",
                                 text_style=ft.TextStyle(font_family=MONO, size=16), expand=True)
        clases = ft.TextField(label="Clases de simbolos (una por linea: NOMBRE = a + b + c  o  NOMBRE = a-z0-9)",
                              multiline=True, min_lines=2, max_lines=4,
                              hint_text="V = a + e + i + o + u",
                              helper="Predefinidas: " + ", ".join(f"[{k}]" for k in er.CLASES_PREDEFINIDAS))
        alfabeto = ft.TextField(label="Simbolos extra del alfabeto (opcional)", width=260)
        error = ft.Text(font_family=MONO, color=ft.Colors.ERROR, selectable=True)
        resumen = ft.Container()
        etapa = ft.Dropdown(label="Automata a mostrar", width=280, value="thompson", options=[
            ft.DropdownOption("thompson", "AFN-λ paso a paso (Thompson)"),
            ft.DropdownOption("afn", "AFN sin transiciones λ"),
            ft.DropdownOption("afd", "AFD por subconjuntos"),
            ft.DropdownOption("minimo", "AFD minimo")])
        deslizador = ft.Slider(min=0, max=1, divisions=1, value=0, label="{value}", expand=True)
        paso_info = ft.Text(selectable=True)
        dibujo_c, tabla_c, detalle = ft.Container(), ft.Container(), texto_salida(10)
        cadena = ft.TextField(label="Cadena a validar", width=260)
        veredicto = ft.Text(size=16, weight=ft.FontWeight.BOLD)
        ocultar_trampa = ft.Checkbox(label="Ocultar estado trampa en el dibujo", value=True)
        estado: dict = {"p": None}
        ejemplos = ft.Dropdown(label="Casos de prueba (casos/practica4)", width=320,
                               options=[ft.DropdownOption(str(i), f"L{c['lista']}-{c['ejercicio']}: {c['expresion']}")
                                        for i, c in enumerate(casos)])

        def insertar(simbolo):
            def manejar(_):
                expresion.value = (expresion.value or "") + simbolo
                self.page.update()
            return manejar

        def elegir_ejemplo(_):
            c = casos[int(ejemplos.value)]
            expresion.value = c["expresion"]
            alfabeto.value = c.get("alfabeto", "")
            construir()

        def construir(_=None):
            error.value = ""
            try:
                cl = er.leer_clases(clases.value or "")
                p = pipeline(expresion.value or "", cl, set(alfabeto.value or ""))
            except ValueError as e:  # ErrorExpresion es subclase de ValueError
                error.value = f"{e}\n{e.señalar()}" if isinstance(e, er.ErrorExpresion) else str(e)
                estado["p"] = None
                resumen.content = dibujo_c.content = tabla_c.content = None
                paso_info.value = detalle.value = veredicto.value = ""
                self.page.update()
                return
            estado["p"] = p
            filas = [[n, str(e), str(t)] for n, e, t in p.resumen()]
            reg = p.registro_minimo
            resumen.content = ft.Column([
                ft.Text(f"Expresion analizada: {er.a_texto(p.arbol)}   ·   Σ = {{{', '.join(p.minimo.alfabeto)}}}",
                        font_family=MONO, selectable=True),
                tabla(["Etapa", "Estados", "Transiciones"], filas),
                ft.Text(f"Minimizacion: {len(p.afd.estados)} estados en el AFD de subconjuntos"
                        f"{' + 1 trampa' if reg['trampa_agregada'] else ''} → {len(p.minimo.estados)} en el AFD minimo"
                        f" (el estado trampa, si existe, cuenta).", size=12)])
            deslizador.max = max(len(p.thompson.pasos) - 1, 1)
            deslizador.divisions = max(len(p.thompson.pasos) - 1, 1)
            deslizador.value = len(p.thompson.pasos) - 1
            mostrar_etapa()

        def mostrar_etapa(_=None):
            p = estado["p"]
            if p is None:
                return
            deslizador.visible = etapa.value == "thompson"
            if etapa.value == "thompson":
                i = int(deslizador.value)
                pt = p.thompson.pasos[i]
                a = pt.automata
                paso_info.value = f"Paso {i + 1}/{len(p.thompson.pasos)} · subexpresion: {pt.subexpresion}\n{pt.regla}"
                detalle.value = "\n".join(f"{o} --{mostrar(s)}--> {d}" for o, s, d in a.lista_transiciones())
            elif etapa.value == "afn":
                a = p.afn
                r = p.registro_lambda
                paso_info.value = "AFN sin λ: δ'(q,a) = cerradura λ(mover(cerradura λ(q), a))"
                detalle.value = "\n".join(
                    [f"cerradura λ({q}) = {conjunto(c)}" for q, c in r["cerraduras"].items() if q in p.afn.estados] +
                    ["", "Nuevos estados de aceptacion: " + (", ".join(r["nuevas_finales"]) or "ninguno")])
            elif etapa.value == "afd":
                a = p.afd
                paso_info.value = "Subconjuntos alcanzables, en el orden en que se generaron:"
                detalle.value = "\n".join(
                    f"{f['nombre']} = {conjunto(f['conjunto'])}{'  *' if f['aceptacion'] else ''}" for f in p.tabla_subconjuntos)
            else:
                a = p.minimo
                reg = p.registro_minimo
                paso_info.value = f"AFD minimo: {reg['estados_despues']} estados ({len(reg['rondas'])} rondas de refinamiento)"
                detalle.value = "\n".join(
                    [f"Ronda {i}: " + "  ".join(conjunto(b) for b in r) for i, r in enumerate(reg["rondas"])] +
                    [""] + [f"{n} = {conjunto(c)}" for n, c in a.composicion.items()])
            visible = cv.sin_trampa(a) if (ocultar_trampa.value and etapa.value in ("afd", "minimo")) else a
            dibujo_c.content = dibujar(visible, ancho=700, alto=440)
            tabla_c.content = tabla_automata(a) if len(a.alfabeto) <= 16 else ft.Text(
                f"Alfabeto de {len(a.alfabeto)} simbolos: la tabla se omite en pantalla; exporte a .jff para verla completa.")
            self.page.update()

        def validar(_):
            p = estado["p"]
            if p is None:
                return
            w = cadena.value or ""
            ok = p.acepta(w)
            fuera = [c for c in w if c not in p.minimo.alfabeto]
            veredicto.value = (f"{mostrar(w)}: {'ACEPTADA' if ok else 'RECHAZADA'}" +
                               (f" (simbolos fuera de Σ: {''.join(sorted(set(fuera)))})" if fuera else ""))
            veredicto.color = ft.Colors.GREEN if ok else ft.Colors.ERROR
            if not fuera:
                _, tr = p.minimo.simular_afd(w)
                ruta = {p.minimo.inicial} | {t["siguiente"] for t in tr if t["siguiente"]}
                etapa.value = "minimo"
                mostrar_etapa()
                dibujo_c.content = dibujar(cv.sin_trampa(p.minimo) if ocultar_trampa.value else p.minimo,
                                           resaltados=ruta, ancho=700, alto=440)
            self.page.update()

        def exportar(_):
            p = estado["p"]
            if p is None:
                return
            base = re.sub(r"[^A-Za-z0-9_-]+", "_", (ejemplos.value and
                                                     f"L{casos[int(ejemplos.value)]['lista']}-{casos[int(ejemplos.value)]['ejercicio']}")
                          or "expresion").strip("_")
            carpeta = SALIDAS / "er-a-automata" / base
            for nombre, a in [("1-afn-lambda", p.thompson.afn_lambda), ("2-afn", p.afn),
                              ("3-afd", p.afd), ("4-afd-minimo", p.minimo)]:
                fm.escribir_archivo(a, carpeta / f"{nombre}.jff")
            guardar(f"er-a-automata/{base}/expresion.txt", (expresion.value or "") + "\n")
            self.aviso(f"Exportados 4 archivos .jff en {ruta_relativa(carpeta)}")

        def al_simulador(_):
            p = estado["p"]
            if p is None:
                return
            if not hasattr(self, "establecer_automata"):
                self.construidas[1] = self.vista_automatas()
            self.establecer_automata(p.minimo.copia(f"AFD minimo de {expresion.value}"),
                                     f"Recibido desde ER → Automata: {expresion.value}")
            self.ir(1)

        etapa.on_select = mostrar_etapa
        deslizador.on_change = mostrar_etapa
        ocultar_trampa.on_change = mostrar_etapa
        ejemplos.on_select = elegir_ejemplo
        expresion.on_submit = construir
        cadena.on_submit = validar

        construir()
        return ft.Column([
            self.encabezado("De expresion regular a automata",
                            "Practica 4 · Ejercicio 2 · primera parte del teorema de Kleene"),
            ft.Text("Notacion: + union · yuxtaposicion concatenacion · * cerradura · λ palabra vacia · ∅ vacio · "
                    "[D] clase · \\c caracter literal. Precedencia: * > concatenacion > +.", size=12),
            ft.Row([expresion, boton("Construir", construir, ft.Icons.PLAY_ARROW, True)]),
            ft.Row([ft.Text("Insertar:")] + [ft.TextButton(s, on_click=insertar(s)) for s in ["λ", "∅", "+", "*", "(", ")"]] +
                   [ejemplos], wrap=True),
            ft.Row([clases], vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Row([alfabeto]),
            error, resumen,
            ft.Row([etapa, ocultar_trampa, boton("Exportar los 4 a .jff", exportar, ft.Icons.SAVE),
                    boton("Abrir AFD minimo en el simulador", al_simulador)], wrap=True),
            deslizador, paso_info,
            ft.Row([dibujo_c, ft.Column([ft.Text("Detalle", weight=ft.FontWeight.BOLD), detalle], expand=True)],
                   vertical_alignment=ft.CrossAxisAlignment.START, wrap=True),
            tabla_c,
            ft.Row([cadena, boton("Validar", validar, principal=True), veredicto], wrap=True),
        ], scroll=ft.ScrollMode.AUTO, spacing=10, expand=True)

    # ============================================ 4. AUTOMATA -> ER (P4, Ejercicio 3)
    def vista_automata_er(self) -> ft.Control:
        lista = ft.Dropdown(label="AFD (.jff, .json o .xml)", width=440, enable_filter=True, editable=True,
                            options=[ft.DropdownOption(r) for r in archivos_automata()])
        orden = ft.TextField(label="Orden de eliminacion (opcional, separado por comas)", width=380)
        estado_txt = ft.Text(selectable=True)
        resultado = ft.Text(font_family=MONO, size=16, selectable=True, weight=ft.FontWeight.BOLD)
        deslizador = ft.Slider(min=0, max=1, divisions=1, value=0, label="{value}", expand=True)
        dibujo_c, tabla_c = ft.Container(), ft.Container()
        jflap = ft.TextField(label="Expresion obtenida con JFLAP (use ! o λ para la palabra vacia)", expand=True,
                             text_style=ft.TextStyle(font_family=MONO))
        comparacion = ft.Text(selectable=True)
        datos: dict = {"pasos": [], "automata": None, "expr": None}

        def convertir(_=None):
            if not lista.value:
                self.aviso("Elija un archivo.", error=True)
                return
            try:
                a = fm.leer_archivo(RAIZ / lista.value)
                orden_l = [x.strip() for x in (orden.value or "").split(",") if x.strip()] or None
                expr, pasos = elim.eliminar_estados(a, orden_l)
            except (fm.ErrorFormato, ValueError) as e:
                estado_txt.value = f"✗ {e}"
                resultado.value = ""
                datos["pasos"] = []
                self.page.update()
                return
            datos.update(pasos=pasos, automata=a, expr=expr)
            estado_txt.value = f"✓ {a.nombre}: AFD con {len(a.estados)} estados. Mueva el control para ver cada eliminacion."
            resultado.value = f"ER = {er.a_texto(expr)}"
            deslizador.max = max(len(pasos) - 1, 1)
            deslizador.divisions = max(len(pasos) - 1, 1)
            deslizador.value = 0
            mostrar()

        def mostrar(_=None):
            pasos = datos["pasos"]
            if not pasos:
                return
            p = pasos[int(deslizador.value)]
            etiquetas = {(i, j): er.a_texto(r) for (i, j), r in p.aristas.items()}
            finales = {p.estados[-1]}
            dibujo_c.content = dibujar(estados=p.estados, inicial=p.estados[0], finales=finales,
                                       etiquetas=etiquetas, ancho=680, alto=420)
            titulo = "Automata generalizado inicial" if p.eliminado is None else f"Tras eliminar {p.eliminado}"
            tabla_c.content = ft.Column([ft.Text(titulo, weight=ft.FontWeight.BOLD),
                                         tabla(["Desde", "Hacia", "Expresion"], [list(f) for f in p.tabla()])])
            self.page.update()

        def comparar(_):
            if datos["expr"] is None:
                return
            texto = (jflap.value or "").replace("!", "λ")
            try:
                otra = pipeline(texto, alfabeto=set(datos["automata"].alfabeto)).minimo
                propia = pipeline(er.a_texto(datos["expr"]), alfabeto=set(datos["automata"].alfabeto)).minimo
            except er.ErrorExpresion as e:
                comparacion.value = f"{e}\n{e.señalar()}"
                self.page.update()
                return
            iguales, detalle, contra = cv.equivalentes(propia, otra)
            comparacion.value = ("Las dos expresiones son EQUIVALENTES (sus AFD minimos son isomorfos). " if iguales
                                 else f"NO son equivalentes: {detalle} Cadena que las distingue: {mostrar(contra or '')}")
            self.page.update()

        def recargar_lista(_):
            lista.options = [ft.DropdownOption(r) for r in archivos_automata()]
            self.page.update()

        deslizador.on_change = mostrar
        return ft.Column([
            self.encabezado("De automata a expresion regular",
                            "Practica 4 · Ejercicio 3 · eliminacion de estados (segunda parte del teorema de Kleene)"),
            ft.Row([lista, ft.IconButton(ft.Icons.REFRESH, on_click=recargar_lista, tooltip="Volver a buscar archivos")]),
            ft.Row([orden, boton("Verificar y convertir", convertir, ft.Icons.PLAY_ARROW, True)], wrap=True),
            estado_txt, resultado, deslizador,
            ft.Row([dibujo_c, tabla_c], wrap=True, vertical_alignment=ft.CrossAxisAlignment.START),
            ft.Divider(),
            ft.Text("Comparar con el resultado de JFLAP", weight=ft.FontWeight.BOLD),
            ft.Row([jflap, boton("Comparar", comparar)]), comparacion,
        ], scroll=ft.ScrollMode.AUTO, spacing=10, expand=True)

    # =============================================== 5. VALIDADORES (P4, Ejercicio 4)
    def vista_validadores(self) -> ft.Control:
        selector = ft.Dropdown(label="Validador", width=340, value="correo",
                               options=[ft.DropdownOption(k, v.nombre) for k, v in val.VALIDADORES.items()])
        ficha = ft.Column(spacing=6)
        entrada = ft.TextField(label="Texto a validar", expand=True, text_style=ft.TextStyle(font_family=MONO))
        veredicto = ft.Column()
        dibujo_c = ft.Container()
        congruencia = ft.Text(selectable=True)

        def etiqueta(t):
            return ft.Text(t, weight=ft.FontWeight.BOLD)

        def codigo(t):
            return ft.Container(ft.Text(t, font_family=MONO, selectable=True, size=13), padding=8,
                                bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST, border_radius=6)

        def mostrar_ficha(_=None):
            v = val.VALIDADORES[selector.value]
            p = v.automata()
            reg = p.registro_minimo
            clases = "\n".join(describir_clase(k, c) for k, c in v.clases_usadas().items())
            ficha.controls = [
                ft.Text(v.descripcion),
                etiqueta("Expresion en la notacion del curso"), codigo(er.a_texto(p.arbol)),
                etiqueta("Clases declaradas"), codigo(clases),
                etiqueta("Traduccion al modulo re de Python (escrita a mano)"), codigo(v.regex_python),
                etiqueta("Traduccion automatica desde el arbol (expresiones.a_python)"),
                codigo(val.traduccion_automatica(v.clave)),
                etiqueta("Automata"),
                tabla(["Etapa", "Estados", "Transiciones"], [[n, str(e), str(t)] for n, e, t in p.resumen()]),
                ft.Text(f"Estados antes de minimizar: {len(p.afd.estados)} (AFD de subconjuntos"
                        f"{', mas el estado trampa al completarlo' if reg['trampa_agregada'] else ''}) · "
                        f"despues: {len(p.minimo.estados)} (incluye la trampa).", size=12),
                etiqueta("Estandar consultado"), ft.Text(v.estandar),
                etiqueta("Casos que quedan fuera"), ft.Text(v.limitaciones),
                etiqueta("Ejemplos"), ft.Text("Validos: " + " · ".join(v.validos)),
                ft.Text("Invalidos: " + " · ".join(v.invalidos)),
            ]
            dibujo_c.content = dibujar(cv.sin_trampa(p.minimo), ancho=760, alto=500)
            veredicto.controls = []
            congruencia.value = ""
            self.page.update()

        def validar(_=None):
            v = val.VALIDADORES[selector.value]
            texto = entrada.value or ""
            por_afd, por_re = v.valida(texto), v.valida_re(texto)
            color = ft.Colors.GREEN if por_afd else ft.Colors.ERROR
            veredicto.controls = [
                ft.Text(f"AFD minimo: {'VALIDO' if por_afd else 'INVALIDO'}", color=color, size=18,
                        weight=ft.FontWeight.BOLD),
                ft.Text(f"re.fullmatch: {'VALIDO' if por_re else 'INVALIDO'}  ·  "
                        f"{'coinciden ✓' if por_afd == por_re else 'NO coinciden ✗'}")]
            self.page.update()

        def probar(_):
            v = val.VALIDADORES[selector.value]
            casos = val.generar_casos(v.clave)
            discrepan = [c for c in casos if v.valida(c) != v.valida_re(c)]
            validas = sum(v.valida(c) for c in casos)
            congruencia.value = (f"{len(casos)} cadenas generadas ({validas} validas, {len(casos) - validas} invalidas). "
                                 f"Discrepancias entre el AFD y re.fullmatch: {len(discrepan)}"
                                 + (f" → {discrepan[:5]}" if discrepan else " ✓"))
            self.page.update()

        def exportar(_):
            v = val.VALIDADORES[selector.value]
            p = v.automata()
            carpeta = SALIDAS / "validadores"
            fm.escribir_archivo(p.afd, carpeta / f"{v.clave}-afd.jff")
            fm.escribir_archivo(p.minimo, carpeta / f"{v.clave}-afd-minimo.jff")
            self.aviso(f"Exportados {v.clave}-afd.jff y {v.clave}-afd-minimo.jff en {ruta_relativa(carpeta)}")

        selector.on_select = mostrar_ficha
        entrada.on_submit = validar
        entrada.on_change = validar
        mostrar_ficha()
        return ft.Column([
            self.encabezado("Validadores con expresiones regulares", "Practica 4 · Ejercicio 4"),
            ft.Row([selector, boton("Exportar AFD a .jff", exportar, ft.Icons.SAVE),
                    boton("Probar congruencia (≥500 cadenas)", probar)], wrap=True),
            ft.Row([entrada, boton("Validar", validar, principal=True)]), veredicto, congruencia,
            ft.Row([ft.Container(ficha, width=560), dibujo_c], wrap=True,
                   vertical_alignment=ft.CrossAxisAlignment.START),
        ], scroll=ft.ScrollMode.AUTO, spacing=10, expand=True)


def main(page: ft.Page):
    App(page)


if __name__ == "__main__":
    os.chdir(RAIZ)
    # FLET_NO_CDN=true sirve CanvasKit y las fuentes desde el propio paquete
    # (util sin internet o detras de un proxy que bloquea el CDN).
    ft.run(main, no_cdn=os.getenv("FLET_NO_CDN", "").lower() in ("1", "true", "si"))

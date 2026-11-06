"""Interfaz para obtener expresiones regulares a partir de archivos .jff."""

from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from regex_por_estados import convertir, leer_jff, revisar_determinismo


RAIZ = Path(__file__).resolve().parents[1]
CARPETA_CASOS = RAIZ / "automatas" / "practica4"


class Aplicacion:
    def __init__(self, ventana: tk.Tk) -> None:
        self.ventana = ventana
        self.ventana.title("Práctica 4 | De AFD a expresión regular")
        self.ventana.geometry("1100x720")
        self.pasos = []
        self.resultado = ""
        self.paso_actual = 0
        self.rutas: dict[str, Path] = {}
        self._crear_interfaz()
        self._cargar_ejemplos()

    def _crear_interfaz(self) -> None:
        principal = ttk.Frame(self.ventana, padding=12)
        principal.pack(fill="both", expand=True)
        ttk.Label(
            principal,
            text="Conversión de AFD a expresión regular",
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            principal,
            text="Importa un .jff determinista y avanza por la eliminación de cada estado.",
        ).pack(anchor="w", pady=(2, 10))

        controles = ttk.Frame(principal)
        controles.pack(fill="x", pady=(0, 8))
        ttk.Label(controles, text="Casos incluidos:").pack(side="left")
        self.ejemplo = tk.StringVar()
        self.lista_ejemplos = ttk.Combobox(
            controles, textvariable=self.ejemplo, state="readonly", width=46
        )
        self.lista_ejemplos.pack(side="left", padx=6)
        self.lista_ejemplos.bind("<<ComboboxSelected>>", self._seleccionar_ejemplo)
        ttk.Button(controles, text="Importar archivo .jff…", command=self._elegir_archivo).pack(
            side="left", padx=4
        )
        self.archivo = ttk.Label(controles, text="Ningún archivo seleccionado")
        self.archivo.pack(side="left", padx=10)

        self.estado = ttk.Label(principal, text="Selecciona un caso o importa un archivo .jff.")
        self.estado.pack(anchor="w", pady=(2, 8))
        self.boton_iniciar = ttk.Button(
            principal, text="Iniciar conversión", command=self._iniciar, state="disabled"
        )
        self.boton_iniciar.pack(anchor="w", pady=(0, 8))

        ttk.Label(
            principal, text="Matriz de transiciones del autómata generalizado", font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")
        marco_tabla = ttk.Frame(principal)
        marco_tabla.pack(fill="both", expand=True, pady=(4, 8))
        self.tabla = ttk.Treeview(marco_tabla, show="tree headings")
        barra_y = ttk.Scrollbar(marco_tabla, orient="vertical", command=self.tabla.yview)
        barra_x = ttk.Scrollbar(marco_tabla, orient="horizontal", command=self.tabla.xview)
        self.tabla.configure(yscrollcommand=barra_y.set, xscrollcommand=barra_x.set)
        self.tabla.grid(row=0, column=0, sticky="nsew")
        barra_y.grid(row=0, column=1, sticky="ns")
        barra_x.grid(row=1, column=0, sticky="ew")
        marco_tabla.rowconfigure(0, weight=1)
        marco_tabla.columnconfigure(0, weight=1)

        navegacion = ttk.Frame(principal)
        navegacion.pack(fill="x", pady=(0, 8))
        self.anterior = ttk.Button(navegacion, text="Paso anterior", command=lambda: self._mostrar(-1), state="disabled")
        self.anterior.pack(side="left")
        self.siguiente = ttk.Button(navegacion, text="Siguiente paso", command=lambda: self._mostrar(1), state="disabled")
        self.siguiente.pack(side="left", padx=6)
        self.indicador = ttk.Label(navegacion, text="")
        self.indicador.pack(side="left", padx=12)

        ttk.Label(principal, text="Expresión resultante", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        salida = ttk.Frame(principal)
        salida.pack(fill="x", pady=(3, 0))
        self.texto_resultado = tk.Text(salida, height=3, wrap="word", state="disabled")
        self.texto_resultado.pack(side="left", fill="x", expand=True)
        self.copiar = ttk.Button(salida, text="Copiar", command=self._copiar, state="disabled")
        self.copiar.pack(side="left", padx=(8, 0), anchor="n")

    def _cargar_ejemplos(self) -> None:
        if not CARPETA_CASOS.exists():
            return
        etiquetas = []
        for ruta in sorted(CARPETA_CASOS.rglob("*.jff")):
            etiqueta = ruta.relative_to(CARPETA_CASOS).as_posix()
            self.rutas[etiqueta] = ruta
            etiquetas.append(etiqueta)
        self.lista_ejemplos["values"] = etiquetas

    def _seleccionar_ejemplo(self, _evento: object = None) -> None:
        ruta = self.rutas.get(self.ejemplo.get())
        if ruta:
            self._cargar_archivo(ruta)

    def _elegir_archivo(self) -> None:
        nombre = filedialog.askopenfilename(
            title="Seleccionar autómata de JFLAP",
            filetypes=[("Autómatas de JFLAP", "*.jff"), ("Todos los archivos", "*.*")],
        )
        if nombre:
            self.ejemplo.set("")
            self._cargar_archivo(Path(nombre))

    def _cargar_archivo(self, ruta: Path) -> None:
        try:
            automata = leer_jff(ruta)
            problemas = revisar_determinismo(automata)
        except ValueError as error:
            self.automata = None
            self.boton_iniciar.configure(state="disabled")
            self.estado.configure(text=str(error))
            return
        self.automata = automata
        self.archivo.configure(text=str(ruta))
        if problemas:
            self.estado.configure(text="No es un AFD:\n" + "\n".join(problemas))
            self.boton_iniciar.configure(state="disabled")
        else:
            self.estado.configure(
                text=f"AFD válido: {len(automata.estados)} estados, "
                f"alfabeto {{{', '.join(automata.alfabeto)}}}, "
                f"estado inicial {automata.inicial}."
            )
            self.boton_iniciar.configure(state="normal")
        self.pasos = []
        self._limpiar_resultado()
        self._mostrar_tabla_vacia()

    def _iniciar(self) -> None:
        if getattr(self, "automata", None) is None:
            return
        try:
            self.pasos, self.resultado = convertir(self.automata)
        except ValueError as error:
            messagebox.showerror("No se puede convertir", str(error))
            return
        self.paso_actual = 0
        self._mostrar_paso()

    def _mostrar_tabla_vacia(self) -> None:
        self.tabla.delete(*self.tabla.get_children())
        self.tabla["columns"] = ()
        self.tabla.heading("#0", text="Origen")

    def _mostrar_paso(self) -> None:
        if not self.pasos:
            return
        paso = self.pasos[self.paso_actual]
        self.tabla.delete(*self.tabla.get_children())
        columnas = tuple(f"c{i}" for i in range(len(paso.estados)))
        self.tabla.configure(columns=columnas)
        self.tabla.heading("#0", text="Origen")
        self.tabla.column("#0", width=120, stretch=False)
        for columna, estado in zip(columnas, paso.estados):
            self.tabla.heading(columna, text=estado)
            self.tabla.column(columna, width=180, minwidth=100, stretch=True)
        for origen, celdas in zip(paso.estados, paso.matriz):
            self.tabla.insert("", "end", text=origen, values=celdas)
        self.indicador.configure(text=f"{paso.titulo} · Paso {self.paso_actual + 1} de {len(self.pasos)}")
        self.anterior.configure(state="normal" if self.paso_actual > 0 else "disabled")
        self.siguiente.configure(
            state="normal" if self.paso_actual < len(self.pasos) - 1 else "disabled"
        )
        if self.paso_actual == len(self.pasos) - 1:
            self._poner_resultado(self.resultado)
        else:
            self._limpiar_resultado()

    def _mostrar(self, avance: int) -> None:
        if self.pasos:
            self.paso_actual = min(max(self.paso_actual + avance, 0), len(self.pasos) - 1)
            self._mostrar_paso()

    def _limpiar_resultado(self) -> None:
        self.texto_resultado.configure(state="normal")
        self.texto_resultado.delete("1.0", "end")
        self.texto_resultado.configure(state="disabled")
        self.copiar.configure(state="disabled")

    def _poner_resultado(self, expresion: str) -> None:
        self.texto_resultado.configure(state="normal")
        self.texto_resultado.delete("1.0", "end")
        self.texto_resultado.insert("1.0", expresion)
        self.texto_resultado.configure(state="disabled")
        self.copiar.configure(state="normal")

    def _copiar(self) -> None:
        if self.resultado:
            self.ventana.clipboard_clear()
            self.ventana.clipboard_append(self.resultado)


def main() -> None:
    ventana = tk.Tk()
    Aplicacion(ventana)
    ventana.mainloop()


if __name__ == "__main__":
    main()

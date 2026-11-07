"""Genera los .jff y las tablas de evidencia de los Ejercicios 2 y 4 de la Practica 4.

Uso (desde la raiz del repositorio):
    python scripts/generar_evidencias.py

Produce:
    automatas/practica4/er-a-automata/<caso>/{1-afn-lambda,2-afn,3-afd,4-afd-minimo}.jff
    automatas/practica4/validadores/<validador>-{afd,afd-minimo}.jff
    automatas/practica4/ejemplos/*.jff        (automatas pequeños para probar el simulador)
    evidencias/practica4/resumen-er-a-automata.md
    evidencias/practica4/resumen-validadores.md
"""

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import expresiones as er  # noqa: E402
import formatos as fm  # noqa: E402
import validadores as val  # noqa: E402
from automata import Automata  # noqa: E402
from thompson import pipeline  # noqa: E402

DESTINO = RAIZ / "automatas" / "practica4"
EVIDENCIAS = RAIZ / "evidencias" / "practica4"


def er_a_automata() -> str:
    datos = json.loads((RAIZ / "casos/practica4/ejercicios_er.json").read_text(encoding="utf-8"))
    lineas = ["# Resumen: de expresion regular a automata", "",
              "Generado por `scripts/generar_evidencias.py`. Los estados del AFD minimo incluyen el "
              "estado trampa cuando el AFD necesita completarse.", "",
              "| Caso | Expresion | AFN-λ | AFN | AFD | AFD minimo |",
              "|---|---|---|---|---|---|"]
    pendientes = []
    for c in datos["casos"]:
        nombre = f"L{c['lista']}-{c['ejercicio']}"
        if not c.get("expresion"):
            pendientes.append(nombre)
            continue
        p = pipeline(c["expresion"], datos.get("clases") or None, set(c["alfabeto"]))
        carpeta = DESTINO / "er-a-automata" / nombre
        for archivo, a in [("1-afn-lambda", p.thompson.afn_lambda), ("2-afn", p.afn),
                           ("3-afd", p.afd), ("4-afd-minimo", p.minimo)]:
            fm.escribir_archivo(a, carpeta / f"{archivo}.jff")
        conteos = " | ".join(str(e) for _, e, _ in p.resumen())
        lineas.append(f"| {nombre} | `{er.a_texto(p.arbol)}` | {conteos} |")
    if pendientes:
        lineas += ["", "Pendientes de capturar en `casos/practica4/ejercicios_er.json`: " + ", ".join(pendientes) + "."]
    return "\n".join(lineas) + "\n"


def validadores() -> str:
    lineas = ["# Resumen: validadores", "",
              "| Validador | Estados AFN-λ | Estados AFD (subconjuntos) | Estados AFD minimo | Cadenas probadas | Validas | Discrepancias |",
              "|---|---|---|---|---|---|---|"]
    for clave, v in val.VALIDADORES.items():
        p = v.automata()
        fm.escribir_archivo(p.afd, DESTINO / "validadores" / f"{clave}-afd.jff")
        fm.escribir_archivo(p.minimo, DESTINO / "validadores" / f"{clave}-afd-minimo.jff")
        casos = val.generar_casos(clave)
        validas = sum(v.valida(x) for x in casos)
        discrepancias = sum(v.valida(x) != v.valida_re(x) for x in casos)
        lineas.append(f"| {v.nombre} | {len(p.thompson.afn_lambda.estados)} | {len(p.afd.estados)} | "
                      f"{len(p.minimo.estados)} | {len(casos)} | {validas} | {discrepancias} |")
    return "\n".join(lineas) + "\n"


def ejemplos() -> None:
    carpeta = DESTINO / "ejemplos"
    anexo = Automata(["q0", "q1"], ["a", "b"], "q0", {"q1"},
                     {("q0", "a"): {"q1"}, ("q0", "b"): {"q0"}, ("q0", ""): {"q1"}}, "anexo3-afnd-lambda")
    pares = Automata(["p", "i"], ["a", "b"], "p", {"p"},
                     {("p", "a"): {"i"}, ("p", "b"): {"p"}, ("i", "a"): {"p"}, ("i", "b"): {"i"}}, "par-de-a")
    termina = pipeline("(a + b)*abb").minimo
    for nombre, a in [("anexo3-afnd-lambda", anexo), ("afd-par-de-a", pares), ("afd-termina-abb", termina)]:
        for ext in (".jff", ".json", ".xml"):
            fm.escribir_archivo(a, carpeta / f"{nombre}{ext}")
    afn = Automata(["0", "1", "2"], ["a", "b"], "0", {"2"},
                   {("0", "a"): {"0", "1"}, ("0", "b"): {"0"}, ("1", "b"): {"2"}}, "afnd-termina-ab")
    fm.escribir_archivo(afn, carpeta / "afnd-termina-ab.jff")
    (carpeta / "cadenas-prueba.txt").write_text("λ\na\nab\nabb\naabb\nbabb\nabba\n", encoding="utf-8")


if __name__ == "__main__":
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    (EVIDENCIAS / "resumen-er-a-automata.md").write_text(er_a_automata(), encoding="utf-8")
    (EVIDENCIAS / "resumen-validadores.md").write_text(validadores(), encoding="utf-8")
    ejemplos()
    print("Listo: revise automatas/practica4/ y evidencias/practica4/")

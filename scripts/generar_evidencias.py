"""Genera los .jff y las tablas de evidencia de los Ejercicios 2 y 4 de la Practica 4.

Uso (desde la raiz del repositorio):
    python scripts/generar_evidencias.py --ejercicio-2
    python scripts/generar_evidencias.py

Produce:
    automatas/practica4/er-a-automata/<caso>/{1-afn-lambda,2-afn,3-afd,4-afd-minimo}.jff
    automatas/practica4/validadores/<validador>-{afd,afd-minimo}.jff
    automatas/practica4/ejemplos/*.jff        (automatas pequeños para probar el simulador)
    evidencias/practica4/resumen-er-a-automata.md
    evidencias/practica4/resumen-validadores.md
"""

import json
import argparse
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import expresiones as er  # noqa: E402
import formatos as fm  # noqa: E402
import conversiones as cv  # noqa: E402
import eliminacion_estados as elim  # noqa: E402
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
        inciso = f"-{c['inciso']}" if c.get("inciso") else ""
        nombre = f"L{c['lista']}-{c['ejercicio']}{inciso}"
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


def validacion_273() -> None:
    """Registra la comprobación por λ-clausuras de las cadenas del ejercicio 273."""
    datos = json.loads((RAIZ / "casos/practica4/ejercicios_er.json").read_text(encoding="utf-8"))
    expresiones = {(c["lista"], c["ejercicio"], c.get("inciso")): c
                   for c in datos["casos"]}
    lineas = ["# Lista 4, ejercicio 273: comprobación por λ-clausuras", ""]
    for validacion in datos.get("validaciones", []):
        caso = expresiones[(validacion["lista"], 272, validacion["inciso"])]
        p = pipeline(caso["expresion"], datos.get("clases") or None, set(caso["alfabeto"]))
        lineas += [f"## Ejercicio 272({validacion['inciso']}): `{caso['expresion']}`", "",
                   "| Cadena | λ-clausura y recorrido | Aceptación | Esperada | Coincide |",
                   "|---|---|---|---|---|"]
        for prueba in validacion["cadenas"]:
            aceptada, pasos = cv.simular_afn(p.thompson.afn_lambda, prueba["cadena"])
            recorrido = ["λ-cl(q0)=" + _conjunto(pasos[0]["despues"])]
            recorrido += [f"{paso['simbolo']}→{_conjunto(paso['mover'])}→λ-cl {_conjunto(paso['despues'])}"
                          for paso in pasos[1:]]
            lineas.append(
                f"| `{prueba['cadena']}` | {'; '.join(recorrido)} | "
                f"{'Sí' if aceptada else 'No'} | {'Sí' if prueba['esperada'] else 'No'} | "
                f"{'Sí' if aceptada == prueba['esperada'] else 'No'} |"
            )
        lineas.append("")
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    (EVIDENCIAS / "validacion-273.md").write_text("\n".join(lineas), encoding="utf-8")


def _conjunto(estados) -> str:
    return "{" + ", ".join(sorted(estados)) + "}" if estados else "∅"


def arden_278() -> None:
    """Aplica Arden al AFD mínimo del ejercicio 278 y compara lenguajes."""
    datos = json.loads((RAIZ / "casos/practica4/ejercicios_er.json").read_text(encoding="utf-8"))
    caso = next(c for c in datos["casos"] if c["lista"] == 4 and c["ejercicio"] == 278)
    p = pipeline(caso["expresion"], datos.get("clases") or None, set(caso["alfabeto"]))
    resultado = elim.a_expresion(p.minimo)
    equivalente = pipeline(resultado, datos.get("clases") or None, set(caso["alfabeto"]))
    iguales, detalle, contraejemplo = cv.equivalentes(p.minimo, equivalente.minimo)
    lineas = [
        "# Lista 4, ejercicio 278(d): resultado con el Lema de Arden", "",
        f"Expresión original: `{caso['expresion']}`", "",
        f"Expresión obtenida del AFD mínimo: `{resultado}`", "",
        f"Estados del AFD por subconjuntos: {len(p.afd.estados)}.",
        f"Estados del AFD mínimo: {len(p.minimo.estados)}.",
        f"AFD mínimo de ambas expresiones: {'equivalentes' if iguales else 'no equivalentes'}.",
        f"{detalle}",
    ]
    if contraejemplo is not None:
        lineas.append(f"Cadena que distingue: `{contraejemplo or 'λ'}`.")
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    (EVIDENCIAS / "resultado-278.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")


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
    parser = argparse.ArgumentParser(description="Genera los autómatas y resúmenes de la Práctica 4.")
    parser.add_argument("--ejercicio-2", action="store_true",
                        help="genera únicamente los resultados del ejercicio 2")
    argumentos = parser.parse_args()
    EVIDENCIAS.mkdir(parents=True, exist_ok=True)
    (EVIDENCIAS / "resumen-er-a-automata.md").write_text(er_a_automata(), encoding="utf-8")
    validacion_273()
    arden_278()
    if not argumentos.ejercicio_2:
        (EVIDENCIAS / "resumen-validadores.md").write_text(validadores(), encoding="utf-8")
        ejemplos()
    print("Listo: revise automatas/practica4/ y evidencias/practica4/")

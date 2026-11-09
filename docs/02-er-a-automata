# Ejercicio 2. De expresión regular a autómata

**Responsable:** Ángel Saúl Hernández Aguilar · **Código:** `src/expresiones.py`, `src/thompson.py`
(y los algoritmos de la Práctica 3 en `src/conversiones.py`) · **Pruebas:** `tests/test_expresiones.py`,
`tests/test_thompson.py`

## 1. Qué se pide y cómo se resolvió

| Requisito | Dónde se cumple |
|---|---|
| Analizar una ER con la notación del curso, respetando precedencia y paréntesis | `expresiones.analizar` (descenso recursivo) |
| Rechazar una expresión mal formada indicando la posición del error | `expresiones.ErrorExpresion` (atributo `posicion`, método `señalar`) |
| Construir el AFN-λ con los casos básicos y las construcciones de unión, concatenación y cerradura, mostrando los autómatas parciales | `thompson.thompson` (lista `pasos`) y la vista *ER a autómata* (deslizador) |
| Aplicar los algoritmos de la Práctica 3 hasta el AFD mínimo y exportar cada autómata a `.jff` | `thompson.pipeline` + botón *Exportar los 4 a .jff* |
| Validar cadenas con el autómata obtenido | `Pipeline.acepta` y el campo *Cadena a validar* |
| Casos de prueba: Lista 3 (241–253) y Lista 4 (272, 273, 278) | `casos/practica4/ejercicios_er.json` + `tests/test_thompson.py` |

## 2. Fundamento teórico

**Teorema de Kleene, primera parte.** Todo lenguaje denotado por una expresión regular es aceptado
por un autómata finito. En Hopcroft, Motwani y Ullman (2007) corresponde al teorema 3.7 de la
sección 3.2.3 (*Converting Regular Expressions to Automata*); en Sipser (2013), al lema 1.55.
La demostración es por inducción estructural sobre la expresión y es constructiva: el programa
sigue exactamente esa construcción, conocida como construcción de Thompson (Thompson, 1968).

> Nota: confirmen la numeración del teorema con la edición de la bibliografía oficial del curso,
> porque cambia entre ediciones.

| Expresión | Autómata parcial (un inicial `i`, un final `f`) |
|---|---|
| `∅` | `i` y `f` sin transiciones |
| `λ` | `i —λ→ f` |
| `a` | `i —a→ f` |
| `r + s` | nuevo `i —λ→` inicios de *r* y *s*; finales de *r* y *s* `—λ→` nuevo `f` |
| `rs` | final de *r* `—λ→` inicio de *s* |
| `r*` | nuevo `i —λ→` inicio de *r* y `—λ→` nuevo `f`; final de *r* `—λ→` inicio de *r* y `—λ→` nuevo `f` |

Cada construcción agrega a lo más dos estados, por lo que una expresión con *n* nodos produce un
AFN-λ con a lo más 2*n* estados. Las clases como `[D]` son abreviaturas de una unión de símbolos;
se construyen directamente con dos estados y una transición por símbolo, lo que reconoce el mismo
lenguaje que la unión desarrollada y evita decenas de estados auxiliares.

## 3. Análisis sintáctico

Gramática que implementa `expresiones.py` (cada nivel es una función del analizador):

```
union     ::= concat ( '+' concat )*          precedencia más baja
concat    ::= cerradura cerradura*            yuxtaposición
cerradura ::= atomo '*'*                      precedencia más alta
atomo     ::= SIMBOLO | 'λ' | '∅' | '(' union ')' | '[' NOMBRE ']' | '\' carácter
```

El orden de las reglas fija la precedencia: `a+bc*` se analiza como `a + (b(c*))`. El árbol resultante
usa las clases `Simbolo`, `Clase`, `Lambda`, `Vacio`, `Union`, `Concat` y `Estrella`, y se puede
volver a escribir con los paréntesis mínimos (`a_texto`) o traducir al módulo `re` (`a_python`).

### Errores detectados

| Entrada | Mensaje |
|---|---|
| *(vacía)* | Posición 1: la expresión está vacía (use λ para la palabra vacía). |
| `a+` | Posición 3: se esperaba un operando al final de la expresión. |
| `*a` | Posición 1: '\*' sin operando a su izquierda. |
| `(a+b` | Posición 1: falta ')' para cerrar el paréntesis abierto aquí. |
| `a+b)` | Posición 4: ')' sin '(' que la abra. |
| `()` | Posición 1: paréntesis vacíos '()'; use λ para la palabra vacía. |
| `[X]` | Posición 1: la clase [X] no está declarada (disponibles: …). |
| `a(b+*c)` | Posición 5: '\*' sin operando a su izquierda. |

En la interfaz, el mensaje va acompañado de la expresión con un `^` bajo el carácter culpable.

## 4. Pseudocódigo y correspondencia con el código

```
pipeline(texto):
    arbol      ← analizar(texto)                       expresiones.analizar
    afn_lambda ← construir(arbol)                      thompson._Constructor.construir (postorden)
    afn        ← eliminar_lambda(afn_lambda)           conversiones.eliminar_lambda   (Práctica 3)
    afd        ← subconjuntos(afn)                     conversiones.subconjuntos      (Práctica 3)
    minimo     ← minimizar(afd)                        conversiones.minimizar         (Práctica 3)

construir(n):
    si n es símbolo, λ o ∅: crear i, f y la transición del caso básico
    si n = r + s: A ← construir(r); B ← construir(s); unir con λ
    si n = rs:    A ← construir(r); B ← construir(s); final(A) —λ→ inicio(B)
    si n = r*:    A ← construir(r); agregar i, f y las cuatro transiciones λ
    registrar (subexpresión, regla, autómata parcial)
```

**Número de pasos.** El análisis es lineal en la longitud de la expresión. Thompson visita cada nodo
una vez: O(*n*) estados y transiciones. La eliminación de λ cuesta O(*m*² · |Σ|) con *m* = 2*n*
estados; la construcción de subconjuntos, en el peor caso O(2^*m* · |Σ| · *m*), aunque en la práctica
solo se generan los subconjuntos alcanzables; y la minimización por particiones, O(*k*² · |Σ|) con
*k* estados del AFD.

## 5. Ejemplo resuelto: `(a + b)*abb`

**Autómatas parciales (10 pasos, uno por nodo del árbol en postorden):**

| Paso | Subexpresión | Regla | Estados |
|---|---|---|---|
| 1 | `a` | caso básico | 2 |
| 2 | `b` | caso básico | 2 |
| 3 | `a + b` | unión | 6 |
| 4 | `(a + b)*` | cerradura | 8 |
| 5 | `a` | caso básico | 2 |
| 6 | `(a + b)*a` | concatenación | 10 |
| 7 | `b` | caso básico | 2 |
| 8 | `(a + b)*ab` | concatenación | 12 |
| 9 | `b` | caso básico | 2 |
| 10 | `(a + b)*abb` | concatenación | 14 |

**Subconjuntos** (a partir del AFN sin λ):

| AFD | Subconjunto | a | b |
|---|---|---|---|
| →S0 | {q6} | S1 | S2 |
| S1 | {q0, q1, q10, q2, q4, q5, q7, q8, q9} | S1 | S3 |
| S2 | {q0, q2, q3, q4, q5, q7, q8} | S1 | S2 |
| S3 | {q0, q11, q12, q2, q3, q4, q5, q7, q8} | S1 | S4 |
| \*S4 | {q0, q13, q2, q3, q4, q5, q7, q8} | S1 | S2 |

S4 es de aceptación porque contiene a q13, el final del AFN-λ.

**Minimización** (rondas de refinamiento): {S4} {S0,S1,S2,S3} → {S4} {S0,S1,S2} {S3} →
{S4} {S0,S2} {S1} {S3}. Se fusionan S0 y S2; el AFD mínimo tiene 4 estados:

| δ | a | b |
|---|---|---|
| →M0 = {S0,S2} | M1 | M0 |
| M1 = {S1} | M1 | M2 |
| M2 = {S3} | M1 | M3 |
| \*M3 = {S4} | M1 | M0 |

Es el AFD mínimo que aparece en la bibliografía para este lenguaje: cada estado recuerda cuánto del
sufijo `abb` se lleva leído. El resultado a mano y el del programa coinciden.

Capturas sugeridas para `evidencias/practica4/`: el paso 4 (cerradura), el paso 10, la vista del AFD
mínimo y la validación de `aabb` (aceptada) y `abba` (rechazada).

## 6. Casos de prueba de las listas

Las expresiones de la Lista 3 (241–253) y de la Lista 4 (272, 273 y 278) se capturan en
`casos/practica4/ejercicios_er.json`, con la notación del curso, junto con algunas cadenas
verificadas a mano. Mientras el campo `expresion` sea `null`, el caso se omite.

Para cada caso, `tests/test_thompson.py` comprueba que el AFN-λ, el AFN, el AFD y el AFD mínimo
aceptan exactamente las mismas cadenas que `re.fullmatch` con la traducción de la expresión,
sobre **todas** las cadenas del alfabeto hasta longitud 8 (511 cadenas si |Σ| = 2). Esa longitud
supera el número de estados de los AFD mínimos de las listas, por lo que cada ciclo se recorre al
menos una vez.

Después de capturarlas, regenere los `.jff` y la tabla de resultados con:

```
python scripts/generar_evidencias.py
```

Resultados actuales (los cinco casos de ejemplo del archivo; la tabla completa queda en
`evidencias/practica4/resumen-er-a-automata.md`):

| Caso | Expresión | AFN-λ | AFN | AFD | AFD mínimo |
|---|---|---|---|---|---|
| ejemplo-1 | `(a + b)*abb` | 14 | 14 | 5 | 4 |
| ejemplo-2 | `a*b* + (ab)*` | 16 | 14 | 8 | 8 |
| ejemplo-3 | `(0 + 1(01*0)*1)*` | 20 | 20 | 7 | 3 |
| ejemplo-4 | `(a + λ)(b + ∅)*` | 14 | 10 | 4 | 3 |
| ejemplo-5 | `(aa + bb + (ab + ba)(aa + bb)*(ab + ba))*` | 46 | 46 | 13 | 4 |

El AFD mínimo cuenta el estado trampa cuando el autómata debe completarse.

## Referencias

Hopcroft, J. E., Motwani, R., y Ullman, J. D. (2007). *Introduction to automata theory, languages, and
computation* (3.ª ed.). Pearson/Addison-Wesley. ISBN 978-0-321-45536-9

Sipser, M. (2013). *Introduction to the theory of computation* (3.ª ed.). Cengage Learning.
ISBN 978-1-133-18779-0

Thompson, K. (1968). Programming techniques: Regular expression search algorithm. *Communications of
the ACM, 11*(6), 419-422. https://doi.org/10.1145/363347.363387

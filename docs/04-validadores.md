# Ejercicio 4. Aplicaciones: validadores

**Responsable:** Ángel Saúl Hernández Aguilar · **Código:** `src/validadores.py` (usa `thompson.pipeline`)
· **Pruebas:** `tests/test_validadores.py` · **Interfaz:** sección *Validadores*

Se implementaron **cuatro** validadores (se pedían al menos tres): correo electrónico, teléfono en
formato nacional, fecha y URL. Cada uno se escribe en la notación del curso; el programa la analiza,
construye el AFN-λ por Thompson, elimina λ, aplica subconjuntos y minimiza, y **valida con el AFD
mínimo**. La expresión para `re` se escribió a mano, por separado, para que la comparación entre
ambos modelos sea una prueba real y no una comparación del programa consigo mismo.

## Clases de símbolos declaradas

| Clase | Símbolos | Uso |
|---|---|---|
| `D` | 0 + 1 + … + 9 | dígitos |
| `P` | 1 + 2 + … + 9 | dígito distinto de cero |
| `L` | a + … + z + A + … + Z | letras ASCII |
| `A` | `L` + `D` | alfanuméricos |
| `H` | `A` + `-` | carácter de una etiqueta de dominio |
| `W` | `A` + `_` + `%` + `+` + `-` | parte local de un correo (sin punto) |
| `R` | `A` + `-` + `.` + `_` + `~` + `%` | segmento de ruta de una URL |

Dentro de una clase, `+` es un símbolo más (la clase es un conjunto, no una expresión).

## 1. Correo electrónico

**Notación del curso**
```
[W]([W] + .[W])* @ ([A] + [A][H]*[A]).(([A] + [A][H]*[A]).)*[L][L][L]*
```
**Módulo `re`**
```
[A-Za-z0-9_%+-]+(?:\.[A-Za-z0-9_%+-]+)*@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}
```
Lectura: una parte local con puntos solo entre caracteres; `@`; una o más etiquetas de dominio que no
empiezan ni terminan en guion, cada una seguida de punto; un dominio de nivel superior de dos o más
letras. La traducción usa equivalencias del álgebra de expresiones: `rr*` se escribe `r+` en `re`,
`(r + λ)` se escribe `r?`, y `[L][L][L]*` es `[A-Za-z]{2,}`.

- **Estándar consultado:** RFC 5321 (SMTP), sección 4.1.2, y RFC 5322, sección 3.4.1 (*addr-spec*).
- **Válidos que quedan fuera:** parte local entre comillas (`"juan perez"@x.mx`), los caracteres
  `! # $ & ' * / = ? ^ ` { | } ~` que el RFC 5322 permite, dominios literales IP (`u@[192.168.0.1]`) y
  nombres internacionalizados (ñ, acentos).
- **Inválidos que se aceptan:** etiquetas de más de 63 caracteres y direcciones de más de 254, porque
  la expresión no limita longitudes (hacerlo es posible, pero multiplica los estados).

## 2. Teléfono (formato nacional, México)

**Notación del curso**
```
(\+52(\  + λ) + λ)( [D][D](\  + - + λ)[D][D][D][D](\  + - + λ)[D][D][D][D]
                  + [D][D][D](\  + - + λ)[D][D][D](\  + - + λ)[D][D][D][D] )
```
**Módulo `re`**
```
(?:\+52 ?)?(?:[0-9]{2}[ -]?[0-9]{4}[ -]?[0-9]{4}|[0-9]{3}[ -]?[0-9]{3}[ -]?[0-9]{4})
```
Diez dígitos agrupados 2-4-4 (lada de dos dígitos, como 55 o 33) o 3-3-4 (lada de tres, como 771),
con espacio, guion o nada entre grupos, y `+52` opcional. Se usa `[0-9]` y no `\d` porque en Python
`\d` también acepta dígitos de otros sistemas de escritura (por ejemplo `٣`), que el AFD rechaza.

- **Estándar consultado:** Plan Técnico Fundamental de Numeración del IFT (marcación de 10 dígitos,
  vigente desde el 3 de agosto de 2019).
- **Fuera de la expresión:** paréntesis (`(55) 1234 5678`), los prefijos 01, 044 y 045 ya eliminados,
  y números internacionales distintos de +52. No se verifica que la lada exista; se aceptan
  separadores mezclados (`55 1234-5678`).

## 3. Fecha (dd/mm/aaaa o aaaa-mm-dd)

**Notación del curso**
```
(0[P] + (1 + 2)[D] + 3(0 + 1))/(0[P] + 1(0 + 1 + 2))/[D][D][D][D]
  + [D][D][D][D]-(0[P] + 1(0 + 1 + 2))-(0[P] + (1 + 2)[D] + 3(0 + 1))
```
**Módulo `re`**
```
(?:0[1-9]|[12][0-9]|3[01])/(?:0[1-9]|1[0-2])/[0-9]{4}|[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01])
```
- **Estándar consultado:** ISO 8601-1:2019, formato extendido de fecha de calendario (aaaa-mm-dd).
- **Fuera de la expresión:** fechas sin ceros a la izquierda (`6/11/2026`) y años de dos dígitos.
- **Inválidos que se aceptan:** `31/02/2026` o `29/02/2025`, porque el día no se relaciona con el mes.
  Comprobar los días de cada mes sigue siendo regular (es una unión finita de casos), pero alarga
  mucho la expresión; los años bisiestos se pueden describir para un rango finito de años.

## 4. URL (http y https)

**Notación del curso**
```
http(s + λ)://([A] + [A][H]*[A]).(([A] + [A][H]*[A]).)*[L][L][L]*(:[P][D]* + λ)(/[R]*)*
```
**Módulo `re`**
```
https?://(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}(?::[1-9][0-9]*)?(?:/[A-Za-z0-9._~%-]*)*
```
- **Estándar consultado:** RFC 3986 (sintaxis genérica de URI), sección 3, y RFC 1123, sección 2.1.
- **Fuera de la expresión:** otros esquemas (ftp, mailto), direcciones IP, `localhost`, credenciales
  (`usuario@host`), consulta (`?q=1`) y fragmento (`#sección`). El puerto no se limita a 65535.

## 5. Autómatas obtenidos

| Validador | Estados AFN-λ | Estados AFD (subconjuntos) | Estados AFD mínimo |
|---|---|---|---|
| Correo electrónico | 52 | 18 | 9 |
| Teléfono | 98 | 41 | 19 |
| Fecha | 110 | 42 | 26 |
| URL | 78 | 26 | 18 |

Los conteos del AFD incluyen el estado trampa (el subconjunto vacío). La interfaz dibuja el AFD
mínimo sin la trampa para que se lea mejor; los archivos `.jff` completos están en
`automatas/practica4/validadores/`.

## 6. Congruencia entre modelos

`tests/test_validadores.py` compara, para cada validador, el AFD mínimo con `re.fullmatch` sobre las
cadenas que produce `validadores.generar_casos`. El procedimiento de generación es:

1. Se incluyen los ejemplos válidos e inválidos escritos a mano y la cadena vacía.
2. Se derivan **240 cadenas al azar del árbol de la expresión**: en una unión se elige una rama, una
   cerradura se repite de 0 a 3 veces y una clase aporta un símbolo al azar. Estas cadenas pertenecen
   al lenguaje por construcción y se obtienen **sin usar el autómata**.
3. Cada derivada se **muta** una o dos veces: insertar, borrar, sustituir o duplicar un carácter, o
   truncar la cadena, con símbolos del alfabeto y de un conjunto de ruido (` #!ñ()/:.@-_+`). La mayoría
   de las mutantes queda fuera del lenguaje y algunas no, lo que pone a prueba las fronteras.
4. Se completa hasta 600 con cadenas aleatorias de 1 a 25 símbolos y se eliminan repetidas.

La semilla es fija, así que el conjunto es el mismo en cada ejecución y en las tres versiones de
Python. La prueba exige al menos 500 cadenas, al menos 100 de cada clase y **cero discrepancias**.
Una segunda prueba compara también el AFD con la traducción automática del árbol (`a_python`).

| Validador | Cadenas probadas | Válidas | Inválidas | Discrepancias |
|---|---|---|---|---|
| Correo electrónico | 592 | 373 | 219 | 0 |
| Teléfono | 592 | 262 | 330 | 0 |
| Fecha | 587 | 255 | 332 | 0 |
| URL | 590 | 339 | 251 | 0 |

Las pruebas aprueban en la integración continua con Python 3.11, 3.12 y 3.13
(captura de la pestaña *Actions* en `evidencias/practica4/`).

## Capturas sugeridas
- La sección *Validadores* con cada validador seleccionado y un texto válido y otro inválido.
- El resultado de *Probar congruencia* para cada uno.
- La ejecución de GitHub Actions con las tres versiones aprobadas.

## Referencias

Braden, R. (Ed.). (1989). *Requirements for Internet hosts — Application and support* (RFC 1123).
Internet Engineering Task Force. https://doi.org/10.17487/RFC1123

Berners-Lee, T., Fielding, R., y Masinter, L. (2005). *Uniform resource identifier (URI): Generic syntax*
(RFC 3986). Internet Engineering Task Force. https://doi.org/10.17487/RFC3986

Instituto Federal de Telecomunicaciones. (2018). *Plan Técnico Fundamental de Numeración* (modificación
para la marcación a 10 dígitos). Diario Oficial de la Federación.

International Organization for Standardization. (2019). *Date and time — Representations for information
interchange — Part 1: Basic rules* (ISO 8601-1:2019).

Klensin, J. (2008). *Simple mail transfer protocol* (RFC 5321). Internet Engineering Task Force.
https://doi.org/10.17487/RFC5321

Python Software Foundation. (2026). *re — Regular expression operations*. En *The Python Standard
Library* (versión 3.12). Recuperado el 6 de noviembre de 2026 de https://docs.python.org/3.12/library/re.html

Resnick, P. (Ed.). (2008). *Internet message format* (RFC 5322). Internet Engineering Task Force.
https://doi.org/10.17487/RFC5322

> Revisen la referencia del IFT antes de entregar: la fecha y el título exacto del acuerdo publicado
> en el DOF que estableció la marcación a 10 dígitos conviene tomarlos del propio documento.

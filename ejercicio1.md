# Ejercicio 1. Investigación sobre Expresiones Regulares

**Asignatura:** Teoría de la Computación  
**Práctica:** 4 - Uso de las Expresiones Regulares y Extensión de Software  

---

## 1. Definición Formal de Lenguaje Regular y Expresión Regular

### Lenguaje Regular
Un lenguaje $L$ sobre un alfabeto $\Sigma$ se define como **regular** si existe un autómata finito (determinista o no determinista) que lo acepta, o de forma equivalente, si puede ser escrito mediante una expresión regular.

### Expresión Regular (Definición Inductiva / Recursiva)
Dado un alfabeto $\Sigma$, el conjunto de las expresiones regulares sobre $\Sigma$ y los lenguajes que denotan (representados por $L(r)$) se definen formalmente de la siguiente manera:

#### Base:
1. $\emptyset$ es una expresión regular y denota el lenguaje vacío: $L(\emptyset) = \emptyset$.
2. $\lambda$ (o $\epsilon$) es una expresión regular y denota el lenguaje que contiene únicamente la cadena vacía: $L(\lambda) = \{\lambda\}$.
3. Para todo símbolo $a \in \Sigma$, $a$ es una expresión regular y denota el lenguaje formado únicamente por el símbolo $a$: $L(a) = \{a\}$.

#### Paso Inductivo:
Si $r$ y $s$ son expresiones regulares que denotan los lenguajes $L(r)$ y $L(s)$ respectivamente, entonces:
1. **Unión ($r + s$ o $r \cup s$):** Es una expresión regular que denota el lenguaje $L(r + s) = L(r) \cup L(s)$.
2. **Concatenación ($rs$ o $r \cdot s$):** Es una expresión regular que denota el lenguaje $L(rs) = L(r)L(s) = \{ w_1 w_2 \mid w_1 \in L(r), w_2 \in L(s) \}$.
3. **Cerradura de Kleene ($r^*$):** Es una expresión regular que denota el lenguaje $L(r^*) = (L(r))^* = \bigcup_{i=0}^{\infty} L(r)^i$, donde $L(r)^0 = \{\lambda\}$ y $L(r)^i = L(r) L(r)^{i-1}$.

---

## 2. Ubicación de los Lenguajes Regulares en la Jerarquía de Chomsky

La **Jerarquía de Chomsky** clasifica las gramáticas formales y los lenguajes en cuatro niveles concéntricos (Tipo 0 a Tipo 3). Los **lenguajes regulares** ocupan el nivel más restrictivo y específico: **Tipo 3**.

- **Tipo 3 (Regulares):** Reconocidos por Autómatas Finitos Deterministas/No Deterministas (AFD/AFN). Las reglas gramaticales son de la forma $A \rightarrow aB$ o $A \rightarrow a$ (derecha).
- **Tipo 2 (Libres del contexto):** Reconocidos por Autómatas de Pila (AP). Reglas de la forma $A \rightarrow \gamma$, donde $A$ es un no terminal.
- **Tipo 1 (Sensibles al contexto):** Reconocidos por Autómatas Finitos Conmensurables / Acotados Linealmente (LBA).
- **Tipo 0 (Recursivamente enumerables):** Reconocidos por Máquinas de Turing (MT).

---

## 3. Enunciado del Teorema de Kleene

> **Teorema de Kleene:** Un lenguaje $L \subseteq \Sigma^*$ es regular si y solo si es aceptado por un autómata finito (determinista o no determinista).

El teorema establece la equivalencia entre las dos representaciones a través de sus dos direcciones:

1. **Dirección 1 ($\text{ER} \Rightarrow \text{Autómata}$):** Para toda expresión regular $r$, existe un Autómata Finito con transiciones $\lambda$ (AFN-$\lambda$) que acepta el lenguaje $L(r)$ (Construcciones de Thompson).
2. **Dirección 2 ($\text{Autómata} \Rightarrow \text{ER}$):** Para todo Autómata Finito $M$, existe una expresión regular $r$ tal que $L(r) = L(M)$ (Método de Eliminación de Estados).

### Referencia Bibliográfica Oficial
- **Hopcroft, J. E., Motwani, R., & Ullman, J. D. (2008).** *Introducción a la teoría de autómatas, lenguajes y computación* (3.ª ed.). Pearson Educación. (Capítulo 3: Expresiones y lenguajes regulares, Sección 3.2, pp. 91–108).
- **Sipser, M. (2013).** *Introduction to the Theory of Computation* (3rd ed.). Cengage Learning. (Theorem 1.54, pp. 66–76).

---

## 4. Leyes Algebraicas de las Expresiones Regulares

Las siguientes equivalencias permiten simplificar expresiones regulares manteniendo la equivalencia del lenguaje denotado:

1. **Conmutatividad de la unión:** $r + s = s + r$
2. **Asociatividad de la unión y concatenación:**
   - $(r + s) + t = r + (s + t)$
   - $(rs)t = r(st)$
3. **Distributividad:**
   - $r(s + t) = rs + rt$ *(izquierda)*
   - $(s + t)r = sr + tr$ *(derecha)*
4. **Elementos neutros:**
   - $r + \emptyset = r$
   - $r \lambda = \lambda r = r$
5. **Elementos aniquiladores:** $r \emptyset = \emptyset r = \emptyset$
6. **Idempotencia de la unión:** $r + r = r$
7. **Leyes de la Cerradura de Kleene:**
   - $\emptyset^* = \lambda$
   - $\lambda^* = \lambda$
   - $r^* = \lambda + r r^* = \lambda + r^* r$
   - $(r^*)^* = r^*$
   - $(r + s)^* = (r^* s^*)^*$

---

## 5. Expresiones Regulares Teóricas vs. Motores de Lenguajes de Programación

- **Teoría de la Computación:** Las ER son modelos formales estrictos equivalentes a autómatas finitos. Evalúan en tiempo $O(n)$ sobre un AFD y no poseen memoria interna para recordar subcadenas previas.
- **Motores en Lenguajes de Programación (`re` en Python, PCRE, etc.):** Incluyen extensiones sintácticas con memoria como **retro-referencias (backreferences)** y *lookaheads*. Funcionan mediante *backtracking* (tiempo $O(2^n)$ en el peor caso) y pueden reconocer lenguajes **no regulares**.

### Análisis de la Expresión con Retro-referencia $(a^*)b\backslash 1$
La sintaxis $(a^*)b\backslash 1$ exige que la secuencia de caracteres capturada en el primer grupo $(a^*)$ vuelva a aparecer de forma idéntica después del símbolo $b$. El lenguaje denotado es:

$$L = \{ a^n b a^n \mid n \ge 0 \}$$

### Demostración de No Regularidad (Lema de Bombeo)

**Demostración por contradicción:**
1. Supongamos que $L = \{ a^n b a^n \mid n \ge 0 \}$ es un lenguaje regular.
2. Por el Lema de Bombeo, existe una constante de bombeo $p \ge 1$.
3. Tomemos la cadena $w = a^p b a^p \in L$, con $|w| = 2p + 1 \ge p$.
4. Según el lema, $w$ se puede dividir en $w = xyz$ tal que:
   - $|y| > 0$
   - $|xy| \le p$
   - $\forall i \ge 0, x y^i z \in L$
5. Como $|xy| \le p$, la subcadena $xy$ consiste únicamente de símbolos del primer bloque de $a$'s. Por lo tanto, $y = a^k$ para algún $k \ge 1$.
6. Bombeando para $i = 2$:
   $$x y^2 z = a^{p-k} a^{2k} b a^p = a^{p+k} b a^p$$
7. Dado que $k \ge 1$, se cumple que $p + k \neq p$. Por lo tanto, la cantidad de $a$'s antes de la $b$ no coincide con la cantidad de $a$'s después de la $b$.
8. Así, $x y^2 z \notin L$, lo cual **contradice el Lema de Bombeo**.
9. **Conclusión:** El lenguaje $L = \{ a^n b a^n \mid n \ge 0 \}$ **no es regular**.

---

## 6. Aplicaciones de las Expresiones Regulares en Computación

### 1. Análisis Léxico en Compiladores
- **Expresión:** `([a-zA-Z_])([a-zA-Z0-9_])*`
- **Explicación:** Identifica nombres de variables o funciones. Exige que el primer carácter sea una letra o guion bajo, seguido de cero o más alfanuméricos o guiones bajos.

### 2. Validación de Formatos de Datos (Email)
- **Expresión:** `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- **Explicación:** Valida nombres de usuario en formularios web exigiendo la estructura `usuario@dominio.tld`.

### 3. Búsqueda y Extracción de Patrones (Comando `grep` / Direcciones IP)
- **Expresión:** `\b([0-9]{1,3}\.){3}[0-9]{1,3}\b`
- **Explicación:** Utilizada en la administración de servidores para extraer direcciones IPv4 desde archivos de registro (*logs*).

### 4. Sanitización de Texto y Limpieza HTML
- **Expresión:** `<[^>]+>`
- **Explicación:** Identifica etiquetas HTML de apertura o cierre para eliminarlas de una cadena de texto y prevenir vulnerabilidades XSS.

### 5. Reescritura de URLs en Servidores Web (Nginx / Apache)
- **Expresión:** `^/producto/([0-9]+)$`
- **Explicación:** Intercepta URLs amigables como `/producto/102` para redirigirlas internamente al manejador `/index.php?id=102`.

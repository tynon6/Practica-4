# Ejercicio 1. Investigación sobre Expresiones Regulares

**Asignatura:** Teoría de la Computación  
**Programa Académico:** Ingeniería en Sistemas Computacionales (ESCOM - IPN)  
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

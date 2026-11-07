# Práctica 4

## Datos Generales

- **Unidad de Aprendizaje:** Teoría de la Computación
- **Carrera:** Ingeniería en Sistemas Computacionales
- **Profesor:** Gabriel Hurtado Aviles
- **Fecha de entrega:** 6 de noviembre de 2026

## Nombres de los integrantes del equipo

- Iker Gael Cruz Vargas
- Maria Fernanda Santos Fuentes
- Perla Santos Martinez
- 
## [Ejercicio 1: Investigación sobre expresiones regulares](Ejercicio1.md)


## Punto 2: De expresión regular a autómata

La aplicación analiza expresiones de la notación del curso, construye el AFN-λ mediante Thompson paso a paso y continúa con los algoritmos de la Práctica 3 para obtener el AFN, el AFD y el AFD mínimo. Permite revisar los autómatas y sus transiciones, validar cadenas y exportar cada etapa a `.jff`.

### Índice de resultados

- [Resumen de los casos de conversión](evidencias/practica4/resumen-er-a-automata.md)
- [Cadenas del ejercicio 273 procesadas por λ-clausuras](evidencias/practica4/validacion-273.md)
- [Resultado de Arden para el ejercicio 278](evidencias/practica4/resultado-278.md)

### Notación aceptada

- `+`: unión.
- Yuxtaposición: concatenación, por ejemplo `ab`.
- `*`: cerradura de Kleene.
- `λ`: cadena vacía; `∅`: lenguaje vacío.
- Paréntesis para agrupar.
- `[D]` para una clase declarada, por ejemplo `D = 0 + 1 + ... + 9`.
- `\c` para usar literalmente un carácter especial.

La precedencia es `*`, concatenación y `+`, de mayor a menor. Los espacios se ignoran salvo que estén escapados.

### Ejecución

Requiere Python 3.11 o posterior. Instala las dependencias y abre la aplicación:

```bash
python -m pip install -r requirements.txt
python src/app.py
```

En la sección **De expresión regular a autómata**, escribe una expresión o selecciona un caso de prueba. Pulsa **Construir** para ver el AFN-λ y usar el control de pasos; los menús permiten ver el AFN, el AFD y el AFD mínimo. Escribe una cadena para validarla. El botón de exportación guarda los cuatro autómatas `.jff` en `salidas/`.

Para los ejercicios 272(b) y 272(c), selecciona el caso y usa **Verificar Ejercicio 273 con λ-clausuras** para procesar las cadenas indicadas en la Lista 4. Los pasos y resultados se muestran en pantalla.

### Casos incluidos

- Lista 3: ejercicios 241–253.
- Lista 4: ejercicios 272(a)–272(e), las cadenas de comprobación del ejercicio 273 y el ejercicio 278.
- Práctica 3: los cinco AFD del Ejercicio 1, usados en la sección de conversión de AFD a expresión regular.

Los datos de las expresiones están en `casos/practica4/ejercicios_er.json`. Los autómatas exportados y los resúmenes de esta sección se guardan en `automatas/practica4/er-a-automata/` y `evidencias/practica4/`.

### Archivos principales

- `src/expresiones.py`: análisis de expresiones y detección de errores con posición.
- `src/thompson.py`: construcción paso a paso y conversión hasta el AFD mínimo.
- `src/conversiones.py`: cerraduras λ, conversión y simulación de autómatas.
- `scripts/generar_evidencias.py`: generación de autómatas y resúmenes.
- `evidencias/practica4/resumen-er-a-automata.md`: resultados de los casos de conversión.
- `evidencias/practica4/validacion-273.md`: recorridos de las cadenas mediante λ-clausuras.
- `evidencias/practica4/resultado-278.md`: resultado de Arden y comprobación del ejercicio 278.

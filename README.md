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

## Conversión de AFD a expresión regular

La aplicación importa un autómata `.jff`, comprueba que sea determinista y obtiene una expresión regular mediante eliminación de estados. La matriz muestra el autómata generalizado inicial y el resultado después de eliminar cada estado; se puede avanzar y retroceder entre pasos.

## Ejecución

Requiere Python 3 y Tkinter, incluido normalmente en la instalación de Python.

```bash
python src/app.py
```

En la lista de casos se pueden abrir directamente los ejercicios incluidos. También se pueden importar otros archivos `.jff`.

## Casos incluidos

- Lista 3: ejercicios 254, 255, 256, 257 y 258.
- Lista 4: ejercicios 276 y 277.
- Práctica 3, Ejercicio 1: AFD de los ejercicios 151, 152, 153, 154 y 155.

Los cinco AFD de la Práctica 3 están en `automatas/practica3/ejercicio1/`. Los casos de las listas están organizados en `automatas/practica4/lista3/` y `automatas/practica4/lista4/`.

## Archivos principales

- `src/app.py`: interfaz para importar el autómata y recorrer los pasos.
- `src/regex_por_estados.py`: lectura de `.jff`, comprobación de determinismo y cálculo de la expresión.

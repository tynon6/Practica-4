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
## [Ejercicio 1: Investigación sobre expresiones regulares](ejercicio1.md)


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

# Ejecutar el software con Docker

Esta guía explica cómo descargar el repositorio, construir los tres entornos de Python con Docker,
correr las pruebas y abrir el software interactivo en el navegador. No necesitas instalar Python
ni ninguna biblioteca en tu computadora: todo vive dentro de los contenedores.

| Servicio | Imagen base | Para qué se usa |
|---|---|---|
| `py311` | `python:3.11-slim` | Ejecutar las pruebas en Python 3.11 |
| `py312` | `python:3.12-slim` | Versión de referencia; **sirve la interfaz gráfica** en el puerto 8550 |
| `py313` | `python:3.13-slim` | Ejecutar las pruebas en Python 3.13 |

---

## 1. Requisitos (solo la primera vez)

1. Instala **Docker Desktop** desde <https://www.docker.com/products/docker-desktop/>.
   - En **Windows** usa WSL 2. Si el instalador lo pide, acéptalo y reinicia.
   - En **Linux** puedes instalar Docker Engine y el complemento `docker compose`.
2. **Abre Docker Desktop** y espera a que indique *Engine running*. Docker tiene que estar
   abierto cada vez que uses estos comandos.
3. Comprueba la instalación en una terminal (PowerShell en Windows, Terminal en Linux o macOS):

   ```bash
   docker --version
   docker compose version
   ```

   Si los dos comandos muestran un número de versión, puedes continuar.

> Se usa `docker compose`, con espacio. La forma `docker-compose`, con guion, es la versión 1
> y ya no se mantiene.

---

## 2. Descargar el repositorio

```bash
git clone https://github.com/USUARIO/REPOSITORIO.git
cd REPOSITORIO
```

Sustituye `USUARIO/REPOSITORIO` por la dirección de este repositorio.
Si ya lo habías clonado, entra a la carpeta y actualízalo con `git pull`.

---

## 3. Construir las imágenes

Todos los comandos de Docker se ejecutan desde la carpeta `entorno/`, que es donde está
`compose.yml`:

```bash
cd entorno
docker compose build
```

La primera vez tarda algunos minutos, porque descarga las tres versiones de Python e instala
`requirements.txt` en cada una. Las siguientes veces es mucho más rápido.

---

## 4. Verificar las tres versiones de Python

```bash
docker compose run --rm py311 python --version
docker compose run --rm py312 python --version
docker compose run --rm py313 python --version
```

Cada uno debe mostrar su versión (`3.11.x`, `3.12.x` y `3.13.x`).
La opción `--rm` borra el contenedor al terminar, para que no se acumulen.

---

## 5. Ejecutar las pruebas

```bash
docker compose run --rm py311 pytest -q
docker compose run --rm py312 pytest -q
docker compose run --rm py313 pytest -q
```

Al final de cada ejecución debe aparecer una línea como `77 passed`.
Si alguna prueba falla, pytest muestra qué archivo y qué prueba fallaron, y por qué.

---

## 6. Abrir el software

```bash
docker compose up py312
```

Cuando la terminal indique que el servidor arrancó, abre en el navegador:

**<http://localhost:8550>**

Para apagarlo, presiona **Ctrl + C** en esa terminal.

### Dejarlo corriendo en segundo plano

```bash
docker compose up -d py312      # arranca y te devuelve la terminal
docker compose logs -f py312    # muestra lo que está pasando (Ctrl + C para salir de los logs)
docker compose down             # apaga y elimina los contenedores
```

---

## 7. Ejecutar desde la raíz del repositorio (opcional)

Si no quieres entrar a `entorno/`, indica dónde está el archivo con `-f`:

```bash
docker compose -f entorno/compose.yml build
docker compose -f entorno/compose.yml run --rm py312 pytest -q
docker compose -f entorno/compose.yml up py312
```

---

## 8. Después de modificar el código

- **Si cambiaste archivos `.py`, `.jff` o la documentación**, no hace falta reconstruir.
  `compose.yml` monta la carpeta del repositorio dentro del contenedor (`volumes: ..:/app`),
  así que basta con volver a ejecutar el comando.
- **Si cambiaste `requirements.txt` o el `Dockerfile`**, reconstruye las imágenes:

  ```bash
  docker compose build
  ```

---

## 9. Comandos de consulta

| Comando | Qué muestra |
|---|---|
| `docker image ls` | Las imágenes construidas |
| `docker ps` | Los contenedores que están corriendo |
| `docker compose logs py312` | Los mensajes del servicio que sirve la interfaz |
| `docker compose down` | Apaga y limpia los contenedores del proyecto |

---

## 10. Solución de problemas

| Mensaje o síntoma | Causa y solución |
|---|---|
| `error during connect` o `cannot find the file specified ... docker_engine` | Docker Desktop no está abierto. Ábrelo y espera a que indique *Engine running*. |
| `no configuration file provided: not found` | No estás en la carpeta `entorno/`. Ejecuta `cd entorno` o usa la opción `-f` (sección 7). |
| `port is already allocated` o el puerto 8550 está en uso | Otro programa usa el puerto, por ejemplo la aplicación abierta con `python src/app.py`. Ciérralo, o cambia en `compose.yml` la línea `"8550:8550"` por `"8551:8550"` y abre <http://localhost:8551>. |
| El navegador no carga `localhost:8550` | Comprueba que el `Dockerfile` tenga `ENV FLET_SERVER_IP=0.0.0.0`. Sin esa línea, el servidor solo escucha dentro del contenedor y el puerto publicado no llega a la aplicación. |
| La página carga pero se queda en blanco | Espera unos segundos y recarga. Revisa `docker compose logs py312` por si hay un error. |
| `TypeError: ... unexpected keyword argument 'openapi_prefix'` | Falta fijar FastAPI. Verifica que `requirements.txt` contenga `fastapi==0.140.0` y reconstruye con `docker compose build`. |
| Docker pide permisos en Linux (`permission denied ... docker.sock`) | Ejecuta los comandos con `sudo` o agrega tu usuario al grupo `docker` (`sudo usermod -aG docker $USER`) y vuelve a iniciar sesión. |

---

## Archivos que intervienen

| Archivo | Función |
|---|---|
| `entorno/Dockerfile` | Receta única para las tres imágenes. Recibe la versión de Python con `ARG PYTHON_VERSION`, crea el entorno virtual en `/opt/venv` e instala `requirements.txt`. |
| `entorno/compose.yml` | Declara los tres servicios (`py311`, `py312`, `py313`), monta el repositorio en `/app` y publica el puerto 8550 del servicio `py312`. |
| `requirements.txt` | Dependencias con versión fijada: `flet[web]`, `fastapi` y `pytest`. |
| `.dockerignore` | Evita copiar a la imagen `venv/`, `.git/`, cachés y salidas generadas. |
| `pytest.ini` | Indica a pytest que el código está en `src/` y las pruebas en `tests/`. |


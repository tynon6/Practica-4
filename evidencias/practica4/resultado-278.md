# Lista 4, ejercicio 278(d): resultado con el Lema de Arden

Expresión original: `(a+b)*b`

Ecuaciones desde el AFD mínimo (M0 inicial, M1 final):
- `M0 = aM0 + bM1`
- `M1 = aM0 + bM1 + λ`

Por Arden, `M1 = b*( aM0 + λ ) = b*aM0 + b*`.
Sustituyendo en M0: `M0 = (a + bb*a)M0 + bb*`.
La expresión obtenida es `(a+bb*a)*bb*`.

Estados del AFD por subconjuntos: 3.
Estados del AFD mínimo: 2.
AFD mínimo de ambas expresiones: equivalentes.
Los AFD minimos tienen 2 estados y son isomorfos.

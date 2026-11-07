# Lista 4, ejercicio 273: comprobación por λ-clausuras

## Ejercicio 272(b): `(ab)*a`

| Cadena | λ-clausura y recorrido | Aceptación | Esperada | Coincide |
|---|---|---|---|---|
| `aba` | λ-cl(q0)={q0, q4, q5, q6}; a→{q1, q7}→λ-cl {q1, q2, q7}; b→{q3}→λ-cl {q0, q3, q5, q6}; a→{q1, q7}→λ-cl {q1, q2, q7} | Sí | Sí | Sí |
| `ab` | λ-cl(q0)={q0, q4, q5, q6}; a→{q1, q7}→λ-cl {q1, q2, q7}; b→{q3}→λ-cl {q0, q3, q5, q6} | No | No | Sí |
| `babb` | λ-cl(q0)={q0, q4, q5, q6}; b→∅→λ-cl ∅; a→∅→λ-cl ∅; b→∅→λ-cl ∅; b→∅→λ-cl ∅ | No | No | Sí |
| `abab` | λ-cl(q0)={q0, q4, q5, q6}; a→{q1, q7}→λ-cl {q1, q2, q7}; b→{q3}→λ-cl {q0, q3, q5, q6}; a→{q1, q7}→λ-cl {q1, q2, q7}; b→{q3}→λ-cl {q0, q3, q5, q6} | No | No | Sí |

## Ejercicio 272(c): `(a+b)*abb`

| Cadena | λ-clausura y recorrido | Aceptación | Esperada | Coincide |
|---|---|---|---|---|
| `aba` | λ-cl(q0)={q0, q2, q4, q6, q7, q8}; a→{q1, q9}→λ-cl {q0, q1, q10, q2, q4, q5, q7, q8, q9}; b→{q11, q3}→λ-cl {q0, q11, q12, q2, q3, q4, q5, q7, q8}; a→{q1, q9}→λ-cl {q0, q1, q10, q2, q4, q5, q7, q8, q9} | No | No | Sí |
| `ab` | λ-cl(q0)={q0, q2, q4, q6, q7, q8}; a→{q1, q9}→λ-cl {q0, q1, q10, q2, q4, q5, q7, q8, q9}; b→{q11, q3}→λ-cl {q0, q11, q12, q2, q3, q4, q5, q7, q8} | No | No | Sí |
| `babb` | λ-cl(q0)={q0, q2, q4, q6, q7, q8}; b→{q3}→λ-cl {q0, q2, q3, q4, q5, q7, q8}; a→{q1, q9}→λ-cl {q0, q1, q10, q2, q4, q5, q7, q8, q9}; b→{q11, q3}→λ-cl {q0, q11, q12, q2, q3, q4, q5, q7, q8}; b→{q13, q3}→λ-cl {q0, q13, q2, q3, q4, q5, q7, q8} | Sí | Sí | Sí |
| `abab` | λ-cl(q0)={q0, q2, q4, q6, q7, q8}; a→{q1, q9}→λ-cl {q0, q1, q10, q2, q4, q5, q7, q8, q9}; b→{q11, q3}→λ-cl {q0, q11, q12, q2, q3, q4, q5, q7, q8}; a→{q1, q9}→λ-cl {q0, q1, q10, q2, q4, q5, q7, q8, q9}; b→{q11, q3}→λ-cl {q0, q11, q12, q2, q3, q4, q5, q7, q8} | No | No | Sí |

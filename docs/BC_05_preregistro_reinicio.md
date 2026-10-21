# BC · Pre-registro · la regla del reinicio

Escrito **antes** de correr. Regla transcrita en `BC_01` §20.

# 1 · Qué se contrasta

El disparo de **transición** que describen, y que `BC_04` no implementaba:

```
temporalidades mayores alineadas en dirección X
temporalidad de ejecución con rango vivo en dirección −X   (en contra)
   ->  aparece una REINICIADA en dirección X en la de ejecución
   ->  entrada en ese momento
```

> «Buscamos una reiniciada alcista en 1H. Cuando aparece, esa temporalidad
> vuelve a alinearse con el contexto de 4H y 1D, y ya tenemos una estructura
> mucho más limpia.»

Y el **filtro negativo**, que se mide aparte:

> «Si en esa temporalidad que tenemos cerrada al alza se nos crea una reiniciada
> bajista, debemos protegernos, porque las demás temporalidades todavía no han
> cerrado.»

# 2 · Definiciones mecánicas

**Reiniciada.** Hay un rango vivo en la temporalidad de ejecución con dirección
−X y vela base con extremos `base_hi`/`base_lo`. El precio se lleva el extremo
**contrario** al que definió ese rango:

```
rango vivo BAJISTA   ->  reiniciada ALCISTA si  high > base_hi
rango vivo ALCISTA   ->  reiniciada BAJISTA si  low  < base_lo
```

Dos lecturas, las dos se prueban y las dos se reportan:

| | condición |
|---|---|
| **R1 · simple** | basta con llevarse el extremo contrario |
| **R2 · estricta** | además el cierre vuelve dentro del cuerpo de la vela base |

**Alineación de las mayores.** Su ejemplo usa 1D y 4H. Se exige que **al menos
dos** temporalidades de contexto (1D, 12H, 4H) tengan objetivo vivo en la misma
dirección X. Se reporta también con una sola, como secundario.

**Entrada** al cierre de la vela que produce la reiniciada.
**Stop** en el extremo de esa misma vela, más un tick.
**Objetivo** el más cercano de los objetivos alineados de temporalidad mayor.
**Filtro** R:R ≥ 3, como en `BC_02` §7.1.
**Guarda de ejecutabilidad** stop ≥ 3× el coste, como en `BC_04` §2.

# 3 · La configuración principal, elegida ahora y por qué

Sigo sin poder calibrar el huso: la calibración de `BC_04` no discriminó, y no
han llegado más operaciones fechadas. Así que **fijo una configuración principal
por argumento, no por resultado**:

**Huso UTC · lectura B.**

- **UTC** porque es la rejilla neutra: no supone ningún huso de bróker ni de
  plaza. Cualquier otra elección sería una suposición sobre ellos.
- **Lectura B** (barre y cierra dentro del cuerpo) porque es **su definición
  escrita**: «la manipulación, donde el precio liquida esa vela base y cierra
  dentro del cuerpo creando un rango». Es la frase más explícita de todo el
  material sobre qué crea un rango.

**Y hago constar que en `BC_04` la mejor celda fue UTC + lectura A.** Elijo
deliberadamente **otra**, la que sostiene su texto, para que nadie —yo el
primero— pueda decir que he heredado el ganador de la prueba anterior.

Las otras once celdas se reportan como secundarias, con su descuento por
contrastes múltiples.

# 4 · Criterio principal

Sobre **UTC + B**, desarrollo **2020-2023**, cinco instrumentos:

**Hay algo si el intervalo de confianza al 95 % de la R neta por operación
excluye el cero por el lado positivo.** Un solo contraste.

## 4.1 · Potencia, declarada ahora

La regla es más restrictiva que la de `BC_04`: exige que la de ejecución esté
**en contra** y luego se dé la vuelta. Es previsible que salgan pocas.

- **n < 100** → infrapotenciada. Se informa el número y **no se concluye nada**.
- **n ≥ 100** → se aplica el criterio del punto 4.

# 5 · El filtro negativo, medido aparte

No es una regla de entrada sino de abstención. Se mide sobre las operaciones de
`BC_04`, celda a celda:

> ¿Rinden peor las operaciones que se tomaron **habiendo una reiniciada en
> contra** con las mayores todavía sin rango creado?

Si su filtro sirve, esas deberían ser claramente peores que el resto. Es un
contraste de **diferencia entre grupos**, con umbral |z| > 2,58.

# 6 · Confirmación

2024-2026 sigue **cerrado**. Solo se abre si el criterio principal se cumple, y
con las dos condiciones de `BC_03` §5: el signo se mantiene y la ventaja neta es
al menos la mitad.

# 7 · Qué invalidaría

- n < 100 → infrapotenciada, sin conclusión.
- |z| > 5 en cualquier celda → **error propio hasta demostrar lo contrario**. Ya
  van cuatro esta semana; la regla se mantiene.

# 8 · Compromiso

Una pasada. Si sale que no, se escribe que no, y se dice qué parte de la lectura
mecánica es mía.

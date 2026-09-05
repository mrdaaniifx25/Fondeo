# BC · Dos fallos en el motor, y la rejilla corregida

Encontrados al traducir la máquina de estados a Pine para el indicador. Traducir
a otro lenguaje obliga a releer línea por línea, y ahí salieron.

**Adelanto del veredicto: la conclusión de `BC_04` no cambia.** Siguen siendo
0 de 12 celdas por encima del umbral y las doce medias recortadas siguen en
negativo. Lo que sí cambia es **qué se puede decir que se ha medido**.

---

# 1 · El reinicio era inalcanzable

`bc/nucleo.py`, función `vida()`, versión anterior:

```python
otra   = (l[i] < cur.base_lo) if cur.lado > 0 else (h[i] > cur.base_hi)  # doble liq.
contra = (h[i] > cur.base_hi) if cur.lado > 0 else (l[i] < cur.base_lo)  # "reinicio"
```

En un rango alcista el objetivo **es** `base_hi`. La rama de `contra` solo se
evalúa cuando el objetivo no se ha alcanzado, es decir cuando `h[i] < base_hi`;
y pide `h[i] > base_hi`. Nunca puede cumplirse. Lo mismo, simétrico, en bajista.

Comprobado sobre EURUSD 2020-2026:

| marco | rangos | reiniciados |
|---|---|---|
| 1D | 272 | **0** |
| 12H | 506 | **0** |
| 4H | 1.334 | **0** |
| 1H | 6.463 | **0** |

Cero de 8.575. Los estados REINICIADO y DESCARTADO no se ejecutaron nunca.

## Lo que dice el material, que es otra cosa

`BC_01` §3, los cuatro reinicios del 24 de agosto. En un rango alcista —que se
activó **barriendo el bajo**, con objetivo en el alto— el reinicio es **volver a
llevarse ese mismo bajo**, no el contrario:

- **Caso 1**, vuelve a tomar el bajo y **cierra dentro** → doble toma de
  liquidez, el rango sigue vivo.
- **Caso 2**, vuelve a tomar el bajo y **cierra fuera** de la estructura →
  descartado.

O sea que doble liquidez y descarte **son el mismo suceso resuelto de dos
formas**, y la versión anterior los trataba como sucesos distintos, uno de ellos
imposible. `bc/reinicio.py` ya lo tenía bien escrito («rango alcista, se lleva el
bajo»); el desacuerdo entre los dos módulos es lo que dio el aviso.

Corregido. Ahora:

| marco | rangos | completados | descartados | relevados |
|---|---|---|---|---|
| 1D | 272 | 135 | 105 | 32 |
| 12H | 506 | 234 | 196 | 76 |
| 4H | 1.334 | 665 | 486 | 182 |

# 2 · El fallo grave: `vivo` no se consultaba

`bc/motor.py`, `objetivos_vivos()`, versión anterior:

```python
t = pd.DataFrame([dict(ts=r.nace, lado=r.lado, obj=r.objetivo, tomas=r.tomas)
                  for r in rangos]).sort_values("ts")
m = pd.merge_asof(..., direction="backward")
```

Monta la tabla con **todos** los rangos y devuelve el último creado antes de
cada instante. El atributo `vivo` no aparece por ningún lado. Idéntico en
`nucleo.mapa_vivos()`.

La función se llama «objetivos vivos» y no devolvía objetivos vivos: devolvía
**el último rango creado, completado o descartado incluido**. Un objetivo
alcanzado tres días antes seguía contando como contexto de temporalidad mayor.

**Consecuencia: la máquina de estados no ha influido nunca en ningún resultado
medido.** El contexto siempre fue «el último rango creado en ese marco», y por
eso el fallo 1 era inocuo por sí solo — corregirlo no movía ni una operación,
porque el estado que corregía no se leía.

Corregido apuntando el instante de muerte en el `Rango` y enmascarando el
contexto a partir de ahí.

# 3 · La rejilla, corregida

Mismas doce celdas, mismo periodo 2020-2023, mismo umbral |z| > 2,87.

| huso | lec | n antes | **n ahora** | R bruta antes | **R bruta ahora** | R neta antes | **R neta ahora** | **recortada** |
|---|---|---|---|---|---|---|---|---|
| UTC | A | 1.602 | 512 | +0,280 | +0,145 | +0,133 | −0,003 | −0,093 |
| UTC | B | 7.597 | 2.911 | +0,059 | +0,123 | −0,077 | −0,019 | −0,061 |
| UTC | C | 405 | **10** | −0,093 | −0,592 | −0,239 | −0,717 | −0,752 |
| NY | A | 1.753 | 364 | +0,082 | +0,091 | −0,066 | −0,057 | −0,125 |
| NY | B | 7.834 | 2.922 | +0,046 | +0,125 | −0,090 | −0,016 | −0,073 |
| NY | C | 377 | **6** | +0,008 | −0,320 | −0,138 | −0,512 | −0,545 |
| Madrid | A | 1.584 | 504 | +0,158 | +0,181 | +0,010 | +0,040 | −0,094 |
| Madrid | B | 7.894 | 3.060 | +0,079 | +0,024 | −0,059 | −0,120 | −0,153 |
| Madrid | C | 326 | **8** | −0,163 | −0,244 | −0,307 | −0,361 | −0,414 |
| Broker | A | 1.605 | 481 | +0,181 | +0,251 | +0,032 | +0,109 | −0,025 |
| Broker | B | 7.773 | 3.005 | +0,084 | −0,038 | −0,054 | −0,181 | −0,215 |
| Broker | C | 314 | **6** | −0,063 | +0,008 | −0,211 | −0,116 | −0,166 |

```
celdas con |z| > 2,87 :  0 de 12      (igual que antes)
medias recortadas en negativo : 12 de 12      (igual que antes)
```

## Qué ha cambiado de verdad

**El volumen cae a un tercio.** De 39.064 operaciones a 13.789. Exigir que el
objetivo de contexto siga vivo elimina dos de cada tres entradas. Eran entradas
hacia objetivos ya alcanzados.

**La ventaja bruta de las celdas B sube.** +0,059 → +0,123 en UTC, +0,046 →
+0,125 en NY. La máquina de estados **sí aporta algo en bruto**: quitar las
entradas hacia objetivos muertos mejora la media. No lo suficiente para cubrir
el coste, pero el signo es el que el método predice.

**La lectura C desaparece.** De 314-405 operaciones a 6-10. Exigir apertura
fuera *y* cierre dentro *y* contexto vivo no deja casi nada en divisas. Con esa
n no se puede decir nada, ni bueno ni malo, y así queda anotado.

# 4 · Qué hay que retirar de lo dicho antes

No la conclusión. **La afirmación de haber probado la máquina de estados.**

En `BC_04` escribí que se había medido la especificación de `BC_02`, que incluye
los cinco estados de §3.4. Es falso: se midió una versión sin estados, donde el
contexto era el último rango creado. La conclusión negativa aguanta —y ahora con
más motivo, porque se sostiene también con el motor correcto— pero durante dos
semanas he tenido en el repositorio un resultado descrito como algo que no era.

Es el tercer fallo de la misma familia en este proyecto: mirar al futuro en
`contexto_diario.py`, la inversión ingenua del control espejo, y ahora este. Los
tres consistían en que **el código no hacía lo que su nombre decía**, y los tres
salieron al releer despacio, no al mirar los resultados. Los resultados no
tenían mala pinta en ninguno de los tres casos.

# 5 · Efecto sobre el resto del repositorio

- **`BC_06` (regla de reinicio).** Usa `bc/reinicio.py`, que tenía la definición
  correcta, pero llama a `M.objetivos_vivos` para el contexto → **afectado por el
  fallo 2**. Pendiente de volver a correr.
- **`RESULTADOS_crt_temporalidad.md`** (el hallazgo del gradiente por
  temporalidad) usa `bt/`, motor independiente → no afectado.
- Todo lo demás en `bt/` es anterior y no toca `bc/`.

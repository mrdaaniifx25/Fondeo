# Juntarlo todo en una sola estrategia · no suma

Pregunta suya: *«si todo lo que te he pasado lo juntas y haces una única
estrategia, ¿no sacas nada?»*. Se prueba apilando lo que había sobrevivido sobre
la base que pasó el preregistro (`RESULTADOS_pase_smc71.md`).

## El apilado

| | M15 | M30 |
|---|---|---|
| la estrategia sola | +0,124 (z +2,55) | +0,129 (z +1,90) |
| + fractal barrido en hora de sesión | **+0,036** | **+0,336** (z +3,36) |
| + solo instrumentos de coste barato | +0,134 | +0,049 |
| las dos cosas juntas | +0,080 | +0,192 |

El filtro horario **hunde M15 y triplica M30**. El de instrumento hace lo
contrario. Un filtro real no se comporta así.

## La celda buena aguantaba sus propias comprobaciones

M30 + hora: n=284, acierto 38,7 %, bruta +0,336, **neta +0,229 (z +2,31)**.

```
  positiva en 6 de 7 instrumentos
  las dos épocas positivas: +0,234 (20-22) y +0,399 (23-26)
  quitando el mejor instrumento: +0,261, z +2,41, neta +0,167
```

Nada de eso la salva. La comprobación que la mata es otra.

## Lo que la mata: los perfiles horarios están invertidos

R bruta según la hora en que se formó el fractal barrido:

| bloque | M15 | M30 |
|---|---|---|
| 00-04 | +0,078 | **−0,138** |
| 04-08 | **+0,346** | +0,207 |
| 08-12 | +0,064 | **+0,351** |
| 12-16 | **−0,055** | **+0,324** |
| 16-20 | +0,108 | **−0,100** |
| 20-24 | **+0,293** | −0,008 |

**Casi anticorrelados.** Las mejores horas de M15 son las flojas de M30, y la peor
de M15 es de las dos mejores de M30. Si el efecto fuera real los perfiles se
parecerían. Es ruido en las dos, y el +0,229 era elegir una celda de doce.

## Consecuencia hacia atrás

Esto también **debilita el hallazgo horario anterior** de
`RESULTADOS_gpso_directo.md` (z +3,09, 4/4 instrumentos, sobre la estrategia del
fibo de H1). Dos estrategias distintas dan perfiles horarios incompatibles. No lo
retiro —allí la estructura por bloques era coherente y salía en 4 de 4— pero deja
de ser algo en lo que apoyarse.

## La respuesta

**Juntarlo no suma.** Lo que hay es la base sola:

```
  la estrategia del 71 %, sin filtros añadidos
  M30:  568 ops · 32,7 % · bruta +0,129 · NETA +0,005
  M60:  246 ops · 34,6 % · bruta +0,191 · NETA +0,112
  pasó tres pruebas preregistradas y selladas
```

Todo lo que le apilo encima o no sobrevive o se contradice consigo mismo. Eso no
es un fracaso del apilado: es la señal de que ya no queda información en estos
datos y de que **cualquier cosa más que salga de aquí será ajuste**.

## Lo único que puede avanzar desde aquí

1. **Datos que no existan todavía**: los meses posteriores a julio de 2026.
2. **El coste real** de índices en su cuenta, que decide si el +0,005 y el +0,112
   son de verdad o son mi estimación.
3. **Operar en real**, pequeño, y medir.

## Reproducir

`TF=30 SUF=_c30 python3 bt/smc_71.py`

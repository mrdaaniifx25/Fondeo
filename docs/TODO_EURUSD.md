# Todo lo medido en EURUSD

El usuario señala que el operador hace **toda la estrategia en EURUSD**. Cierto.
Y también lo es todo lo de este documento.

EURUSD es el instrumento con **más datos del proyecto**: `data/eurusd_m1.parquet`,
**2.055.684 minutos**, 2021-01-03 a 2026-09-01, 5,7 años completos, cargados de
los ZIP que subió él. **199 de los scripts de `bt/` corren sobre ese fichero.**

Esta tabla no mide nada nuevo. Junta en un sitio lo que estaba repartido en
cuarenta documentos.

## La familia de los tres operadores, toda en EURUSD

| prueba | n | acierto | umbral | resultado | documento |
|---|---|---|---|---|---|
| su regla de barrido (M2, niveles H1, sus horas) | **29.959** | 33,4 % | 40,8 % | plano | `RESULTADOS_benjamin_regla.md` |
| la misma con sus correcciones | **14.637** | 32,8 % | 41,4 % | plano | `RESULTADOS_barrido_sesion_v2.md` |
| su regla en M15/H1, stop por ATR, 12 celdas | **~28.000** | — | — | plano | `RESULTADOS_benjamin_v3.md` |
| 14 variables al entrar, mejor decil **con trampa** | **29.614** | 38,2 % máx | 37,4 % | no llega | `RESULTADOS_techo_filtro.md` |
| modelo sobre las 14 a la vez, fuera de muestra | **24.679** | 31,5 % | 43,8 % | AUC 0,4945 | `RESULTADOS_techo_filtro.md` |
| R:R de 2:1 a 30:1, 21 celdas | **~30.000** | — | — | las 21 negativas | `RESULTADOS_rr_extremo.md` |
| su spec completa (PDH/PDL/PSH/PSL + H4 + H1 + M5) | **167** | 22,2 % | 38,9 % | peor que el azar | `RESULTADOS_liquidez_sesiones_v2.md` |
| niveles de sesión vivos de días anteriores | **10.138** barridos | 49,7 % | 50,0 % | una moneda | `RESULTADOS_liquidez_sesiones.md` |
| la regla de Asia escrita por él mismo | **2.080** | 30,8 % | — | negativo | `RESULTADOS_asia_nivel.md` |
| divergencia SMT con DAX y con oro | **6.122** | +0,8 pts | — | t = +0,68 | `RESULTADOS_smt.md` |
| AMD + FVG (corregido) | **587** | 63,8 % | — | −0,057 | `CORRECCION_objetivo_rebasado.md` |
| PSH solo, sin cadena | **340** | 29,1 % | 38,3 % | negativo | `RESULTADOS_psh_oro_dax.md` |
| máximo y mínimo del día previo | — | — | — | plano | `RESULTADOS_dia_previo.md` |
| soportes/resistencias H1 + EMA 50 en M5 | — | — | — | plano | `RESULTADOS_ema_sr.md` |
| timing multiframe M5/M15 | — | — | — | plano | `RESULTADOS_m5_timing.md` |

**Más de 175.000 operaciones medidas en EURUSD**, sólo en la familia que usan
los tres operadores.

## Los tres controles que hacen que esto no sea opinión

1. **Placebo de lados barajados.** En `rr_extremo`, a 12:1 y 20 días, la señal da
   razón acierto/azar **1,120** y barajar la dirección al azar da **1,120**.
   Idénticos al tercer decimal.
2. **Modelo fuera de muestra.** Un gradient boosting con 14 variables entrenado
   con el pasado y evaluado sobre el futuro da **AUC 0,4945** — por debajo de
   0,5. Las operaciones que señala como mejores aciertan **menos** que la media.
3. **Sus propios números.** Él dice que el SMT da «un 51 %»; la medición sobre
   6.122 operaciones da **50,8 %**. Y el historial que lee en pantalla de dos de
   sus cuentas da **33,3 % exacto**, el precio justo de un 1:2
   (`VERIFICACION_lozano.md`).

## Lo que nunca se midió en EURUSD, y por qué

Nada de esta familia. La única razón por la que algunas pruebas se llevaron a
oro y DAX fue **replicar fuera de muestra** lo que salía en EURUSD, que es lo
que manda el artículo 17 de su propia especificación.

Y el momento y el carry, que son lo único que funciona, no son intradía ni son
de EURUSD: son de 26 mercados y 632 meses (`RESULTADOS_momento_largo.md`,
`RESULTADOS_carry.md`). EURUSD es uno de ellos.

## Resumen en una línea

**No es que no lo haya probado en EURUSD. Es que EURUSD es exactamente donde
está probado, con más datos que en ningún otro sitio, y donde sale cero.**
